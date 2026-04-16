import psycopg2
from psycopg2.extras import execute_values
import logging
import os

class JobLoader:
    def __init__(self, db_url=None):
        self.db_url = db_url or os.getenv('DB_URL')
        self.logger = logging.getLogger(__name__)

    def _ensure_schema_exists(self, cur):
        """Checks if tables exist, and creates them from schema.sql if they don't."""
        try:
            cur.execute("SELECT 1 FROM jobs LIMIT 1")
        except psycopg2.errors.UndefinedTable:
            self.logger.info("Database tables missing. Initializing schema from schema.sql...")
            # We need to rollback the failed check transaction
            cur.connection.rollback()
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            if os.path.exists(schema_path):
                with open(schema_path, 'r') as f:
                    cur.execute(f.read())
                cur.connection.commit()
                self.logger.info("Schema initialized successfully.")
            else:
                self.logger.error(f"Schema file not found at {schema_path}")
                raise

    def load_jobs(self, cleaned_jobs):
        """Loads cleaned jobs and job-skill relationships into PostgreSQL."""
        if not self.db_url:
            self.logger.warning("No DB_URL provided. Skipping loading.")
            return

        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    # Ensure tables exist
                    self._ensure_schema_exists(cur)

                    # Batch Insert Jobs (UPSERT)
                    job_values = [
                        (
                            job['job_id'], job['title'], job['role'], job['company'], job['location'],
                            job['salary_min'], job['salary_max'], job['avg_salary'],
                            job['date_posted']
                        )
                        for job in cleaned_jobs
                    ]

                    insert_job_query = """
                        INSERT INTO jobs (job_id, title, role, company, location, salary_min, salary_max, avg_salary, date_posted)
                        VALUES %s
                        ON CONFLICT (job_id) DO UPDATE SET
                            title = EXCLUDED.title,
                            role = EXCLUDED.role,
                            company = EXCLUDED.company,
                            location = EXCLUDED.location,
                            salary_min = EXCLUDED.salary_min,
                            salary_max = EXCLUDED.salary_max,
                            avg_salary = EXCLUDED.avg_salary,
                            date_posted = EXCLUDED.date_posted;
                    """
                    execute_values(cur, insert_job_query, job_values)

                    # Loading Skills (assuming they are already seeded or exist)
                    # We need to map labels to skill_id
                    cur.execute("SELECT skill_id, skill_name FROM skills")
                    skill_map = {name: sid for sid, name in cur.fetchall()}

                    # Batch Insert Job-Skill Relationships
                    job_skill_values = []
                    for job in cleaned_jobs:
                        for skill in job['skills']:
                            if skill in skill_map:
                                job_skill_values.append((job['job_id'], skill_map[skill]))

                    if job_skill_values:
                        insert_job_skill_query = """
                            INSERT INTO job_skills (job_id, skill_id)
                            VALUES %s
                            ON CONFLICT (job_id, skill_id) DO NOTHING;
                        """
                        execute_values(cur, insert_job_skill_query, job_skill_values)

                    conn.commit()
                    self.logger.info(f"Successfully loaded {len(job_values)} jobs.")
        except Exception as e:
            self.logger.error(f"Error loading to Postgres: {e}")
            raise

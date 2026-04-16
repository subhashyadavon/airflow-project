-- Drop tables if they exist
DROP TABLE IF EXISTS job_skills CASCADE;
DROP TABLE IF EXISTS skills CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;

-- Jobs table
CREATE TABLE jobs (
    job_id VARCHAR(50) PRIMARY KEY,
    title TEXT NOT NULL,
    role VARCHAR(100),
    company TEXT,
    location TEXT,
    salary_min NUMERIC,
    salary_max NUMERIC,
    avg_salary NUMERIC,
    date_posted TIMESTAMPTZ,
    source VARCHAR(50) DEFAULT 'Adzuna'
);

-- Skills table
CREATE TABLE skills (
    skill_id SERIAL PRIMARY KEY,
    skill_name VARCHAR(50) UNIQUE NOT NULL
);

-- Job Skills (Bridge table)
CREATE TABLE job_skills (
    job_id VARCHAR(50) REFERENCES jobs(job_id) ON DELETE CASCADE,
    skill_id INT REFERENCES skills(skill_id) ON DELETE CASCADE,
    PRIMARY KEY (job_id, skill_id)
);

-- Seed skills table with initial keywords
INSERT INTO skills (skill_name)
SELECT DISTINCT UNNEST(ARRAY['Python', 'SQL', 'AWS', 'Azure', 'GCP', 'Postgres', 'MySQL', 'MongoDB',
    'Airflow', 'Spark', 'Kafka', 'Docker', 'Kubernetes', 'React', 'Node.js',
    'Java', 'C#', 'C++', 'Go', 'Rust', 'Tableau', 'Power BI', 'Snowflake',
    'dbt', 'Redshift', 'BigQuery', 'GraphQL', 'REST', 'TensorFlow', 'PyTorch',
    'Scikit-learn', 'Pandas', 'NumPy', 'Selenium', 'Scrapy'])
ON CONFLICT (skill_name) DO NOTHING;

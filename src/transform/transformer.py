import re
import logging
from src.transform.skills_list import TECH_SKILLS


class JobTransformer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def clean_jobs(self, raw_data):
        """Cleans and extracts skills from raw job data."""
        results = raw_data.get("results", [])
        cleaned_jobs = []

        for job in results:
            job_id = str(job.get("id"))
            title = job.get("title")
            company = job.get("company", {}).get("display_name", "Unknown")
            location = job.get("location", {}).get("display_name", "Unknown")
            salary_min = job.get("salary_min")
            salary_max = job.get("salary_max")
            date_posted = job.get("created")
            description = job.get("description", "")

            # Basic Validation: No null job titles
            if not title:
                self.logger.warning(f"Job {job_id} has no title. Skipping.")
                continue

            # Normalized salary (average)
            avg_salary = None
            if salary_min and salary_max:
                avg_salary = (float(salary_min) + float(salary_max)) / 2
            elif salary_min:
                avg_salary = float(salary_min)
            elif salary_max:
                avg_salary = float(salary_max)

            extracted_skills = self.extract_skills(description)

            cleaned_jobs.append(
                {
                    "job_id": job_id,
                    "title": title,
                    "company": company,
                    "location": location,
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "avg_salary": avg_salary,
                    "date_posted": date_posted,
                    "skills": extracted_skills,
                }
            )

        return cleaned_jobs

    def extract_skills(self, text):
        """Extracts skills using case-insensitive regex matching."""
        if not text:
            return []

        found_skills = []
        for skill in TECH_SKILLS:
            pattern = rf"\b{re.escape(skill)}\b"
            if re.search(pattern, text, re.IGNORECASE):
                found_skills.append(skill)
        return found_skills

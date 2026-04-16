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

            extracted_skills = self.extract_skills(f"{title} {description}")
            extracted_role = self.extract_role(title)

            cleaned_jobs.append(
                {
                    "job_id": job_id,
                    "title": title,
                    "role": extracted_role,
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

        # Strip HTML tags
        clean_text = re.sub(r'<[^>]*>', ' ', text)
        
        found_skills = []
        for skill in TECH_SKILLS:
            pattern = rf"(?<!\w){re.escape(skill)}(?!\w)"
            if re.search(pattern, clean_text, re.IGNORECASE):
                found_skills.append(skill)
        return found_skills

    def extract_role(self, title):
        """Extracts a normalized role from the job title."""
        roles = {
            "Data Scientist": [r"data scientist", r"machine learning", r"ml engineer", r"ai engineer"],
            "Data Engineer": [r"data engineer", r"etl", r"data warehouse", r"pipeline"],
            "DevOps Engineer": [r"devops", r"site reliability", r"sre", r"cloud engineer", r"infrastructure"],
            "Software Engineer": [r"software engineer", r"developer", r"full stack", r"backend", r"frontend"],
            "Product Manager": [r"product manager", r"product owner"],
            "Data Analyst": [r"data analyst", r"business intelligence", r"bi analyst"],
            "Cybersecurity": [r"security", r"cybersecurity", r"infosec"],
            "UI/UX Designer": [r"designer", r"ui/ux", r"user experience", r"product designer"],
            "Intern": [r"intern", r"co-op", r"internship", r"student"]
        }

        for role_name, patterns in roles.items():
            for pattern in patterns:
                if re.search(pattern, title, re.IGNORECASE):
                    return role_name
        
        return "Other"

import os
import requests
import logging

class AdzunaExtractor:
    def __init__(self, app_id=None, app_key=None, country='ca'):
        self.app_id = app_id or os.getenv('ADZUNA_APP_ID')
        self.app_key = app_key or os.getenv('ADZUNA_APP_KEY')
        self.country = country
        self.base_url = f"https://api.adzuna.com/v1/api/jobs/{self.country}/search/1"
        self.logger = logging.getLogger(__name__)

    def fetch_jobs(self, what="software engineer", where="Winnipeg", results_per_page=10):
        if not self.app_id or not self.app_key:
            raise ValueError("No Adzuna credentials provided. ADZUNA_APP_ID and ADZUNA_APP_KEY must be set.")

        params = {
            'app_id': self.app_id,
            'app_key': self.app_key,
            'results_per_page': results_per_page,
            'what': what,
            'where': where,
            'content-type': 'application/json'
        }

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Error fetching from Adzuna: {e}")
            raise


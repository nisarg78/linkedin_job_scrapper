# Scrapping Logic
import requests
import json
import sqlite3
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
from urllib.parse import quote
from langdetect import detect, LangDetectException
import pandas as pd


def load_config(file_name):
    """Load configuration from a JSON file."""
    with open(file_name) as f:
        return json.load(f)


class JobScraper:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()  # Use session for connection pooling

    def get_with_retry(self, url, retries=3, delay=1):
        """Fetch a URL with retries."""
        for attempt in range(retries):
            try:
                response = self.session.get(
                    url,
                    headers=self.config['headers'],
                    proxies=self.config.get('proxies'),
                    timeout=5
                )
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1}/{retries} failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(delay)
        print(f"Failed to retrieve {url} after {retries} attempts.")
        return None

    def parse_job_cards(self, soup):
        """Extract job details from the job card page."""
        job_cards = []
        if not soup:
            return job_cards

        for item in soup.find_all('div', class_='base-search-card__info'):
            title = item.find('h3').text.strip()
            company = item.find('a', class_='hidden-nested-link')
            location = item.find('span', class_='job-search-card__location')
            parent_div = item.parent
            job_id = parent_div['data-entity-urn'].split(':')[-1]
            job_url = f"https://www.linkedin.com/jobs/view/{job_id}/"

            date_tag = item.find('time')
            date = date_tag['datetime'] if date_tag else ''

            job_cards.append({
                'title': title,
                'company': company.text.strip() if company else '',
                'location': location.text.strip() if location else '',
                'date': date,
                'job_url': job_url,
                'applied': 0,
                'hidden': 0,
                'interview': 0,
                'rejected': 0
            })
        return job_cards

    def fetch_job_descriptions(self, job_url):
        """Retrieve the detailed job description."""
        soup = self.get_with_retry(job_url)
        if not soup:
            return "Description not available."

        description_div = soup.find('div', class_='description__text--rich')
        if description_div:
            return description_div.get_text(separator='\n').strip()
        return "Description not available."

    def filter_jobs(self, jobs):
        """Filter out irrelevant jobs based on config rules."""
        config = self.config
        filtered_jobs = [
            job for job in jobs
            if all(
                word.lower() not in job['title'].lower() for word in config['title_exclude']
            )
            and detect(job['title']) in config['languages']
        ]
        return filtered_jobs

    def save_to_database(self, conn, table_name, data):
        """Save job data to an SQLite database."""
        df = pd.DataFrame(data)
        if not df.empty:
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"Saved {len(df)} records to {table_name}.")
        else:
            print(f"No data to save for {table_name}.")


def main(config_file):
    # Load configuration
    config = load_config(config_file)

    # Initialize scraper
    scraper = JobScraper(config)

    # Create database connection
    conn = sqlite3.connect(config['db_path'])

    all_jobs = []
    for query in config['search_queries']:
        keywords = quote(query['keywords'])
        location = quote(query['location'])

        for page in range(config['pages_to_scrape']):
            url = (
                f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
                f"?keywords={keywords}&location={location}&start={25 * page}"
            )
            soup = scraper.get_with_retry(url)
            if not soup:
                continue

            jobs = scraper.parse_job_cards(soup)
            all_jobs.extend(jobs)

    # Filter and save jobs
    filtered_jobs = scraper.filter_jobs(all_jobs)
    scraper.save_to_database(conn, config['jobs_tablename'], filtered_jobs)

    print("Job scraping completed successfully.")


if __name__ == "__main__":
    config_file = 'config.json'
    main(config_file)

# LinkedIn Job Scraper

This is a Python application designed to scrape job postings from LinkedIn, filter out irrelevant results, and store them in a SQLite database. It includes a user-friendly web interface to manage job postings and now supports **OpenAI integration** for generating personalized cover letters.

---

## 🛠️ Features

- **Efficient Scraping**: Fetches LinkedIn job postings based on configurable keywords, locations, and filters.
- **Advanced Filtering**: Exclude jobs by title, company, or description keywords. Include only relevant job titles and languages.
- **Database Storage**: Saves job data into an SQLite database for persistence.
- **Web Interface**: Manage your job search with a Flask-based UI:
  - Mark jobs as `applied`, `rejected`, `interview`, or `hidden`.
  - View job statuses at a glance with color-coded tags.
- **OpenAI Integration**: Automatically generate tailored cover letters using OpenAI's GPT models.
- **Duplicate Elimination**: Avoids redundant listings by removing duplicates based on LinkedIn IDs.
- **Random Delay Mechanism**: Mimics human-like browsing to reduce the risk of being rate-limited by LinkedIn.
- **Scraping Logs**: Logs every action taken during scraping, including retry attempts, failed requests, and successful data extraction.

---

## ⚠️ Important Note

Scraping LinkedIn violates its [Terms of Service](https://www.linkedin.com/legal/user-agreement). Use this project at your own risk. It is highly recommended to use proxy servers to avoid being blocked. Refer to the **Configuration** section for setting up proxies.

---

## 📋 Prerequisites

- Python 3.6 or higher
- Libraries: Flask, Requests, BeautifulSoup, Pandas, SQLite3, Pysocks
- OpenAI API Key (for cover letter generation)

---

## 🚀 Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/nisarg78/linkedin_job_scrapper/edit/main/README.md
cd linkedin-job-scraper
```

### Step 2: Install Required Packages
```
pip install -r requirements.txt
```

### Step 3: Configure config.json
Create a config.json file in the root directory. Refer to the Configuration section below for details or use config_example.json as a template.

### Step 4: Run the Scraper
```
python main.py
```

### Step 5: Launch the Web Interface
```
python app.py
```

- Access the web interface at: http://127.0.0.1:5000

## 📊 Usage

### Scraper (`main.py`)

Scrapes job postings from LinkedIn using search queries defined in `config.json`. It filters out irrelevant results based on title, description, or company keywords and stores the job postings in an SQLite database.

Run the scraper with:

```
python main.py
```

## Web Interface (`app.py`)

Provides a UI to manage and track job applications:

- **Applied Jobs**: Highlighted in blue.
- **Rejected Jobs**: Highlighted in red.
- **Interview Jobs**: Highlighted in green.
- **Hidden Jobs**: Removed from the list.

Launch the UI with:

```bash
python app.py
```

## ⚙️ Configuration

The `config.json` file contains the application's settings. Here's an overview of the configuration options:

### General Settings

- **proxies**: Proxy settings to avoid rate limits. Set `http` and `https` with valid proxy URLs.
- **headers**: Set the `User-Agent` header to mimic a browser. Use [WhatIsMyUserAgent](https://www.whatismybrowser.com/detect/what-is-my-user-agent) to find yours.
- **OpenAI_API_KEY**: API key for OpenAI (optional, required for cover letter generation).
- **resume_path**: Path to your resume in PDF format for generating cover letters.
- **jobs_tablename**: Table name for storing job data in the database.
- **filtered_jobs_tablename**: Table name for storing filtered job postings.
- **db_path**: Path to the SQLite database file.
- **pages_to_scrape**: Number of LinkedIn pages to scrape for each query.
- **rounds**: Number of scraping rounds to repeat (LinkedIn may show different results over time).

### Search Filters

- **search_queries**: Array of search objects with keywords and location.
- **title_include**: Include jobs with these keywords in their title.
- **title_exclude**: Exclude jobs with these keywords in their title.
- **company_exclude**: Exclude jobs from specific companies.
- **languages**: Only include job postings in specific languages (e.g., `"en"` for English).
- **desc_words**: Exclude jobs based on keywords in their descriptions.
- **timespan**: Filter jobs by time posted (e.g., `r604800` for the past week).

## 📝 Scraping Logs

The application logs all scraping activities, including:

- **Retry Attempts**: Tracks retries for failed requests.
- **Errors**: Records HTTP errors like 429 (Too Many Requests).
- **Successful Scrapes**: Logs the number of job postings extracted per query and page.

### Sample Log Output:

```rust
Attempt 1/3 failed for URL: https://www.linkedin.com/jobs/api...
Attempt 2/3 failed for URL: https://www.linkedin.com/jobs/api...
Attempt 3/3 succeeded for URL: https://www.linkedin.com/jobs/api...
Saved 154 records to jobs.

Logs can be found in `scraper.log`.

## 📅 Planned Features

- Add functionality to:
  - Unhide jobs.
  - Unmark "applied" or "rejected" jobs.
  - Sorting options in the web interface:
    - By date added to the database.
    - By LinkedIn's "date posted."
- Front-end configuration for search queries and scraping execution.

## 🤝 Contributing

Contributions are welcome! If you’d like to improve this project, feel free to open an issue or submit a pull request.

### How to Contribute:
1. Fork the repository.
2. Clone your fork to your local machine.
3. Create a new branch for your changes.
4. Implement your feature or fix a bug.
5. Commit your changes and push them to your fork.
6. Create a pull request to the main repository.

We welcome all contributions that improve the functionality, performance, or usability of this project. Please ensure that your changes are well-tested, and provide clear explanations in your pull request.

## 📜 License

This project is licensed under the MIT License. See the LICENSE file for details.

---

# workatycstartup

A semantic search engine over YC job portal (https://www.workatastartup.com/jobs).

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Download ChromeDriver:
   - Visit [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
   - Download the version that matches your Chrome browser
   - Update the path in `scraper.py` to point to your ChromeDriver location:

```python
service = Service('path/to/your/chromedriver')
```

## Running the Scraper

```bash
python scraper.py
```

The scraper will:

1. Collect all job listings from Work at a Startup
2. Extract company and job details
3. Scrape founder information from company profile pages
4. JSON data returned from scraper is used for VectorDB to do semantic searching

## Data Format

The scraper outputs JSON data with the following structure:

```json
{
  "company_name": "Example Corp",
  "batch": "W24",
  "description": "Company description here",
  "company_link": "https://www.workatastartup.com/companies/example",
  "job_name": "Senior Software Engineer",
  "job_link": "https://www.workatastartup.com/jobs/12345",
  "job_type": "Full-time",
  "location": "San Francisco, CA",
  "tech_stack": "Python, React, AWS",
  "founders": [
    {
      "name": "Jane Doe",
      "linkedin_url": "https://www.linkedin.com/in/janedoe",
      "bio": "Previously worked at..."
    }
  ]
}
```

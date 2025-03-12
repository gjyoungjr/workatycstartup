from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
import random

def configure_webdriver():
    """Return a configured headless Chrome webdriver."""
    options = Options()
    options.add_argument('--headless')
    service = Service('/Users/gilbertyoung/Downloads/chromedriver-mac-arm64/chromedriver')
    return webdriver.Chrome(service=service, options=options)

def split_company_and_batch(text):
    """Split company name and batch from formatted text."""
    parts = text.split('\u00a0')
    return (parts[0].strip(), parts[1].strip('()')) if len(parts) == 2 else (text, None)

def scrape_job_listings(url):
    """Scrape job listings from the provided URL."""
    driver = configure_webdriver()
    job_cards_html = []
    prev_count = 0

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        while True:
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            try:
                wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'Loader')))
            except:
                pass

            time.sleep(random.uniform(2, 5))
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            job_cards = soup.find_all('div', class_='w-full bg-beige-lighter mb-2 rounded-md p-2 border border-gray-200 flex')
            new_count = len(job_cards)

            if new_count == prev_count:
                break

            job_cards_html.extend(map(str, job_cards[prev_count:new_count]))
            prev_count = new_count

    finally:
        driver.quit()

    return job_cards_html

def parse_job_card(html):
    """Extract job details from job card HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    job_listing = {}

    # Extract company name, batch, and description
    company_details_tag = soup.find('div', class_="company-details")
    if company_details_tag:
        company_name_tag = company_details_tag.find('span', class_='font-bold')
        if company_name_tag:
            company_name, batch = split_company_and_batch(company_name_tag.text.strip())
            job_listing.update({'company_name': company_name, 'batch': batch})

        description_tag = company_details_tag.find('span', class_='text-gray-600')
        if description_tag:
            job_listing['description'] = description_tag.text.strip()

        link_tag = company_details_tag.find('a', href=True)
        if link_tag:
            job_listing['company_link'] = link_tag['href']

    # Extract job title, job type, location, and tech stack
    job_name_tag = soup.find('a', class_='font-bold captialize mr-5')
    if job_name_tag:
        job_listing['job_name'] = job_name_tag.text.strip()

    job_details_tag = soup.find('p', class_='job-details my-auto break-normal')
    if job_details_tag:
        spans = job_details_tag.find_all('span')
        job_listing.update({
            'job_type': spans[0].text.strip() if len(spans) > 0 else '',
            'location': spans[1].text.strip() if len(spans) > 1 else '',
            'tech_stack': spans[2].text.strip() if len(spans) > 2 else ''
        })

    return job_listing

def save_to_json(data, filename="yc_job_listings.json"):
    """Save job listings to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(data)} job listings to {filename}")

def main():
    # Scrape and parse job listings
    url = "https://www.workatastartup.com/jobs"
    print("Starting to scrape job listings...")
    
    job_cards_html = scrape_job_listings(url)
    print(f"Successfully scraped {len(job_cards_html)} job listings")

    job_listings = [parse_job_card(html) for html in job_cards_html]

    # Save results to JSON
    save_to_json(job_listings)

    # Optionally print a sample job listing
    if job_listings:
        print("\nSample job listing:")
        print(json.dumps(job_listings[0], indent=2))

if __name__ == "__main__":
    main()

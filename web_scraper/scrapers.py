from utils.web_driver import configure_webdriver
from llm.extractor import extract_job_description
from utils.helpers import split_company_and_batch
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
from tqdm import tqdm


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


def scrape_company_founders(job_listings):
    """Scrape founder information from company profile pages for each job listing."""
    driver = configure_webdriver()
    
    try:
        for job in tqdm(job_listings, desc="Scraping company founders", unit="company"):
            if 'company_link' not in job or not job['company_link']:
                job['founders'] = []  # No link to scrape
                continue
                
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            try:
                driver.get(job['company_link'])
                wait = WebDriverWait(driver, 10)
                
                # Wait for content to load and handle potential loading indicators
                try:
                    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'Loader')))
                except:
                    pass
                
                # Parse the founder information
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Look for founder section - this will need to be adjusted based on the actual HTML structure
                founder_section = soup.find('div', class_='flex flex-col md:flex-row')
                
                founders = []
                if founder_section:
                    # Extract founder profiles
                    founder_elements = founder_section.find_all('div', class_='ml-2 w-full sm:ml-9')
                    
                    for element in founder_elements:
                        founder_info = {}
                        
                        # Extract name
                        name_elem = element.find('div', class_='mb-1 font-medium')
                        if name_elem:
                            # Get the text content without the LinkedIn link
                            name_text = name_elem.contents[0]
                            founder_info['name'] = name_text.strip()
                        
                        # Extract LinkedIn URL
                        linkedin_elem = element.find('a', class_='fa fa-linkedin ml-4 p-1 text-blue-600')
                        if linkedin_elem and 'href' in linkedin_elem.attrs:
                            founder_info['linkedin_url'] = linkedin_elem['href']
                        
                        # Extract bio
                        bio_elem = element.find('div', class_='sm:text-md w-full text-sm')
                        if bio_elem:
                            founder_info['bio'] = bio_elem.text.strip()
                        
                        founders.append(founder_info)
                
                # Add founders to the job listing
                job['founders'] = founders
                
            except Exception as e:
                print(f"Error scraping {job.get('company_name', 'unknown company')}: {str(e)}")
                job['founders'] = []  # Empty list for failed scrapes
    
    finally:
        driver.quit()
    
    return job_listings

def scrape_job_descriptions(job_listings):
    """Scrape detailed job descriptions from job listing URLs using a more flexible approach."""
    driver = configure_webdriver()
    
    try:
        for job in tqdm(job_listings, desc="Scraping job descriptions", unit="job"):
            if 'job_link' not in job or not job['job_link']:
                job['detailed_description'] = ""  # No link to scrape
                continue
                
            time.sleep(random.uniform(1, 3))
            
            try:
                driver.get(job['job_link'])
                wait = WebDriverWait(driver, 10)
                
                # Wait for content to load
                time.sleep(2)  # Simple wait to ensure page loads
                
            
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                job_description_html = soup.find('div', class_='prose max-w-full')
                job_description = extract_job_description(job_description_html)
                job['job_description_detailed'] = job_description

               
                
            except Exception as e:
                print(f"Error scraping job description for {job.get('job_name', 'unknown job')} at {job.get('company_name', 'unknown company')}: {str(e)}")
                job['detailed_description'] = {}
                job['full_text'] = ""
    
    finally:
        driver.quit()
    
    return job_listings

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
    job_name_tag = soup.find('div', class_='job-name')
    if job_name_tag:
        job_listing['job_name'] = job_name_tag.find('a').text.strip()
        job_link_tag = job_name_tag.find('a', href=True)
        if job_link_tag: 
            job_listing['job_link'] = job_link_tag['href']

    job_details_tag = soup.find('p', class_='job-details my-auto break-normal')
    if job_details_tag:
        spans = job_details_tag.find_all('span')
        job_listing.update({
            'job_type': spans[0].text.strip() if len(spans) > 0 else '',
            'location': spans[1].text.strip() if len(spans) > 1 else '',
            'tech_stack': spans[2].text.strip() if len(spans) > 2 else ''
        })

    return job_listing


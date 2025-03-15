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
from tqdm import tqdm
from pprint import pprint

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

def save_to_json(data, filename="yc_job_listings.json"):
    """Save job listings to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(data)} job listings to {filename}")


def get_company_founders(job_listings):
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

def get_job_descriptions(job_listings):
    """Scrape detailed job descriptions from job listing URLs using a more flexible approach."""
    driver = configure_webdriver()
    
    try:
        for job in tqdm(job_listings, desc="Scraping job descriptions", unit="job"):
            if 'job_link' not in job or not job['job_link']:
                job['detailed_description'] = ""  # No link to scrape
                continue
                
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            try:
                driver.get(job['job_link'])
                wait = WebDriverWait(driver, 10)
                
                # Wait for content to load
                time.sleep(2)  # Simple wait to ensure page loads
                
                # First, try to find the main content container
                # This will require some experimentation based on the site structure
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Try several potential selectors for the job description content
                # This is where you'll need to adapt based on your observations
                potential_containers = [
                    soup.find('div', class_=lambda c: c and 'prose' in c),
                    soup.find('div', class_=lambda c: c and 'job-description' in c),
                    soup.find('div', class_=lambda c: c and 'description' in c),
                    soup.find('div', role='main'),
                    soup.find('main'),
                    # Add more potential selectors as needed
                ]
                
                # Find the first non-None container
                container = next((c for c in potential_containers if c), None)
                
                # If we found a container, extract its text
                if container:
                    # Store the structured content
                    job['detailed_description_html'] = str(container)
                    
                    # Extract sections based on headers (h1, h2, h3, h4, strong)
                    sections = {}
                    current_section = "overview"
                    sections[current_section] = []
                    
                    # Recursive function to process nested elements
                    def extract_content(element, current_section):
                        for child in element.children:
                            # Skip empty or non-tag elements
                            if not hasattr(child, 'name') or not child.name:
                                continue
                                
                            # Check if this is a section header
                            is_header = child.name in ['h1', 'h2', 'h3', 'h4'] or (child.name == 'p' and child.find('strong'))
                            
                            if is_header:
                                # Get section title from header
                                if child.name in ['h1', 'h2', 'h3', 'h4']:
                                    section_title = child.text.strip().lower()
                                else:
                                    section_title = child.find('strong').text.strip().lower()
                                
                                # Clean up section title
                                section_title = section_title.replace(':', '').strip()
                                
                                # Create new section if it doesn't exist
                                if section_title not in sections:
                                    sections[section_title] = []
                                
                                # Update current section
                                return section_title
                            
                            # Handle list elements
                            elif child.name == 'ul' or child.name == 'ol':
                                for li in child.find_all('li'):
                                    sections[current_section].append(li.text.strip())
                            
                            # Handle paragraphs and other text elements
                            elif child.name == 'p' or child.name in ['div', 'span']:
                                # Ignore empty paragraphs
                                if child.text.strip():
                                    sections[current_section].append(child.text.strip())
                            
                            # Recursively process nested elements
                            else:
                                updated_section = extract_content(child, current_section)
                                if updated_section:
                                    current_section = updated_section
                        
                        return None
                    
                    # Process the container to extract sections
                    extract_content(container, current_section)
                    
                    # Store the extracted sections
                    job['detailed_description'] = sections
                    
                    # As a fallback, also store the full text
                    job['full_text'] = container.text.strip()
                else:
                    # If we couldn't find a container, store the page title and body text
                    job['detailed_description'] = {}
                    job['full_text'] = soup.body.text.strip() if soup.body else ""
                
            except Exception as e:
                print(f"Error scraping job description for {job.get('job_name', 'unknown job')} at {job.get('company_name', 'unknown company')}: {str(e)}")
                job['detailed_description'] = {}
                job['full_text'] = ""
    
    finally:
        driver.quit()
    
    return job_listings

def main():
    # Scrape and parse job listings
    url = "https://www.workatastartup.com/jobs"
    print("Starting to scrape job listings...")
    
    job_cards_html = scrape_job_listings(url)
    print(f"Successfully scraped {len(job_cards_html)} job listings")

    job_listings = []
    
    for html in tqdm(job_cards_html, desc="Parsing job listings", unit="job"):
        job_listing = parse_job_card(html)
        job_listings.append(job_listing)    
        
    enhanced_job_listing = get_company_founders(job_listings)
    enhanced_job_listing = get_job_descriptions(job_listings)
    

    # Save results to JSON
    save_to_json(enhanced_job_listing)

    # # Optionally print a sample job listing
    # if job_listings:
    #     print("\nSample job listing:")
    #     print(json.dumps(enhanced_job_listing[0], indent=2))

if __name__ == "__main__":
    main()

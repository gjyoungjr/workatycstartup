
from web_scraper.scrapers import scrape_job_listings, scrape_company_founders, scrape_job_descriptions, parse_job_card
from utils.helpers import save_to_json

from tqdm import tqdm

YC_JOB_LISTING_URL = "https://www.workatastartup.com/jobs"

def main():
    job_cards_html = scrape_job_listings(YC_JOB_LISTING_URL)
    
    job_listings = []
    
    for html in tqdm(job_cards_html, desc="Parsing job listings", unit="job"):
        job_listing = parse_job_card(html)
        job_listings.append(job_listing)    
        
    job_listings = scrape_company_founders(job_listings)
    job_listings = scrape_job_descriptions(job_listings) 
    
    save_to_json(job_listings)  
  

if __name__ == "__main__":
    main()
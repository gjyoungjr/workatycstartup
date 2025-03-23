from web_scraper.scrapers import scrape_job_listings, scrape_company_founders, scrape_job_descriptions, parse_job_card
from utils.helpers import save_to_json, clean_document_text
from llm.vector_db import upsert_documents, create_documents, init_vector_store, load_pinecone_index
from pprint import pprint
from tqdm import tqdm
import os 
from dotenv import load_dotenv

load_dotenv()

YC_JOB_LISTING_URL = "https://www.workatastartup.com/jobs"

def main():
    pinecone_index = load_pinecone_index(index_name=os.environ['PINECONE_INDEX_NAME'])
    vector_store = init_vector_store(index=pinecone_index, embed_model='sentence-transformers/all-mpnet-base-v2')
    docs = create_documents(file_path='yc_job_listings.json')
    
    upsert_documents(documents=docs, vector_store=vector_store)
    
    # job_cards_html = scrape_job_listings(YC_JOB_LISTING_URL)
    
    # job_listings = []
    
    # for html in tqdm(job_cards_html, desc="Parsing job listings", unit="job"):
    #     job_listing = parse_job_card(html)
    #     job_listings.append(job_listing)    
        
    # job_listings = scrape_company_founders(job_listings)
    # job_listings = scrape_job_descriptions(job_listings)     
    # save_to_json(job_listings)  
  

if __name__ == "__main__":
    main()
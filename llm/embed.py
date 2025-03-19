from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveJsonSplitter
from typing import Dict, List
import json 
from  pprint import pprint
from utils.helpers import clean_document_text

def load_json_data(file_path: str) -> List[Dict]:
    """
    Load JSON data from a file.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        List[Dict]: List of job listings from the JSON file
        
    Raises:
        FileNotFoundError: If the JSON file doesn't exist
        json.JSONDecodeError: If the JSON file is invalid
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find JSON file at {file_path}")
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"Invalid JSON file at {file_path}")
    
def generate_embeddings(file_path: str):
    data = load_json_data(file_path=file_path)
    splitter = RecursiveJsonSplitter(max_chunk_size=300)
    documents = []
   
    for item in data:
        docs = splitter.create_documents(
            texts=[{'job_description_detailed': clean_document_text(item['job_description_detailed'])}],
            metadatas=[{
                'company_name': item['company_name'],
                'company_link': item['company_link'],
                'company_description': item['description'],
                'batch': item['batch'],
                'source': item['job_link'],
                'job_name': item['job_name'],
                'location': item['location'],
                'job_type': item['job_type'],
                'tech_stack': item['tech_stack'],
                'founders': item['founders'],
            }]
            )
        documents.extend(docs)
        
    pprint(f"Documents : {documents[0]}")
        
        

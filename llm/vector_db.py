from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import os
import time 
from langchain_core.documents import Document
from uuid import uuid4
from langchain_text_splitters import RecursiveJsonSplitter
from typing import  List
from  pprint import pprint
from utils.helpers import clean_document_text, load_json_data

load_dotenv()

pinecone = Pinecone(api_key=os.environ['PINECONE_API_KEY'])

def load_pinecone_index(index_name:str): 
    existing_indexes = [index_info["name"] for index_info in pinecone.list_indexes()]
    
    if index_name not in existing_indexes:
        pinecone.create_index(
            name=index_name,
            dimension=3072,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        while not pinecone.describe_index(index_name).status["ready"]:
            time.sleep(1)

    return pinecone.Index(index_name)
    
def upsert_documents(documents: List[Document]):
    uuids = [str(uuid4()) for _ in range(len(documents))]
    pprint(uuids)
    
def create_documents(file_path: str):
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
        
    return documents
                

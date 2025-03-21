from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import os
import time 

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
    
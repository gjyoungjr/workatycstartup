from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveJsonSplitter
from typing import Dict, List
import json 
from  pprint import pprint

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
      json_chunks = splitter.split_json(json_data=item)
      pprint(json_chunks)
        
        
        
    # pprint(documents)
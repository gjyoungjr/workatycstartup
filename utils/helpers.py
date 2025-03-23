import json
import re
from typing import List, Dict

def split_company_and_batch(text):
    """Split company name and batch from formatted text."""
    parts = text.split('\u00a0')
    return (parts[0].strip(), parts[1].strip('()')) if len(parts) == 2 else (text, None)

def save_to_json(data, filename="yc_job_listings.json"):
    """Save job listings to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(data)} job listings to {filename}")

def clean_document_text(text):
        # Clean markdown elements
        # Remove bold markers
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        
        # Remove bullet points and indentation markers
        text = re.sub(r'[\n\r]*\s*[\+\*\-]\s*', ' ', text)
        
        # Remove tab indentation
        text = re.sub(r'\\t\+\s*', '', text)
        
        # Convert multiple newlines to a single space
        text = re.sub(r'\\n+', ' ', text)
        
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

        
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
    

def transform_founders_data(founders):
    """
    Transforms a list of founder dictionaries into a list of formatted strings.
    
    Args:
        founders (list of dict): List of founders with keys 'name', 'linkedin_url', and 'bio'.
    
    Returns:
        list of str: List of formatted strings for each founder.
    """
    
    return [
        f"{founder['name']} | {founder.get('bio', 'Bio not available')} | {founder['linkedin_url']}"
        for founder in founders
    ]
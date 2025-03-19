import json
import re

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

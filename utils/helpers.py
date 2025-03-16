import json

def split_company_and_batch(text):
    """Split company name and batch from formatted text."""
    parts = text.split('\u00a0')
    return (parts[0].strip(), parts[1].strip('()')) if len(parts) == 2 else (text, None)

def save_to_json(data, filename="yc_job_listings.json"):
    """Save job listings to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(data)} job listings to {filename}")


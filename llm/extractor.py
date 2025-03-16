from dotenv import load_dotenv
from groq import Groq
import os 

load_dotenv()

groq = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)


def extract_job_description(html_content): 
    prompt = f"""
    You are an expert in extracting information from HTML elements. Given the below html
    extract all information related to job description.
    
    {html_content}
    """
    
    response = groq.chat.completions.create(
            model="llama3-70b-8192",  # Use Llama-3 70B model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,  # Low temperature for more deterministic responses
            max_tokens=4000
        )
    return response.choices[0].message.content
    

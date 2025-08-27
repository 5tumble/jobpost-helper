from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import requests
from bs4 import BeautifulSoup
import ollama
import os
from datetime import datetime
import json
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="JobPost Helper MVP")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create output directory
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

class JobRequest(BaseModel):
    company_url: str
    position_title: Optional[str] = None
    user_notes: Optional[str] = None

def analyze_company(url: str) -> dict:
    """Simple company analysis"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract basic info
        title = soup.find('title')
        title_text = title.get_text() if title else "Unknown Company"
        
        # Look for company description
        description = ""
        for meta in soup.find_all('meta'):
            if meta.get('name') == 'description':
                description = meta.get('content', '')
                break
        
        # Look for about page
        about_links = soup.find_all('a', href=True)
        about_url = None
        for link in about_links:
            href = link.get('href', '').lower()
            if 'about' in href or 'over' in href or 'company' in href:
                about_url = link['href']
                break
        
        return {
            "company_name": title_text.split('|')[0].strip() if '|' in title_text else title_text,
            "description": description,
            "about_url": about_url,
            "main_url": url
        }
    except Exception as e:
        return {"error": f"Could not analyze company: {str(e)}"}

def generate_cover_letter(company_info: dict, position: str = "junior developer", notes: str = "") -> dict:
    """Generate cover letter using OpenAI"""
    logger.debug(f"Starting cover letter generation for company: {company_info.get('company_name')}")
    try:
        prompt = f"""
Generate a casual professional cover letter for a junior developer position.

Company: {company_info.get('company_name', 'Unknown')}
Company Description: {company_info.get('description', 'No description available')}
Position: {position}
User Notes: {notes}

Requirements:
- Casual professional tone (IT guy who passed math and physics)
- Direct and practical
- Show genuine interest in their technical work
- Include this phrase: "I would love to have a junior role at your company, but if it's too much to ask, I'm also ready to prove myself with an internship of a duration of your choice"
- Keep it honest and straightforward
- Avoid overly flowery language

Generate three versions:
1. Short (1 paragraph)
2. Medium (1/4 page)
3. Long (1/2 page)
"""

        logger.debug("Making Ollama API call...")
        response = ollama.chat(
            model="mistral-small",
            messages=[{"role": "user", "content": prompt}]
        )
        
        logger.debug("Ollama API call successful")
        content = response['message']['content']
        
        # Split into versions (simple approach)
        lines = content.split('\n')
        versions = {"short": "", "medium": "", "long": ""}
        current_version = "short"
        
        for line in lines:
            if "short" in line.lower() or "1." in line:
                current_version = "short"
            elif "medium" in line.lower() or "2." in line:
                current_version = "medium"
            elif "long" in line.lower() or "3." in line:
                current_version = "long"
            else:
                versions[current_version] += line + "\n"
        
        return versions
        
    except Exception as e:
        logger.error(f"Error in generate_cover_letter: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        return {"error": f"Could not generate cover letter: {str(e)}"}

def generate_linkedin_message(company_info: dict) -> str:
    """Generate LinkedIn message"""
    logger.debug(f"Starting LinkedIn message generation for company: {company_info.get('company_name')}")
    try:
        prompt = f"""
Generate a casual LinkedIn message for spontaneous application.

Company: {company_info.get('company_name', 'Unknown')}
Company Description: {company_info.get('description', 'No description available')}

Requirements:
- Casual and friendly tone
- Under 150 words
- Mention you'll attach your CV
- Ask to forward profile to IT team
- Show enthusiasm for their work
- Direct and practical (IT professional style)
"""

        logger.debug("Making Ollama API call for LinkedIn message...")
        response = ollama.chat(
            model="mistral-small",
            messages=[{"role": "user", "content": prompt}]
        )
        
        logger.debug("LinkedIn message Ollama API call successful")
        return response['message']['content']
        
    except Exception as e:
        logger.error(f"Error in generate_linkedin_message: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        return f"Error generating LinkedIn message: {str(e)}"

def save_application(company_info: dict, cover_letters: dict, linkedin_message: str, position: str):
    """Save application to text files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    company_name = company_info.get('company_name', 'unknown').replace(' ', '_').replace('/', '_')
    
    # Create company directory
    company_dir = output_dir / f"{timestamp}_{company_name}"
    company_dir.mkdir(exist_ok=True)
    
    # Save company info
    with open(company_dir / "company_info.txt", "w") as f:
        f.write(f"Company: {company_info.get('company_name')}\n")
        f.write(f"URL: {company_info.get('main_url')}\n")
        f.write(f"Description: {company_info.get('description')}\n")
        f.write(f"Position: {position}\n")
        f.write(f"Generated: {datetime.now()}\n")
    
    # Save cover letters
    with open(company_dir / "cover_letter_short.txt", "w") as f:
        f.write(cover_letters.get("short", "Error generating short version"))
    
    with open(company_dir / "cover_letter_medium.txt", "w") as f:
        f.write(cover_letters.get("medium", "Error generating medium version"))
    
    with open(company_dir / "cover_letter_long.txt", "w") as f:
        f.write(cover_letters.get("long", "Error generating long version"))
    
    # Save LinkedIn message
    with open(company_dir / "linkedin_message.txt", "w") as f:
        f.write(linkedin_message)
    
    return str(company_dir)

@app.get("/")
async def root():
    return {"message": "JobPost Helper MVP - Working!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "JobPost Helper MVP is running!"}

@app.post("/generate")
async def generate_application(request: JobRequest):
    """Generate cover letters and LinkedIn message for a company"""
    logger.debug(f"Received request for URL: {request.company_url}")
    try:
        # Analyze company
        company_info = analyze_company(request.company_url)
        if "error" in company_info:
            raise HTTPException(status_code=400, detail=company_info["error"])
        
        # Generate cover letters
        cover_letters = generate_cover_letter(
            company_info, 
            request.position_title or "junior developer",
            request.user_notes or ""
        )
        
        if "error" in cover_letters:
            raise HTTPException(status_code=500, detail=cover_letters["error"])
        
        # Generate LinkedIn message
        linkedin_message = generate_linkedin_message(company_info)
        
        # Save to files
        output_path = save_application(
            company_info, 
            cover_letters, 
            linkedin_message,
            request.position_title or "junior developer"
        )
        
        return {
            "status": "success",
            "company": company_info.get('company_name'),
            "output_path": output_path,
            "cover_letters": cover_letters,
            "linkedin_message": linkedin_message
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

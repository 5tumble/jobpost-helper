from fastapi import FastAPI, HTTPException, File, UploadFile
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
import PyPDF2
import docx
import io

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

# CV storage
cv_data = None
cv_file_path = None

class JobRequest(BaseModel):
    company_url: str
    position_title: Optional[str] = None
    user_notes: Optional[str] = None

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        return ""

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(io.BytesIO(file_content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {e}")
        return ""

def analyze_cv(cv_text: str) -> dict:
    """Analyze CV text and extract key information"""
    try:
        logger.debug("Analyzing CV content...")
        
        prompt = f"""
Analyze this CV and extract key information for job applications:

CV Content:
{cv_text}

Please extract and structure the following information:
1. Name
2. Email
3. Phone (if available)
4. Location
5. Education (degrees, institutions, years)
6. Work Experience (companies, positions, durations, key responsibilities)
7. Technical Skills (programming languages, frameworks, tools)
8. Projects (if any)
9. Languages (if any)
10. Key achievements or highlights

Format the response as a structured summary that can be used for cover letter generation.
"""

        response = ollama.chat(
            model="mistral-small",
            messages=[{"role": "user", "content": prompt}]
        )
        
        logger.debug("CV analysis completed")
        return {
            "raw_text": cv_text,
            "analysis": response['message']['content']
        }
        
    except Exception as e:
        logger.error(f"Error analyzing CV: {e}")
        return {"raw_text": cv_text, "analysis": "Error analyzing CV"}

def analyze_company(url: str) -> dict:
    """Simple company analysis"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract basic info
        title = soup.find('title')
        title_text = title.get_text() if title else "Unknown Company"
        
        # Check if we got an error page
        if "403" in title_text or "forbidden" in title_text.lower() or "error" in title_text.lower():
            return {
                "error": f"Could not access company website: {title_text}. Try using the main company URL instead of specific pages."
            }
        
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
        
        # Extract additional company information
        company_details = {
            'clients': [],
            'projects': [],
            'services': [],
            'technologies': [],
            'achievements': []
        }
        
        # Look for client mentions, projects, services
        page_text = soup.get_text().lower()
        
        # Common client indicators
        client_indicators = ['clients', 'customers', 'partners', 'we work with', 'our clients', 'trusted by']
        for indicator in client_indicators:
            if indicator in page_text:
                # Extract text around client mentions
                start_idx = page_text.find(indicator)
                if start_idx != -1:
                    context = page_text[start_idx:start_idx + 500]
                    # Look for company names (capitalized words)
                    import re
                    potential_clients = re.findall(r'\b[A-Z][a-zA-Z\s&]+(?:\.com|\.be|\.eu|\.org)?\b', context)
                    company_details['clients'].extend(potential_clients[:5])  # Limit to 5
        
        # Look for services/technologies
        tech_indicators = ['technologies', 'tech stack', 'we use', 'built with', 'developed with']
        for indicator in tech_indicators:
            if indicator in page_text:
                start_idx = page_text.find(indicator)
                if start_idx != -1:
                    context = page_text[start_idx:start_idx + 300]
                    # Look for common tech terms
                    tech_terms = ['react', 'angular', 'vue', 'node.js', 'python', 'java', 'php', 'wordpress', 'shopify', 'aws', 'azure', 'docker', 'kubernetes']
                    found_tech = [tech for tech in tech_terms if tech in context]
                    company_details['technologies'].extend(found_tech)
        
        # Look for project mentions
        project_indicators = ['projects', 'portfolio', 'case studies', 'we built', 'we developed']
        for indicator in project_indicators:
            if indicator in page_text:
                start_idx = page_text.find(indicator)
                if start_idx != -1:
                    context = page_text[start_idx:start_idx + 400]
                    # Extract potential project descriptions
                    sentences = context.split('.')
                    project_sentences = [s.strip() for s in sentences if any(word in s.lower() for word in ['app', 'website', 'system', 'platform', 'tool'])]
                    company_details['projects'].extend(project_sentences[:3])  # Limit to 3
        
        # Clean up company name and description
        company_name = title_text.split('|')[0].strip() if '|' in title_text else title_text
        clean_description = description if description else 'No description found'
        
        # Check if we have meaningful company information
        has_meaningful_info = (
            company_name and 
            company_name.lower() not in ['403 forbidden', '404 not found', 'error', 'access denied'] and
            len(company_name) > 3
        )
        
        # If we have error messages, replace with generic info
        if not has_meaningful_info:
            company_name = "the company"
            clean_description = "a technology company"
        
        # Create a formatted analysis summary
        analysis_summary = f"""Company Name: {company_name}
Website: {url}
Description: {clean_description}

Analysis Summary:
- Company appears to be: {company_name if has_meaningful_info else 'Unknown (website access issue)'}
- Main business focus: {clean_description[:200] + '...' if clean_description and len(clean_description) > 200 and clean_description.lower() not in ['no description found', '403 forbidden', '404 not found'] else clean_description if clean_description and clean_description.lower() not in ['no description found', '403 forbidden', '404 not found'] else 'Could not determine (website access issue)'}
- About page available: {'Yes' if about_url else 'No'}
- Information quality: {'Good' if has_meaningful_info else 'Limited (website access issues detected)'}

Additional Information Found:"""

        # Add clients if found
        if company_details['clients']:
            analysis_summary += f"\n- Notable clients/partners: {', '.join(set(company_details['clients']))}"
        
        # Add technologies if found
        if company_details['technologies']:
            analysis_summary += f"\n- Technologies used: {', '.join(set(company_details['technologies']))}"
        
        # Add projects if found
        if company_details['projects']:
            analysis_summary += f"\n- Sample projects: {company_details['projects'][0][:100]}..."
        
        analysis_summary += "\n\nThis information was extracted from the company's website and will be used to personalize your cover letter."
        
        return {
            "company_name": company_name,
            "description": clean_description,
            "about_url": about_url,
            "main_url": url,
            "analysis_summary": analysis_summary,
            "clients": company_details['clients'],
            "technologies": company_details['technologies'],
            "projects": company_details['projects']
        }
    except Exception as e:
        error_msg = str(e)
        if "403" in error_msg or "forbidden" in error_msg.lower():
            return {"error": "Could not access company website (403 Forbidden). Try using the main company URL instead of specific pages like /careers or /join-us."}
        elif "404" in error_msg:
            return {"error": "Company website not found (404). Please check the URL and try again."}
        else:
            return {"error": f"Could not analyze company: {error_msg}"}

def generate_cover_letter(company_info: dict, cv_info: dict = None, position: str = "junior developer", notes: str = "") -> dict:
    """Generate cover letter using Mistral-small"""
    logger.debug(f"Starting cover letter generation for company: {company_info.get('company_name')}")
    try:
        cv_context = ""
        if cv_info and cv_info.get('analysis'):
            cv_context = f"""
CV Information:
{cv_info['analysis']}
"""
        
        prompt = f"""
Generate a casual professional cover letter for a junior developer position.

Company: {company_info.get('company_name', 'Unknown')}
Company Description: {company_info.get('description', 'No description available')}
Position: {position}
User Notes: {notes}
{cv_context}

IMPORTANT: If the company name or description contains error messages like "403 Forbidden", "404 Not Found", "Error", or similar technical terms, treat this as missing information and focus on the position and your skills instead.

Requirements:
- Casual professional tone
- Direct and practical
- Show genuine interest in their technical work
- Include this phrase: "I would love to have a junior role at your company, but if it's too much to ask, I'm also ready to prove myself with an internship of a duration of your choice"
- Keep it honest and straightforward
- Avoid overly flowery language
- If CV information is provided, reference specific skills and experience that match the company's needs
- If there are skill gaps, mention them as learning opportunities
- If company information is limited or contains errors, focus on your enthusiasm for the position and willingness to learn

Generate two versions:
1. Short (1 paragraph)
2. Medium (1/4 page)
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
        versions = {"short": "", "medium": ""}
        current_version = "short"
        
        for line in lines:
            if "short" in line.lower() or "1." in line:
                current_version = "short"
            elif "medium" in line.lower() or "2." in line:
                current_version = "medium"
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
Generate a casual LinkedIn message for spontaneous application as a junior developer/intern.

Company: {company_info.get('company_name', 'Unknown')}
Company Description: {company_info.get('description', 'No description available')}

Requirements:
- Casual and friendly tone
- Under 150 words
- Mention you'll attach your CV
- Ask to forward profile to IT team
- Show enthusiasm for learning and growing
- Position yourself as a junior developer/intern looking to learn
- Express interest in gaining experience
- Avoid sounding like an experienced professional
- Focus on willingness to learn and contribute
- Direct and practical tone
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
    
    # Clean company name for filename
    company_name = company_info.get('company_name', 'unknown')
    # Remove special characters and clean up the name
    import re
    clean_company_name = re.sub(r'[^\w\s-]', '', company_name)  # Remove special chars except spaces and hyphens
    clean_company_name = re.sub(r'[-\s]+', '_', clean_company_name)  # Replace spaces and hyphens with underscores
    clean_company_name = clean_company_name.strip('_')  # Remove leading/trailing underscores
    
    # Create company directory
    company_dir = output_dir / f"{timestamp}_{clean_company_name}"
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

@app.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    """Upload and analyze CV file"""
    global cv_data, cv_file_path
    
    try:
        logger.debug(f"Uploading CV file: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Extract text based on file type
        if file.filename.lower().endswith('.pdf'):
            cv_text = extract_text_from_pdf(content)
        elif file.filename.lower().endswith('.docx'):
            cv_text = extract_text_from_docx(content)
        elif file.filename.lower().endswith('.txt'):
            cv_text = content.decode('utf-8')
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, DOCX, or TXT.")
        
        if not cv_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from file.")
        
        # Analyze CV
        cv_data = analyze_cv(cv_text)
        cv_file_path = file.filename
        
        logger.debug("CV uploaded and analyzed successfully")
        
        return {
            "status": "success",
            "message": f"CV '{file.filename}' uploaded and analyzed successfully",
            "filename": file.filename
        }
        
    except Exception as e:
        logger.error(f"Error uploading CV: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cv-status")
async def get_cv_status():
    """Get current CV status"""
    return {
        "has_cv": cv_data is not None,
        "filename": cv_file_path,
        "cv_analysis": cv_data.get('analysis', '') if cv_data else None
    }

@app.delete("/cv")
async def remove_cv():
    """Remove current CV"""
    global cv_data, cv_file_path
    cv_data = None
    cv_file_path = None
    return {"status": "success", "message": "CV removed successfully"}

@app.post("/generate")
async def generate_application(request: JobRequest):
    """Generate cover letters and LinkedIn message for a company"""
    import time
    start_time = time.time()
    
    logger.debug(f"Received request for URL: {request.company_url}")
    try:
        # Analyze company
        company_info = analyze_company(request.company_url)
        if "error" in company_info:
            raise HTTPException(status_code=400, detail=company_info["error"])
        
        # Generate cover letters with CV info if available
        cover_letters = generate_cover_letter(
            company_info, 
            cv_data,  # Pass CV data if available
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
        
        end_time = time.time()
        processing_time = round(end_time - start_time, 2)
        
        # Debug logging
        logger.debug(f"Company analysis available: {company_info.get('analysis_summary') is not None}")
        logger.debug(f"Processing time: {processing_time}")
        
        return {
            "status": "success",
            "company": company_info.get('company_name'),
            "output_path": output_path,
            "company_analysis": company_info.get('analysis_summary', 'No company analysis available'),
            "cover_letters": cover_letters,
            "linkedin_message": linkedin_message,
            "cv_used": cv_data is not None,
            "processing_time": processing_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

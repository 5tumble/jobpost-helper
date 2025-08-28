# JobPost Helper - AI-Powered Job Application Generator

An AI-powered tool that automatically generates personalized cover letters and LinkedIn messages for job and internship applications. Perfect for overcoming the psychological barrier of job applications by automating the creation of tailored content.

## 🚀 Features

- **Smart Company Analysis**: Analyzes company websites to understand their business, goals, and technology stack
- **Intelligent CV Processing**: Advanced AI-powered CV analysis with structured JSON output
- **Automatic Name Extraction**: Extracts applicant name from CV automatically - no manual input needed
- **Personalized Content**: Generates cover letters and LinkedIn messages tailored to each company
- **Multiple Formats**: Creates short and medium-length cover letters
- **Self-Validation**: Built-in quality checks ensure consistent, professional output
- **Smart URL Handling**: Automatically handles URLs with or without https:// or www prefixes
- **Local Processing**: Uses Ollama with Mistral-small for privacy and cost-free operation
- **Local Storage**: Saves all generated content to organized text files
- **Privacy-First**: No personal data stored beyond what's extracted from your CV

## 🛠️ Technology Stack

- **Backend**: Python, FastAPI, Uvicorn
- **AI/LLM**: Ollama with Mistral-small (local, free)
- **Web Scraping**: Requests, BeautifulSoup
- **CV Processing**: PyPDF2, python-docx
- **Frontend**: Simple HTML with JavaScript
- **Storage**: Local text files

## 📋 Requirements

- Python 3.8+
- 14GB+ RAM (for Mistral-small model)
- Ollama installed and running

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip3 install --break-system-packages -r requirements.txt
   ```

2. **Install Ollama** (if not already installed):
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

3. **Download Mistral-small Model**:
   ```bash
   ollama pull mistral-small
   ```

4. **Start the Application**:
   ```bash
   python3 main.py
   ```

5. **Open in Browser**:
   Navigate to `http://localhost:8000`

## 📖 Usage

1. **Upload Your CV** (optional but recommended):
   - Click "Choose File" and select your CV (PDF, DOCX, or TXT)
   - Click "Upload CV" to analyze and store it
   - Your name will be automatically extracted from the CV

2. **Generate Application**:
   - Enter the company website URL (with or without https://)
   - Optionally specify the position title
   - Add any additional notes
   - Click "Generate Application"

3. **Review Results**:
   - View the company analysis
   - Read the generated cover letters (short and medium)
   - Copy the LinkedIn message
   - All content is automatically saved to local files

## 📁 Project Structure

```
jobpost_helper/
├── main.py              # FastAPI backend
├── index.html           # Frontend interface
├── requirements.txt     # Python dependencies
├── start.sh            # Startup script
├── output/             # Generated applications (auto-created)
└── README.md           # This file
```

## 🔧 API Endpoints

- `GET /` - Main interface
- `GET /health` - Health check
- `POST /generate` - Generate application content
- `POST /upload-cv` - Upload and analyze CV
- `GET /cv-status` - Check CV upload status
- `DELETE /cv` - Remove stored CV

## 💡 Example Output

**Company Analysis**:
```
Company Name: Example Tech
Website: https://example.com
Description: Custom software development company

Analysis Summary:
- Company appears to be: Example Tech
- Main business focus: Custom software development
- Technologies used: React, Node.js, Python
- Notable clients: DHL, SNCB
```

**Cover Letter** (Medium):
```
Dear Hiring Manager,

I'm writing to express my interest in the junior developer position at Example Tech. With my background in Python and React development, I believe I can contribute effectively to your team. I would love to have a junior role at your company, but if it's too much to ask, I'm also ready to prove myself with an internship of a duration of your choice.

[Personalized content based on company analysis and CV skills]
```

**LinkedIn Message**:
```
Hey there,

I hope this message finds you well! I'm [Your Name], a student eager to kickstart my career in tech. I came across Example Tech and was really excited about the opportunity to learn and grow as a junior developer/intern.

I've attached my CV for your review. Could you please forward it to the IT team? I'm super enthusiastic about gaining experience and contributing to your projects while learning from the best.

Looking forward to hearing back!

Best,
[Your Name]
```

## 🔮 Future Features

- Queue system for multiple applications
- Progress indicators and status tracking
- Copy-to-clipboard functionality
- Export to different formats
- Template customization
- Advanced company research

## 🤝 Contributing

This is a personal project designed to help with job applications. Feel free to fork and adapt for your own needs!

## 📄 License

Personal use - feel free to modify and use for your own job applications.

## 💭 Motivation

Job applications can be psychologically challenging. This tool aims to reduce that burden by automating the repetitive parts while maintaining personalization and authenticity.

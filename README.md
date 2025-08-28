# JobPost Helper - AI-Powered Job Application Generator

An AI-powered tool that automatically generates personalized cover letters and LinkedIn messages for job and internship applications. Perfect for overcoming the psychological barrier of job applications by automating the creation of tailored content.

## 🚀 Features

- **Smart Company Analysis**: Analyzes company websites to understand their business, goals, and technology stack
- **CV Integration**: Upload your CV once and use it for all applications
- **Personalized Content**: Generates cover letters and LinkedIn messages tailored to each company
- **Multiple Formats**: Creates short and medium-length cover letters
- **Local Processing**: Uses Ollama with Mistral-small for privacy and cost-free operation
- **Smart URL Handling**: Automatically handles URLs with or without https:// or www prefixes
- **Local Storage**: Saves all generated content to organized text files

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

I'm writing to express my interest in the junior developer position at Example Tech...

[Personalized content based on company analysis and CV]
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

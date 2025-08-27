# JobPost Helper MVP

An AI-powered tool that generates personalized cover letters and LinkedIn messages for spontaneous job applications. Built with Python, FastAPI, and local AI models.

## 🚀 Features

- **Company Analysis**: Automatically analyzes company websites to understand their business, goals, and focus areas
- **Personalized Cover Letters**: Generates three versions (short, medium) tailored to each company
- **LinkedIn Messages**: Creates professional LinkedIn messages for spontaneous applications
- **Local AI**: Uses Mistral-small via Ollama for privacy and zero API costs
- **Web Interface**: Simple HTML form for easy interaction
- **Local Storage**: Saves all generated content to text files

## 🤖 AI Model

This project uses **Mistral-small** via **Ollama** for all AI text generation:
- **Model**: Mistral-small (local, free)
- **Memory Usage**: ~9.7GB RAM
- **Speed**: 5-15 seconds per generation
- **Privacy**: All processing happens locally on your machine
- **Cost**: Completely free (no API costs)

## 📋 Requirements

- Python 3.8+
- 32GB+ RAM (for Mistral-small model)
- Ollama installed

## 🛠 Installation

1. **Install Ollama**:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Download Mistral-small**:
   ```bash
   ollama pull mistral-small
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the application**:
   ```bash
   python3 main.py
   ```

5. **Open the web interface**:
   - Open `index.html` in your browser
   - Or access `http://localhost:8000` if serving via FastAPI

## 📁 Project Structure

```
jobpost_helper/
├── main.py              # FastAPI backend with AI integration
├── index.html           # Web interface
├── requirements.txt     # Python dependencies
├── start.sh            # Startup script
├── output/             # Generated cover letters and messages
└── README.md           # This file
```

## 🎯 Usage

1. **Input Company URL**: Paste the company website you want to apply to
2. **Optional Fields**: Add position title and notes if desired
3. **Generate**: Click to analyze company and generate content
4. **Results**: Get three cover letters and a LinkedIn message
5. **Files**: All content is saved to the `output/` directory

## 🔧 API Endpoints

- `GET /health` - Health check
- `POST /generate` - Generate cover letters and LinkedIn message
- `GET /` - Root endpoint

## 🎨 Example Output

Generated files are saved in timestamped directories:
```
output/
└── 20241227_143022_Company_Name/
    ├── company_info.txt
    ├── cover_letter_short.txt
    ├── cover_letter_medium.txt
    └── linkedin_message.txt
```

## 🚧 Future Features

- [ ] CV upload and analysis (.pdf, .docx, .txt)
- [ ] Queue system with status indicators
- [ ] Multiple AI model support
- [ ] Export to different formats
- [ ] Application history tracking

## 🤝 Contributing

This is a personal project for learning LLM integration and automating job applications. Feel free to fork and adapt for your own needs!

## 📄 License

Personal use - feel free to use and modify for your own job applications.

## 💡 Motivation

Built to reduce the psychological barrier of job applications by automating the repetitive parts while maintaining personalization and quality.

---

**Built with ❤️ for job seekers who want to focus on what matters most.**

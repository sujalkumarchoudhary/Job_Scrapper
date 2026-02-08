<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white" alt="Vercel"/>
</p>

<h1 align="center">💼 Job Scraper</h1>

<p align="center">
  <strong>Search thousands of jobs with AI-powered insights</strong>
</p>

<p align="center">
  <a href="https://findjob.takhos.com">
    <img src="https://img.shields.io/badge/🚀_Live_Demo-findjob.takhos.com-6366f1?style=for-the-badge" alt="Live Demo"/>
  </a>
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Smart Job Search** | Search by job title and location using Google Jobs |
| 🏠 **Remote Filter** | Filter for remote-only opportunities |
| 🤖 **AI Summaries** | Get instant job summaries powered by Groq AI |
| 🛡️ **Rate Limited** | Protected API (4 requests/min per IP) |
| 🎨 **Modern UI** | Glassmorphism dark theme with animations |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- [SerpAPI Key](https://serpapi.com) (free tier: 100 searches/month)
- [Groq API Key](https://console.groq.com) (optional, for AI summaries)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/job-scraper.git
cd job-scraper

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the server
python -m uvicorn main:app --reload
```

### Open in browser
```
http://localhost:8000
```

---

## 🛠️ Tech Stack

```
┌─────────────────────────────────────────┐
│  Frontend                               │
│  ├── HTML5 + CSS3 (Glassmorphism)      │
│  └── Vanilla JavaScript                 │
├─────────────────────────────────────────┤
│  Backend                                │
│  ├── FastAPI (Python)                   │
│  ├── SerpAPI (Job Data)                 │
│  └── Groq (AI Summaries)                │
├─────────────────────────────────────────┤
│  Infrastructure                         │
│  ├── Vercel (Hosting)                   │
│  └── SlowAPI (Rate Limiting)            │
└─────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
job-scraper/
├── 📄 main.py           # FastAPI application
├── 📄 serp_client.py    # SerpAPI integration
├── 📄 groq_client.py    # Groq AI integration
├── 📄 config.py         # Configuration
├── 📄 requirements.txt  # Dependencies
├── 📄 vercel.json       # Vercel config
├── 📄 .env.example      # Environment template
└── 📁 static/
    ├── 📄 index.html    # Main page
    ├── 📄 styles.css    # Styling
    └── 📄 app.js        # Frontend logic
```

---

## 🔒 API Endpoints

| Method | Endpoint | Description | Rate Limit |
|--------|----------|-------------|------------|
| `GET` | `/` | Serve frontend | - |
| `POST` | `/api/search` | Search jobs | 4/min |
| `POST` | `/api/summarize` | AI summary | 4/min |
| `GET` | `/api/health` | Health check | - |

### Example Request

```bash
curl -X POST https://findjob.takhos.com/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Software Engineer", "location": "New York"}'
```

---

## 🌐 Deployment

Deploy your own instance to Vercel:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/job-scraper)

See [DEPLOY.md](DEPLOY.md) for detailed instructions.

---

## 📝 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SERP_API_KEY` | ✅ | Your SerpAPI key |
| `GROQ_API_KEY` | ❌ | Your Groq API key (for AI features) |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">
  Made with ❤️ using FastAPI & Groq AI
</p>

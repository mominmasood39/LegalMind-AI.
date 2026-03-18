# ⚖️ LegalMind-AI

> **AI-powered legal assistance platform — Final Year Project**

LegalMind-AI is an intelligent legal assistance system that democratises access to legal knowledge using Artificial Intelligence. It provides three core capabilities:

| Feature | Description |
|---|---|
| 💬 **Legal Q&A Chat** | Ask legal questions in plain English and receive clear, educational AI-powered answers |
| 📄 **Document Analysis** | Upload or paste legal documents to receive summaries, key clauses, risk factors, and recommendations |
| 🔍 **Case Research** | Identify applicable legal principles, arguments, and related areas of law for any scenario |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or later

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/mominmasood39/LegalMind-AI..git
cd LegalMind-AI.

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Linux / macOS
# venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. (Optional) Configure environment
cp .env.example .env
# Edit .env to add your OpenAI API key (leave blank for demo mode)
```

### Running the Application

```bash
# Start the FastAPI backend (serves the frontend too)
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

Then open **http://localhost:8000** in your browser.

The interactive API documentation is available at **http://localhost:8000/docs**.

---

## 🏗️ Project Structure

```
LegalMind-AI/
├── backend/
│   ├── app.py                  # FastAPI application & API routes
│   ├── config.py               # Settings (demo mode, API keys, etc.)
│   ├── requirements.txt        # Python dependencies
│   ├── models/
│   │   └── schemas.py          # Pydantic request/response models
│   └── services/
│       ├── legal_assistant.py  # Legal Q&A service
│       ├── document_analyzer.py # Document analysis service
│       └── case_researcher.py  # Case research service
├── frontend/
│   ├── index.html              # Landing page
│   ├── chat.html               # Legal Q&A chat interface
│   ├── analyse.html            # Document analysis interface
│   ├── research.html           # Case research interface
│   ├── css/
│   │   └── styles.css          # Global stylesheet
│   └── js/
│       └── app.js              # Shared JS utilities
├── tests/
│   ├── test_api.py             # API endpoint tests
│   └── test_services.py        # Service unit tests
├── .env.example                # Environment variable template
├── pytest.ini                  # Pytest configuration
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/legal-query` | Legal Q&A |
| `POST` | `/api/analyse-document` | Analyse document text |
| `POST` | `/api/upload-document` | Upload & analyse a file (TXT, PDF, DOCX) |
| `POST` | `/api/case-research` | Legal case research |

Full interactive documentation: **http://localhost:8000/docs**

---

## 🤖 Demo Mode vs Live AI Mode

The application runs in **Demo Mode** by default — it uses pre-built legal knowledge bases and heuristic analysis, requiring no external API keys.

To enable **Live AI Mode** with real OpenAI responses:

1. Add your OpenAI API key to `.env`:
   ```
   OPENAI_API_KEY=sk-...
   DEMO_MODE=False
   ```
2. Restart the server.

---

## 🧪 Running Tests

```bash
# Install test dependencies (already in requirements.txt)
pip install -r backend/requirements.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run only API tests
pytest tests/test_api.py -v

# Run only service unit tests
pytest tests/test_services.py -v
```

---

## ⚠️ Disclaimer

LegalMind-AI is an **educational tool** developed as a Final Year Project. It does **not** provide professional legal advice. The information generated is for general educational purposes only and may not be accurate, complete, or applicable to your specific jurisdiction or circumstances.

**Always consult a qualified legal professional for advice specific to your situation.**

---

## 📜 License

This project is licensed under the MIT Licence. See the [LICENSE](LICENSE) file for details.


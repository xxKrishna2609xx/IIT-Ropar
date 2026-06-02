<div align="center">

# 🏛️ Vicharanashala Internship Portal
### Official FAQ & Information Hub — IIT Ropar

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-Vercel-black?style=for-the-badge)](https://iit-ropar.vercel.app)
[![Backend](https://img.shields.io/badge/⚙️_API-Render-46E3B7?style=for-the-badge)](https://vicharanashala-internship.onrender.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-Python-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-AI-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev)

</div>

---

## 📌 About the Project

A full-stack web application built for the **Vicharanashala Internship Programme at IIT Ropar** — a two-month, fully-online open-source internship run by Prof. Sudarshan Iyengar's lab.

The portal provides:
- 📚 A comprehensive, searchable **FAQ system** with bilingual support (English / Hindi)
- 🤖 **Yaksha** — an AI assistant powered by Gemini 2.5 Flash, trained on the full internship knowledge base
- 👍 A **voting system** so interns can upvote/downvote FAQ helpfulness
- 📊 A live **server status** indicator and real-time clock
- 🌙 **Dark / Light mode** toggle with persistent preference

---

## 🖥️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19 + Vite 8 + React Router v7 |
| **Backend** | Python 3 + FastAPI + Uvicorn |
| **AI / Chat** | Google Gemini 2.5 Flash (`google-genai` SDK) |
| **Styling** | Vanilla CSS (glassmorphism dark/light theme) |
| **Deployment** | Vercel (frontend) · Render (backend) |
| **Data** | JSON flat-file store (`faqs.json`, `faqs_hi.json`, `votes.json`) |

---

## 🗂️ Project Structure

```
IIT-Ropar/
├── frontend/                   # React + Vite application
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chatbot.jsx     # Yaksha AI chat widget
│   │   │   ├── Header.jsx      # Sticky navigation bar
│   │   │   ├── FAQItem.jsx     # Accordion FAQ card with voting
│   │   │   ├── ServerStatus.jsx# Live backend health + clock
│   │   │   └── VoiceAssistant.jsx
│   │   ├── pages/
│   │   │   ├── Overview.jsx    # Programme overview page
│   │   │   └── FAQPage.jsx     # Full FAQ with search & sidebar
│   │   ├── App.jsx
│   │   └── index.css           # Full design system (CSS variables)
│   ├── .env                    # Local dev API URL (gitignored)
│   ├── .env.production         # Production API URL (committed)
│   └── vercel.json             # React Router SPA rewrites
│
├── backend/                    # FastAPI server
│   ├── main.py                 # All API routes + Yaksha AI logic
│   ├── requirements.txt        # Python dependencies
│   ├── faqs.json               # English FAQ knowledge base
│   ├── faqs_hi.json            # Hindi FAQ knowledge base
│   ├── votes.json              # Aggregate vote counts
│   └── .env                    # GEMINI_API_KEY (gitignored)
│
└── README.md
```

---

## ✨ Features

### 🔍 Searchable FAQ
- Instant client-side search across all questions and answers
- Category sidebar (desktop) and scrollable chips (mobile)
- Bilingual toggle: English ↔ Hindi
- Expand All / Collapse All controls

### 🤖 Yaksha AI Assistant
- Powered by **Gemini 2.5 Flash** with the full FAQ as its knowledge base
- Maintains conversation history across turns
- Rate-limit aware — graceful 5-second cooldown between messages
- Suggested questions on first open

### 👍 Voting System
- Upvote / downvote each FAQ answer
- Votes persist in localStorage (per browser) and sync to the backend
- Optimistic UI updates for instant feedback

### 🎨 Premium UI/UX
- Glassmorphism design with animated gradients
- Smooth dark ↔ light mode with `data-theme` CSS variables
- Responsive layout — works on mobile, tablet, and desktop
- Live server status pill (online / offline / checking)

---

## 🚀 Running Locally

You need **both** servers running at the same time.

### Prerequisites
- Node.js ≥ 18
- Python ≥ 3.10
- A [Google AI Studio](https://aistudio.google.com) API key

### 1. Backend (FastAPI)

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Create the .env file
echo GEMINI_API_KEY=your_key_here > .env

# Start the server
uvicorn main:app --reload
```
> Backend runs at **http://localhost:8000**

### 2. Frontend (React + Vite)

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```
> Frontend runs at **http://localhost:5173**

---

## 🌐 Deployment

| Service | Purpose | Config |
|---|---|---|
| **Vercel** | Hosts the React frontend | Root dir: `frontend/`, `vercel.json` handles SPA routing |
| **Render** | Hosts the FastAPI backend | Start cmd: `uvicorn main:app --host 0.0.0.0 --port $PORT` |

### Environment Variables

**Render** (backend) — set in the Render dashboard:
```
GEMINI_API_KEY=your_gemini_api_key
```

**Vercel** (frontend) — committed in `frontend/.env.production`:
```
VITE_API_BASE=https://vicharanashala-internship.onrender.com/api
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Server health check + uptime |
| `GET` | `/api/faqs?lang=en` | Fetch all FAQs (`lang=en` or `lang=hi`) |
| `GET` | `/api/votes` | Fetch aggregate vote counts |
| `POST` | `/api/vote` | Cast or remove a vote |
| `POST` | `/api/chat` | Send a message to Yaksha AI |

---

## 👨‍💻 Author

Built with ❤️ for the **Vicharanashala Internship Programme 2026**  
[IIT Ropar](https://www.iitrpr.ac.in) · Lab of Prof. Sudarshan Iyengar · [samagama.in](https://samagama.in)

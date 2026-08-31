# FinPal — Voice-First AI Financial Advisor

> An AI-powered conversational financial advisor that delivers **computed, grounded advice** — not hallucinated numbers. Chat by text or voice; the LLM collects your financial facts and delegates every numeric answer to a deterministic rules engine.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Backend Setup](#2-backend-setup)
  - [3. Frontend Setup](#3-frontend-setup)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Frontend Development](#frontend-development)
- [Production Deployment](#production-deployment)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

FinPal is a full-stack, voice-enabled personal finance assistant. Users converse with an AI advisor (by text or live microphone) that asks about their income, expenses, debts, and goals — then calls a purpose-built **rules engine** to compute real answers for:

- 50/30/20 budget allocation
- SIP / investment projections
- EMI affordability checks
- Debt payoff strategy (avalanche / snowball)
- Emergency fund sizing
- Financial Independence (FI) number
- Subscription & BNPL trap audits
- Investment instrument comparisons

A real-time dashboard visualises the session's financial profile as the conversation progresses.

> 🤖 **The frontend (UI/UX) was designed and developed with the assistance of [IBM Bob](https://www.ibm.com/products/watsonx/bob), IBM's AI-powered software engineering agent.**

---

## Features

| Feature | Description |
|---|---|
| 🎙️ Voice & Text Chat | Speak or type — `MediaRecorder` captures audio in-browser; Groq Whisper handles transcription |
| 🔢 Rules-Based Calculations | Every numeric answer comes from a deterministic calculator, never from the LLM directly |
| 📊 Live Dashboard | Profile panel updates in real time as the advisor collects your data |
| 🌊 Streaming Responses | Server-Sent Events (SSE) stream advisor tokens to the UI as they are generated |
| 🗃️ Session Persistence | PostgreSQL (or SQLite for local dev) stores financial profiles per session |
| 🔌 Pluggable LLM | Default: Groq; swap to OpenRouter or Google Gemini via a single env var |
| ♿ Accessible UI | ARIA live regions, keyboard navigation, `prefers-reduced-motion` support |
| 📦 No-Build Frontend | Plain HTML/CSS/JS — no bundler, no framework, no build step required |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Browser (Frontend)                │
│  index.html  ·  app.html  ·  dashboard.html          │
│  styles.css  ·  api.js (REST + SSE client)           │
└────────────────────────┬────────────────────────────┘
                         │ HTTP / SSE
┌────────────────────────▼────────────────────────────┐
│              FastAPI Backend  (:8000)                │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  Orchestrator  (LLM conversation loop)        │   │
│  │  ┌──────────────┐   ┌─────────────────────┐  │   │
│  │  │  LLM (Groq / │   │   Tool Dispatcher   │  │   │
│  │  │  OpenRouter / │──▶│  update_profile     │  │   │
│  │  │  Gemini)      │   │  run_calculation    │  │   │
│  │  └──────────────┘   └──────────┬──────────┘  │   │
│  └─────────────────────────────────┼─────────────┘   │
│                                    │                  │
│  ┌─────────────────────────────────▼─────────────┐   │
│  │  Rules Engine  (pure Python calculators)       │   │
│  │  budget · sip · emi · debt · fi_number · …     │   │
│  └────────────────────────────────────────────────┘   │
│                                                      │
│  ┌──────────────────┐   ┌──────────────────────────┐ │
│  │  Voice Module    │   │  Database (Postgres /     │ │
│  │  STT: Whisper    │   │  SQLite)                  │ │
│  │  TTS: Orpheus    │   │  SQLAlchemy ORM           │ │
│  └──────────────────┘   └──────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

The LLM **never performs arithmetic** — it drives conversation and calls one of two tools:
- **`update_profile`** — persists facts (income, expenses, debts, goals) to the session database.
- **`run_calculation`** — invokes a specific rules-engine function with verified inputs and returns computed results.

---

## Project Structure

```
FIN_PAL_ADVISOR/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── voice.py              # Session, chat (SSE), voice endpoints
│   │   ├── db/
│   │   │   ├── models.py             # SQLAlchemy ORM models
│   │   │   └── session.py            # DB engine / session factory
│   │   ├── orchestrator/
│   │   │   ├── conversation.py       # LLM conversation loop
│   │   │   ├── system_prompt.py      # Advisor persona & instructions
│   │   │   └── tools.py              # Tool schemas & dispatcher
│   │   ├── rules_engine/
│   │   │   ├── budget_allocator.py   # 50/30/20 budgeting
│   │   │   ├── sip_projection.py     # SIP / investment growth
│   │   │   ├── emi.py                # EMI affordability
│   │   │   ├── debt_payoff.py        # Avalanche / snowball strategies
│   │   │   ├── emergency_fund.py     # Emergency corpus sizing
│   │   │   ├── fi_number.py          # Financial independence number
│   │   │   ├── subscription_audit.py # Subscription cost analysis
│   │   │   ├── bnpl_trap.py          # BNPL risk detection
│   │   │   ├── instrument_comparison.py
│   │   │   └── priority_check.py
│   │   ├── voice/
│   │   │   ├── stt.py                # Groq Whisper (speech-to-text)
│   │   │   └── tts.py                # Groq Orpheus (text-to-speech)
│   │   ├── config.py                 # Pydantic-settings configuration
│   │   └── main.py                   # FastAPI app entrypoint
│   └── requirements.txt
│
├── frontend/
│   ├── index.html                    # Landing page
│   ├── app.html                      # Chat + voice advisor UI
│   ├── dashboard.html                # Financial profile dashboard
│   ├── styles.css                    # Full design system
│   ├── api.js                        # REST + SSE API client
│   └── README.md                     # Frontend-specific docs
│
├── .env.example                      # Environment variable template
├── .gitignore
└── README.md
```

---

## Tech Stack

### Backend

| Layer | Technology |
|---|---|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn |
| Language | Python 3.11+ |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL (`psycopg2`) — SQLite supported for local dev |
| LLM (default) | [Groq](https://groq.com/) (`openai/gpt-oss-120b`) |
| LLM (optional) | OpenRouter or Google Gemini (via `CHAT_PROVIDER` env var) |
| Speech-to-Text | Groq Whisper (`whisper-large-v3`) |
| Text-to-Speech | Groq Canopy Labs Orpheus (`canopylabs/orpheus-v1-english`) |
| Streaming | Server-Sent Events (SSE) |
| Config | `pydantic-settings` (env file) |

### Frontend

| Layer | Technology |
|---|---|
| Framework | Plain HTML5 / CSS3 / Vanilla JavaScript — no build step |
| Voice Capture | `MediaRecorder` / `getUserMedia` Web APIs |
| Fonts | Google Fonts — Sora (headings) + Manrope (body) |
| Design Tool | Developed with **[IBM Bob](https://www.ibm.com/products/watsonx/bob)** |

---

## Prerequisites

- **Python 3.11+** — use a standard [python.org](https://www.python.org/downloads/) or Windows Store build (avoid MSYS/MinGW on Windows — missing prebuilt wheels).
- **PostgreSQL** running locally — or swap `DATABASE_URL` for a SQLite path; no code changes needed.
- **Groq API key** — create a free account at [console.groq.com](https://console.groq.com). Required; no default.

---

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/FIN_PAL_ADVISOR.git
cd FIN_PAL_ADVISOR
```

### 2. Backend Setup

**Create and activate a virtual environment:**

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Create `backend/.env`:**

```env
# Required
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Database — choose one:
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/financial_advisor
# DATABASE_URL=sqlite:///./financial_advisor.db   # zero-setup local dev

# Optional: alternate LLM provider
# CHAT_PROVIDER=openrouter
# OPENROUTER_API_KEY=your_key

# CHAT_PROVIDER=gemini
# GEMINI_API_KEY=your_key
```

**Create the Postgres database (skip if using SQLite):**

```bash
psql -U postgres -c "CREATE DATABASE financial_advisor;"
```

Tables are created automatically on startup — no migrations needed.

**Start the API server:**

```bash
uvicorn app.main:app --reload --port 8000
```

Verify it's running:

```bash
curl http://localhost:8000/health
# → {"status":"ok"}
```

### 3. Frontend Setup

The frontend is served automatically by FastAPI when you start the backend — just open:

```
http://localhost:8000
```

**Alternative — standalone static server (for frontend development):**

In a second terminal:

```bash
cd frontend
python -m http.server 5500
```

Then open <http://localhost:5500/index.html>.

Because the frontend (`:5500`) and backend (`:8000`) are on different origins, set the API base in each HTML file while developing (remove before deploying):

```html
<script>window.FINPAL_API_BASE = 'http://localhost:8000';</script>
```

Or append `?api=http://localhost:8000` to the URL query string.

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GROQ_API_KEY` | ✅ | — | Groq API key (LLM + STT + TTS) |
| `OPENAI_API_KEY` | ✅ | — | OpenAI API key (fallback model) |
| `DATABASE_URL` | ✅ | `postgresql://...` | Postgres or SQLite connection string |
| `GROQ_TTS_MODEL` | ❌ | `canopylabs/orpheus-v1-english` | TTS model ID |
| `GROQ_TTS_VOICE` | ❌ | `tara` | TTS voice name |
| `OPENAI_MODEL` | ❌ | `gpt-4o-mini` | Chat completion model |
| `OPENAI_STT_MODEL` | ❌ | `gpt-4o-mini-transcribe` | Transcription model |
| `CHAT_PROVIDER` | ❌ | `groq` | `groq` \| `openrouter` \| `gemini` |
| `OPENROUTER_API_KEY` | ❌ | — | Required if `CHAT_PROVIDER=openrouter` |
| `GEMINI_API_KEY` | ❌ | — | Required if `CHAT_PROVIDER=gemini` |

---

## API Reference

All endpoints are prefixed under the FastAPI app at `http://localhost:8000`.

| Method | Path | Body | Response | Description |
|---|---|---|---|---|
| `GET` | `/health` | — | `{"status":"ok"}` | Liveness check |
| `POST` | `/api/sessions` | — | `{session_id, user_id}` | Create a new chat session |
| `POST` | `/api/sessions/{id}/chat/stream` | `{"message":"…"}` | SSE stream | Send a message; stream advisor reply tokens |
| `POST` | `/api/sessions/{id}/voice` | `multipart/form-data` (field: `audio`) | `{user_text, advisor_text, audio_b64, profile}` | Send audio; receive transcript + spoken reply |
| `GET` | `/api/sessions/{id}/profile` | — | Profile object | Fetch the session's financial profile |

### SSE Event Types (`/chat/stream`)

| `type` | Payload fields | Description |
|---|---|---|
| `token` | `text` | Incremental advisor response text |
| `done` | `profile`, `user_text` | Stream complete; updated profile included |
| `error` | `text` | Stream error message |

### Interactive API Docs

FastAPI's auto-generated docs are available at:
- **Swagger UI:** <http://localhost:8000/docs>
- **ReDoc:** <http://localhost:8000/redoc>

---

## Frontend Development

The frontend was built with **[IBM Bob](https://www.ibm.com/products/watsonx/bob)**, IBM's AI-powered software engineering agent, which assisted in designing and implementing the complete UI — including the design system, component layout, accessibility features, and API integration layer.

### Pages

| File | Route | Purpose |
|---|---|---|
| `index.html` | `/` | Landing page |
| `app.html` | `/app.html` | Chat + voice advisor |
| `dashboard.html` | `/dashboard.html` | Financial profile & budget snapshot |

### Design System

- **Palette:** Ink `#101F1A`, Pine `#17594A`, Mint `#6FD6A6`, Mist `#EFF4F1`, white surfaces, `#D5E1DB` borders
- **Typography:** Sora (headings), Manrope (body)
- **Layout:** Responsive bento grids via `repeat(auto-fit, minmax(…))`
- **Motion:** 120ms colour/border transitions; `prefers-reduced-motion: reduce` cuts all transitions to ~0ms
- **Accessibility:** ARIA live regions (`role="log"`, `role="status"`), semantic HTML, full keyboard operability, visible `:focus-visible` rings

### Session Model

The session ID lives in the URL as `?session=<id>`. A fresh visit to `app.html` creates a new session; `app.html?session=<id>` resumes one. The ID is written into the address bar via `history.replaceState` so reloading preserves the thread.

---

## Production Deployment

### Single-Origin (Recommended)

Mount the frontend directly on FastAPI — already done in [`backend/app/main.py`](backend/app/main.py). The backend serves all pages and assets from the same origin, eliminating CORS entirely:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Visit `http://<your-server>:8000` — done.

### Tighten CORS for Separate-Origin Deploy

If you choose to deploy the frontend on a CDN or separate domain, restrict CORS in [`backend/app/main.py`](backend/app/main.py):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://finpal.example.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes with clear messages: `git commit -m "feat: add xyz"`
4. Push to your fork: `git push origin feature/your-feature-name`
5. Open a Pull Request against `main`.

Please keep PRs focused — one feature or fix per PR. Ensure the backend starts cleanly (`/health` returns `ok`) and the browser console is free of errors before submitting.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  Built with ❤️ · Frontend developed with <a href="https://www.ibm.com/products/watsonx/bob">IBM Bob</a>
</p>

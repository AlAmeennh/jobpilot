# JobPilot

![Tests](https://github.com/AlAmeennh/jobpilot/actions/workflows/tests.yml/badge.svg)
An AI-assisted job application tracker. Keep every application in one place, and paste a job description to see which skills you match and which you're missing.

> **Status:** In active development. Built solo as a learning project and for my own job search.

**Live demo:** _coming soon_

<!-- Replace with a real screenshot or GIF once the UI is working -->

## Why I built this

I'm a final-year CSE student applying for software roles off-campus. Spreadsheets got messy fast, and I wanted something that also tells me how well my resume fits each job. So I built it.

## Features

**Planned for v1**

- [x] Sign up and log in (JWT authentication)
- [x] Add, edit, delete and filter job applications
- [x] Track status: Applied, Interview, Offer, Rejected
- [x] Dashboard with simple stats (applications per status, per week)
- [x] AI resume matcher: paste a job description and get matched skills, missing skills and suggestions
- [x] Each user only sees their own data

      **Later**

- [ ] Reminders for follow-ups
- [ ] Export to CSV
- [ ] Docker setup (`docker compose up`)
- [x] CI with GitHub Actions

## Tech stack

| Layer      | Technology                          |
| ---------- | ----------------------------------- |
| Backend    | Python, FastAPI                     |
| Database   | SQLite (SQLAlchemy)                 |
| Auth       | JWT                                 |
| AI         | Gemini API                          |
| Frontend   | React, Vite, Tailwind CSS           |
| Testing    | pytest                              |
| Deployment | Render (backend), Vercel (frontend) |

## Project structure

```
jobpilot/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── models.py        # Database models
│   │   ├── schemas.py       # Request/response schemas
│   │   ├── auth.py          # Signup, login, JWT
│   │   ├── routes/
│   │   │   ├── applications.py
│   │   │   └── matcher.py
│   │   └── services/
│   │       └── ai_matcher.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── (React + Vite app)
├── docs/
│   └── screenshot.png
├── .gitignore
└── README.md
```

## Getting started

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows; use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
cp .env.example .env         # then add your own keys
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

### Environment variables

| Variable         | Purpose                   |
| ---------------- | ------------------------- |
| `GEMINI_API_KEY` | Powers the resume matcher |
| `SECRET_KEY`     | Signs JWT tokens          |

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Running tests

```bash
cd backend
pytest
```

## What I'm learning

- Designing a REST API and structuring a FastAPI project
- Implementing authentication and per-user data access
- Prompting an LLM for structured output
- Testing, CI and deployment

## Roadmap

See the checklist under **Features**. I update it as I ship each piece.

## Author

**Al Ameen N H**
Final-year B.Tech CSE, Govt. Model Engineering College, Kochi
GitHub: [@AlAmeennh](https://github.com/AlAmeennh) | Email: alameennh.mec@gmail.com

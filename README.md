# JobPilot

![Tests](https://github.com/AlAmeennh/jobpilot/actions/workflows/tests.yml/badge.svg)

An AI-assisted job application tracker. Keep every application in one place, see where you stand at a glance, and check how well your resume (PDF or pasted text) matches a job description.

> **Status:** Under active development. Built solo as a learning project and for my own job search.

**Live demo:** _coming soon_

<!-- Add screenshots here once saved in docs/, for example: ![Applications page](docs/applications.png) -->

## Why I built this

I'm a final-year CSE student applying for software roles off-campus. Spreadsheets got messy fast, and I wanted a tool that also tells me how well my resume fits each job. So I built it.

## Features

**Done**

- [x] Sign up and log in with JWT authentication (passwords are hashed)
- [x] Add, edit, delete and filter job applications
- [x] Track status: Applied, Interview, Offer, Rejected
- [x] Dashboard summary cards with per-status counts
- [x] Each user only sees their own data
- [x] AI resume matcher: get a match score, matched skills, missing skills and suggestions
- [x] Resume input as a **PDF upload** or pasted text
- [x] React frontend with login, applications and matcher pages
- [x] Automated backend tests (pytest) and CI with GitHub Actions

**Planned**

- [ ] Notes and follow-up dates, with an overdue highlight
- [ ] Search and sort
- [ ] Export to CSV
- [ ] Docker setup (`docker compose up`)
- [ ] Deployment with a live demo link (PostgreSQL)

## Tech stack

| Layer      | Technology                                   |
| ---------- | -------------------------------------------- |
| Backend    | Python, FastAPI                              |
| Database   | SQLite with SQLAlchemy                       |
| Auth       | JWT                                          |
| AI         | Google Gemini API                            |
| PDF text   | pypdf                                        |
| Frontend   | React, Vite, Tailwind CSS, React Router      |
| Testing    | pytest, GitHub Actions                       |
| Deployment | Planned: Render (backend), Vercel (frontend) |

## API overview

| Method | Endpoint                | Purpose                                | Auth |
| ------ | ----------------------- | -------------------------------------- | ---- |
| POST   | `/auth/signup`          | Create an account                      | No   |
| POST   | `/auth/login`           | Log in and receive a token             | No   |
| GET    | `/applications`         | List your applications (`?status=`)    | Yes  |
| POST   | `/applications`         | Add an application                     | Yes  |
| GET    | `/applications/stats`   | Counts per status                      | Yes  |
| GET    | `/applications/{id}`    | Get one application                    | Yes  |
| PATCH  | `/applications/{id}`    | Update an application                  | Yes  |
| DELETE | `/applications/{id}`    | Delete an application                  | Yes  |
| POST   | `/matcher`              | Match a job description with resume text | Yes |
| POST   | `/matcher/upload`       | Match a job description with a resume PDF | Yes |

Interactive docs are available at `http://localhost:8000/docs` when the backend is running.

## Project structure

```
jobpilot/
├── .github/workflows/
│   └── tests.yml                # CI: runs the tests on every push
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, routers
│   │   ├── database.py          # SQLAlchemy engine and session
│   │   ├── models.py            # User and Application models
│   │   ├── schemas.py           # Request/response schemas
│   │   ├── auth.py              # Password hashing and JWT helpers
│   │   ├── routes/
│   │   │   ├── auth.py          # Signup and login
│   │   │   ├── applications.py  # CRUD and stats
│   │   │   └── matcher.py       # Text and PDF matching
│   │   └── services/
│   │       ├── ai_matcher.py    # Gemini call with retries
│   │       └── pdf_reader.py    # PDF text extraction and validation
│   ├── tests/
│   │   └── test_applications.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── api.js               # All backend calls
│       ├── App.jsx              # Routes and login protection
│       ├── components/
│       │   └── StatsBar.jsx
│       └── pages/
│           ├── AuthPage.jsx
│           ├── Dashboard.jsx
│           └── MatcherPage.jsx
├── .gitignore
└── README.md
```

## Getting started

You need Python 3.13 and Node.js (current LTS). Run the backend and the frontend in two separate terminals.

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows; on macOS/Linux use: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env       # Windows; on macOS/Linux use: cp .env.example .env
# then open .env and add your own values
uvicorn app.main:app --reload
```

The API runs at http://localhost:8000 (docs at http://localhost:8000/docs).

### Environment variables

| Variable         | Required | Purpose                                                |
| ---------------- | -------- | ------------------------------------------------------ |
| `SECRET_KEY`     | Yes      | Signs JWT tokens                                       |
| `GEMINI_API_KEY` | Yes      | Powers the resume matcher                              |
| `GEMINI_MODEL`   | No       | Gemini model to use (default: `gemini-3.5-flash-lite`) |

Generate a secret key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Never commit your `.env` file. Get a Gemini API key from Google AI Studio.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The backend must be running on port 8000.

## Running tests

```bash
cd backend
python -m pytest -v
```

The tests use an in-memory database and a fake AI response, so they need no API key and make no network calls. They cover authentication, per-user data isolation, CRUD, stats and PDF upload validation.

## Notes on the resume matcher

- Only text-based PDFs are supported. Scanned or image-only PDFs have no readable text, and the app says so.
- Uploads are limited to 5 MB. The file is read in memory and is not stored.
- The extracted resume text is sent to Google's Gemini API for analysis.
- If the Gemini model is busy, the backend retries automatically before returning an error.

## What I'm learning

- Designing a REST API and structuring a FastAPI project
- Authentication, password hashing and per-user data access
- Prompting an LLM for structured output, and handling its failures
- Building a React frontend that talks to a protected API
- Testing, CI and, next, deployment

## Roadmap

See the checklist under **Features**. I update it as I ship each piece.

## Author

**Al Ameen N H**
Final-year B.Tech CSE, Govt. Model Engineering College, Kochi
GitHub: [@AlAmeennh](https://github.com/AlAmeennh) | Email: alameennh.mec@gmail.com

from fastapi import FastAPI

from .database import Base, engine
from . import models
from .routes import applications, auth, matcher
from app.services import ai_matcher

Base.metadata.create_all(bind=engine)

app = FastAPI(title="JobPilot API")
app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(matcher.router)


@app.get("/health")
def health():
    return {"status": "ok"}

def test_matcher_requires_login():
    r = client.post("/matcher", json={"job_description": "x" * 40, "resume_text": "y" * 40})
    assert r.status_code == 401


def test_matcher_returns_result(monkeypatch):
    def fake_analyze(job_description, resume_text):
        return {
            "required_skills": ["Python", "SQL"],
            "matched_skills": ["Python"],
            "missing_skills": ["SQL"],
            "match_score": 70,
            "suggestions": ["Add a SQL project"],
        }

    monkeypatch.setattr(ai_matcher, "analyze_match", fake_analyze)
    h = auth_headers()
    r = client.post(
        "/matcher",
        json={"job_description": "x" * 40, "resume_text": "y" * 40},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["match_score"] == 70
    assert r.json()["missing_skills"] == ["SQL"]
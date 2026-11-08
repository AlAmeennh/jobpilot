import io


import pytest
from pypdf import PdfWriter
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.services import ai_matcher
from app.services import ai_matcher, pdf_reader

# A separate in-memory database, so tests never touch jobpilot.db
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def auth_headers(email="a@example.com", password="password123"):
    client.post("/auth/signup", json={"email": email, "password": password})
    r = client.post("/auth/login", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_requires_login():
    assert client.get("/applications").status_code == 401


def test_signup_duplicate_email():
    body = {"email": "a@example.com", "password": "password123"}
    assert client.post("/auth/signup", json=body).status_code == 201
    assert client.post("/auth/signup", json=body).status_code == 400


def test_wrong_password():
    auth_headers()
    r = client.post("/auth/login", data={"username": "a@example.com", "password": "wrongpass1"})
    assert r.status_code == 401


def test_create_and_list():
    h = auth_headers()
    r = client.post("/applications", json={"company": "Acme", "role": "Intern"}, headers=h)
    assert r.status_code == 201
    assert len(client.get("/applications", headers=h).json()) == 1


def test_update_and_delete():
    h = auth_headers()
    app_id = client.post("/applications", json={"company": "Acme", "role": "Dev"}, headers=h).json()["id"]
    r = client.patch(f"/applications/{app_id}", json={"status": "Interview"}, headers=h)
    assert r.json()["status"] == "Interview"
    assert client.delete(f"/applications/{app_id}", headers=h).status_code == 204
    assert client.get(f"/applications/{app_id}", headers=h).status_code == 404


def test_users_cannot_see_each_others_data():
    h1 = auth_headers("one@example.com")
    h2 = auth_headers("two@example.com")
    app_id = client.post("/applications", json={"company": "Acme", "role": "Dev"}, headers=h1).json()["id"]
    assert client.get("/applications", headers=h2).json() == []
    assert client.get(f"/applications/{app_id}", headers=h2).status_code == 404


def test_invalid_status_rejected():
    h = auth_headers()
    r = client.post("/applications", json={"company": "A", "role": "B", "status": "Banana"}, headers=h)
    assert r.status_code == 422


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

def test_stats_counts_by_status():
    h = auth_headers()
    client.post("/applications", json={"company": "A", "role": "Dev"}, headers=h)
    client.post("/applications", json={"company": "B", "role": "Dev", "status": "Interview"}, headers=h)
    r = client.get("/applications/stats", headers=h)
    assert r.status_code == 200
    assert r.json()["total"] == 2
    assert r.json()["by_status"]["Applied"] == 1
    assert r.json()["by_status"]["Interview"] == 1
    assert r.json()["by_status"]["Offer"] == 0


def test_stats_only_counts_own_applications():
    h1 = auth_headers("one@example.com")
    h2 = auth_headers("two@example.com")
    client.post("/applications", json={"company": "A", "role": "Dev"}, headers=h1)
    assert client.get("/applications/stats", headers=h2).json()["total"] == 0

def blank_pdf_bytes():
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


JD = "x" * 40


def test_pdf_upload_requires_login():
    r = client.post(
        "/matcher/upload",
        data={"job_description": JD},
        files={"resume": ("cv.pdf", b"%PDF-1.4", "application/pdf")},
    )
    assert r.status_code == 401


def test_pdf_upload_rejects_non_pdf():
    h = auth_headers()
    r = client.post(
        "/matcher/upload",
        data={"job_description": JD},
        files={"resume": ("cv.txt", b"hello world", "text/plain")},
        headers=h,
    )
    assert r.status_code == 400


def test_pdf_upload_rejects_pdf_without_text():
    h = auth_headers()
    r = client.post(
        "/matcher/upload",
        data={"job_description": JD},
        files={"resume": ("cv.pdf", blank_pdf_bytes(), "application/pdf")},
        headers=h,
    )
    assert r.status_code == 422


def test_pdf_upload_returns_result(monkeypatch):
    monkeypatch.setattr(pdf_reader, "extract_text", lambda data: "Python and FastAPI developer " * 3)

    def fake_analyze(job_description, resume_text):
        return {
            "required_skills": ["Python"],
            "matched_skills": ["Python"],
            "missing_skills": [],
            "match_score": 90,
            "suggestions": [],
        }

    monkeypatch.setattr(ai_matcher, "analyze_match", fake_analyze)
    h = auth_headers()
    r = client.post(
        "/matcher/upload",
        data={"job_description": JD},
        files={"resume": ("cv.pdf", b"%PDF-1.4 fake", "application/pdf")},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["match_score"] == 90
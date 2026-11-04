import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

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
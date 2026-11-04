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


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_create_and_list():
    r = client.post("/applications", json={"company": "Acme", "role": "Python Intern"})
    assert r.status_code == 201
    assert r.json()["status"] == "Applied"

    r = client.get("/applications")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_update_status():
    created = client.post("/applications", json={"company": "Acme", "role": "Dev"}).json()
    r = client.patch(f"/applications/{created['id']}", json={"status": "Interview"})
    assert r.status_code == 200
    assert r.json()["status"] == "Interview"


def test_delete_then_not_found():
    created = client.post("/applications", json={"company": "Acme", "role": "Dev"}).json()
    assert client.delete(f"/applications/{created['id']}").status_code == 204
    assert client.get(f"/applications/{created['id']}").status_code == 404


def test_invalid_status_rejected():
    r = client.post(
        "/applications",
        json={"company": "Acme", "role": "Dev", "status": "Banana"},
    )
    assert r.status_code == 422
import pytest

from app import create_app
from app.models import db


@pytest.fixture
def client():
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_index_shows_seeded_profile(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Bharath C Y" in resp.data


def test_edit_updates_profile(client):
    resp = client.post(
        "/edit",
        data={
            "name": "Updated Name",
            "title": "Lead SRE",
            "summary": "New summary",
            "about": "New about",
            "location": "Remote",
            "email": "new@example.com",
            "github": "https://github.com/updated",
            "linkedin": "#",
            "years_experience": "10+",
            "pipelines": "200+",
            "uptime": "99.99%",
            "clusters": "60+",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Updated Name" in resp.data
    assert b"Lead SRE" in resp.data

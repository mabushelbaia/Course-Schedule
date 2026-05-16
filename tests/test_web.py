from fastapi.testclient import TestClient
import pytest


@pytest.fixture
def client():
    from course_schedule.web import app
    return TestClient(app)


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_upload_no_file(client):
    r = client.post("/api/upload")
    assert r.status_code == 422


def test_upload_non_html(client):
    r = client.post("/api/upload", files={"file": ("test.txt", b"hello", "text/plain")})
    assert r.status_code == 400


def test_download_missing(client):
    r = client.get("/api/download/nonexistent")
    assert r.status_code == 404

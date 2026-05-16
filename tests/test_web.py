import pytest


@pytest.fixture
def client():
    from course_schedule.web import app
    from fastapi.testclient import TestClient
    return TestClient(app)


def test_home_page_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_upload_page_returns_200(client):
    response = client.get("/upload")
    assert response.status_code == 200


def test_live_page_returns_200(client):
    response = client.get("/live")
    assert response.status_code == 200


def test_calendar_page_returns_200(client):
    response = client.get("/calendar")
    assert response.status_code == 200


def test_download_missing_returns_404(client):
    response = client.get("/download/nonexistent")
    assert response.status_code == 404


def test_upload_without_file_returns_422(client):
    response = client.post("/upload")
    assert response.status_code == 422


def test_upload_with_non_html_returns_error_partial(client):
    response = client.post("/upload", files={"file": ("test.txt", b"hello", "text/plain")})
    assert response.status_code == 200
    assert "Error" in response.text or "error" in response.text

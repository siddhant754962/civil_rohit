from fastapi.testclient import TestClient
from app.main import app

def test_public_pages():
    client = TestClient(app)
    for path in ["/", "/about", "/services", "/projects", "/contact", "/health", "/privacy", "/terms"]:
        response = client.get(path)
        assert response.status_code == 200, (path, response.status_code)

def test_admin_login_page():
    client = TestClient(app)
    assert client.get("/admin/login").status_code == 200

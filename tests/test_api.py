"""
API Integration Tests
Tests for all API endpoints and functionality.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.database import get_database
from app.database.models import Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_database] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers():
    """Get authentication headers for testing."""
    # Register a test user
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }
    
    with TestClient(app) as client:
        response = client.post("/api/v1/auth/register", json=user_data)
        token = response.json()["access_token"]
        
        return {"Authorization": f"Bearer {token}"}

def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "unhealthy"]

def test_register_user(client):
    """Test user registration."""
    user_data = {
        "email": "newuser@example.com",
        "password": "TestPassword123!",
        "full_name": "New User"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == user_data["email"]

def test_login_user(client):
    """Test user login."""
    # First register a user
    user_data = {
        "email": "loginuser@example.com",
        "password": "TestPassword123!",
        "full_name": "Login User"
    }
    client.post("/api/v1/auth/register", json=user_data)
    
    # Then login
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

def test_protected_endpoint_without_auth(client):
    """Test protected endpoint without authentication."""
    response = client.get("/api/v1/files")
    assert response.status_code == 401

def test_file_upload_with_auth(client, auth_headers):
    """Test file upload with authentication."""
    # Create a test CSV file
    csv_content = "name,age,city\nJohn,25,NYC\nJane,30,LA"
    
    files = {"file": ("test.csv", csv_content, "text/csv")}
    response = client.post("/api/v1/upload/", files=files, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "file_id" in data

def test_file_upload_invalid_type(client, auth_headers):
    """Test file upload with invalid file type."""
    files = {"file": ("test.txt", "invalid content", "text/plain")}
    response = client.post("/api/v1/upload/", files=files, headers=auth_headers)
    
    assert response.status_code == 400
    assert "File type" in response.json()["detail"]

def test_analysis_without_file(client, auth_headers):
    """Test analysis without uploaded file."""
    analysis_data = {
        "file_id": "nonexistent",
        "include_correlation": True,
        "include_outliers": True
    }
    
    response = client.post("/api/v1/analysis/", json=analysis_data, headers=auth_headers)
    assert response.status_code == 404

def test_visualization_without_file(client, auth_headers):
    """Test visualization without uploaded file."""
    viz_data = {
        "file_id": "nonexistent",
        "chart_type": "bar",
        "column": "test"
    }
    
    response = client.post("/api/v1/visualization/", json=viz_data, headers=auth_headers)
    assert response.status_code == 404

def test_insights_without_file(client, auth_headers):
    """Test insights generation without uploaded file."""
    insight_data = {
        "file_id": "nonexistent",
        "llm_provider": "groq"
    }
    
    response = client.post("/api/v1/insights/", json=insight_data, headers=auth_headers)
    assert response.status_code == 404 
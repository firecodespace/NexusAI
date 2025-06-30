import pytest
from fastapi.testclient import TestClient
import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to NexusAI API" in response.json()["message"]

def test_invoice_upload_endpoint(sample_invoice_path):
    # Create test invoice content
    with open(sample_invoice_path, "wb") as f:
        f.write(b"Test invoice content")
    
    # Test file upload
    with open(sample_invoice_path, "rb") as f:
        response = client.post(
            "/api/v1/invoices/upload",
            files={"file": ("sample_invoice.pdf", f, "application/pdf")}
        )
    
    assert response.status_code == 200
    assert "invoice_id" in response.json()

def test_invoice_processing():
    # Test invoice processing endpoint
    response = client.post("/api/v1/invoices/1/process")  # Assuming invoice ID 1 exists
    assert response.status_code == 200
    assert "ocr" in response.json()
    assert "gst" in response.json()

def test_invoice_list():
    # Test getting list of invoices
    response = client.get("/api/v1/invoices/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_invoice_detail():
    # Test getting specific invoice details
    response = client.get("/api/v1/invoices/1")  # Assuming invoice ID 1 exists
    assert response.status_code == 200
    assert "invoice_number" in response.json()

@pytest.fixture(autouse=True)
def cleanup():
    # Cleanup after each test
    yield
    test_file_path = Path("backend/tests/test_data/sample_invoice.pdf")
    if test_file_path.exists():
        os.remove(test_file_path) 
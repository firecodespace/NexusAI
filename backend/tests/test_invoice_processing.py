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
            "/invoices/upload",
            files={"file": ("sample_invoice.pdf", f, "application/pdf")}
        )
    
    assert response.status_code == 200
    assert "invoice_id" in response.json()

def test_invoice_processing():
    # Test invoice processing endpoint
    response = client.get("/invoices/process/1")  # Assuming invoice ID 1 exists
    assert response.status_code == 200
    assert "status" in response.json()
    assert "extracted_data" in response.json()

def test_invoice_validation():
    # Test invoice data validation
    test_data = {
        "invoice_number": "INV-001",
        "date": "2024-03-20",
        "amount": 1000.00,
        "vendor": "Test Vendor"
    }
    
    response = client.post("/invoices/validate", json=test_data)
    assert response.status_code == 200
    assert "is_valid" in response.json()
    assert "validation_errors" in response.json()

@pytest.fixture(autouse=True)
def cleanup():
    # Cleanup after each test
    yield
    test_file_path = Path("backend/tests/test_data/sample_invoice.pdf")
    if test_file_path.exists():
        os.remove(test_file_path) 
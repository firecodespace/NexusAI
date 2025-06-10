import pytest
import os
from pathlib import Path
import sys

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

@pytest.fixture(scope="session")
def test_data_dir():
    """Create and return the test data directory path"""
    test_dir = Path(__file__).parent / "test_data"
    test_dir.mkdir(exist_ok=True)
    return test_dir

@pytest.fixture(scope="session")
def sample_invoice_path(test_data_dir):
    """Create and return a path to a sample invoice file"""
    return test_data_dir / "sample_invoice.pdf"

@pytest.fixture(autouse=True)
def cleanup_test_files(sample_invoice_path):
    """Clean up test files after each test"""
    yield
    if sample_invoice_path.exists():
        os.remove(sample_invoice_path) 
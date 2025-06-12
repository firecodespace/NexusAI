import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.ocr_service import get_vision_client, run_ocr_on_file

def test_ocr():
    """Test the OCR service with a sample image."""
    try:
        # First test if we can get the Vision client
        print("🔍 Testing Vision client initialization...")
        client = get_vision_client()
        print("✅ Vision client initialized successfully!")
        
        # Test with a sample image
        test_image_path = Path(__file__).parent.parent / "data" / "test_images" / "test_invoice.jpg"
        
        if not test_image_path.exists():
            print("❌ Test image not found. Please place a test invoice image at:", test_image_path)
            print("\nTo test the OCR service:")
            print("1. Place a sample invoice image (JPG or PNG) at:", test_image_path)
            print("2. Run this script again")
            return
            
        print(f"🔍 Testing OCR with image: {test_image_path}")
        
        # Read the image file
        with open(test_image_path, "rb") as f:
            image_bytes = f.read()
            
        # Run OCR
        result = run_ocr_on_file(image_bytes)
        
        print("\n📄 OCR Results:")
        print("---------------")
        for key, value in result.items():
            print(f"{key}: {value}")
            
        print("\n✅ OCR test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during OCR test: {str(e)}")
        raise

if __name__ == "__main__":
    test_ocr() 
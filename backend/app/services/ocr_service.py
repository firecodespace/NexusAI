import os

from google.cloud import vision

def run_ocr_on_file(file_bytes: bytes) -> str:
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=file_bytes)
    response = client.document_text_detection(image=image)

    if response.error.message:
        raise Exception(f"Vision API error: {response.error.message}")

    return response.full_text_annotation.text

print("🔑 Using Google key:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
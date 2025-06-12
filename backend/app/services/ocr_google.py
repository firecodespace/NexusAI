import os
from google.cloud import vision
from PIL import Image
import io
from typing import Dict, List, Tuple
from .invoice_extraction import extract_fields_with_model

def run_google_vision_and_layoutlm(file_path: str) -> Dict[str, str]:
    """
    Process an invoice using Google Vision OCR and LayoutLMv3
    """
    try:
        # Initialize Google Vision client
        client = vision.ImageAnnotatorClient()

        # Read the file
        with open(file_path, 'rb') as image_file:
            content = image_file.read()

        # Create image object
        image = vision.Image(content=content)

        # Perform document text detection
        response = client.document_text_detection(image=image)

        if response.error.message:
            raise Exception(f"Vision API error: {response.error.message}")

        # Extract text and bounding boxes
        words = []
        boxes = []
        
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        word_text = ''.join([
                            symbol.text for symbol in word.symbols
                        ])
                        words.append(word_text)
                        
                        # Get bounding box
                        vertices = word.bounding_box.vertices
                        box = [
                            vertices[0].x,
                            vertices[0].y,
                            vertices[2].x,
                            vertices[2].y
                        ]
                        boxes.append(box)

        # Use LayoutLMv3 to extract structured fields
        fields = extract_fields_with_model(file_path, words, boxes)

        # Add any missing fields with default values
        required_fields = [
            "invoice_number", "invoice_date", "due_date", "gstin",
            "total", "currency", "vendor_name", "vendor_tax_id",
            "customer_name", "payment_terms"
        ]

        for field in required_fields:
            if field not in fields:
                fields[field] = "N/A"

        return fields

    except Exception as e:
        raise Exception(f"Error processing invoice: {str(e)}")
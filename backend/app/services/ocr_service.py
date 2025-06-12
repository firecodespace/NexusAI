import os
from google.cloud import vision
from typing import Dict, Any, Optional
from google.oauth2 import service_account
import json
from datetime import datetime
import re

def get_vision_client():
    """Initialize and return a Google Cloud Vision client with proper credentials."""
    try:
        # First try to get credentials from environment variable
        credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if credentials_path and os.path.exists(credentials_path):
            print(f"🔑 Using credentials from: {credentials_path}")
            try:
                with open(credentials_path, 'r') as f:
                    credentials_info = json.load(f)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_info,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
                return vision.ImageAnnotatorClient(credentials=credentials)
            except Exception as e:
                print(f"❌ Error loading credentials from {credentials_path}: {str(e)}")
        
        # If not found in env, try to find in credentials directory
        default_credentials_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                              'credentials', 'google-vision-key.json')
        
        if os.path.exists(default_credentials_path):
            print(f"🔑 Using credentials from default path: {default_credentials_path}")
            try:
                with open(default_credentials_path, 'r') as f:
                    credentials_info = json.load(f)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_info,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
                return vision.ImageAnnotatorClient(credentials=credentials)
            except Exception as e:
                print(f"❌ Error loading credentials from {default_credentials_path}: {str(e)}")
            
        raise Exception("Google Cloud credentials not found or invalid. Please check your credentials file and ensure it has the correct permissions.")
        
    except Exception as e:
        raise Exception(f"Failed to initialize Google Cloud Vision client: {str(e)}")

def run_ocr_on_file(file_bytes: bytes) -> Dict[str, Any]:
    """
    Perform OCR on an invoice file using Google Vision API.
    
    Args:
        file_bytes: The invoice file content as bytes
        
    Returns:
        Dict containing extracted invoice data
    """
    try:
        # Initialize the Vision API client
        client = get_vision_client()
        
        # Create an image object
        image = vision.Image(content=file_bytes)
        
        # Perform text detection
        response = client.text_detection(image=image)
        texts = response.text_annotations
        
        if not texts:
            raise Exception("No text detected in the image")
            
        # Get the full text
        full_text = texts[0].description
        
        # Extract invoice data
        return extract_invoice_data(full_text)
        
    except Exception as e:
        raise Exception(f"OCR processing failed: {str(e)}")

def extract_invoice_data(text: str) -> Dict[str, Any]:
    """
    Extract key information from OCR text.
    
    Args:
        text: The OCR text to process
        
    Returns:
        Dict containing extracted invoice data
    """
    try:
        # Initialize result dictionary
        result = {
            "invoice_number": None,
            "date": None,
            "vendor": None,
            "amount": None,
            "gstin": None,
            "hsn_code": None
        }
        
        # Extract invoice number (common patterns)
        invoice_patterns = [
            r'INV[-\s]?(\d+)',
            r'Invoice\s*#?\s*(\d+)',
            r'Bill\s*#?\s*(\d+)'
        ]
        for pattern in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["invoice_number"] = match.group(0)
                break
                
        # Extract date (common formats)
        date_patterns = [
            r'\d{2}[-/]\d{2}[-/]\d{4}',
            r'\d{4}[-/]\d{2}[-/]\d{2}',
            r'\d{2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                result["date"] = match.group(0)
                break
                
        # Extract amount (look for currency symbols and numbers)
        amount_pattern = r'(?:Rs\.?|INR|₹)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'
        match = re.search(amount_pattern, text)
        if match:
            amount_str = match.group(1).replace(',', '')
            result["amount"] = float(amount_str)
            
        # Extract GSTIN (standard format)
        gstin_pattern = r'\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}'
        match = re.search(gstin_pattern, text)
        if match:
            result["gstin"] = match.group(0)
            
        # Extract HSN code (4-8 digit number)
        hsn_pattern = r'\b\d{4,8}\b'
        match = re.search(hsn_pattern, text)
        if match:
            result["hsn_code"] = match.group(0)
            
        # Extract vendor name (look for common keywords)
        vendor_keywords = ['From:', 'Vendor:', 'Supplier:', 'Bill To:', 'Sold By:']
        for keyword in vendor_keywords:
            if keyword in text:
                # Get the line containing the keyword
                lines = text.split('\n')
                for line in lines:
                    if keyword in line:
                        # Extract the vendor name (everything after the keyword)
                        vendor = line.split(keyword)[1].strip()
                        if vendor:
                            result["vendor"] = vendor
                            break
                if result["vendor"]:
                    break
                    
        return result
        
    except Exception as e:
        raise Exception(f"Failed to extract invoice data: {str(e)}")

print("🔑 Using Google key:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
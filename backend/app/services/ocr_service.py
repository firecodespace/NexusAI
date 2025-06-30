import os
import easyocr
from typing import Dict, Any, Optional, List
import re
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize EasyOCR reader (will download models on first use)
reader = None

def get_ocr_reader():
    """Initialize and return EasyOCR reader."""
    global reader
    if reader is None:
        try:
            logger.info("🔄 Initializing EasyOCR reader...")
            # Initialize with English language
            reader = easyocr.Reader(['en'])
            logger.info("✅ EasyOCR reader initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize EasyOCR reader: {str(e)}")
            raise Exception(f"Failed to initialize EasyOCR reader: {str(e)}")
    return reader

def run_ocr_on_file(file_bytes: bytes) -> Dict[str, Any]:
    """
    Perform OCR on an invoice file using EasyOCR.
    
    Args:
        file_bytes: The invoice file content as bytes
        
    Returns:
        Dict containing extracted invoice data
    """
    try:
        # Get OCR reader
        ocr_reader = get_ocr_reader()
        
        # Perform OCR
        logger.info("🔍 Performing OCR on image...")
        results = ocr_reader.readtext(file_bytes)
        
        if not results:
            raise Exception("No text detected in the image")
        
        # Extract text from results
        full_text = ' '.join([text[1] for text in results])
        logger.info(f"📝 Extracted text length: {len(full_text)} characters")
        
        # Extract invoice data
        return extract_invoice_data(full_text)
        
    except Exception as e:
        logger.error(f"❌ OCR processing failed: {str(e)}")
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
        # Initialize result dictionary with more detailed fields
        result = {
            "invoice_number": None,
            "receipt_number": None,
            "date": None,
            "time": None,
            "vendor": None,
            "vendor_address": None,
            "vendor_phone": None,
            "vendor_fax": None,
            "amount": None,
            "subtotal": None,
            "discount": None,
            "gst_amount": None,
            "gstin": None,
            "hsn_code": None,
            "salesperson": None,
            "cashier": None,
            "items": [],
            "raw_text": text[:1000]  # Store first 1000 chars for debugging
        }
        
        # Extract invoice number (common patterns)
        invoice_patterns = [
            r'INV[-\s]?(\d+)',
            r'Invoice\s*#?\s*(\d+)',
            r'Bill\s*#?\s*(\d+)',
            r'Invoice\s*No[.:]?\s*(\d+)',
            r'Bill\s*No[.:]?\s*(\d+)'
        ]
        for pattern in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["invoice_number"] = match.group(0)
                break
                
        # Extract receipt number
        receipt_patterns = [
            r'Receipt\s*#?\s*(\w+)',
            r'Receipt\s*No[.:]?\s*(\w+)',
            r'CS\d+',  # Common receipt format like CS0009309
        ]
        for pattern in receipt_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["receipt_number"] = match.group(0)
                break
                
        # Extract date (common formats)
        date_patterns = [
            r'\d{2}[-/]\d{2}[-/]\d{4}',
            r'\d{4}[-/]\d{2}[-/]\d{2}',
            r'\d{2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',
            r'\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}'
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                result["date"] = match.group(0)
                break
                
        # Extract time
        time_patterns = [
            r'Time[:\s]*(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?)',
            r'(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?)'
        ]
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["time"] = match.group(1)
                break
                
        # Extract vendor information
        vendor_info = extract_vendor_info(text)
        result.update(vendor_info)
                
        # Extract amounts (look for currency symbols and numbers)
        amount_info = extract_amount_info(text)
        result.update(amount_info)
            
        # Extract GSTIN (standard format)
        gstin_pattern = r'\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}'
        match = re.search(gstin_pattern, text)
        if match:
            result["gstin"] = match.group(0)
            
        # Extract HSN code (4-8 digit number, often near "HSN" or "SAC")
        hsn_patterns = [
            r'HSN[:\s]*(\d{4,8})',
            r'SAC[:\s]*(\d{4,8})',
            r'\b(\d{4,8})\b'  # Any 4-8 digit number
        ]
        for pattern in hsn_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["hsn_code"] = match.group(1)
                break
                
        # Extract salesperson and cashier
        salesperson_match = re.search(r'Salesperson[:\s]*(\w+)', text, re.IGNORECASE)
        if salesperson_match:
            result["salesperson"] = salesperson_match.group(1)
            
        cashier_match = re.search(r'Cashier[:\s]*(\w+)', text, re.IGNORECASE)
        if cashier_match:
            result["cashier"] = cashier_match.group(1)
            
        # Extract item details
        result["items"] = extract_item_details(text)
                    
        logger.info(f"✅ Extracted data: {result}")
        return result
        
    except Exception as e:
        logger.error(f"❌ Failed to extract invoice data: {str(e)}")
        raise Exception(f"Failed to extract invoice data: {str(e)}")

def extract_vendor_info(text: str) -> Dict[str, Any]:
    """Extract vendor information from text"""
    vendor_info = {
        "vendor": None,
        "vendor_address": None,
        "vendor_phone": None,
        "vendor_fax": None
    }
    
    # Extract vendor name (look for common keywords)
    vendor_keywords = ['From:', 'Vendor:', 'Supplier:', 'Bill To:', 'Sold By:', 'Company:', 'Business:']
    for keyword in vendor_keywords:
        if keyword in text:
            # Get the line containing the keyword
            lines = text.split('\n')
            for line in lines:
                if keyword in line:
                    # Extract the vendor name (everything after the keyword)
                    vendor = line.split(keyword)[1].strip()
                    if vendor and len(vendor) > 2:  # Ensure it's not just whitespace
                        vendor_info["vendor"] = vendor
                        break
            if vendor_info["vendor"]:
                break
    
    # If no vendor found, try to extract from common patterns
    if not vendor_info["vendor"]:
        # Look for company names in all caps
        company_pattern = r'\b[A-Z][A-Z\s&]+(?:LTD|LLC|INC|CORP|COMPANY|CO\.|SDN BHD)\b'
        match = re.search(company_pattern, text)
        if match:
            vendor_info["vendor"] = match.group(0)
    
    # Extract phone number
    phone_patterns = [
        r'TEL[:\s]*(\d{2,4}[-\s]?\d{3,4}[-\s]?\d{4})',
        r'Phone[:\s]*(\d{2,4}[-\s]?\d{3,4}[-\s]?\d{4})',
        r'(\d{2,4}[-\s]?\d{3,4}[-\s]?\d{4})'
    ]
    for pattern in phone_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            vendor_info["vendor_phone"] = match.group(1)
            break
    
    # Extract fax number
    fax_patterns = [
        r'FAX[:\s]*(\d{2,4}[-\s]?\d{3,4}[-\s]?\d{4})',
        r'Fax[:\s]*(\d{2,4}[-\s]?\d{3,4}[-\s]?\d{4})'
    ]
    for pattern in fax_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            vendor_info["vendor_fax"] = match.group(1)
            break
    
    # Extract address (look for address patterns)
    address_patterns = [
        r'NO\s+\d+[A-Z]?,\s+[A-Z\s]+(?:SECTION\d+)?',
        r'\d+[A-Z]?,\s+[A-Z\s]+(?:ROAD|STREET|AVENUE|LANE)',
        r'[A-Z\s]+(?:CITY|STATE|PROVINCE)'
    ]
    for pattern in address_patterns:
        match = re.search(pattern, text)
        if match:
            vendor_info["vendor_address"] = match.group(0)
            break
    
    return vendor_info

def extract_amount_info(text: str) -> Dict[str, Any]:
    """Extract amount information from text"""
    amount_info = {
        "amount": None,
        "subtotal": None,
        "discount": None,
        "gst_amount": None
    }
    
    # Extract total amount (look for currency symbols and numbers)
    total_patterns = [
        r'(?:Rs\.?|INR|₹)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'Total[:\s]*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'Amount[:\s]*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'Grand\s*Total[:\s]*(\d+(?:,\d{3})*(?:\.\d{2})?)'
    ]
    for pattern in total_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                amount_info["amount"] = float(amount_str)
                break
            except ValueError:
                continue
    
    # Extract subtotal
    subtotal_patterns = [
        r'Sub\s*Total[:\s]*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'Subtotal[:\s]*(\d+(?:,\d{3})*(?:\.\d{2})?)'
    ]
    for pattern in subtotal_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                amount_info["subtotal"] = float(amount_str)
                break
            except ValueError:
                continue
    
    # Extract discount
    discount_patterns = [
        r'Discount[:\s]*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'Disc[:\s]*(\d+(?:,\d{3})*(?:\.\d{2})?)'
    ]
    for pattern in discount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                amount_info["discount"] = float(amount_str)
                break
            except ValueError:
                continue
    
    # Extract GST amount
    gst_patterns = [
        r'Total\s*GST[:\s]*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'GST[:\s]*(\d+(?:,\d{3})*(?:\.\d{2})?)',
        r'(?:GST|GST)\s*Amount[:\s]*(\d+(?:,\d{3})*(?:\.\d{2})?)'
    ]
    for pattern in gst_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                amount_info["gst_amount"] = float(amount_str)
                break
            except ValueError:
                continue
    
    return amount_info

def extract_item_details(text: str) -> List[Dict[str, Any]]:
    """Extract item details from text"""
    items = []
    
    # Look for item patterns
    lines = text.split('\n')
    for line in lines:
        # Look for lines with item codes, descriptions, and amounts
        item_pattern = r'(\d{6,})\s+([A-Z\s\-]+)\s+(\d+\.\d{2})'
        match = re.search(item_pattern, line)
        if match:
            item_code = match.group(1)
            description = match.group(2).strip()
            amount = float(match.group(3))
            
            items.append({
                "code": item_code,
                "description": description,
                "amount": amount
            })
    
    return items

# Test function for debugging
def test_ocr():
    """Test OCR functionality with a sample image."""
    try:
        # Create a simple test image with text
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Create a test image
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add some test text
        test_text = [
            "INVOICE #12345",
            "Date: 28/06/2025",
            "Vendor: Test Company Ltd",
            "Amount: Rs. 1500.00",
            "GSTIN: 22AAAAA0000A1Z5"
        ]
        
        y_position = 20
        for line in test_text:
            draw.text((20, y_position), line, fill='black')
            y_position += 30
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()
        
        # Test OCR
        result = run_ocr_on_file(img_bytes)
        print("🧪 OCR Test Result:", result)
        return result
        
    except Exception as e:
        print(f"❌ OCR Test failed: {str(e)}")
        return None

if __name__ == "__main__":
    test_ocr()
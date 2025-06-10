"""
Invoice Data Models

This module defines SQLAlchemy models for invoice-related data:
- Invoice metadata (ID, date, amount, etc.)
- Vendor information
- Line items and details
- Processing status and history

Author: Dev 1
"""

# app/models/invoice.py

from sqlalchemy import Column, Integer, String, Float, Date
from app.db.base_class import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, nullable=False)
    invoice_date = Column(String)  # You can convert to Date later
    due_date = Column(String)
    gstin = Column(String)
    total = Column(String)
    currency = Column(String)

    vendor_name = Column(String)
    vendor_tax_id = Column(String)
    customer_name = Column(String)
    payment_terms = Column(String)

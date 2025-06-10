"""
Application Configuration

This module contains application-wide configuration settings:
- Environment variables and secrets
- Security settings and authentication
- Database configuration
- API settings and rate limits

Author: Shared
"""
from pydantic_settings import BaseSettings  # ✅ correct for Pydantic v2


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./invoices.db"  # or your Postgres URI
    # other settings like:
    # ENV: str = "development"
    # DEBUG: bool = True

settings = Settings()
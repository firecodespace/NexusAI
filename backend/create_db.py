# create_db.py

from app.db.session import engine
from app.models.invoice import Base

Base.metadata.create_all(bind=engine)

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings
import os

# Use echo=True in development, False in production
DB_ECHO = os.getenv("DB_ECHO", "False").lower() in ("true", "1", "yes")
engine = create_engine(settings.DATABASE_URL, echo=DB_ECHO)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import logging

# Database URL - will be set via environment variable for deployment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/election_db")

# Fix for Render PostgreSQL URL format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQL echo is opt-in (SQL_ECHO=1) - it floods the log with every query otherwise.
engine = create_engine(DATABASE_URL, echo=os.getenv("SQL_ECHO", "0") == "1")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("Database tables created successfully")
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
        raise e

# Drop all tables (for development)
def drop_tables():
    try:
        Base.metadata.drop_all(bind=engine)
        logging.info("Database tables dropped successfully")
    except Exception as e:
        logging.error(f"Error dropping tables: {e}")
        raise e

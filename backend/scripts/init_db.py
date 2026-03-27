"""
Initialize database tables
Run this script to create all database tables
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import init_db

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database tables created successfully!")

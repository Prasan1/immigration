"""
Database migration: Add one_time_purchases table

Run this script to add the one_time_purchases table to your database:
    python migration_add_one_time_purchases.py
"""

from app import app, db
from models import OneTimePurchase

def migrate():
    """Create one_time_purchases table"""
    with app.app_context():
        print("Creating one_time_purchases table...")

        # Create the table
        db.create_all()

        print("✓ Migration completed successfully!")
        print("The one_time_purchases table has been created.")

if __name__ == '__main__':
    migrate()

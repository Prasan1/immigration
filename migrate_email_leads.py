"""Migration script to create email_leads table"""
from app import app
from models import db, EmailLead

def migrate():
    """Create email_leads table"""
    with app.app_context():
        # Create the table
        db.create_all()
        print("✅ email_leads table created successfully!")

if __name__ == '__main__':
    migrate()

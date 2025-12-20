#!/usr/bin/env python3
"""
Migration script to add enterprise_settings table
Run this after updating models.py with EnterpriseSettings model
"""
from app import app
from models import db, EnterpriseSettings

with app.app_context():
    # Create the enterprise_settings table
    db.create_all()
    print("✓ Enterprise settings table created successfully!")
    print("\nEnterprise users can now configure:")
    print("  - Custom branding (logo & colors)")
    print("  - Site name")
    print("  - Footer text")
    print("  - Remove 'Powered by' text")

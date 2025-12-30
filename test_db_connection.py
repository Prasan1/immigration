#!/usr/bin/env python3
"""
Database Connection Diagnostic Tool
Run this locally and on DigitalOcean to see what's happening
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("DATABASE CONNECTION DIAGNOSTIC")
print("=" * 60)
print()

# Step 1: Check environment
print("1. ENVIRONMENT CHECK")
print("-" * 60)
database_url = os.getenv('DATABASE_URL')
print(f"DATABASE_URL: {database_url}")
print(f"Length: {len(database_url) if database_url else 0} characters")

if database_url:
    if database_url.startswith('sqlite'):
        print("⚠️  Using SQLite (local development)")
        db_type = "SQLite"
    elif database_url.startswith('postgres'):
        print("✓ Using PostgreSQL (production)")
        db_type = "PostgreSQL"
    else:
        print(f"⚠️  Unknown database type: {database_url[:20]}...")
        db_type = "Unknown"
else:
    print("❌ DATABASE_URL not set!")
    sys.exit(1)

print()

# Step 2: Try to connect
print("2. CONNECTION TEST")
print("-" * 60)

try:
    from app import app, db
    from models import User, ImmigrationForm
    from document_models import PassportApplication, FileCompressionJob

    print("✓ Imports successful")

    with app.app_context():
        # Test connection
        print("Testing database connection...")
        db.engine.connect()
        print("✓ Database connection successful")
        print()

        # Step 3: Query data
        print("3. DATA CHECK")
        print("-" * 60)

        # Count records
        user_count = User.query.count()
        form_count = ImmigrationForm.query.count()

        try:
            passport_count = PassportApplication.query.count()
        except Exception as e:
            passport_count = f"Error: {str(e)}"

        try:
            compressor_count = FileCompressionJob.query.count()
        except Exception as e:
            compressor_count = f"Error: {str(e)}"

        print(f"Users: {user_count}")
        print(f"Immigration Forms: {form_count}")
        print(f"Passport Applications: {passport_count}")
        print(f"File Compression Jobs: {compressor_count}")
        print()

        # Step 4: Sample data
        if user_count > 0:
            print("4. SAMPLE USER DATA")
            print("-" * 60)
            users = User.query.limit(3).all()
            for user in users:
                print(f"  - User ID: {user.id}, Clerk ID: {user.clerk_user_id}, Tier: {user.subscription_tier}")
        else:
            print("4. NO USERS FOUND")
            print("-" * 60)
            print("❌ Database has no users!")
            print("This means either:")
            print("  1. Data is in a different database")
            print("  2. Tables haven't been created")
            print("  3. Connection is to the wrong database")

        print()

        # Step 5: Table check
        print("5. TABLE CHECK")
        print("-" * 60)
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Found {len(tables)} tables:")
        for table in tables:
            print(f"  - {table}")

        print()
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Database Type: {db_type}")
        print(f"Database URL: {database_url[:50]}..." if len(database_url) > 50 else f"Database URL: {database_url}")
        print(f"Total Tables: {len(tables)}")
        print(f"Total Users: {user_count}")
        print(f"Total Forms: {form_count}")

        if user_count == 0:
            print()
            print("⚠️  WARNING: No data found!")
            print()
            print("NEXT STEPS:")
            print("1. Verify you're connecting to the correct database")
            print("2. Check if DATABASE_URL in DigitalOcean matches your production database")
            print("3. Run 'python init_db.py' to initialize the database")
        else:
            print()
            print("✓ Database connection working properly!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

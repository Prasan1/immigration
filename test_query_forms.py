#!/usr/bin/env python3
"""
Test if the app can actually QUERY the forms you manually inserted
Run this in DigitalOcean Console
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("FORM QUERY DIAGNOSTIC - Testing if app can read your inserted forms")
print("=" * 70)
print()

try:
    from app import app, db
    from models import ImmigrationForm

    with app.app_context():
        print("1. DIRECT DATABASE QUERY")
        print("-" * 70)

        # Test 1: Raw SQL query
        print("Running RAW SQL query...")
        result = db.session.execute(db.text("SELECT COUNT(*) FROM immigration_forms"))
        count = result.scalar()
        print(f"✓ Raw SQL: Found {count} forms in database")
        print()

        # Test 2: SQLAlchemy query (EXACT query the app uses)
        print("Running SQLAlchemy query (same as /api/documents endpoint)...")
        forms = ImmigrationForm.query.all()
        print(f"✓ SQLAlchemy: Found {len(forms)} forms")
        print()

        if count != len(forms):
            print(f"⚠️  MISMATCH! Database has {count} forms but SQLAlchemy found {len(forms)}")
            print("This indicates a schema or table name problem!")
            print()

        if len(forms) == 0:
            print("❌ PROBLEM: Database has forms but SQLAlchemy can't find them!")
            print()
            print("This usually means:")
            print("  1. Table schema doesn't match the model")
            print("  2. Primary key issue")
            print("  3. SQLAlchemy not seeing the right table")
            print()

            # Check table structure
            print("2. SCHEMA MISMATCH DIAGNOSTIC")
            print("-" * 70)
            result = db.session.execute(db.text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='immigration_forms' ORDER BY ordinal_position"))
            db_columns = result.fetchall()

            print("Columns in DATABASE:")
            db_col_dict = {}
            for col in db_columns:
                print(f"  - {col[0]}: {col[1]}")
                db_col_dict[col[0]] = col[1]
            print()

            # Show what model expects
            print("Columns the MODEL expects:")
            model_col_dict = {}
            for column in ImmigrationForm.__table__.columns:
                print(f"  - {column.name}: {column.type}")
                model_col_dict[column.name] = str(column.type)
            print()

            # Find differences
            print("DIFFERENCES:")
            missing_in_db = set(model_col_dict.keys()) - set(db_col_dict.keys())
            extra_in_db = set(db_col_dict.keys()) - set(model_col_dict.keys())

            if missing_in_db:
                print(f"  ❌ Missing in database: {', '.join(missing_in_db)}")
            if extra_in_db:
                print(f"  ⚠️  Extra in database: {', '.join(extra_in_db)}")
            if not missing_in_db and not extra_in_db:
                print(f"  ✓ All columns match!")
            print()

        else:
            print("✓ SQLAlchemy can read the forms!")
            print()
            print("2. FORM DETAILS")
            print("-" * 70)
            for idx, form in enumerate(forms, 1):
                print(f"\nForm {idx}:")
                print(f"  ID: {form.id}")
                print(f"  Title: {form.title}")
                print(f"  Category: {form.category}")
                print(f"  Access Level: {form.access_level}")
                print(f"  Filing Fee: {form.fee}")
            print()

        # Test 3: Test specific query that the app uses
        print("3. TESTING APP'S ACTUAL QUERIES")
        print("-" * 70)

        # This is what /api/documents uses
        try:
            all_forms_api = ImmigrationForm.query.all()
            print(f"✓ /api/documents query: {len(all_forms_api)} forms")
        except Exception as e:
            print(f"❌ /api/documents query failed: {e}")
            all_forms_api = []

        # Test ordering
        try:
            all_forms_ordered = ImmigrationForm.query.order_by(ImmigrationForm.category, ImmigrationForm.title).all()
            print(f"✓ Forms ordered by category: {len(all_forms_ordered)}")
        except Exception as e:
            print(f"⚠️  Ordering failed: {e}")

        # Test filtering
        try:
            featured_forms = ImmigrationForm.query.filter_by(access_level='free').limit(3).all()
            print(f"✓ Free forms (for homepage): {len(featured_forms)}")
        except Exception as e:
            print(f"⚠️  Filtering failed: {e}")
        print()

        # Test 4: Check if data is actually complete
        if forms:
            print("4. DATA COMPLETENESS CHECK")
            print("-" * 70)
            for form in forms:
                issues = []
                if not form.title:
                    issues.append("Missing title")
                if not form.category:
                    issues.append("Missing category")
                if not form.access_level:
                    issues.append("Missing access_level")

                if issues:
                    print(f"⚠️  Form {form.id}: {', '.join(issues)}")
                else:
                    print(f"✓ Form {form.id}: Complete")
            print()

        # Test 5: Test raw SQL select
        print("5. RAW SQL DATA SAMPLE")
        print("-" * 70)
        result = db.session.execute(db.text("SELECT id, title, category, access_level FROM immigration_forms LIMIT 3"))
        rows = result.fetchall()
        for row in rows:
            print(f"  ID={row[0]}, Title={row[1][:50]}, Category={row[2]}, Access={row[3]}")
        print()

        # Summary
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Database has: {count} forms (raw SQL)")
        print(f"SQLAlchemy found: {len(forms)} forms")

        if count > 0 and len(forms) == 0:
            print()
            print("❌ CRITICAL ISSUE: Schema mismatch!")
            print("Database has data but SQLAlchemy can't read it.")
            print()
            print("SOLUTION:")
            print("1. Drop the manually created table")
            print("2. Run: python init_db.py")
            print("3. This will create tables with correct schema")

        elif len(forms) > 0:
            print()
            print("✓ Everything looks good!")
            print()
            print("If forms still don't show on website, the issue is in:")
            print("  1. Frontend/templates not rendering data")
            print("  2. Routes not passing data to templates")
            print("  3. JavaScript filtering/hiding the forms")
            print("  4. User authentication blocking access")

        else:
            print()
            print("❌ Database is empty")
            print("Run: python init_db.py")

except Exception as e:
    print(f"❌ ERROR: {e}")
    print()
    import traceback
    traceback.print_exc()
    print()
    print("Common causes:")
    print("  1. App not connected to database")
    print("  2. Model definitions don't match table structure")
    print("  3. Database permissions issue")

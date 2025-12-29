#!/usr/bin/env python
"""
Create a test user and generate a login session for local development

Usage:
    python create_test_user.py

This script creates a test user in the database and shows you how to
manually create a session for testing.
"""

from app import create_app
from models import db, User
from datetime import datetime

def create_test_user():
    """Create a test user for local development"""
    app, limiter = create_app()

    with app.app_context():
        # Check if test user exists
        test_email = "test@example.com"
        user = User.query.filter_by(email=test_email).first()

        if user:
            print(f"\n✅ Test user already exists:")
            print(f"   Email: {user.email}")
            print(f"   Name: {user.full_name}")
            print(f"   Subscription: {user.subscription_tier}")
            print(f"   User ID: {user.id}")
        else:
            # Create new test user
            user = User(
                clerk_user_id="test_user_123",
                email=test_email,
                full_name="Test User",
                subscription_tier="basic",  # Give them Professional tier for testing
                subscription_status="active"
            )
            db.session.add(user)
            db.session.commit()

            print(f"\n✅ Created test user:")
            print(f"   Email: {user.email}")
            print(f"   Name: {user.full_name}")
            print(f"   Subscription: {user.subscription_tier}")
            print(f"   User ID: {user.id}")

        print("\n" + "="*60)
        print("🔐 To log in as this test user:")
        print("="*60)
        print("\n1. Open your browser's Developer Tools (F12)")
        print("2. Go to the Console tab")
        print("3. Run this command:\n")
        print(f"""
fetch('/api/auth/session', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{
        clerk_user_id: 'test_user_123',
        email: '{test_email}',
        full_name: 'Test User'
    }})
}}).then(r => r.json()).then(data => {{
    console.log('Logged in:', data);
    window.location.href = '/file-compressor';
}});
""")
        print("\n4. Press Enter - you'll be redirected to the file compressor")
        print("\n" + "="*60)
        print("\nOr visit: http://localhost:5000/dev-login")
        print("(If you add the dev-login route below)")
        print("="*60)

if __name__ == '__main__':
    create_test_user()

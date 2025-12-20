"""
Minimal Flask app for debugging deployment issues
This strips out all complex features to isolate the problem
"""
from flask import Flask
import os
import sys
import traceback

# Print Python version and environment
print(f"Python version: {sys.version}", flush=True)
print(f"Environment variables:", flush=True)
for key in ['FLASK_ENV', 'FLASK_SECRET_KEY', 'DATABASE_URL', 'PORT']:
    print(f"  {key}: {'SET' if os.getenv(key) else 'NOT SET'}", flush=True)

app = Flask(__name__)

# Test 1: Can Flask start at all?
print("✓ Flask app created", flush=True)

# Test 2: Can we load config?
try:
    from config import Config
    app.config.from_object(Config)
    print("✓ Config loaded", flush=True)
except Exception as e:
    print(f"✗ Config failed: {e}", flush=True)
    traceback.print_exc()

# Test 3: Can we initialize database?
try:
    from models import db
    db.init_app(app)
    print("✓ Database initialized", flush=True)
except Exception as e:
    print(f"✗ Database init failed: {e}", flush=True)
    traceback.print_exc()

# Test 4: Can we create tables?
try:
    with app.app_context():
        db.create_all()
    print("✓ Database tables created", flush=True)
except Exception as e:
    print(f"✗ Database table creation failed: {e}", flush=True)
    traceback.print_exc()

@app.route('/')
def index():
    return f"""
    <h1>Debug App Running!</h1>
    <p>Environment: {os.getenv('FLASK_ENV', 'not set')}</p>
    <p>Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'not set')[:50]}...</p>
    <p>If you see this, the app is working!</p>
    """

@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'App is running'}

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

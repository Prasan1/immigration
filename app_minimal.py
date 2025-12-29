"""Minimal Flask app to test deployment"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <head><title>Immigration App - Initializing</title></head>
    <body>
        <h1>Immigration App is Running!</h1>
        <p>The app started successfully.</p>
        <p><a href="/initialize-database">Click here to initialize the database</a></p>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'message': 'Minimal app running',
        'version': 'minimal-test-v2'
    })

@app.route('/initialize-database')
def initialize_db():
    """Initialize database tables"""
    try:
        # Import here to avoid startup crashes
        from config import Config
        from models import db, ImmigrationForm
        from document_models import PassportApplication, DocumentProcessingTransaction, FileCompressionJob
        from datetime import datetime

        # Configure app
        app.config.from_object(Config)
        db.init_app(app)

        with app.app_context():
            # Create all tables
            db.create_all()

            # Check if forms exist
            existing_forms = ImmigrationForm.query.count()
            if existing_forms > 0:
                return jsonify({
                    'success': True,
                    'message': f'Database already initialized with {existing_forms} forms'
                })

            # Add sample forms
            forms_data = [
                {
                    "title": "Form I-130 - Immediate Relative/Family Preference Petition",
                    "category": "Family-Based Immigration",
                    "description": "Petition filed by U.S. citizens and lawful permanent residents.",
                    "pdf_url": "https://www.uscis.gov/sites/default/files/document/forms/i-130.pdf",
                    "info_url": "https://www.uscis.gov/i-130",
                    "last_updated": "2024-01-15",
                    "processing_time": "12-33 months",
                    "fee": "$535",
                    "access_level": "free",
                    "checklist": ["Completed Form I-130", "Filing fee of $535"]
                }
            ]

            for form_data in forms_data:
                form = ImmigrationForm(
                    title=form_data['title'],
                    category=form_data['category'],
                    description=form_data['description'],
                    pdf_url=form_data['pdf_url'],
                    info_url=form_data['info_url'],
                    processing_time=form_data['processing_time'],
                    fee=form_data['fee'],
                    last_updated=datetime.strptime(form_data['last_updated'], '%Y-%m-%d').date(),
                    access_level=form_data.get('access_level', 'free')
                )
                form.set_checklist(form_data['checklist'])
                db.session.add(form)

            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Database initialized!',
                'next_step': 'Update Procfile to use app:app instead of app_minimal:app'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

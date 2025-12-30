"""Routes for document processing (checklists, cover letters, I-94 history)"""
from flask import jsonify, request, render_template, session, send_file
from functools import wraps
from datetime import datetime
from models import db, User, ImmigrationForm
from pdf_generator import ChecklistPDFGenerator, CoverLetterGenerator, I94HistoryGenerator
import os

def register_document_routes(app, limiter):
    """Register all document processing routes"""

    def get_current_user():
        """Get current user from session"""
        clerk_user_id = session.get('clerk_user_id')
        if clerk_user_id:
            return User.query.filter_by(clerk_user_id=clerk_user_id).first()
        return None

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'clerk_user_id' not in session:
                return jsonify({'error': 'Authentication required', 'redirect': '/login'}), 401
            return f(*args, **kwargs)
        return decorated_function

    def subscription_required(f):
        """Check if user has active subscription"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401

            if user.subscription_tier == 'free' or not user.has_active_subscription():
                return jsonify({
                    'error': 'Subscription required',
                    'message': 'Get Complete Package to access PDF features',
                    'required_tier': 'complete',
                    'current_tier': user.subscription_tier,
                    'redirect': '/pricing'
                }), 403

            return f(*args, **kwargs)
        return decorated_function

    # ============== CHECKLIST PDF ROUTES ==============

    @app.route('/api/forms/<int:form_id>/checklist-pdf', methods=['GET'])
    @login_required
    @subscription_required
    @limiter.limit("20 per minute")
    def download_checklist_pdf(form_id):
        """Download checklist PDF for a specific form"""
        user = get_current_user()
        form = ImmigrationForm.query.get_or_404(form_id)

        # Check if user can access this form
        if not user.can_access_form(form):
            return jsonify({'error': 'You do not have access to this form'}), 403

        try:
            # Create uploads directory
            uploads_dir = os.path.join(app.root_path, 'static', 'uploads', 'checklists')
            os.makedirs(uploads_dir, exist_ok=True)

            # Generate PDF
            generator = ChecklistPDFGenerator()
            checklist_items = form.get_checklist() or []
            pdf_elements = generator.generate(form.title, checklist_items, user.full_name)

            # Save PDF
            filename = f"checklist_{form.id}_{user.id}_{datetime.now().strftime('%Y%m%d')}.pdf"
            filepath = os.path.join(uploads_dir, filename)
            generator.save_to_file(pdf_elements, filepath)

            # Return file
            return send_file(filepath, as_attachment=True, download_name=f"{form.title.replace('/', '-')}_Checklist.pdf")

        except Exception as e:
            return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500

    # ============== COVER LETTER ROUTES ==============

    @app.route('/documents/cover-letter')
    @login_required
    @subscription_required
    def cover_letter_page():
        """Cover letter generator page"""
        user = get_current_user()
        return render_template('cover_letter_generator.html', user=user)

    @app.route('/api/documents/cover-letter/generate', methods=['POST'])
    @login_required
    @subscription_required
    @limiter.limit("10 per minute")
    def generate_cover_letter():
        """Generate USCIS cover letter PDF"""
        user = get_current_user()
        data = request.json

        try:
            # Create uploads directory
            uploads_dir = os.path.join(app.root_path, 'static', 'uploads', 'cover-letters')
            os.makedirs(uploads_dir, exist_ok=True)

            # Prepare user data
            user_data = {
                'full_name': data.get('full_name', user.full_name),
                'email': data.get('email', user.email),
                'phone': data.get('phone', ''),
                'case_number': data.get('case_number', '')
            }

            # Prepare form info
            form_info = {
                'title': data.get('form_title', 'Immigration Application'),
                'documents': data.get('documents', [])
            }

            # Generate PDF
            generator = CoverLetterGenerator()
            pdf_elements = generator.generate(user_data, form_info)

            # Save PDF
            filename = f"cover_letter_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(uploads_dir, filename)
            generator.save_to_file(pdf_elements, filepath)

            return jsonify({
                'success': True,
                'message': 'Cover letter generated successfully',
                'download_url': f"/static/uploads/cover-letters/{filename}"
            })

        except Exception as e:
            return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500

    # ============== I-94 HISTORY ROUTES ==============

    @app.route('/documents/i94-history')
    @login_required
    @subscription_required
    def i94_history_page():
        """I-94 travel history generator page"""
        user = get_current_user()
        return render_template('i94_history_generator.html', user=user)

    @app.route('/api/documents/i94-history/generate', methods=['POST'])
    @login_required
    @subscription_required
    @limiter.limit("10 per minute")
    def generate_i94_history():
        """Generate I-94 travel history PDF"""
        user = get_current_user()
        data = request.json

        try:
            # Create uploads directory
            uploads_dir = os.path.join(app.root_path, 'static', 'uploads', 'i94-history')
            os.makedirs(uploads_dir, exist_ok=True)

            # Prepare user data
            user_data = {
                'full_name': data.get('full_name', user.full_name),
                'date_of_birth': data.get('date_of_birth', ''),
                'passport_number': data.get('passport_number', ''),
                'country': data.get('country', '')
            }

            # Prepare travel history
            travel_history = data.get('travel_history', [])

            # Generate PDF
            generator = I94HistoryGenerator()
            pdf_elements = generator.generate(user_data, travel_history)

            # Save PDF
            filename = f"i94_history_{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(uploads_dir, filename)
            generator.save_to_file(pdf_elements, filepath)

            return jsonify({
                'success': True,
                'message': 'I-94 travel history generated successfully',
                'download_url': f"/static/uploads/i94-history/{filename}"
            })

        except Exception as e:
            return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500

    # ============== DASHBOARD - MY DOCUMENTS ==============

    @app.route('/api/documents/my-documents')
    @login_required
    def get_my_documents():
        """Get all generated documents for current user"""
        user = get_current_user()

        documents = []

        # Get passport applications
        from document_models import PassportApplication
        passports = PassportApplication.query.filter_by(user_id=user.id).all()
        for passport in passports:
            if passport.pdf_url:
                documents.append({
                    'type': 'passport',
                    'name': f'Passport Application - {passport.full_name}',
                    'url': passport.pdf_url,
                    'created_at': passport.created_at.isoformat(),
                    'status': passport.status
                })

        # Get cover letters, I-94 history, etc. from file system
        # (Can enhance this to track in database if needed)

        return jsonify(documents)

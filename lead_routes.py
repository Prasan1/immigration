"""Routes for lead generation and email capture"""
from flask import render_template, jsonify, request, send_file
from models import db, EmailLead
from datetime import datetime
import re
import os


def register_lead_routes(app, limiter):
    """Register lead generation routes"""

    @app.route('/free-i130-checklist')
    def free_i130_checklist():
        """Landing page for free I-130 checklist"""
        return render_template('free_i130_checklist.html')

    @app.route('/api/capture-email', methods=['POST'])
    @limiter.limit("5 per minute")
    def capture_email():
        """Capture email lead from landing pages"""
        try:
            data = request.get_json()

            # Validate email
            email = data.get('email', '').strip().lower()
            if not email or not is_valid_email(email):
                return jsonify({'error': 'Invalid email address'}), 400

            # Get source and UTM parameters
            source = data.get('source', 'unknown')
            utm_source = data.get('utm_source', '')
            utm_medium = data.get('utm_medium', '')
            utm_campaign = data.get('utm_campaign', '')

            # Check if email already exists
            existing_lead = EmailLead.query.filter_by(email=email).first()

            if existing_lead:
                # Update existing lead
                existing_lead.source = source
                existing_lead.utm_source = utm_source or existing_lead.utm_source
                existing_lead.utm_medium = utm_medium or existing_lead.utm_medium
                existing_lead.utm_campaign = utm_campaign or existing_lead.utm_campaign
                existing_lead.updated_at = datetime.utcnow()
            else:
                # Create new lead
                new_lead = EmailLead(
                    email=email,
                    source=source,
                    utm_source=utm_source,
                    utm_medium=utm_medium,
                    utm_campaign=utm_campaign
                )
                db.session.add(new_lead)

            db.session.commit()

            # TODO: Send welcome email with checklist PDF
            # send_welcome_email(email, source)

            return jsonify({
                'success': True,
                'message': 'Email captured successfully',
                'download_url': '/static/downloads/i130-checklist.pdf'
            }), 200

        except Exception as e:
            print(f"Error capturing email: {e}", flush=True)
            db.session.rollback()
            return jsonify({'error': 'Failed to capture email'}), 500

    @app.route('/api/leads/stats')
    def leads_stats():
        """Get lead statistics (admin only in production)"""
        try:
            total_leads = EmailLead.query.count()
            today_leads = EmailLead.query.filter(
                EmailLead.created_at >= datetime.utcnow().date()
            ).count()

            # Group by source
            sources = db.session.query(
                EmailLead.source,
                db.func.count(EmailLead.id)
            ).group_by(EmailLead.source).all()

            # Group by UTM source
            utm_sources = db.session.query(
                EmailLead.utm_source,
                db.func.count(EmailLead.id)
            ).filter(EmailLead.utm_source != '').group_by(EmailLead.utm_source).all()

            return jsonify({
                'total_leads': total_leads,
                'today_leads': today_leads,
                'by_source': {source: count for source, count in sources},
                'by_utm_source': {utm: count for utm, count in utm_sources}
            })

        except Exception as e:
            print(f"Error getting lead stats: {e}", flush=True)
            return jsonify({'error': 'Failed to get stats'}), 500


def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def send_welcome_email(email, source):
    """
    Send welcome email with free checklist
    TODO: Integrate with email service (SendGrid, Mailgun, etc.)
    """
    # This is a placeholder - you'll need to integrate with an email service
    # For now, users can download directly from the landing page
    pass

"""Routes for file compression feature"""
from flask import jsonify, request, render_template, session, send_file
from functools import wraps
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from document_models import FileCompressionJob
from models import db, User
from config import Config
import stripe
import os
from werkzeug.utils import secure_filename

def register_file_compressor_routes(app, limiter):
    """Register all file compressor routes"""

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

    def check_compression_limits(user):
        """Check if user can compress files (for free tier)"""
        if user.subscription_tier in ['basic', 'pro', 'enterprise']:
            # Paid tiers have unlimited premium compression
            return {
                'allowed': True,
                'tier': 'premium',
                'remaining': None,
                'limit': None
            }

        # Free tier - check monthly limit
        limits = Config.FILE_COMPRESSOR_LIMITS['free']
        monthly_limit = limits['monthly_limit']

        # Count compressions this month
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        compressions_this_month = FileCompressionJob.query.filter(
            FileCompressionJob.user_id == user.id,
            FileCompressionJob.created_at >= month_start,
            FileCompressionJob.compression_tier == 'free'
        ).count()

        remaining = monthly_limit - compressions_this_month

        return {
            'allowed': remaining > 0,
            'tier': 'free',
            'remaining': remaining,
            'limit': monthly_limit,
            'used': compressions_this_month
        }

    # ============== FILE COMPRESSOR ROUTES ==============

    @app.route('/file-compressor')
    def file_compressor_page():
        """File compressor page (accessible to all, but requires login to use)"""
        user = get_current_user()

        # Get usage info for free users
        usage_info = None
        if user:
            usage_info = check_compression_limits(user)

        return render_template('file_compressor.html', user=user, config=Config, usage_info=usage_info)

    @app.route('/api/file-compressor/usage', methods=['GET'])
    @login_required
    def get_compression_usage():
        """Get user's compression usage info"""
        user = get_current_user()
        usage_info = check_compression_limits(user)
        return jsonify(usage_info)

    @app.route('/api/file-compressor/jobs', methods=['GET'])
    @login_required
    @limiter.limit("20 per minute")
    def get_compression_jobs():
        """Get all compression jobs for the user"""
        user = get_current_user()

        jobs = FileCompressionJob.query.filter_by(user_id=user.id).order_by(
            FileCompressionJob.created_at.desc()
        ).limit(50).all()

        response = jsonify([job.to_dict() for job in jobs])
        # Prevent caching of sensitive user data
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    @app.route('/api/file-compressor/upload', methods=['POST'])
    @login_required
    @limiter.limit("10 per minute")
    def upload_and_compress():
        """Upload PDF and compress it (free tier or premium)"""
        user = get_current_user()

        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Check if PDF
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are supported'}), 400

        # Get compression tier from request (free or premium)
        requested_tier = request.form.get('tier', 'free')

        # Check limits
        usage_info = check_compression_limits(user)

        if requested_tier == 'free':
            if not usage_info['allowed'] and usage_info['tier'] == 'free':
                return jsonify({
                    'error': 'Monthly compression limit reached',
                    'limit': usage_info['limit'],
                    'used': usage_info['used'],
                    'message': 'Upgrade to Professional plan for unlimited compressions, or pay $5 for premium compression of this file',
                    'redirect': '/pricing'
                }), 403

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        # Determine which limits to use based on user's subscription tier
        # PDF compression is now bundled into subscriptions
        tier_limits = Config.FILE_COMPRESSOR_LIMITS.get(usage_info['tier'], Config.FILE_COMPRESSOR_LIMITS['free'])

        max_size_bytes = tier_limits['max_file_size_mb'] * 1024 * 1024

        if file_size > max_size_bytes:
            return jsonify({
                'error': f'File too large. Maximum size: {tier_limits["max_file_size_mb"]}MB',
                'max_size': tier_limits['max_file_size_mb']
            }), 400

        try:
            # Create upload directory
            upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'compressed-files')
            os.makedirs(upload_dir, exist_ok=True)

            # Save original file
            original_filename = secure_filename(file.filename)
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{user.id}_{timestamp}_{original_filename}"
            original_path = os.path.join(upload_dir, unique_filename)
            file.save(original_path)

            # Create compression job record
            job = FileCompressionJob(
                user_id=user.id,
                original_filename=original_filename,
                original_file_size=file_size,
                original_file_path=original_path,
                compression_tier=requested_tier,
                target_quality=tier_limits['compression_quality'],
                status='pending'
            )

            db.session.add(job)
            db.session.commit()

            return jsonify({
                'success': True,
                'job_id': job.id,
                'status': 'pending',
                'message': 'File uploaded. Compression will start shortly.',
                'tier': requested_tier
            })

        except Exception as e:
            return jsonify({'error': f'Upload failed: {str(e)}'}), 500

    @app.route('/api/file-compressor/jobs/<int:job_id>/compress', methods=['POST'])
    @login_required
    @limiter.limit("10 per minute")
    def compress_file(job_id):
        """Trigger compression for uploaded file"""
        user = get_current_user()
        job = FileCompressionJob.query.filter_by(id=job_id, user_id=user.id).first_or_404()

        if job.status != 'pending':
            return jsonify({'error': 'Job is not in pending state'}), 400

        try:
            # Import PDF compression utility
            from pdf_compressor import compress_pdf

            # Determine compression settings based on job's tier
            # Map to user's subscription tier for compression quality
            tier_limits = Config.FILE_COMPRESSOR_LIMITS.get(
                job.compression_tier,
                Config.FILE_COMPRESSOR_LIMITS['free']
            )

            job.status = 'processing'
            db.session.commit()

            # Generate compressed filename
            compressed_filename = f"compressed_{job.id}_{job.original_filename}"
            upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'compressed-files')
            compressed_path = os.path.join(upload_dir, compressed_filename)

            # Compress the PDF
            compressed_size = compress_pdf(
                job.original_file_path,
                compressed_path,
                target_ratio=tier_limits['target_compression_ratio'],
                quality=tier_limits['compression_quality']
            )

            # Calculate compression ratio
            compression_ratio = compressed_size / job.original_file_size if job.original_file_size > 0 else 0

            # Update job
            job.mark_completed(compressed_size, compression_ratio)
            job.compressed_file_path = compressed_path
            db.session.commit()

            return jsonify({
                'success': True,
                'job': job.to_dict()
            })

        except Exception as e:
            job.status = 'failed'
            db.session.commit()
            return jsonify({'error': f'Compression failed: {str(e)}'}), 500

    # NOTE: Premium compression checkout removed - now bundled into subscriptions
    # Free users get 5/month basic compression, paid users get unlimited premium compression
    # No separate $5 payment option anymore

    @app.route('/api/file-compressor/jobs/<int:job_id>/checkout', methods=['POST'])
    @login_required
    @limiter.limit("5 per minute")
    def create_compression_checkout(job_id):
        """DEPRECATED: Premium compression is now bundled into subscriptions"""
        return jsonify({
            'error': 'Premium compression is now included in Professional, Team, and Business subscriptions',
            'message': 'Upgrade your subscription to get unlimited premium compression',
            'redirect': '/pricing'
        }), 400

        # LEGACY CODE - Removed separate $5 premium compression payment
        """
        user = get_current_user()
        job = FileCompressionJob.query.filter_by(id=job_id, user_id=user.id).first_or_404()

        # Check if already paid
        if job.payment_status == 'paid':
            return jsonify({'error': 'Compression already paid'}), 400

        try:
            # Get compression price
            compressor_config = Config.DOCUMENT_TYPES.get('file_compressor_premium')

            if not compressor_config or not compressor_config.get('price_id'):
                return jsonify({'error': 'Premium compression price not configured'}), 500

            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=int(compressor_config['price'] * 100),  # Convert to cents
                currency='usd',
                customer=user.stripe_customer_id if user.stripe_customer_id else None,
                metadata={
                    'user_id': user.id,
                    'job_id': job.id,
                    'document_type': 'file_compressor',
                    'filename': job.original_filename
                },
                description=f'Premium File Compression - {job.original_filename}'
            )

            # Update job
            job.stripe_payment_intent_id = payment_intent.id
            job.compression_tier = 'premium'
            db.session.commit()

            return jsonify({
                'client_secret': payment_intent.client_secret,
                'amount': compressor_config['price']
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/file-compressor/jobs/<int:job_id>/confirm-payment', methods=['POST'])
    @login_required
    def confirm_compression_payment(job_id):
        """DEPRECATED: Premium compression is now bundled into subscriptions"""
        return jsonify({
            'error': 'Premium compression is now included in Professional, Team, and Business subscriptions',
            'message': 'Upgrade your subscription to get unlimited premium compression',
            'redirect': '/pricing'
        }), 400

        # LEGACY CODE - Payment confirmation no longer needed
        """
        user = get_current_user()
        job = FileCompressionJob.query.filter_by(id=job_id, user_id=user.id).first_or_404()

        data = request.json
        payment_intent_id = data.get('payment_intent_id')

        if not payment_intent_id:
            return jsonify({'error': 'Payment intent ID required'}), 400

        try:
            # Verify payment with Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            if payment_intent.status == 'succeeded':
                # Mark job as paid
                job.mark_paid(payment_intent_id)
                db.session.commit()

                return jsonify({
                    'success': True,
                    'message': 'Payment confirmed. Your file will be compressed with premium quality.',
                    'job': job.to_dict()
                })
            else:
                return jsonify({'error': 'Payment not successful'}), 400

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        """

    @app.route('/api/file-compressor/jobs/<int:job_id>/download', methods=['GET'])
    @login_required
    @limiter.limit("30 per minute")
    def download_compressed_file(job_id):
        """Download compressed PDF file"""
        user = get_current_user()
        job = FileCompressionJob.query.filter_by(id=job_id, user_id=user.id).first_or_404()

        if job.status != 'completed':
            return jsonify({'error': 'Compression not completed yet'}), 400

        if not job.compressed_file_path or not os.path.exists(job.compressed_file_path):
            return jsonify({'error': 'Compressed file not found'}), 404

        try:
            download_name = f"compressed_{job.original_filename}"
            return send_file(
                job.compressed_file_path,
                as_attachment=True,
                download_name=download_name,
                mimetype='application/pdf'
            )
        except Exception as e:
            return jsonify({'error': f'Download failed: {str(e)}'}), 500

    @app.route('/api/file-compressor/jobs/<int:job_id>', methods=['DELETE'])
    @login_required
    def delete_compression_job(job_id):
        """Delete a compression job and its files"""
        user = get_current_user()
        job = FileCompressionJob.query.filter_by(id=job_id, user_id=user.id).first_or_404()

        try:
            # Delete files from disk
            if job.original_file_path and os.path.exists(job.original_file_path):
                os.remove(job.original_file_path)

            if job.compressed_file_path and os.path.exists(job.compressed_file_path):
                os.remove(job.compressed_file_path)

            # Delete database record
            db.session.delete(job)
            db.session.commit()

            return jsonify({'success': True})

        except Exception as e:
            return jsonify({'error': f'Delete failed: {str(e)}'}), 500

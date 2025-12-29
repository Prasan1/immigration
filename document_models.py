from models import db
from datetime import datetime
import json

class PassportApplication(db.Model):
    """Model for passport application processing"""
    __tablename__ = 'passport_applications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Application Status
    status = db.Column(db.String(50), default='draft')  # draft, pending_payment, paid, processing, completed
    payment_status = db.Column(db.String(50), default='unpaid')  # unpaid, paid, refunded
    stripe_payment_intent_id = db.Column(db.String(255))

    # Personal Information
    full_name = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    place_of_birth = db.Column(db.String(255))
    ssn = db.Column(db.String(20))
    gender = db.Column(db.String(20))

    # Physical Characteristics
    height = db.Column(db.String(20))
    hair_color = db.Column(db.String(50))
    eye_color = db.Column(db.String(50))

    # Contact Information
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))

    # Address
    mailing_address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(20))

    # Emergency Contact
    emergency_contact_name = db.Column(db.String(255))
    emergency_contact_phone = db.Column(db.String(50))
    emergency_contact_relationship = db.Column(db.String(100))

    # Employment
    occupation = db.Column(db.String(255))
    employer = db.Column(db.String(255))

    # Travel Plans
    travel_date = db.Column(db.Date)
    destination = db.Column(db.String(255))

    # Parent Information
    parent1_name = db.Column(db.String(255))
    parent1_birthplace = db.Column(db.String(255))
    parent1_dob = db.Column(db.Date)

    parent2_name = db.Column(db.String(255))
    parent2_birthplace = db.Column(db.String(255))
    parent2_dob = db.Column(db.Date)

    # Additional Data (JSON for flexibility)
    additional_data = db.Column(db.Text)  # JSON field for extra information

    # Generated Files
    pdf_url = db.Column(db.String(500))  # URL to generated PDF
    checklist_url = db.Column(db.String(500))  # URL to checklist PDF

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', backref='passport_applications')

    def __repr__(self):
        return f'<PassportApplication {self.full_name} - {self.status}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'payment_status': self.payment_status,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'place_of_birth': self.place_of_birth,
            'gender': self.gender,
            'email': self.email,
            'phone': self.phone,
            'mailing_address': self.mailing_address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'height': self.height,
            'hair_color': self.hair_color,
            'eye_color': self.eye_color,
            'occupation': self.occupation,
            'employer': self.employer,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'travel_date': self.travel_date.isoformat() if self.travel_date else None,
            'destination': self.destination,
            'pdf_url': self.pdf_url,
            'checklist_url': self.checklist_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
        }

    def set_additional_data(self, data):
        """Set additional data as JSON"""
        self.additional_data = json.dumps(data)

    def get_additional_data(self):
        """Get additional data from JSON"""
        if self.additional_data:
            return json.loads(self.additional_data)
        return {}

    def is_complete(self):
        """Check if all required fields are filled"""
        required_fields = [
            self.full_name, self.date_of_birth, self.email,
            self.mailing_address, self.city, self.state, self.zip_code
        ]
        return all(required_fields)

    def mark_paid(self, payment_intent_id):
        """Mark application as paid"""
        self.payment_status = 'paid'
        self.stripe_payment_intent_id = payment_intent_id
        self.status = 'paid'
        self.submitted_at = datetime.utcnow()


class DocumentProcessingTransaction(db.Model):
    """Track all document processing transactions"""
    __tablename__ = 'document_processing_transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Transaction Details
    document_type = db.Column(db.String(50), nullable=False)  # passport, visa, etc.
    document_id = db.Column(db.Integer)  # ID of the specific document (e.g., passport_application.id)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')

    # Payment Info
    stripe_payment_intent_id = db.Column(db.String(255), unique=True)
    stripe_charge_id = db.Column(db.String(255))
    payment_status = db.Column(db.String(50), default='pending')  # pending, succeeded, failed, refunded

    # Metadata
    description = db.Column(db.String(500))
    extra_metadata = db.Column(db.Text)  # JSON for additional info

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', backref='document_transactions')

    def __repr__(self):
        return f'<DocumentTransaction {self.document_type} - ${self.amount} - {self.payment_status}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'document_type': self.document_type,
            'document_id': self.document_id,
            'amount': self.amount,
            'currency': self.currency,
            'payment_status': self.payment_status,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
        }


class FileCompressionJob(db.Model):
    """Model for tracking file compression jobs"""
    __tablename__ = 'file_compression_jobs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Job Status
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    compression_tier = db.Column(db.String(20), default='free')  # free or premium
    payment_status = db.Column(db.String(50), default='unpaid')  # unpaid, paid (for premium)
    stripe_payment_intent_id = db.Column(db.String(255))

    # File Information
    original_filename = db.Column(db.String(500), nullable=False)
    original_file_size = db.Column(db.Integer)  # Size in bytes
    compressed_file_size = db.Column(db.Integer)  # Size in bytes after compression
    compression_ratio = db.Column(db.Float)  # Percentage of original size

    # File Storage Paths
    original_file_path = db.Column(db.String(500))
    compressed_file_path = db.Column(db.String(500))

    # Compression Settings
    target_quality = db.Column(db.String(20))  # 'basic' or 'premium'

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', backref='compression_jobs')

    def __repr__(self):
        return f'<FileCompressionJob {self.original_filename} - {self.status}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'compression_tier': self.compression_tier,
            'payment_status': self.payment_status,
            'original_filename': self.original_filename,
            'original_file_size': self.original_file_size,
            'compressed_file_size': self.compressed_file_size,
            'compression_ratio': self.compression_ratio,
            'target_quality': self.target_quality,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }

    def mark_paid(self, payment_intent_id):
        """Mark compression job as paid"""
        self.payment_status = 'paid'
        self.stripe_payment_intent_id = payment_intent_id
        self.compression_tier = 'premium'

    def mark_completed(self, compressed_size, compression_ratio):
        """Mark compression job as completed"""
        self.status = 'completed'
        self.compressed_file_size = compressed_size
        self.compression_ratio = compression_ratio
        self.completed_at = datetime.utcnow()

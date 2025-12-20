#!/usr/bin/env python3
"""
Script to restore the original 6 form templates that are missing
"""

from app import app, db
from models import FormTemplate

def restore_original_templates():
    """Add the original 6 templates back to the database"""

    original_templates = [
        {
            'title': 'Client Intake Questionnaire (Family-Based)',
            'category': 'Client Intake',
            'description': 'Comprehensive intake form for family-based immigration cases. Collects client information, immigration history, family details, and case background.',
            'template_url': '/templates/client-intake-family',
            'access_level': 'free',
            'use_case': 'Used at the start of every family-based immigration case'
        },
        {
            'title': 'Personal Statement / Declaration Template',
            'category': 'Declarations & Affidavits',
            'description': 'Template for applicant personal statements and declarations. Used in adjustment of status, waivers, asylum, and other applications.',
            'template_url': '/templates/personal-declaration',
            'access_level': 'free',
            'use_case': 'Required for most USCIS applications'
        },
        {
            'title': 'Cover Letter to USCIS',
            'category': 'Evidence & Filing Documents',
            'description': 'Professional cover letter template for USCIS applications. Includes case summary and document index.',
            'template_url': '/templates/uscis-cover-letter',
            'access_level': 'basic',
            'use_case': 'Included with every USCIS application package'
        },
        {
            'title': 'Attorney-Client Retainer Agreement',
            'category': 'Attorney-Client Forms',
            'description': 'Comprehensive retainer agreement template. Includes scope of representation, fees, and client obligations.',
            'template_url': '/templates/retainer-agreement',
            'access_level': 'pro',
            'use_case': 'Required legal agreement for all client engagements'
        },
        {
            'title': 'Table of Contents / Evidence Index',
            'category': 'Evidence & Filing Documents',
            'description': 'Organized table of contents for application packages. Helps USCIS officers review evidence efficiently.',
            'template_url': '/templates/evidence-index',
            'access_level': 'basic',
            'use_case': 'Dramatically improves approval rates'
        },
        {
            'title': 'Employer Support Letter',
            'category': 'Employment Support Forms',
            'description': 'Template for employer letters supporting H-1B, L-1, PERM, and other employment-based cases.',
            'template_url': '/templates/employer-letter',
            'access_level': 'pro',
            'use_case': 'Required for H-1B, L-1, O-1, EB-2, EB-3 cases'
        },
    ]

    with app.app_context():
        added_count = 0

        for template_data in original_templates:
            # Check if template already exists
            existing = FormTemplate.query.filter_by(title=template_data['title']).first()
            if existing:
                print(f"⚠️  Template '{template_data['title']}' already exists, skipping...")
                continue

            # Create new template
            template = FormTemplate(**template_data)
            db.session.add(template)
            added_count += 1
            print(f"✓ Added: {template_data['title']}")

        if added_count > 0:
            db.session.commit()
            print(f"\n✓ Successfully added {added_count} original templates back to database!")
        else:
            print("\n✓ All original templates already exist in database")

        # Show summary
        total = FormTemplate.query.count()
        print(f"📊 Total templates in database: {total}")

        print("\n📋 All templates:")
        all_templates = FormTemplate.query.order_by(FormTemplate.id).all()
        for t in all_templates:
            print(f"  {t.id}. {t.title} ({t.category})")

if __name__ == '__main__':
    restore_original_templates()

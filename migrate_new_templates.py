#!/usr/bin/env python3
"""
Migration script to add 7 new high-priority form templates to database
"""

from app import app, db
from models import FormTemplate

def add_new_templates():
    """Add new form templates to database"""

    new_templates = [
        {
            'title': 'Marriage Bona Fide Declaration',
            'category': 'Declarations & Affidavits',
            'description': 'Declaration proving the genuineness of marriage for family-based immigration applications',
            'template_url': '/templates/marriage-bona-fide',
            'access_level': 'basic',
            'use_case': 'I-130, I-485, I-751, consular processing - proving marriage is genuine and not for immigration fraud'
        },
        {
            'title': 'Extreme Hardship Declaration (I-601/I-601A)',
            'category': 'Waiver & Humanitarian',
            'description': 'Declaration of extreme hardship to qualifying U.S. citizen or LPR relative for waiver applications',
            'template_url': '/templates/hardship-declaration',
            'access_level': 'pro',
            'use_case': 'I-601 and I-601A waiver applications - proving extreme hardship for unlawful presence or other inadmissibility grounds'
        },
        {
            'title': 'RFE Response Cover Letter',
            'category': 'Evidence & Filing',
            'description': 'Professional cover letter template for responding to USCIS Requests for Evidence (RFE)',
            'template_url': '/templates/rfe-response',
            'access_level': 'pro',
            'use_case': 'Responding to RFEs for any USCIS petition - organizes evidence and addresses each requested item'
        },
        {
            'title': 'Job Offer Letter',
            'category': 'Employment & Business',
            'description': 'Formal job offer letter template for employment-based immigration cases',
            'template_url': '/templates/job-offer-letter',
            'access_level': 'basic',
            'use_case': 'H-1B, L-1, E-3, TN, PERM, EB cases - detailed offer with salary, duties, requirements, and immigration sponsorship commitment'
        },
        {
            'title': 'Spouse Affidavit',
            'category': 'Declarations & Affidavits',
            'description': 'Affidavit from U.S. citizen or LPR spouse supporting immigration application',
            'template_url': '/templates/spouse-affidavit',
            'access_level': 'basic',
            'use_case': 'I-130, I-485, I-751, waivers - spouse declares marriage is genuine and commits to financial support'
        },
        {
            'title': 'Extreme Hardship Analysis Worksheet',
            'category': 'Waiver & Humanitarian',
            'description': 'Attorney tool to systematically analyze and document hardship factors for waiver applications',
            'template_url': '/templates/hardship-worksheet',
            'access_level': 'pro',
            'use_case': 'Case preparation for I-601/I-601A - evaluates medical, financial, educational, psychological, and country condition factors'
        },
        {
            'title': 'Immigration History Worksheet',
            'category': 'Client Intake',
            'description': 'Comprehensive worksheet to document complete immigration history and identify potential issues',
            'template_url': '/templates/immigration-history',
            'access_level': 'basic',
            'use_case': 'Initial client intake - captures all entries, exits, status changes, violations, and applications for any case type'
        }
    ]

    with app.app_context():
        # Check if templates already exist
        for template_data in new_templates:
            existing = FormTemplate.query.filter_by(title=template_data['title']).first()
            if existing:
                print(f"⚠️  Template '{template_data['title']}' already exists, skipping...")
                continue

            # Create new template
            template = FormTemplate(**template_data)
            db.session.add(template)
            print(f"✓ Added: {template_data['title']}")

        db.session.commit()
        print(f"\n✓ Successfully added new form templates to database!")

        # Show summary
        total = FormTemplate.query.count()
        print(f"📊 Total templates in database: {total}")

if __name__ == '__main__':
    add_new_templates()

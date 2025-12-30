#!/usr/bin/env python3
"""
Quick script to populate form templates in production
Run this in DigitalOcean Console
"""
from app import app
from models import db, FormTemplate

with app.app_context():
    # Create table if it doesn't exist
    db.create_all()

    # Check if templates already exist
    existing_count = FormTemplate.query.count()
    if existing_count > 0:
        print(f"✓ Form templates table already has {existing_count} templates!")
        print("\nExisting templates:")
        templates = FormTemplate.query.all()
        for t in templates:
            print(f"  - {t.title} ({t.access_level})")
    else:
        print("Adding form templates...")

        # Add initial form templates
        templates = [
            FormTemplate(
                title="Client Intake Questionnaire (Family-Based)",
                category="Client Intake",
                description="Comprehensive intake form for family-based immigration cases. Collects client information, immigration history, family details, and case background.",
                template_url="/templates/client-intake-family",
                access_level="free",
                use_case="Used at the start of every family-based immigration case"
            ),
            FormTemplate(
                title="Personal Statement / Declaration Template",
                category="Declarations & Affidavits",
                description="Template for applicant personal statements and declarations. Used in adjustment of status, waivers, asylum, and other applications.",
                template_url="/templates/personal-declaration",
                access_level="free",
                use_case="Required for most USCIS applications"
            ),
            FormTemplate(
                title="Cover Letter to USCIS",
                category="Evidence & Filing Documents",
                description="Professional cover letter template for USCIS applications. Includes case summary and document index.",
                template_url="/templates/uscis-cover-letter",
                access_level="basic",
                use_case="Included with every USCIS application package"
            ),
            FormTemplate(
                title="Attorney-Client Retainer Agreement",
                category="Attorney-Client Forms",
                description="Comprehensive retainer agreement template. Includes scope of representation, fees, and client obligations.",
                template_url="/templates/retainer-agreement",
                access_level="pro",
                use_case="Required legal agreement for all client engagements"
            ),
            FormTemplate(
                title="Table of Contents / Evidence Index",
                category="Evidence & Filing Documents",
                description="Organized table of contents for application packages. Helps USCIS officers review evidence efficiently.",
                template_url="/templates/evidence-index",
                access_level="basic",
                use_case="Dramatically improves approval rates"
            ),
            FormTemplate(
                title="Employer Support Letter",
                category="Employment Support Forms",
                description="Template for employer letters supporting H-1B, L-1, PERM, and other employment-based cases.",
                template_url="/templates/employer-letter",
                access_level="pro",
                use_case="Required for H-1B, L-1, O-1, EB-2, EB-3 cases"
            ),
            FormTemplate(
                title="Client Intake Questionnaire (Employment-Based)",
                category="Client Intake",
                description="Specialized intake form for employment-based immigration cases. Captures job details, education, work history.",
                template_url="/templates/client-intake-employment",
                access_level="pro",
                use_case="Used for H-1B, L-1, EB-2, EB-3 cases"
            ),
            FormTemplate(
                title="Request for Evidence (RFE) Response Template",
                category="Evidence & Filing Documents",
                description="Template for responding to USCIS Requests for Evidence. Helps organize comprehensive responses.",
                template_url="/templates/rfe-response",
                access_level="basic",
                use_case="Required when USCIS issues an RFE"
            ),
            FormTemplate(
                title="Affidavit of Support Guide (I-864)",
                category="Declarations & Affidavits",
                description="Step-by-step guide for completing Form I-864 Affidavit of Support with checklists.",
                template_url="/templates/affidavit-support",
                access_level="free",
                use_case="Required for all family-based green card applications"
            ),
            FormTemplate(
                title="Bona Fide Marriage Evidence Checklist",
                category="Evidence & Filing Documents",
                description="Comprehensive checklist for gathering evidence of bona fide marriage for I-130/I-485 applications.",
                template_url="/templates/marriage-evidence",
                access_level="basic",
                use_case="Critical for marriage-based green card cases"
            ),
        ]

        for template in templates:
            db.session.add(template)

        db.session.commit()
        print(f"✓ Successfully added {len(templates)} form templates!")

        print("\nTemplates by access level:")
        free_count = FormTemplate.query.filter_by(access_level='free').count()
        basic_count = FormTemplate.query.filter_by(access_level='basic').count()
        pro_count = FormTemplate.query.filter_by(access_level='pro').count()

        print(f"  Free tier: {free_count} templates")
        print(f"  Professional: {basic_count} templates")
        print(f"  Team/Business: {pro_count} templates")

print("\n✓ Form templates ready!")

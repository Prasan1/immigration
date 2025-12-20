#!/usr/bin/env python3
"""
Migration script to add form_templates table and populate initial templates
"""
from app import app
from models import db, FormTemplate

with app.app_context():
    # Create the form_templates table
    db.create_all()
    print("✓ Form templates table created successfully!")

    # Check if templates already exist
    if FormTemplate.query.count() > 0:
        print("Templates already exist. Skipping population.")
    else:
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
        ]

        for template in templates:
            db.session.add(template)

        db.session.commit()
        print(f"\n✓ Added {len(templates)} form templates to database")

    print("\nAvailable template categories:")
    print("  - Client Intake")
    print("  - Declarations & Affidavits")
    print("  - Evidence & Filing Documents")
    print("  - Attorney-Client Forms")
    print("  - Employment Support Forms")

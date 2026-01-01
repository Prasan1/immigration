"""Add missing templates to database"""
from app import app, db
from models import FormTemplate

def add_missing_templates():
    """Add the 3 missing templates to the database"""
    with app.app_context():
        # Check if templates already exist
        existing_urls = [t.template_url for t in FormTemplate.query.all()]

        templates_to_add = []

        # 1. Affidavit of Support Guide (I-864) - FREE
        if '/templates/affidavit-support' not in existing_urls:
            templates_to_add.append(FormTemplate(
                title='Affidavit of Support Guide (I-864)',
                description='Step-by-step guide and checklist for completing Form I-864 Affidavit of Support',
                category='Evidence & Filing Documents',
                access_level='free',
                template_url='/templates/affidavit-support',
                use_case='Required for all family-based green card applications - ensures sponsor meets income requirements and commits to financial support'
            ))

        # 2. Client Intake Questionnaire (Employment-Based) - Agency Plan
        if '/templates/client-intake-employment' not in existing_urls:
            templates_to_add.append(FormTemplate(
                title='Client Intake Questionnaire (Employment-Based)',
                description='Comprehensive intake form for employment-based immigration cases. Collects work history, education, employer details, and case background.',
                category='Client Intake',
                access_level='pro',
                template_url='/templates/client-intake-employment',
                use_case='Initial client intake for H-1B, L-1, PERM, EB-1/2/3, O-1, and other employment-based immigration cases'
            ))

        # 3. Bona Fide Marriage Evidence Checklist - BASIC tier
        if '/templates/marriage-evidence' not in existing_urls:
            templates_to_add.append(FormTemplate(
                title='Bona Fide Marriage Evidence Checklist',
                description='Organized checklist to track and prepare evidence proving marriage is genuine and not for immigration fraud',
                category='Evidence & Filing Documents',
                access_level='basic',
                template_url='/templates/marriage-evidence',
                use_case='I-130, I-485, I-751, K-1 - organize joint documents, photos, financial records, and affidavits to prove genuine marriage'
            ))

        if templates_to_add:
            print(f"Adding {len(templates_to_add)} missing templates:")
            for template in templates_to_add:
                print(f"  - {template.title} ({template.access_level})")
                db.session.add(template)

            db.session.commit()
            print("\n✓ Templates added successfully!")
        else:
            print("✓ All templates already exist in database")

        # Show all templates
        all_templates = FormTemplate.query.order_by(FormTemplate.id).all()
        print(f"\nTotal templates in database: {len(all_templates)}")
        for t in all_templates:
            print(f"  {t.id:2d}. {t.title} ({t.access_level})")

if __name__ == '__main__':
    add_missing_templates()

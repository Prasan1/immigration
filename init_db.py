from app import create_app
from models import db, ImmigrationForm
from document_models import PassportApplication, DocumentProcessingTransaction, FileCompressionJob
from datetime import datetime

def init_database():
    """Initialize database and migrate existing forms data"""
    app, limiter = create_app()

    with app.app_context():
        # Drop all tables and recreate (for development)
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")

        # Check if forms already exist
        existing_forms = ImmigrationForm.query.count()
        if existing_forms > 0:
            print(f"Database already has {existing_forms} forms. Skipping migration.")
            return

        print("Migrating existing forms data...")

        # Original forms data from app.py
        forms_data = [
            {
                "title": "Form I-130 - Immediate Relative/Family Preference Petition",
                "category": "Family-Based Immigration",
                "description": "Petition filed by U.S. citizens and lawful permanent residents to establish qualifying family relationship for relatives seeking to immigrate to or adjust status in the United States.",
                "pdf_url": "https://www.uscis.gov/sites/default/files/document/forms/i-130.pdf",
                "info_url": "https://www.uscis.gov/i-130",
                "last_updated": "2024-01-15",
                "processing_time": "12-33 months",
                "fee": "$535",
                "access_level": "free",  # First 3 forms are free
                "checklist": [
                    "Completed Form I-130",
                    "Filing fee of $535",
                    "Proof of U.S. citizenship or permanent residence",
                    "Proof of relationship to beneficiary",
                    "Passport-style photos of petitioner and beneficiary",
                    "Birth certificates",
                    "Marriage certificate (if applicable)",
                    "Divorce decree (if previously married)"
                ]
            },
            {
                "title": "Form I-485 - Application to Adjust Status to Permanent Resident",
                "category": "Adjustment of Status",
                "description": "Used to apply for adjustment of status to become a lawful permanent resident of the United States.",
                "pdf_url": "https://www.uscis.gov/sites/default/files/document/forms/i-485.pdf",
                "info_url": "https://www.uscis.gov/i-485",
                "last_updated": "2024-02-01",
                "processing_time": "13-25 months",
                "fee": "$1,225",
                "access_level": "free",
                "checklist": [
                    "Completed Form I-485",
                    "Filing fee of $1,225",
                    "Form I-693 Medical Examination",
                    "Two passport-style photographs",
                    "Copy of birth certificate",
                    "Copy of passport and I-94",
                    "Form I-864 Affidavit of Support",
                    "Tax returns for past 3 years",
                    "Employment authorization (if applicable)"
                ]
            },
            {
                "title": "Form N-400 - Naturalization Application for U.S. Citizenship",
                "category": "Naturalization",
                "description": "Used to apply for U.S. citizenship through naturalization.",
                "pdf_url": "https://www.uscis.gov/sites/default/files/document/forms/n-400.pdf",
                "info_url": "https://www.uscis.gov/n-400",
                "last_updated": "2024-01-20",
                "processing_time": "14-22 months",
                "fee": "$725",
                "access_level": "free",
                "checklist": [
                    "Completed Form N-400",
                    "Filing fee of $725",
                    "Copy of Permanent Resident Card",
                    "Copy of marriage certificate (if applicable)",
                    "Divorce decree (if previously married)",
                    "Tax returns for past 5 years",
                    "Travel history records",
                    "Two passport-style photographs"
                ]
            },
            {
                "title": "Form I-765 - Employment Authorization Document Application",
                "category": "Work Authorization",
                "description": "Used to request an Employment Authorization Document (EAD) to work in the United States.",
                "pdf_url": "https://www.uscis.gov/sites/default/files/document/forms/i-765.pdf",
                "info_url": "https://www.uscis.gov/i-765",
                "last_updated": "2024-01-10",
                "processing_time": "3-6 months",
                "fee": "$410",
                "access_level": "basic",  # Form 4 of 7 in Basic tier
                "checklist": [
                    "Completed Form I-765",
                    "Filing fee of $410",
                    "Copy of I-94 arrival/departure record",
                    "Copy of passport biographical page",
                    "Two passport-style photographs",
                    "Supporting documentation for eligibility category",
                    "Copy of pending I-485 (if applicable)"
                ]
            },
            {
                "title": "Form I-129 - Petition for Nonimmigrant Professional Worker",
                "category": "Temporary Workers",
                "description": "Used by employers to petition for nonimmigrant workers in specialty occupations, temporary workers, and other categories.",
                "pdf_url": "https://www.uscis.gov/sites/default/files/document/forms/i-129.pdf",
                "info_url": "https://www.uscis.gov/i-129",
                "last_updated": "2024-01-25",
                "processing_time": "3-6 months",
                "fee": "$460",
                "access_level": "basic",
                "checklist": [
                    "Completed Form I-129",
                    "Filing fee of $460",
                    "Labor Condition Application (if H-1B)",
                    "Job offer letter",
                    "Educational credentials evaluation",
                    "Resume of beneficiary",
                    "Company financial documents",
                    "Employer letter explaining need for worker"
                ]
            },
            {
                "title": "Form I-539 - Extension/Change of Nonimmigrant Status Application",
                "category": "Status Changes",
                "description": "Used to apply for an extension of stay or change of nonimmigrant status while in the United States.",
                "pdf_url": "https://www.uscis.gov/sites/default/files/document/forms/i-539.pdf",
                "info_url": "https://www.uscis.gov/i-539",
                "last_updated": "2024-02-05",
                "processing_time": "6-12 months",
                "fee": "$370",
                "access_level": "basic",
                "checklist": [
                    "Completed Form I-539",
                    "Filing fee of $370",
                    "Copy of I-94 arrival/departure record",
                    "Copy of passport biographical page",
                    "Financial support documentation",
                    "Explanation letter for extension/change",
                    "Supporting documents for new status category"
                ]
            },
            {
                "title": "Form I-131 - Reentry Permit/Refugee Travel Document Application",
                "category": "Travel Documents",
                "description": "Application for reentry permits, refugee travel documents, and advance parole documents to allow travel outside the United States.",
                "pdf_url": "https://www.uscis.gov/sites/default/files/document/forms/i-131.pdf",
                "info_url": "https://www.uscis.gov/i-131",
                "last_updated": "2024-02-10",
                "processing_time": "4-8 months",
                "fee": "$575",
                "access_level": "pro",
                "checklist": [
                    "Completed Form I-131",
                    "Filing fee of $575",
                    "Copy of permanent resident card or other status document",
                    "Two passport-style photographs",
                    "Copy of passport biographical page",
                    "Travel itinerary or explanation of travel purpose",
                    "Supporting documentation for travel necessity",
                    "Copy of pending adjustment application (if applicable)"
                ]
            },
            {
                "title": "Form I-90 - Permanent Resident Card Replacement Application",
                "category": "Green Card / Permanent Residence",
                "description": "Application to replace, renew, or obtain a permanent resident card (Green Card) due to loss, theft, damage, or expiration.",
                "pdf_url": "https://www.uscis.gov/sites/default/files/document/forms/i-90.pdf",
                "info_url": "https://www.uscis.gov/i-90",
                "last_updated": "2024-01-30",
                "processing_time": "12-18 months",
                "fee": "$540",
                "access_level": "basic",  # Form 7 of 7 in Basic tier
                "checklist": [
                    "Completed Form I-90",
                    "Filing fee of $540",
                    "Copy of current or expired permanent resident card",
                    "Police report (if card was stolen)",
                    "Court order for legal name change (if applicable)",
                    "Two passport-style photographs",
                    "Copy of marriage certificate (if name change due to marriage)",
                    "Copy of divorce decree (if name change due to divorce)"
                ]
            },
            {
                "title": "Form DS-160 - Online Nonimmigrant Visa Application",
                "category": "Visa Applications",
                "description": "Mandatory online application form for nonimmigrant visa applicants applying at U.S. consulates and embassies worldwide.",
                "pdf_url": "https://ceac.state.gov/genniv/",
                "info_url": "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/forms/ds-160-online-nonimmigrant-visa-application.html",
                "last_updated": "2024-02-15",
                "processing_time": "Varies by embassy",
                "fee": "$185 (varies by visa type)",
                "access_level": "pro",  # Form 9 of 9 in Pro tier
                "checklist": [
                    "Valid passport with 6+ months validity",
                    "Digital passport-style photograph",
                    "Travel itinerary details",
                    "Employment or educational information",
                    "Family information and contacts",
                    "Previous U.S. travel history",
                    "Purpose of travel documentation",
                    "Financial support evidence"
                ]
            },
            {
                "title": "Form DS-260 - Online Immigrant Visa and Alien Registration Application",
                "category": "Visa Applications",
                "description": "Electronic application for immigrant visas processed by the National Visa Center for family-based and employment-based immigrant petitions.",
                "pdf_url": "https://ceac.state.gov/iv/",
                "info_url": "https://travel.state.gov/content/travel/en/us-visas/immigrate/the-immigrant-visa-process/step-1-submit-a-petition/step-2-begin-nvc-process.html",
                "last_updated": "2024-02-08",
                "processing_time": "6-12 months after approval",
                "fee": "$325",
                "access_level": "enterprise",
                "checklist": [
                    "Approved I-130 or I-140 petition",
                    "Valid passport for all family members",
                    "Birth certificates for all applicants",
                    "Marriage certificate (if applicable)",
                    "Divorce decrees (if previously married)",
                    "Police certificates from all countries of residence",
                    "Medical examination results",
                    "Affidavit of Support (Form I-864)",
                    "Financial documents and tax returns",
                    "Passport-style photographs"
                ]
            },
            {
                "title": "Form I-407 - Voluntary Abandonment of Permanent Resident Status",
                "category": "Green Card / Permanent Residence",
                "description": "Record of abandonment by lawful permanent residents who voluntarily relinquish their permanent resident status in the United States.",
                "pdf_url": "https://www.uscis.gov/sites/default/files/document/forms/i-407.pdf",
                "info_url": "https://www.uscis.gov/i-407",
                "last_updated": "2024-01-18",
                "processing_time": "Immediate processing",
                "fee": "No fee",
                "access_level": "enterprise",
                "checklist": [
                    "Completed Form I-407",
                    "Original permanent resident card",
                    "Valid passport",
                    "Reason for abandoning status",
                    "Documentation supporting abandonment decision",
                    "Copy of tax returns filed while permanent resident",
                    "Evidence of ties to home country"
                ]
            }
        ]

        # Insert forms into database
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
        print(f"Successfully migrated {len(forms_data)} forms to database!")


if __name__ == '__main__':
    init_database()

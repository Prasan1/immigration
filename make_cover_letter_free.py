"""Make USCIS Cover Letter template free tier"""
from app import app, db
from models import FormTemplate

def make_cover_letter_free():
    """Change USCIS Cover Letter template from basic to free tier"""
    with app.app_context():
        # Find the cover letter template
        cover_letter = FormTemplate.query.filter_by(
            template_url='/templates/uscis-cover-letter'
        ).first()

        if cover_letter:
            print(f"Found: {cover_letter.title}")
            print(f"  Current access level: {cover_letter.access_level}")

            # Change to free tier
            cover_letter.access_level = 'free'
            db.session.commit()

            print(f"  ✓ Updated access level: {cover_letter.access_level}")
            print("\n✓ USCIS Cover Letter is now FREE!")
        else:
            print("⚠️  Cover letter template not found")

        # Show all free templates
        print("\n" + "="*60)
        print("ALL FREE TIER TEMPLATES:")
        print("="*60)
        free_templates = FormTemplate.query.filter_by(access_level='free').order_by(FormTemplate.id).all()
        for t in free_templates:
            print(f"  ✓ {t.title}")

if __name__ == '__main__':
    make_cover_letter_free()

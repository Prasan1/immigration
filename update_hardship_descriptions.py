"""Update hardship template descriptions to clarify their differences"""
from app import app, db
from models import FormTemplate

def update_descriptions():
    """Update descriptions for the two hardship templates"""
    with app.app_context():
        # Update Extreme Hardship Analysis Worksheet
        worksheet = FormTemplate.query.filter_by(template_url='/templates/hardship-worksheet').first()
        if worksheet:
            worksheet.description = 'Internal case analysis tool for attorneys to systematically evaluate and document all hardship factors before drafting the formal declaration'
            worksheet.use_case = 'Attorney case prep tool - analyze medical, financial, educational, psychological, and country condition factors. Use this FIRST to organize evidence, then draft the formal declaration.'
            print("✓ Updated: Extreme Hardship Analysis Worksheet")
            print(f"  New Description: {worksheet.description}")
            print(f"  New Use Case: {worksheet.use_case}")

        # Update Extreme Hardship Declaration
        declaration = FormTemplate.query.filter_by(template_url='/templates/hardship-declaration').first()
        if declaration:
            declaration.description = 'Formal sworn declaration submitted to USCIS proving extreme hardship to qualifying U.S. citizen or LPR relative (the actual document filed with your waiver application)'
            declaration.use_case = 'Final document for I-601/I-601A waiver applications - this is the sworn statement you SUBMIT to USCIS after completing your case analysis using the worksheet.'
            print("\n✓ Updated: Extreme Hardship Declaration (I-601/I-601A)")
            print(f"  New Description: {declaration.description}")
            print(f"  New Use Case: {declaration.use_case}")

        db.session.commit()
        print("\n✓ Both descriptions updated successfully!")

        print("\n" + "="*60)
        print("HOW THEY WORK TOGETHER:")
        print("="*60)
        print("Step 1: Use 'Extreme Hardship Analysis Worksheet' to:")
        print("        - Analyze your case")
        print("        - Organize evidence")
        print("        - Document hardship factors")
        print("        (NOT submitted to USCIS)")
        print()
        print("Step 2: Use 'Extreme Hardship Declaration' to:")
        print("        - Create formal sworn statement")
        print("        - File with I-601/I-601A application")
        print("        (SUBMITTED to USCIS)")

if __name__ == '__main__':
    update_descriptions()

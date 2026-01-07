"""Generate free I-130 checklist PDF"""
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime


def generate_free_i130_checklist():
    """Generate the free I-130 checklist PDF"""

    filename = "static/downloads/i130-checklist.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []

    # Styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0284c7'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )

    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=colors.HexColor('#0284c7'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8,
        leading=14
    )

    # Title Page
    elements.append(Spacer(1, 1*inch))
    elements.append(Paragraph("Form I-130", title_style))
    elements.append(Paragraph("Marriage Green Card Checklist", heading_style))
    elements.append(Spacer(1, 0.3*inch))

    elements.append(Paragraph(
        "Complete Document Checklist for Filing Form I-130<br/>Petition for Alien Relative",
        body_style
    ))

    elements.append(Spacer(1, 0.5*inch))

    # Info box
    info_text = """
    <font color='#0d9488'><b>What This Checklist Includes:</b></font><br/>
    ✓ All required documents for I-130 petition<br/>
    ✓ Evidence of bona fide marriage<br/>
    ✓ Common mistakes to avoid<br/>
    ✓ Filing instructions and fees<br/><br/>

    <font color='#64748b'><i>Downloaded from ImmigrationTemplates.com</i></font>
    """
    elements.append(Paragraph(info_text, body_style))

    elements.append(PageBreak())

    # Main Checklist
    elements.append(Paragraph("Required Documents Checklist", heading_style))
    elements.append(Spacer(1, 0.2*inch))

    # Section 1: Forms and Fees
    elements.append(Paragraph("1. Forms and Filing Fees", subheading_style))

    checklist_data = [
        ["☐", "Form I-130, Petition for Alien Relative (completed and signed)"],
        ["☐", "Filing fee: $535 (check or money order payable to \"U.S. Department of Homeland Security\")"],
        ["☐", "Two passport-style photos of the petitioner (U.S. citizen)"],
        ["☐", "Two passport-style photos of the beneficiary (spouse)"],
    ]

    table = Table(checklist_data, colWidths=[0.4*inch, 5.5*inch])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0284c7')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)

    # Section 2: Proof of U.S. Citizenship
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("2. Proof of U.S. Citizenship (Petitioner)", subheading_style))

    checklist_data = [
        ["☐", "Copy of U.S. birth certificate (if born in the U.S.)"],
        ["☐", "Copy of U.S. passport (bio page)"],
        ["☐", "Copy of Certificate of Naturalization or Citizenship (if naturalized)"],
        ["☐", "Copy of Consular Report of Birth Abroad (if born abroad to U.S. citizens)"],
    ]

    table = Table(checklist_data, colWidths=[0.4*inch, 5.5*inch])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0284c7')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)

    # Section 3: Proof of Marriage
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("3. Proof of Legal Marriage", subheading_style))

    checklist_data = [
        ["☐", "Copy of marriage certificate (certified copy from vital records office)"],
        ["☐", "Proof of termination of ALL previous marriages (divorce decrees, death certificates, annulments)"],
        ["☐", "Legal name change documents (if applicable)"],
    ]

    table = Table(checklist_data, colWidths=[0.4*inch, 5.5*inch])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0284c7')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)

    # Section 4: Proof of Bona Fide Marriage
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("4. Evidence of Bona Fide (Real) Marriage", subheading_style))

    checklist_data = [
        ["☐", "Joint bank account statements (3-6 months)"],
        ["☐", "Joint lease or mortgage documents"],
        ["☐", "Joint utility bills (electric, gas, internet, phone)"],
        ["☐", "Joint insurance policies (car, health, life)"],
        ["☐", "Joint tax returns (if filed jointly)"],
        ["☐", "Photos together (20-30 photos spanning the relationship)"],
        ["☐", "Travel documents (boarding passes, hotel reservations, itineraries)"],
        ["☐", "Affidavits from friends and family (2-3 letters)"],
        ["☐", "Correspondence (emails, texts, letters - sample 10-15 pages)"],
        ["☐", "Social media evidence (relationship status, photos, posts)"],
    ]

    table = Table(checklist_data, colWidths=[0.4*inch, 5.5*inch])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0284c7')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)

    elements.append(PageBreak())

    # Section 5: Identity Documents
    elements.append(Paragraph("5. Identity Documents (Both Spouses)", subheading_style))

    checklist_data = [
        ["☐", "Copy of passport bio pages (both petitioner and beneficiary)"],
        ["☐", "Copy of birth certificates (both spouses)"],
        ["☐", "Copy of government-issued ID (driver's license, state ID)"],
    ]

    table = Table(checklist_data, colWidths=[0.4*inch, 5.5*inch])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#0284c7')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)

    # Common Mistakes Section
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("⚠️ Common Mistakes to Avoid", heading_style))

    mistakes = [
        "<b>Unsigned form:</b> Make sure you sign and date the I-130 in BLACK INK.",
        "<b>Incorrect fees:</b> Verify current filing fees at uscis.gov before mailing.",
        "<b>Missing evidence of previous marriage termination:</b> USCIS will reject if you don't prove ALL previous marriages ended.",
        "<b>Poor quality photos:</b> Passport photos must be recent (within 6 months), 2x2 inches, white background.",
        "<b>Incomplete translations:</b> All foreign language documents need certified English translations.",
        "<b>Not enough bona fide marriage evidence:</b> Include at least 6-8 different types of evidence.",
    ]

    for mistake in mistakes:
        elements.append(Paragraph(f"• {mistake}", body_style))
        elements.append(Spacer(1, 0.05*inch))

    # Filing Instructions
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("📮 Where to File", heading_style))

    filing_info = """
    <b>USCIS Chicago Lockbox:</b><br/>
    USCIS<br/>
    Attn: I-130<br/>
    P.O. Box 804625<br/>
    Chicago, IL 60680-4107<br/><br/>

    <b>Important Tips:</b><br/>
    • Use certified mail with return receipt for proof of delivery<br/>
    • Make photocopies of your entire application before mailing<br/>
    • Keep your receipt notice (Form I-797) in a safe place<br/>
    • Processing time: Typically 10-14 months (varies by location)<br/><br/>

    <font color='#64748b'><i>Check uscis.gov for the most current filing addresses and fees</i></font>
    """

    elements.append(Paragraph(filing_info, body_style))

    # Upgrade CTA
    elements.append(PageBreak())
    elements.append(Spacer(1, 1.5*inch))

    cta_style = ParagraphStyle(
        'CTA',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=15,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    elements.append(Paragraph("✅ Got Your I-130 Checklist?", cta_style))
    elements.append(Spacer(1, 0.3*inch))

    upgrade_text = """
    <font size='12' color='#0284c7'><b>Now Get the COMPLETE Marriage Green Card Package:</b></font><br/><br/>

    ✓ <b>I-485 Adjustment of Status</b> - Complete checklist and guide<br/>
    ✓ <b>I-864 Affidavit of Support</b> - Financial requirements & documentation<br/>
    ✓ <b>I-765 Work Authorization</b> - Get your EAD card faster<br/>
    ✓ <b>I-131 Travel Document</b> - Advance parole application<br/>
    ✓ <b>Cover Letter Templates</b> - Professional USCIS-ready letters<br/>
    ✓ <b>Evidence Organizer</b> - Organize photos, texts, financial docs<br/>
    ✓ <b>PDF Compressor</b> - Reduce file sizes for online filing<br/>
    ✓ <b>I-94 Travel History Generator</b> - Auto-organize entry/exit records<br/><br/>

    <font size='18' color='#0284c7'><b>$149 one-time</b></font> <font size='10' color='#64748b'>(Save $2,851+ in attorney fees)</font><br/><br/>

    <font size='10' color='#10b981'>✓ 30-day money-back guarantee</font><br/><br/>

    <b>Visit: ImmigrationTemplates.com/pricing</b><br/>
    Or email us at: support@immigrationtemplates.com
    """

    elements.append(Paragraph(upgrade_text, body_style))

    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#94a3b8'),
        alignment=TA_CENTER
    )

    footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y')} | ImmigrationTemplates.com<br/>This checklist is for informational purposes only and does not constitute legal advice."
    elements.append(Paragraph(footer_text, footer_style))

    # Build PDF
    doc.build(elements)
    print(f"✅ Free I-130 checklist PDF generated: {filename}")
    return filename


if __name__ == "__main__":
    generate_free_i130_checklist()

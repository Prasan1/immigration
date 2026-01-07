"""PDF Generation utilities for immigration documents"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime
import os
from io import BytesIO

class PDFGenerator:
    """Base class for generating immigration-related PDFs"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Field label
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            spaceAfter=2,
            fontName='Helvetica-Bold'
        ))

        # Field value
        self.styles.add(ParagraphStyle(
            name='FieldValue',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            fontName='Helvetica'
        ))

    def _add_header(self, elements, title, subtitle=None):
        """Add standard header to PDF"""
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        if subtitle:
            elements.append(Paragraph(subtitle, self.styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))
        elements.append(Spacer(1, 0.3*inch))

    def _add_footer(self, elements):
        """Add standard footer"""
        elements.append(Spacer(1, 0.5*inch))
        footer_style = ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y')} | ImmigrationTemplates.com"
        elements.append(Paragraph(footer_text, footer_style))

    def _add_field(self, elements, label, value):
        """Add a labeled field to the PDF"""
        if value:
            elements.append(Paragraph(label, self.styles['FieldLabel']))
            elements.append(Paragraph(str(value), self.styles['FieldValue']))

    def save_to_file(self, elements, filename):
        """Save PDF to file"""
        doc = SimpleDocTemplate(filename, pagesize=letter,
                              rightMargin=0.75*inch, leftMargin=0.75*inch,
                              topMargin=0.75*inch, bottomMargin=0.75*inch)
        doc.build(elements)
        return filename

    def save_to_bytes(self, elements):
        """Save PDF to bytes buffer"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=0.75*inch, leftMargin=0.75*inch,
                              topMargin=0.75*inch, bottomMargin=0.75*inch)
        doc.build(elements)
        buffer.seek(0)
        return buffer


class PassportPDFGenerator(PDFGenerator):
    """Generate passport application DS-11 form PDF"""

    def generate(self, application_data):
        """Generate passport application PDF"""
        elements = []

        # Header
        self._add_header(
            elements,
            "U.S. PASSPORT APPLICATION (DS-11)",
            "Application for a U.S. Passport"
        )

        # Important notice
        notice_style = ParagraphStyle(
            name='Notice',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.red,
            spaceAfter=20,
            leftIndent=20,
            rightIndent=20
        )
        elements.append(Paragraph(
            "<b>IMPORTANT:</b> This is a pre-filled guide. You must still complete the official DS-11 form "
            "and submit it in person at an acceptance facility or passport agency.",
            notice_style
        ))
        elements.append(Spacer(1, 0.3*inch))

        # Personal Information
        elements.append(Paragraph("PERSONAL INFORMATION", self.styles['SectionHeader']))
        self._add_field(elements, "Full Legal Name", application_data.get('full_name'))
        self._add_field(elements, "Date of Birth", application_data.get('date_of_birth'))
        self._add_field(elements, "Place of Birth", application_data.get('place_of_birth'))
        self._add_field(elements, "Gender", application_data.get('gender'))
        self._add_field(elements, "Social Security Number", application_data.get('ssn', 'Not Provided'))

        elements.append(Spacer(1, 0.2*inch))

        # Physical Description
        elements.append(Paragraph("PHYSICAL DESCRIPTION", self.styles['SectionHeader']))
        self._add_field(elements, "Height", application_data.get('height'))
        self._add_field(elements, "Hair Color", application_data.get('hair_color'))
        self._add_field(elements, "Eye Color", application_data.get('eye_color'))

        elements.append(Spacer(1, 0.2*inch))

        # Contact Information
        elements.append(Paragraph("CONTACT INFORMATION", self.styles['SectionHeader']))
        self._add_field(elements, "Email Address", application_data.get('email'))
        self._add_field(elements, "Phone Number", application_data.get('phone'))

        # Mailing Address
        address_parts = []
        if application_data.get('mailing_address'):
            address_parts.append(application_data.get('mailing_address'))
        if application_data.get('city'):
            city_state_zip = application_data.get('city')
            if application_data.get('state'):
                city_state_zip += f", {application_data.get('state')}"
            if application_data.get('zip_code'):
                city_state_zip += f" {application_data.get('zip_code')}"
            address_parts.append(city_state_zip)

        if address_parts:
            self._add_field(elements, "Mailing Address", "<br/>".join(address_parts))

        elements.append(Spacer(1, 0.2*inch))

        # Emergency Contact
        if application_data.get('emergency_contact_name'):
            elements.append(Paragraph("EMERGENCY CONTACT", self.styles['SectionHeader']))
            self._add_field(elements, "Contact Name", application_data.get('emergency_contact_name'))
            self._add_field(elements, "Contact Phone", application_data.get('emergency_contact_phone'))
            self._add_field(elements, "Relationship", application_data.get('emergency_contact_relationship'))
            elements.append(Spacer(1, 0.2*inch))

        # Employment
        if application_data.get('occupation') or application_data.get('employer'):
            elements.append(Paragraph("EMPLOYMENT INFORMATION", self.styles['SectionHeader']))
            self._add_field(elements, "Occupation", application_data.get('occupation'))
            self._add_field(elements, "Employer", application_data.get('employer'))
            elements.append(Spacer(1, 0.2*inch))

        # Travel Plans
        if application_data.get('travel_date') or application_data.get('destination'):
            elements.append(Paragraph("TRAVEL PLANS", self.styles['SectionHeader']))
            self._add_field(elements, "Expected Travel Date", application_data.get('travel_date'))
            self._add_field(elements, "Destination", application_data.get('destination'))
            elements.append(Spacer(1, 0.2*inch))

        # Parent Information
        if application_data.get('parent1_name') or application_data.get('parent2_name'):
            elements.append(Paragraph("PARENT INFORMATION", self.styles['SectionHeader']))
            if application_data.get('parent1_name'):
                self._add_field(elements, "Parent 1 Full Name", application_data.get('parent1_name'))
                self._add_field(elements, "Parent 1 Place of Birth", application_data.get('parent1_birthplace'))
                self._add_field(elements, "Parent 1 Date of Birth", application_data.get('parent1_dob'))
                elements.append(Spacer(1, 0.1*inch))

            if application_data.get('parent2_name'):
                self._add_field(elements, "Parent 2 Full Name", application_data.get('parent2_name'))
                self._add_field(elements, "Parent 2 Place of Birth", application_data.get('parent2_birthplace'))
                self._add_field(elements, "Parent 2 Date of Birth", application_data.get('parent2_dob'))

        # Next Steps
        elements.append(PageBreak())
        elements.append(Paragraph("NEXT STEPS", self.styles['SectionHeader']))

        next_steps = [
            "1. Download the official DS-11 form from travel.state.gov",
            "2. Fill out the DS-11 form using the information above",
            "3. Gather required documents (see checklist below)",
            "4. Find a passport acceptance facility: iafdb.travel.state.gov",
            "5. Schedule an appointment (if required)",
            "6. Bring all documents and payment to your appointment",
            "7. Submit application in person (DO NOT SIGN DS-11 UNTIL AT FACILITY)"
        ]

        for step in next_steps:
            elements.append(Paragraph(step, self.styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))

        elements.append(Spacer(1, 0.3*inch))

        # Required Documents Checklist
        elements.append(Paragraph("REQUIRED DOCUMENTS CHECKLIST", self.styles['SectionHeader']))

        checklist_items = [
            ["☐", "Completed DS-11 form (DO NOT SIGN until at facility)"],
            ["☐", "Proof of U.S. citizenship (birth certificate, naturalization certificate, etc.)"],
            ["☐", "Photocopy of citizenship proof"],
            ["☐", "Valid government-issued photo ID"],
            ["☐", "Photocopy of ID"],
            ["☐", "One passport photo (2x2 inches, taken within last 6 months)"],
            ["☐", "Payment: $130 (application) + $35 (execution fee) = $165 total"],
            ["☐", "Parental consent (if applicant under 16)"],
        ]

        checklist_table = Table(checklist_items, colWidths=[0.4*inch, 5.5*inch])
        checklist_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(checklist_table)

        # Footer
        self._add_footer(elements)

        return elements


class ChecklistPDFGenerator(PDFGenerator):
    """Generate checklist PDF for immigration forms"""

    def generate(self, form_title, checklist_items, user_name=None):
        """Generate checklist PDF"""
        elements = []

        # Header
        self._add_header(
            elements,
            f"{form_title}",
            "Document Checklist"
        )

        if user_name:
            elements.append(Paragraph(f"Prepared for: <b>{user_name}</b>", self.styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))

        # Instructions
        elements.append(Paragraph(
            "Check off each item as you gather the required documents. Keep all documents organized and ready for submission.",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 0.3*inch))

        # Checklist table
        checklist_data = [["", "Required Document"]]
        for item in checklist_items:
            checklist_data.append(["☐", item])

        table = Table(checklist_data, colWidths=[0.4*inch, 5.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f7fa')]),
        ]))
        elements.append(table)

        # Footer
        self._add_footer(elements)

        return elements


class CoverLetterGenerator(PDFGenerator):
    """Generate USCIS cover letter"""

    def _get_form_address(self, form_title):
        """Get appropriate USCIS address based on form type"""
        form_upper = form_title.upper()

        if 'I-130' in form_upper:
            return "USCIS<br/>Attn: I-130<br/>P.O. Box 804625<br/>Chicago, IL 60680-4107"
        elif 'I-485' in form_upper:
            return "USCIS<br/>Attn: I-485<br/>P.O. Box 805887<br/>Chicago, IL 60680-4120"
        elif 'I-765' in form_upper:
            return "USCIS<br/>Attn: I-765<br/>P.O. Box 805373<br/>Chicago, IL 60680"
        elif 'I-131' in form_upper:
            return "USCIS<br/>Attn: I-131<br/>P.O. Box 805625<br/>Chicago, IL 60680"
        elif 'N-400' in form_upper:
            return "USCIS<br/>Attn: N-400<br/>P.O. Box 660060<br/>Dallas, TX 75266"
        elif 'I-864' in form_upper:
            return "USCIS<br/>Attn: I-864<br/>P.O. Box 804625<br/>Chicago, IL 60680-4107"
        else:
            return "U.S. Citizenship and Immigration Services<br/>Appropriate Service Center"

    def _get_document_list(self, form_title):
        """Get form-specific document checklist"""
        form_upper = form_title.upper()

        if 'I-130' in form_upper:
            return [
                "1. Completed Form I-130, Petition for Alien Relative",
                "2. Filing fee: Check or money order for $535",
                "3. Proof of U.S. citizenship (birth certificate or naturalization certificate)",
                "4. Marriage certificate (if applicable)",
                "5. Proof of termination of previous marriages (if applicable)",
                "6. Two passport-style photographs of petitioner",
                "7. Two passport-style photographs of beneficiary",
                "8. Proof of bona fide relationship (photos, correspondence, joint accounts)"
            ]
        elif 'I-485' in form_upper:
            return [
                "1. Completed Form I-485, Application to Register Permanent Residence",
                "2. Filing fee and biometric fee",
                "3. Copy of passport biographical pages",
                "4. Two passport-style photographs",
                "5. Form I-693, Medical Examination (in sealed envelope)",
                "6. Birth certificate with certified English translation",
                "7. Form I-864, Affidavit of Support",
                "8. Employment authorization documents (if applicable)"
            ]
        elif 'N-400' in form_upper:
            return [
                "1. Completed Form N-400, Application for Naturalization",
                "2. Filing fee: Check or money order for $640 ($725 with biometrics)",
                "3. Copy of Permanent Resident Card (front and back)",
                "4. Two passport-style photographs",
                "5. Proof of marital status (marriage certificate, divorce decree)",
                "6. Evidence of any name changes",
                "7. Documentation for any trips outside the U.S. over 6 months"
            ]
        elif 'I-765' in form_upper:
            return [
                "1. Completed Form I-765, Application for Employment Authorization",
                "2. Filing fee (if required for your category)",
                "3. Copy of Form I-94, Arrival/Departure Record",
                "4. Two passport-style photographs",
                "5. Copy of pending I-485 receipt (if filing based on pending AOS)",
                "6. Copy of passport biographical pages"
            ]
        elif 'I-131' in form_upper:
            return [
                "1. Completed Form I-131, Application for Travel Document",
                "2. Filing fee: $575 (or $630 if under 16)",
                "3. Two passport-style photographs",
                "4. Copy of Permanent Resident Card or pending I-485 receipt",
                "5. Copy of passport biographical pages",
                "6. Evidence of travel plans (if applicable)"
            ]
        else:
            return [
                f"1. Completed {form_title}",
                "2. Filing fee payment (check or money order)",
                "3. Supporting documents as required by form instructions",
                "4. Passport-style photographs (if required)",
                "5. Photocopies of identity documents"
            ]

    def generate(self, user_data, form_info):
        """Generate cover letter PDF"""
        elements = []

        # Date and address block
        date_style = ParagraphStyle(
            name='Date',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_RIGHT,
            spaceAfter=40
        )
        elements.append(Paragraph(datetime.now().strftime('%B %d, %Y'), date_style))

        # USCIS address (use custom if provided, otherwise auto-generate)
        address_style = ParagraphStyle(
            name='Address',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=30
        )
        # Use custom mailing address if provided, otherwise auto-generate based on form
        custom_address = form_info.get('mailing_address', '').strip()
        if custom_address:
            # User provided custom address - use it as-is
            form_address = custom_address.replace('\n', '<br/>')
        else:
            # Auto-generate address based on form type
            form_address = self._get_form_address(form_info.get('title', ''))
        elements.append(Paragraph(form_address, address_style))

        # Subject line
        subject_style = ParagraphStyle(
            name='Subject',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            spaceAfter=20
        )
        elements.append(Paragraph(f"RE: {form_info.get('title', 'Immigration Application')}", subject_style))
        elements.append(Paragraph(f"Applicant: {user_data.get('full_name', 'N/A')}", subject_style))
        if user_data.get('case_number'):
            elements.append(Paragraph(f"Case Number: {user_data.get('case_number')}", subject_style))

        elements.append(Spacer(1, 0.2*inch))

        # Salutation
        elements.append(Paragraph("Dear USCIS Officer:", self.styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))

        # Body (fixed wording - not "on behalf of")
        body_paragraphs = [
            f"I am submitting this {form_info.get('title', 'application')}. "
            "Please find enclosed all required forms, supporting documents, and fees as specified in the filing instructions.",

            "The enclosed package contains the following:",
        ]

        for para in body_paragraphs:
            elements.append(Paragraph(para, self.styles['Normal']))
            elements.append(Spacer(1, 0.15*inch))

        # Document list (form-specific)
        doc_list_style = ParagraphStyle(
            name='DocList',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=30,
            spaceAfter=10
        )

        documents = self._get_document_list(form_info.get('title', ''))

        for doc in documents:
            elements.append(Paragraph(doc, doc_list_style))

        elements.append(Spacer(1, 0.3*inch))

        # Closing
        closing_para = [
            "Please review this application at your earliest convenience. Should you require any additional information or documentation, "
            "please do not hesitate to contact me at the phone number or email address listed below.",

            "Thank you for your time and consideration."
        ]

        for para in closing_para:
            elements.append(Paragraph(para, self.styles['Normal']))
            elements.append(Spacer(1, 0.15*inch))

        elements.append(Spacer(1, 0.3*inch))

        # Signature block
        elements.append(Paragraph("Respectfully submitted,", self.styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("_________________________", self.styles['Normal']))
        elements.append(Paragraph(user_data.get('full_name', 'Applicant Name'), self.styles['Normal']))
        if user_data.get('email'):
            elements.append(Paragraph(user_data.get('email'), self.styles['Normal']))
        if user_data.get('phone'):
            elements.append(Paragraph(user_data.get('phone'), self.styles['Normal']))

        # Footer
        self._add_footer(elements)

        return elements


class I94HistoryGenerator(PDFGenerator):
    """Generate I-94 travel history PDF"""

    def generate(self, user_data, travel_history):
        """Generate I-94 travel history PDF"""
        elements = []

        # Header
        self._add_header(
            elements,
            "I-94 TRAVEL HISTORY",
            f"Travel Record for {user_data.get('full_name', 'N/A')}"
        )

        # Personal Information
        elements.append(Paragraph("PERSONAL INFORMATION", self.styles['SectionHeader']))
        self._add_field(elements, "Full Name", user_data.get('full_name'))
        self._add_field(elements, "Date of Birth", user_data.get('date_of_birth'))
        self._add_field(elements, "Passport Number", user_data.get('passport_number'))
        self._add_field(elements, "Country of Citizenship", user_data.get('country'))

        elements.append(Spacer(1, 0.3*inch))

        # Travel History Table
        elements.append(Paragraph("TRAVEL HISTORY", self.styles['SectionHeader']))

        if travel_history:
            table_data = [["Entry Date", "Departure Date", "I-94 Number", "Port of Entry", "Status"]]

            for record in travel_history:
                table_data.append([
                    record.get('entry_date', ''),
                    record.get('departure_date', ''),
                    record.get('i94_number', ''),
                    record.get('port_of_entry', ''),
                    record.get('status', '')
                ])

            table = Table(table_data, colWidths=[1.1*inch, 1.1*inch, 1.2*inch, 1.8*inch, 0.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f7fa')]),
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("No travel history records available.", self.styles['Normal']))

        elements.append(Spacer(1, 0.3*inch))

        # Notes
        elements.append(Paragraph("NOTES", self.styles['SectionHeader']))
        notes = [
            "• This document is compiled from I-94 Arrival/Departure Records",
            "• Verify all dates and information with official I-94 records at cbp.gov/I94",
            "• Keep copies of all I-94 forms for your records",
            "• Report any discrepancies to CBP immediately"
        ]
        for note in notes:
            elements.append(Paragraph(note, self.styles['Normal']))
            elements.append(Spacer(1, 0.05*inch))

        # Footer
        self._add_footer(elements)

        return elements

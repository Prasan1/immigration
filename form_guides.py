"""
Form Filling Guides - Step-by-step instructions, common mistakes, and tips
for the most popular immigration forms
"""

FORM_GUIDES = {
    'I-130': {
        'filling_steps': [
            {
                'part': 'Part 1: Information About You (Petitioner)',
                'instructions': [
                    'Line 1a-1c: Enter your full legal name exactly as it appears on your birth certificate or passport',
                    'Line 2: Include all other names you have used (maiden name, previous married names, nicknames)',
                    'Line 3: Enter your current mailing address where USCIS can reach you',
                    'Line 4-5: Provide your date of birth (MM/DD/YYYY) and country of birth',
                    'Line 6: Enter your U.S. citizenship status (Born in U.S., Naturalized, etc.)',
                    'Line 7-8: Provide your A-Number (if you have one) and Social Security Number'
                ],
                'tips': [
                    '💡 Make sure your name spelling is consistent across all documents',
                    '💡 Use your current legal address, not a PO Box',
                    '💡 If you don\'t have an A-Number, write "None" - don\'t leave it blank'
                ]
            },
            {
                'part': 'Part 2: Information About Your Relative',
                'instructions': [
                    'Line 1a-1c: Enter your relative\'s full legal name',
                    'Line 2: List all other names your relative has used',
                    'Line 3: Enter your relative\'s current address',
                    'Line 4-5: Provide date of birth and country of birth',
                    'Line 6: Enter citizenship or nationality',
                    'Line 7-8: Provide A-Number and Social Security Number (if applicable)',
                    'Line 9: Enter U.S. entry date (if in the U.S.)',
                    'Line 10: Provide I-94 Number (found on I-94 arrival/departure record)',
                    'Line 11: Enter passport information'
                ],
                'tips': [
                    '💡 If relative is not in the U.S., write "Not in U.S." for entry date',
                    '💡 The I-94 number is found at cbp.gov/i94 if entered recently',
                    '💡 Make sure passport information matches exactly'
                ]
            },
            {
                'part': 'Part 3: Additional Information About Your Relative',
                'instructions': [
                    'Line 1: Check the box for your relationship (spouse, parent, child, sibling)',
                    'Line 2-4: If relative has been in the U.S., provide immigration history',
                    'Line 5: List current and prior spouses of your relative',
                    'Line 6: Indicate if relative has filed other immigrant petitions',
                    'Line 7: Answer yes/no to ever filing an I-130 for this person before'
                ],
                'tips': [
                    '💡 Be honest about immigration history - USCIS will check',
                    '💡 Include divorced spouses - this affects eligibility',
                    '💡 If unsure about previous filings, say "Unknown" and explain'
                ]
            },
            {
                'part': 'Part 4: Information About Your Relative\'s Parents',
                'instructions': [
                    'Provide mother\'s name (maiden name preferred)',
                    'Provide mother\'s date and country of birth',
                    'Provide father\'s name',
                    'Provide father\'s date and country of birth'
                ],
                'tips': [
                    '💡 Use mother\'s maiden name if known',
                    '💡 If parent\'s info is unknown, write "Unknown"',
                    '💡 This helps USCIS verify relationship'
                ]
            },
            {
                'part': 'Part 5: Information About Your Relative\'s Marital History',
                'instructions': [
                    'List current spouse (if married)',
                    'Provide marriage date and place',
                    'List all prior marriages with dates',
                    'Explain how each marriage ended (divorce, death, annulment)'
                ],
                'tips': [
                    '💡 Include ALL previous marriages',
                    '💡 Attach divorce certificates or death certificates',
                    '💡 If never married, write "Never Married"'
                ]
            },
            {
                'part': 'Part 6: Petitioner\'s Statement, Contact Information, Declaration, Certification, and Signature',
                'instructions': [
                    'Indicate if you used a preparer or attorney',
                    'Provide your daytime and mobile phone numbers',
                    'Provide your email address',
                    'Sign and date the form',
                    'Print your name clearly'
                ],
                'tips': [
                    '💡 SIGN IN BLACK INK ONLY',
                    '💡 Date should be when you actually sign (MM/DD/YYYY)',
                    '💡 Your email will be used for USCIS communications'
                ]
            }
        ],
        'common_mistakes': [
            '❌ Using nicknames instead of legal names',
            '❌ Forgetting to sign Part 6 - petition will be rejected!',
            '❌ Not including middle names',
            '❌ Wrong date format (use MM/DD/YYYY)',
            '❌ Leaving A-Number blank (write "None" if you don\'t have one)',
            '❌ Not listing ALL previous marriages',
            '❌ Inconsistent spellings between this form and birth certificate',
            '❌ Using pencil or colored ink (use black ink only)',
            '❌ Missing pages or attachments',
            '❌ Not signing the most recent version of the form'
        ],
        'before_submit': [
            'All pages filled out completely (no blank fields unless marked N/A)',
            'Signed and dated in Part 6',
            'Correct filing fee ($535 as of 2024) - check or money order only',
            'Copy of your proof of U.S. citizenship (birth certificate, passport, naturalization certificate)',
            'Copy of your relative\'s birth certificate with English translation',
            'Marriage certificate (if petitioning for spouse)',
            'Proof of relationship (photos, joint accounts, etc. for spouses)',
            'Divorce/death certificates for any previous marriages',
            'Two passport-style photos of your relative',
            'Form G-1145 (optional - for electronic notifications)'
        ],
        'pro_tips': [
            '📌 Make copies of everything before mailing',
            '📌 Use USPS certified mail with tracking',
            '📌 Keep your receipt notice - you\'ll need the receipt number',
            '📌 Processing time is typically 10-13 months',
            '📌 Check status online at egov.uscis.gov/casestatus',
            '📌 Respond quickly to any RFEs (Request for Evidence)'
        ]
    },

    'I-485': {
        'filling_steps': [
            {
                'part': 'Part 1: Information About You',
                'instructions': [
                    'Enter your full legal name (Last Name, First Name, Middle Name)',
                    'Provide all other names used (maiden name, aliases)',
                    'Enter your current address',
                    'Provide date of birth, country of birth, and country of citizenship',
                    'Enter your A-Number (found on previous USCIS notices)',
                    'Provide Social Security Number',
                    'Enter your USCIS Online Account Number (if you have one)'
                ],
                'tips': [
                    '💡 Your A-Number is critical - check old documents',
                    '💡 Use current address where you actually live',
                    '💡 If no SSN, apply for one immediately'
                ]
            },
            {
                'part': 'Part 2: Application Type or Filing Category',
                'instructions': [
                    'Check ONE box that applies to your case',
                    'Most common: Box "h" - Immediate relative of U.S. citizen',
                    'Include receipt number of your approved I-130 or other petition',
                    'Provide priority date if applicable'
                ],
                'tips': [
                    '💡 This is crucial - check with your attorney if unsure',
                    '💡 The priority date determines your place in line',
                    '💡 Your I-130 must be approved before filing I-485 (concurrent filing allowed for immediate relatives)'
                ]
            },
            {
                'part': 'Part 3: Additional Information About You',
                'instructions': [
                    'Provide date and place of last entry to U.S.',
                    'Enter your I-94 number and passport information',
                    'Indicate current immigration status',
                    'List travel history in past 5 years',
                    'Provide your parents\' information'
                ],
                'tips': [
                    '💡 Get I-94 from cbp.gov/i94',
                    '💡 Be accurate about overstays or status violations',
                    '💡 Include trips longer than 24 hours'
                ]
            },
            {
                'part': 'Part 4: Information About Your Parents',
                'instructions': [
                    'Father\'s full name, date of birth, country of birth',
                    'Mother\'s full name (maiden name), date of birth, country of birth',
                    'Indicate if each parent is a U.S. citizen'
                ],
                'tips': [
                    '💡 Use mother\'s maiden name',
                    '💡 If parent deceased, indicate in form'
                ]
            },
            {
                'part': 'Part 5: Information About Your Marital History',
                'instructions': [
                    'Current marital status',
                    'If married: spouse\'s full name, date and place of marriage',
                    'List all prior marriages with dates and how they ended',
                    'Your spouse\'s information and A-Number'
                ],
                'tips': [
                    '💡 Include ALL marriages - hiding one is fraud',
                    '💡 Attach marriage certificate',
                    '💡 Attach divorce decrees for previous marriages'
                ]
            },
            {
                'part': 'Part 6: Information About Your Employment and Schools Attended',
                'instructions': [
                    'List current employer with address',
                    'List all employment in past 5 years',
                    'List all schools attended',
                    'Include dates and locations'
                ],
                'tips': [
                    '💡 Include unemployed periods',
                    '💡 List schools from highest to lowest level',
                    '💡 Include vocational training'
                ]
            },
            {
                'part': 'Part 7: Biographic Information',
                'instructions': [
                    'Ethnicity, race, height, weight, eye color, hair color',
                    'Don\'t leave blank - select "Not Applicable" if needed'
                ],
                'tips': [
                    '💡 Be accurate - this goes on your Green Card',
                    '💡 Height in feet and inches'
                ]
            },
            {
                'part': 'Part 8: General Eligibility and Inadmissibility Grounds',
                'instructions': [
                    'Answer YES or NO to all questions',
                    'Questions about criminal history, immigration violations, public charge',
                    'If YES to any, provide detailed explanation'
                ],
                'tips': [
                    '💡 BE HONEST - lying is grounds for denial',
                    '💡 Include traffic tickets if asked',
                    '💡 Get certified court records if you have criminal history'
                ]
            },
            {
                'part': 'Part 12: Additional Information',
                'instructions': [
                    'Use this section for additional explanations',
                    'Reference part and line numbers',
                    'Attach extra pages if needed'
                ],
                'tips': [
                    '💡 Explain any YES answers from Part 8',
                    '💡 Explain gaps in employment or travel',
                    '💡 Attach continuation sheets if out of space'
                ]
            },
            {
                'part': 'Part 13: Applicant\'s Statement, Contact Information, Certification, and Signature',
                'instructions': [
                    'Indicate if you need an interpreter',
                    'Provide current phone and email',
                    'Read the declarations',
                    'Sign and date the form'
                ],
                'tips': [
                    '💡 SIGN IN BLACK INK',
                    '💡 Date when you actually sign',
                    '💡 Print name clearly under signature'
                ]
            }
        ],
        'common_mistakes': [
            '❌ Not signing the form',
            '❌ Using old version of form (check edition date)',
            '❌ Wrong filing fee ($1,140 + $85 biometrics as of 2024)',
            '❌ Missing medical exam (Form I-693)',
            '❌ Not answering all questions in Part 8',
            '❌ Incorrect A-Number',
            '❌ Missing passport photos (2 required)',
            '❌ Not including copy of I-94',
            '❌ Missing birth certificate translation',
            '❌ Filing too early (before I-130 approval for non-immediate relatives)'
        ],
        'before_submit': [
            'Form I-485 completed and signed',
            'Filing fee: $1,140 (application) + $85 (biometrics) = $1,225 total',
            'Two passport-style color photos',
            'Copy of birth certificate with certified English translation',
            'Copy of passport biographical pages',
            'Copy of I-94 arrival/departure record',
            'Form I-693 (Medical Examination) in sealed envelope',
            'Copy of I-130 approval notice',
            'Marriage certificate (if applicable)',
            'Affidavit of Support (Form I-864) from sponsor',
            'Employment authorization (Form I-765) if filing concurrently',
            'Advance Parole (Form I-131) if filing concurrently',
            'Police certificates (if lived abroad)',
            'Court records (if any criminal history)'
        ],
        'pro_tips': [
            '📌 File I-765 and I-131 together to save time',
            '📌 Use USCIS lockbox address (check current address on uscis.gov)',
            '📌 Keep copies of everything',
            '📌 Medical exam is valid for 2 years - don\'t get it too early',
            '📌 Get tracking for your mailing',
            '📌 Expect biometrics appointment 4-8 weeks after filing',
            '📌 Processing time: 10-24 months typically',
            '📌 Check case status at egov.uscis.gov/casestatus'
        ]
    },

    'N-400': {
        'filling_steps': [
            {
                'part': 'Part 1: Your Name',
                'instructions': [
                    'Enter your current legal name',
                    'Provide name exactly as it appears on Green Card',
                    'List other names used since becoming permanent resident',
                    'Indicate if you want to change name (court order required)'
                ],
                'tips': [
                    '💡 Match Green Card exactly',
                    '💡 Include maiden name if applicable',
                    '💡 Name change adds time to process'
                ]
            },
            {
                'part': 'Part 2: Information About Your Eligibility',
                'instructions': [
                    'Check basis for eligibility (most common: 5 years as LPR)',
                    'If married to U.S. citizen, may apply after 3 years',
                    'Military members have special rules'
                ],
                'tips': [
                    '💡 Count from date you became permanent resident',
                    '💡 You can apply 90 days before your eligibility date',
                    '💡 Military service can waive residence requirements'
                ]
            },
            {
                'part': 'Part 3: Information About You',
                'instructions': [
                    'Social Security Number',
                    'Date of birth',
                    'Date you became permanent resident',
                    'Country of birth and citizenship',
                    'Disability accommodations needed (if any)'
                ],
                'tips': [
                    '💡 Check your Green Card for LPR date',
                    '💡 Request accommodations if needed',
                    '💡 Provide SSN - required for naturalization'
                ]
            },
            {
                'part': 'Part 4: Addresses and Phone Numbers',
                'instructions': [
                    'Current physical address (no PO Box)',
                    'Mailing address if different',
                    'Phone numbers and email',
                    'List all addresses for past 5 years'
                ],
                'tips': [
                    '💡 Include all addresses - even short stays',
                    '💡 USCIS will verify residence requirement',
                    '💡 Don\'t skip any time periods'
                ]
            },
            {
                'part': 'Part 5: Information for Criminal Records Search',
                'instructions': [
                    'Mother\'s maiden name',
                    'Father\'s first and last name',
                    'Height, weight, eye color, hair color',
                    'Race and ethnicity'
                ],
                'tips': [
                    '💡 FBI will use this for background check',
                    '💡 Be accurate - it\'s checked against databases'
                ]
            },
            {
                'part': 'Part 6: Information About Your Residence',
                'instructions': [
                    'When did you become permanent resident?',
                    'Have you been absent from U.S. for 6+ months?',
                    'State and county of residence'
                ],
                'tips': [
                    '💡 Trips over 6 months can break continuous residence',
                    '💡 Must live in state for 3 months before filing',
                    '💡 Explain long absences in Part 12'
                ]
            },
            {
                'part': 'Part 7: Time Outside the United States',
                'instructions': [
                    'List ALL trips outside U.S. in past 5 years',
                    'Include dates left and returned',
                    'Countries visited',
                    'Total days outside U.S.'
                ],
                'tips': [
                    '💡 Check passport stamps for exact dates',
                    '💡 Include day trips to Canada/Mexico',
                    '💡 Business travel counts',
                    '💡 Get I-94 travel history from cbp.gov'
                ]
            },
            {
                'part': 'Part 8: Information About Your Marital History',
                'instructions': [
                    'Current marital status',
                    'Current spouse information',
                    'Number of times married',
                    'Information about previous spouses'
                ],
                'tips': [
                    '💡 Include ALL marriages',
                    '💡 If spouse is applying, note it',
                    '💡 Bring marriage certificate to interview'
                ]
            },
            {
                'part': 'Part 9: Information About Your Children',
                'instructions': [
                    'List ALL children (biological, adopted, step)',
                    'Include children over 18',
                    'Provide current address of each child',
                    'Indicate if child is applying for certificate of citizenship'
                ],
                'tips': [
                    '💡 Don\'t forget children from previous relationships',
                    '💡 Include adult children',
                    '💡 Children under 18 may get citizenship automatically'
                ]
            },
            {
                'part': 'Part 10: Additional Questions',
                'instructions': [
                    'Answer YES or NO to all questions',
                    'Questions about crimes, immigration fraud, selective service',
                    'Questions about oath and good moral character',
                    'Selective service registration (men 18-26)'
                ],
                'tips': [
                    '💡 BE HONEST - background check will find issues',
                    '💡 Even minor arrests must be disclosed',
                    '💡 Bring court records to interview',
                    '💡 DUIs count as crimes - disclose them'
                ]
            },
            {
                'part': 'Part 12: Additional Information',
                'instructions': [
                    'Use for explanations and additional details',
                    'Reference specific part and item numbers',
                    'Attach extra sheets if needed'
                ],
                'tips': [
                    '💡 Explain any YES answers',
                    '💡 Explain long absences from U.S.',
                    '💡 Explain employment gaps'
                ]
            }
        ],
        'common_mistakes': [
            '❌ Applying too early (before 90 days before eligibility)',
            '❌ Not listing all trips outside U.S.',
            '❌ Hiding arrests or traffic tickets',
            '❌ Not registering for Selective Service (men 18-26)',
            '❌ Wrong filing fee ($640 + $85 biometrics = $725 total)',
            '❌ Not including copies of Green Card',
            '❌ Missing signatures',
            '❌ Old version of form',
            '❌ Not explaining YES answers to Part 10',
            '❌ Failing to list all children and marriages'
        ],
        'before_submit': [
            'Form N-400 completed and signed',
            'Filing fee: $640 + $85 biometrics = $725 (fee waiver available for low income)',
            'Copy of front and back of Green Card',
            'Two passport-style photos',
            'If applying based on marriage: copy of spouse\'s citizenship proof',
            'If applicable: marriage certificate, divorce decrees',
            'If name change: court order or marriage certificate',
            'If arrests: certified court records and disposition',
            'If military service: Form N-426 or DD-214',
            'Proof of Selective Service registration (men born after 1960)',
            'Travel history documentation (passport stamps, I-94s)'
        ],
        'pro_tips': [
            '📌 Study for civics test - 100 questions available at uscis.gov',
            '📌 Practice English reading and writing',
            '📌 Bring certified translations of foreign documents',
            '📌 Arrive 15 minutes early to interview',
            '📌 Bring GREEN originals of all documents',
            '📌 Processing time: 8-14 months typically',
            '📌 Oath ceremony usually within 6 weeks of approval',
            '📌 You can vote once you take oath - register!'
        ]
    }
}


def get_form_guide(form_title):
    """
    Get the filling guide for a specific form
    Returns None if guide not available
    """
    # Extract form number from title (e.g., "Form I-130" -> "I-130")
    for form_code in FORM_GUIDES.keys():
        if form_code in form_title:
            return FORM_GUIDES[form_code]
    return None

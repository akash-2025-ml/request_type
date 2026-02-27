#!/usr/bin/env python3
"""
Generate Test CSV Files
=======================
Creates CSV files with sample emails for testing the classifier.

Usage:
    python3 generate_test_csv.py               # Generate default test file
    python3 generate_test_csv.py --count 50    # Generate 50 random emails
    python3 generate_test_csv.py --output custom.csv --threats-only
"""

import csv
import random
import argparse

# Sample threat emails by category
THREAT_SAMPLES = {
    "invoice_payment": [
        ("Invoice #4521 Payment Due", "Please pay the invoice attached. The amount due is $5200. Kindly transfer funds to the bank details provided before the due date."),
        ("Outstanding Invoice Notice", "Your invoice #INV-2891 is overdue. Please settle the amount of $8,450 and remit payment to our new bank account."),
        ("Payment Required Immediately", "Attached invoice for March services. Amount due: $12,500. Please process the payment using the bank details in the attachment."),
    ],
    "wire_transfer": [
        ("Urgent Wire Transfer Needed", "I need you to initiate a wire transfer of $45,000 immediately. Please use the routing number and account number below. Transfer funds today."),
        ("Time Sensitive Transfer", "Please make a wire transfer of $30,000 to our vendor. Account details attached. This is urgent, please send money today."),
        ("SWIFT Transfer Required", "Initiate a SWIFT transfer for €50,000 to IBAN GB29NWBK60161331926819. Beneficiary: Acme Corp. Transfer the amount immediately."),
    ],
    "gift_card_request": [
        ("Quick Favor Needed", "Can you purchase 5 Amazon gift cards worth $200 each? Send me the redemption codes. Keep this confidential."),
        ("Need Gift Cards ASAP", "Buy 10 iTunes cards at $100 each for client gifts. Scratch and send me the pin codes. Don't tell anyone about this yet."),
        ("Urgent - Gift Cards for Event", "Purchase Google Play cards totaling $1000. Send the codes to this email. E-gift cards preferred."),
    ],
    "credential_request": [
        ("Your Account Has Been Suspended", "We detected unusual activity. Your email has been suspended. Sign in to verify and enter your username and password to restore access."),
        ("Verify Your Login Credentials", "Your account requires verification. Click here to confirm your credentials and reset your password immediately."),
        ("Security Alert - Action Required", "Account verification required. Provide your credentials to confirm your account or access will be terminated."),
    ],
    "sensitive_data_request": [
        ("Urgent: W-2 Forms Required", "We need W-2 tax forms for all employees along with the employee list and salary details. Finance team needs this by EOD."),
        ("Employee Records Request", "Please send the employee list with social security numbers and compensation details for our audit."),
        ("Payroll Data Needed", "Send us the payroll data including employee records and salary slips for compliance review."),
    ],
    "document_download": [
        ("Please Review Contract", "Please find your contract via DocuSign. Click to download the document and open the attachment to review. Download now."),
        ("Document Ready for Signature", "Your document is ready. Open attached file and download the PDF to complete your signature today."),
        ("Shared Document Notification", "A document has been shared with you on OneDrive. Click to download and review the attached file."),
    ],
    "link_click": [
        ("Verify Your Microsoft Account", "Your Microsoft 365 account requires attention. Click here to verify: http://microsoft-verify.suspicious.com. Confirm now."),
        ("Action Required: Click Below", "Click the link to update your account: http://bit.ly/2x9kF3q. Follow this link immediately."),
        ("Account Security Update", "Click on the link below to verify your identity: http://tinyurl.com/account-verify. Action required."),
    ],
    "urgent_callback": [
        ("URGENT: Account Will Be Closed", "Your account shows suspicious activity and will be frozen in 24 hours. Call us immediately at +1-800-555-0199."),
        ("Final Notice - Call Now", "This is your last warning. Dial this number immediately: +1-888-555-0123 to prevent account closure."),
        ("Call Back Urgently", "Please call now on +1-877-555-9999. Failure to respond within 24 hours will result in suspension."),
    ],
    "bank_detail_update": [
        ("Updated Banking Information", "We have updated our banking information effective immediately. Please update bank details with the new account number and routing number provided."),
        ("Important: New Bank Account", "Please update your records with our new banking information. Change payment details to the new routing number attached."),
        ("Vendor Bank Details Change", "Effective today, please update our banking in your system. New account details for all future payments are attached."),
    ],
    "legal_threat": [
        ("Notice of Legal Action", "Legal action will be filed against your organization. Our attorney has been instructed to file a lawsuit unless you respond within 48 hours."),
        ("Subpoena - Immediate Response", "You are hereby served with a court order. Failure to comply will result in legal proceedings and damages."),
        ("Final Legal Warning", "This is a violation notice. Legal proceedings will commence unless you take action immediately."),
    ],
    "executive_request": [
        ("Confidential - CEO Request", "This is on behalf of the CEO. The CEO has requested you handle this immediately. Keep this confidential, do not discuss with team."),
        ("From the Director - Urgent", "Per the director's instructions, process this payment before close of business. Leadership has directed this as top priority."),
        ("Executive Team Directive", "The president needs you to handle this confidential matter. Management has approved, bypass normal process."),
    ],
    "vpn_or_mfa_reset": [
        ("Approve Your MFA Reset", "A new device detected signing into your account. Approve the login by entering the 2FA code from your authenticator app."),
        ("VPN Access Verification", "Your VPN access requires verification. Provide your one-time password (OTP code) to our security team."),
        ("Security Token Reset", "Please approve sign-in request. Enter the 6-digit code from your authenticator to verify your device."),
    ],
    "meeting_request": [
        ("Urgent Meeting Invitation", "You have been invited to an urgent meeting. Join here: http://zoom-meeting.phishing.net/join. Click to join immediately."),
        ("Executive Video Conference", "Join the meeting now: http://teams-urgent-meeting.com. Meeting ID: 845-291-0022. Your presence is required."),
        ("Calendar Invite - Click to Join", "Urgent Zoom meeting. Join video conference here: http://meet.suspicious.com/conference. Join now."),
    ],
}

# Legitimate email samples
LEGITIMATE_SAMPLES = [
    ("Team Lunch This Friday", "Hi everyone, reminder about team lunch this Friday at 1pm. Let me know if you can make it!"),
    ("Weekly Standup Meeting", "Reminder about our weekly standup tomorrow at 10am. We'll discuss project updates and sprint planning."),
    ("Project Documentation", "I've uploaded the latest project docs to our shared drive. Please review and let me know if you have questions."),
    ("Happy Birthday!", "Happy birthday Sarah! Hope you have a wonderful day. We'll celebrate with cake at 3pm."),
    ("Coffee Chat Next Week", "Want to grab coffee next Tuesday? I'd love to catch up and hear about what you're working on."),
    ("Quarterly Report Ready", "The Q3 financial report is ready for review. PDF attached with all key metrics and analysis."),
    ("Thanks for Your Help", "Just wanted to say thanks for your help on the project yesterday. Really appreciate your input!"),
    ("Out of Office Next Week", "I'll be out of office next Monday through Wednesday. Please contact Jane for urgent matters."),
    ("Great Job on Presentation", "Your presentation today was excellent! The client was really impressed with the data analysis."),
    ("Lunch and Learn Session", "Reminder: Lunch and Learn session on AWS best practices this Thursday at noon in conference room B."),
    ("Team Building Event", "Save the date! Team building event next month on the 15th. More details to follow soon."),
    ("New Hire Announcement", "Please welcome our new team member Alex who joins us as Senior Developer starting Monday!"),
    ("Office Closed Holiday", "Reminder that the office will be closed next Friday for the holiday. Enjoy the long weekend!"),
    ("Survey: Team Feedback", "Please take 5 minutes to complete our team feedback survey. Your input helps us improve!"),
    ("Book Club Next Meeting", "Book club meets next Tuesday. We're discussing 'The Phoenix Project'. See you there!"),
]

def generate_csv(output_file, count=20, threats_only=False, legitimate_only=False):
    """Generate a CSV file with sample emails"""

    emails = []
    email_id = 1

    if threats_only:
        # Only threat emails
        while len(emails) < count:
            category = random.choice(list(THREAT_SAMPLES.keys()))
            subject, body = random.choice(THREAT_SAMPLES[category])
            emails.append({
                'id': email_id,
                'subject': subject,
                'body': body,
                'actual_category': category
            })
            email_id += 1

    elif legitimate_only:
        # Only legitimate emails
        while len(emails) < count:
            subject, body = random.choice(LEGITIMATE_SAMPLES)
            emails.append({
                'id': email_id,
                'subject': subject,
                'body': body,
                'actual_category': 'none'
            })
            email_id += 1

    else:
        # Mix of both (70% threats, 30% legitimate)
        threat_count = int(count * 0.7)
        legit_count = count - threat_count

        # Add threats
        for _ in range(threat_count):
            category = random.choice(list(THREAT_SAMPLES.keys()))
            subject, body = random.choice(THREAT_SAMPLES[category])
            emails.append({
                'id': email_id,
                'subject': subject,
                'body': body,
                'actual_category': category
            })
            email_id += 1

        # Add legitimate
        for _ in range(legit_count):
            subject, body = random.choice(LEGITIMATE_SAMPLES)
            emails.append({
                'id': email_id,
                'subject': subject,
                'body': body,
                'actual_category': 'none'
            })
            email_id += 1

    # Shuffle to mix threats and legitimate
    random.shuffle(emails)

    # Re-assign sequential IDs after shuffle
    for i, email in enumerate(emails, 1):
        email['id'] = i

    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'subject', 'body'])
        writer.writeheader()
        for email in emails:
            writer.writerow({
                'id': email['id'],
                'subject': email['subject'],
                'body': email['body']
            })

    # Print summary
    threat_count = sum(1 for e in emails if e['actual_category'] != 'none')
    print(f"✅ Generated {output_file}")
    print(f"   Total emails: {len(emails)}")
    print(f"   Threats: {threat_count} ({threat_count/len(emails)*100:.0f}%)")
    print(f"   Legitimate: {len(emails) - threat_count} ({(len(emails)-threat_count)/len(emails)*100:.0f}%)")

    # Show category breakdown
    category_counts = {}
    for email in emails:
        cat = email['actual_category']
        category_counts[cat] = category_counts.get(cat, 0) + 1

    print(f"\n   Category breakdown:")
    for cat, cnt in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"     {cat:25s}: {cnt:2d}")

def main():
    parser = argparse.ArgumentParser(description='Generate test CSV files with sample emails')
    parser.add_argument('-o', '--output', default='generated_emails.csv', help='Output CSV file')
    parser.add_argument('-c', '--count', type=int, default=20, help='Number of emails to generate')
    parser.add_argument('--threats-only', action='store_true', help='Generate only threat emails')
    parser.add_argument('--legitimate-only', action='store_true', help='Generate only legitimate emails')

    args = parser.parse_args()

    if args.threats_only and args.legitimate_only:
        print("ERROR: Cannot use both --threats-only and --legitimate-only")
        return

    generate_csv(args.output, args.count, args.threats_only, args.legitimate_only)

if __name__ == "__main__":
    main()

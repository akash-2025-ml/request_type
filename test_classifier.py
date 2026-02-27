#!/usr/bin/env python3
"""
Test script for Mailarmor Classifier
Run this after starting the server with: python3 mailarmor_classifier.py
"""

import requests
import json

# API endpoint
API_URL = "http://localhost:8000/classify"

# Test cases
test_emails = [
    {
        "name": "Invoice Payment Scam",
        "payload": {
            "subject": "Invoice #4521 Payment Due",
            "body": "Please pay the invoice attached. Amount due is $5,200. Transfer funds to bank details provided.",
            "include_debug": True
        }
    },
    {
        "name": "Gift Card Request",
        "payload": {
            "subject": "Need your help",
            "body": "Can you purchase 5 iTunes gift cards worth $200 each? Send me the codes. Don't tell anyone.",
            "include_debug": True
        }
    },
    {
        "name": "Credential Phishing",
        "payload": {
            "subject": "Account Suspended",
            "body": "Your email has been suspended due to unusual activity. Click here to verify and enter your username and password.",
            "include_debug": True
        }
    },
    {
        "name": "Wire Transfer",
        "payload": {
            "subject": "Urgent Wire Needed",
            "body": "Please initiate a wire transfer of $45,000 immediately to account number 123456. Use SWIFT code ABCD1234.",
            "include_debug": True
        }
    },
    {
        "name": "Legitimate Email",
        "payload": {
            "subject": "Team Lunch Friday",
            "body": "Hi everyone, reminder about team lunch this Friday at 1pm. Please let me know if you can make it!",
            "include_debug": True
        }
    }
]

def test_email(name, payload):
    """Send a test email to the classifier"""
    print(f"\n{'='*70}")
    print(f"Testing: {name}")
    print(f"{'='*70}")
    print(f"Subject: {payload['subject']}")
    print(f"Body: {payload['body'][:80]}...")

    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        result = response.json()

        print(f"\n🎯 RESULT:")
        print(f"  Request Type: {result['request_type']}")
        print(f"  Confidence Score: {result['confidence_score']}")
        print(f"  Runner-up: {result.get('runner_up', 'None')}")
        print(f"  Runner-up Score: {result.get('runner_up_score', 0)}")

        if result.get('matched_phrases'):
            print(f"\n  Matched Phrases:")
            for phrase in result['matched_phrases'][:5]:  # Show first 5
                print(f"    • {phrase}")

        if payload.get('include_debug') and result.get('all_scores'):
            print(f"\n  All Category Scores:")
            sorted_scores = sorted(result['all_scores'].items(), key=lambda x: x[1], reverse=True)
            for category, score in sorted_scores[:5]:  # Top 5
                print(f"    {category:25s}: {score:3d}")

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server. Is it running?")
        print("   Start it with: python3 mailarmor_classifier.py")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("Mailarmor Classifier - Test Script")
    print("="*70)
    print(f"Testing {len(test_emails)} email samples...")

    for test in test_emails:
        test_email(test['name'], test['payload'])

    print("\n" + "="*70)
    print("Testing complete!")
    print("="*70 + "\n")

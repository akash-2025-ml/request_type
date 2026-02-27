#!/usr/bin/env python3
"""Simple one-liner test - just change the email text and run"""

import requests

# Change this to test different emails
email = {
    "subject": "Urgent Payment Required",
    "body": "Please wire transfer $10,000 to our new bank account immediately. Account details attached.",
    "include_debug": True
}

try:
    response = requests.post("http://localhost:8000/classify", json=email)
    result = response.json()

    print(f"\n🚨 Detection Result: {result['request_type'].upper()}")
    print(f"📊 Confidence: {result['confidence_score']}/100")
    print(f"\n✅ Matched patterns:")
    for phrase in result.get('matched_phrases', []):
        print(f"   • {phrase}")

except requests.exceptions.ConnectionError:
    print("❌ Server not running! Start it with: python3 mailarmor_classifier.py")

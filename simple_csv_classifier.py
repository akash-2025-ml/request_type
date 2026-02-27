#!/usr/bin/env python3
"""
Simple CSV Email Classifier
============================
Basic script to classify emails from CSV - no fancy features, just results.

Usage:
    python3 simple_csv_classifier.py input.csv output.csv
"""

import csv
import sys
import requests

def classify_emails_from_csv(input_file, output_file):
    """Read CSV, classify emails, save results"""

    # Check server
    try:
        requests.get("http://localhost:8000/health", timeout=2)
    except:
        print("ERROR: Server not running! Start with: python3 mailarmor_classifier.py")
        sys.exit(1)

    # Read input CSV
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        emails = list(reader)

    print(f"Found {len(emails)} emails. Classifying...")

    # Classify each email
    results = []
    for i, email in enumerate(emails, 1):
        subject = email.get('subject', '')
        body = email.get('body', '')

        # Call API
        response = requests.post(
            "http://localhost:8000/classify",
            json={"subject": subject, "body": body, "include_debug": False}
        )
        result = response.json()

        # Store result
        results.append({
            'id': email.get('id', i),
            'subject': subject,
            'request_type': result['request_type'],
            'confidence_score': result['confidence_score'],
            'runner_up': result.get('runner_up', ''),
        })

        print(f"  [{i}/{len(emails)}] {result['request_type']} (score: {result['confidence_score']})")

    # Save results
    print(f"\nSaving results to {output_file}...")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'subject', 'request_type', 'confidence_score', 'runner_up'])
        writer.writeheader()
        writer.writerows(results)

    # Print summary
    threats = sum(1 for r in results if r['request_type'] != 'none')
    print(f"\nDone! Processed {len(results)} emails")
    print(f"Threats found: {threats}")
    print(f"Clean emails: {len(results) - threats}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 simple_csv_classifier.py input.csv output.csv")
        sys.exit(1)

    classify_emails_from_csv(sys.argv[1], sys.argv[2])

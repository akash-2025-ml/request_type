#!/usr/bin/env python3
"""
Mailarmor CSV Classifier
========================
Read emails from CSV file, classify them, and save results.

CSV Format Required:
- Must have 'subject' and 'body' columns
- Optional: 'email_id' or 'id' column for tracking

Usage:
    python3 classify_from_csv.py input_emails.csv
    python3 classify_from_csv.py input_emails.csv --output results.csv
    python3 classify_from_csv.py input_emails.csv --debug
"""

import csv
import sys
import requests
import argparse
from datetime import datetime
from typing import List, Dict
import time

# API Configuration
API_URL = "http://localhost:8000/classify"
BULK_API_URL = "http://localhost:8000/classify/bulk"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def check_server():
    """Check if the classifier server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            return True
    except:
        pass
    return False

def read_csv(file_path: str) -> List[Dict]:
    """Read emails from CSV file"""
    print(f"{Colors.BLUE}📂 Reading CSV file: {file_path}{Colors.END}")

    emails = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # Validate required columns
            if 'body' not in reader.fieldnames:
                print(f"{Colors.RED}❌ ERROR: CSV must have 'body' column{Colors.END}")
                sys.exit(1)

            for i, row in enumerate(reader):
                email = {
                    'id': row.get('id', row.get('email_id', i+1)),
                    'subject': row.get('subject', ''),
                    'body': row.get('body', ''),
                }
                emails.append(email)

        print(f"{Colors.GREEN}✅ Loaded {len(emails)} emails{Colors.END}\n")
        return emails

    except FileNotFoundError:
        print(f"{Colors.RED}❌ ERROR: File not found: {file_path}{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}❌ ERROR reading CSV: {e}{Colors.END}")
        sys.exit(1)

def classify_single(email: Dict, include_debug: bool = False) -> Dict:
    """Classify a single email"""
    payload = {
        "subject": email.get('subject', ''),
        "body": email.get('body', ''),
        "include_debug": include_debug
    }

    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {
            "request_type": "error",
            "confidence_score": 0,
            "error": str(e)
        }

def classify_bulk(emails: List[Dict], include_debug: bool = False) -> List[Dict]:
    """Classify multiple emails using bulk endpoint (max 100)"""
    payload = {
        "emails": [
            {
                "subject": email.get('subject', ''),
                "body": email.get('body', ''),
                "include_debug": include_debug
            }
            for email in emails
        ]
    }

    try:
        response = requests.post(BULK_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()['results']
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Bulk API failed, falling back to single requests: {e}{Colors.END}")
        return None

def process_emails(emails: List[Dict], include_debug: bool = False, use_bulk: bool = True):
    """Process and classify all emails"""
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}Starting Classification{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}\n")

    results = []

    # Try bulk processing first (if enabled and <= 100 emails)
    if use_bulk and len(emails) <= 100:
        print(f"{Colors.BLUE}🚀 Using bulk classification for faster processing...{Colors.END}\n")
        bulk_results = classify_bulk(emails, include_debug)

        if bulk_results:
            for i, (email, result) in enumerate(zip(emails, bulk_results)):
                result['id'] = email['id']
                result['subject'] = email['subject']
                result['body_preview'] = email['body'][:100]
                results.append(result)
                print_result(i+1, len(emails), result)
            return results

    # Fallback to single requests
    print(f"{Colors.BLUE}📧 Processing emails one by one...{Colors.END}\n")
    for i, email in enumerate(emails):
        result = classify_single(email, include_debug)
        result['id'] = email['id']
        result['subject'] = email['subject']
        result['body_preview'] = email['body'][:100]
        results.append(result)

        print_result(i+1, len(emails), result)

        # Small delay to avoid overwhelming server
        if i < len(emails) - 1:
            time.sleep(0.1)

    return results

def print_result(current: int, total: int, result: Dict):
    """Print a single classification result"""
    email_id = result.get('id', current)
    request_type = result.get('request_type', 'unknown')
    score = result.get('confidence_score', 0)
    subject = result.get('subject', 'No subject')

    # Color code based on threat type
    if request_type == 'none':
        color = Colors.GREEN
        icon = '✅'
    elif request_type == 'error':
        color = Colors.RED
        icon = '❌'
    else:
        color = Colors.RED
        icon = '🚨'

    print(f"[{current}/{total}] Email ID: {email_id}")
    print(f"  Subject: {subject[:60]}{'...' if len(subject) > 60 else ''}")
    print(f"  {color}{icon} Threat: {request_type.upper()}{Colors.END}")
    print(f"  📊 Score: {score}")

    if result.get('runner_up'):
        print(f"  🥈 Runner-up: {result['runner_up']} ({result.get('runner_up_score', 0)})")

    if result.get('matched_phrases'):
        print(f"  🎯 Matches: {', '.join(result['matched_phrases'][:3])}")

    print()

def save_results(results: List[Dict], output_file: str):
    """Save classification results to CSV"""
    print(f"\n{Colors.BLUE}💾 Saving results to: {output_file}{Colors.END}")

    fieldnames = [
        'id',
        'subject',
        'body_preview',
        'request_type',
        'confidence_score',
        'runner_up',
        'runner_up_score',
        'matched_phrases',
        'timestamp'
    ]

    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for result in results:
                row = {
                    'id': result.get('id', ''),
                    'subject': result.get('subject', ''),
                    'body_preview': result.get('body_preview', ''),
                    'request_type': result.get('request_type', ''),
                    'confidence_score': result.get('confidence_score', 0),
                    'runner_up': result.get('runner_up', ''),
                    'runner_up_score': result.get('runner_up_score', 0),
                    'matched_phrases': '; '.join(result.get('matched_phrases', [])),
                    'timestamp': datetime.now().isoformat()
                }
                writer.writerow(row)

        print(f"{Colors.GREEN}✅ Results saved successfully{Colors.END}")
    except Exception as e:
        print(f"{Colors.RED}❌ ERROR saving results: {e}{Colors.END}")

def print_summary(results: List[Dict]):
    """Print summary statistics"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}Summary Statistics{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}\n")

    # Count by category
    category_counts = {}
    total_threats = 0

    for result in results:
        category = result.get('request_type', 'unknown')
        category_counts[category] = category_counts.get(category, 0) + 1
        if category != 'none':
            total_threats += 1

    print(f"📊 Total Emails Processed: {len(results)}")
    print(f"🚨 Threats Detected: {total_threats} ({total_threats/len(results)*100:.1f}%)")
    print(f"✅ Clean Emails: {category_counts.get('none', 0)} ({category_counts.get('none', 0)/len(results)*100:.1f}%)\n")

    print("Threat Breakdown:")
    print("-" * 50)

    # Sort by count
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)

    for category, count in sorted_categories:
        percentage = count / len(results) * 100
        bar_length = int(percentage / 2)  # Scale for display
        bar = '█' * bar_length

        if category == 'none':
            color = Colors.GREEN
        else:
            color = Colors.RED

        print(f"{category:25s} {color}{bar}{Colors.END} {count:3d} ({percentage:5.1f}%)")

    print()

def main():
    parser = argparse.ArgumentParser(
        description='Classify emails from CSV file using Mailarmor classifier',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 classify_from_csv.py emails.csv
  python3 classify_from_csv.py emails.csv --output results.csv
  python3 classify_from_csv.py emails.csv --debug --no-bulk
        """
    )

    parser.add_argument('input_file', help='Input CSV file with emails')
    parser.add_argument('-o', '--output', help='Output CSV file for results', default=None)
    parser.add_argument('-d', '--debug', action='store_true', help='Include debug information')
    parser.add_argument('--no-bulk', action='store_true', help='Disable bulk processing')

    args = parser.parse_args()

    # Check if server is running
    if not check_server():
        print(f"{Colors.RED}❌ ERROR: Classifier server is not running!{Colors.END}")
        print(f"{Colors.YELLOW}Start it with: python3 mailarmor_classifier.py{Colors.END}")
        sys.exit(1)

    print(f"{Colors.GREEN}✅ Server is running{Colors.END}\n")

    # Read emails from CSV
    emails = read_csv(args.input_file)

    # Process emails
    results = process_emails(emails, include_debug=args.debug, use_bulk=not args.no_bulk)

    # Print summary
    print_summary(results)

    # Save results if output file specified
    if args.output:
        save_results(results, args.output)
    else:
        # Auto-generate output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"classification_results_{timestamp}.csv"
        save_results(results, output_file)

    print(f"\n{Colors.GREEN}{Colors.BOLD}✅ Classification Complete!{Colors.END}\n")

if __name__ == "__main__":
    main()

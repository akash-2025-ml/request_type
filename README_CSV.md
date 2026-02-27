# 📧 CSV Email Classification - Complete Guide

Process bulk emails from CSV files using the Mailarmor classifier.

---

## 🚀 Quick Start (3 Steps)

```bash
# Step 1: Start the classifier server
python3 mailarmor_classifier.py

# Step 2: In another terminal, install requests library
pip install requests

# Step 3: Classify emails from CSV
python3 classify_from_csv.py sample_emails.csv
```

**Done!** Results are automatically saved to `classification_results_[timestamp].csv`

---

## 📁 Files Created for You

| File | Purpose |
|------|---------|
| **`classify_from_csv.py`** | Full-featured CSV classifier with colors & stats |
| **`simple_csv_classifier.py`** | Basic CSV classifier (no fancy features) |
| **`sample_emails.csv`** | 20 pre-made test emails (ready to use!) |
| **`template.csv`** | Empty CSV template for your data |
| **`generate_test_csv.py`** | Generate random test emails |
| **`CSV_USAGE.md`** | Detailed documentation |

---

## 📊 Your CSV File Format

**Required columns:**
- `body` - Email body text (REQUIRED)
- `subject` - Email subject (recommended)
- `id` - Email identifier (optional)

**Example:**
```csv
id,subject,body
1,Urgent Payment,Please wire $50000 immediately to account 123456
2,Team Meeting,Reminder about our weekly sync tomorrow at 10am
```

---

## 💻 Usage Examples

### Example 1: Basic Usage
```bash
python3 classify_from_csv.py sample_emails.csv
```

**Output:**
```
✅ Server is running

📂 Reading CSV file: sample_emails.csv
✅ Loaded 20 emails

🚀 Using bulk classification for faster processing...

[1/20] Email ID: 1
  Subject: Invoice #4521 Payment Due
  🚨 Threat: INVOICE_PAYMENT
  📊 Score: 19

[2/20] Email ID: 2
  Subject: Team Lunch This Friday
  ✅ Threat: NONE
  📊 Score: 0

...

📊 Total Emails Processed: 20
🚨 Threats Detected: 13 (65.0%)
✅ Clean Emails: 7 (35.0%)

💾 Saving results to: classification_results_20260227_143022.csv
```

---

### Example 2: Custom Output File
```bash
python3 classify_from_csv.py my_emails.csv --output results.csv
```

---

### Example 3: Debug Mode (See All Scores)
```bash
python3 classify_from_csv.py sample_emails.csv --debug
```

---

### Example 4: Simple Script (No Colors)
```bash
python3 simple_csv_classifier.py input.csv output.csv
```

**Output:**
```
Reading input.csv...
Found 20 emails. Classifying...
  [1/20] invoice_payment (score: 19)
  [2/20] none (score: 0)
  [3/20] wire_transfer (score: 23)
  ...

Done! Processed 20 emails
Threats found: 13
Clean emails: 7
```

---

### Example 5: Generate Test Data
```bash
# Generate 50 random test emails
python3 generate_test_csv.py --count 50 --output test50.csv

# Generate only threat emails
python3 generate_test_csv.py --threats-only --count 30

# Generate only legitimate emails
python3 generate_test_csv.py --legitimate-only --count 20
```

---

## 📋 Output CSV Format

Results include:

| Column | Description | Example |
|--------|-------------|---------|
| `id` | Email ID | 1 |
| `subject` | Subject line | "Urgent Payment" |
| `body_preview` | First 100 chars | "Please wire transfer..." |
| `request_type` | Threat category | "wire_transfer" |
| `confidence_score` | Confidence (0-100+) | 23 |
| `runner_up` | 2nd likely category | "invoice_payment" |
| `runner_up_score` | Runner-up score | 12 |
| `matched_phrases` | Detected phrases | "[primary] 'wire transfer'" |
| `timestamp` | Processing time | "2026-02-27T14:30:22" |

**Example output CSV:**
```csv
id,subject,request_type,confidence_score,runner_up,runner_up_score
1,Urgent Payment,wire_transfer,23,invoice_payment,12
2,Team Meeting,none,0,,0
3,Gift Card Request,gift_card_request,26,executive_request,8
```

---

## 🎯 Real-World Workflow

### Scenario: Classify 100 Emails from Your Inbox

**Step 1: Export emails to CSV**
```csv
id,subject,body
1,Subject line 1,Email body text goes here...
2,Subject line 2,Another email body...
...
```

**Step 2: Start classifier**
```bash
python3 mailarmor_classifier.py
```

**Step 3: Process emails**
```bash
python3 classify_from_csv.py inbox_export.csv --output threats_detected.csv
```

**Step 4: Review results**
```bash
# View threats only
grep -v "none" threats_detected.csv

# Count by category
cut -d',' -f4 threats_detected.csv | sort | uniq -c
```

---

## 🛠️ Command Reference

### Full-Featured Script

```bash
python3 classify_from_csv.py <input.csv> [options]

Options:
  -o, --output FILE     Output CSV file (auto-generated if omitted)
  -d, --debug          Include all category scores
  --no-bulk            Process one-by-one instead of bulk API
  -h, --help           Show help message
```

### Simple Script

```bash
python3 simple_csv_classifier.py <input.csv> <output.csv>
```

### Test Data Generator

```bash
python3 generate_test_csv.py [options]

Options:
  -o, --output FILE     Output file (default: generated_emails.csv)
  -c, --count N        Number of emails (default: 20)
  --threats-only       Generate only threats
  --legitimate-only    Generate only legitimate emails
```

---

## ⚡ Performance

| Email Count | Method | Speed |
|-------------|--------|-------|
| 1-100 | Bulk API | ~1-2 seconds |
| 100+ | Batched | ~0.1s per email |
| 1000+ | Split files | Process in parallel |

**Tip:** For 1000+ emails, split into multiple CSV files and run in parallel:
```bash
split -l 100 large_file.csv chunk_
python3 classify_from_csv.py chunk_aa &
python3 classify_from_csv.py chunk_ab &
python3 classify_from_csv.py chunk_ac &
```

---

## ❌ Troubleshooting

### "Server not running" Error
**Problem:** Classifier API is not running

**Solution:**
```bash
# Terminal 1: Start server
python3 mailarmor_classifier.py

# Terminal 2: Run classifier
python3 classify_from_csv.py input.csv
```

---

### "CSV must have 'body' column"
**Problem:** CSV missing required column

**Solution:** Ensure CSV has `body` column:
```csv
subject,body
Test,This is the body
```

---

### "ModuleNotFoundError: No module named 'requests'"
**Problem:** Missing dependency

**Solution:**
```bash
pip install requests
```

---

### Empty Results (all "none")
**Problem:** Emails don't match any threat patterns

**Possible causes:**
- Emails are actually legitimate
- Different language/phrasing than rules
- Very short email bodies

**Test with known phishing:**
```bash
python3 classify_from_csv.py sample_emails.csv
```

---

## 📖 Category Reference

| Category | Description | Example |
|----------|-------------|---------|
| `invoice_payment` | Fake invoice scam | "Pay invoice #123, bank details attached" |
| `wire_transfer` | Wire transfer fraud | "Wire $50k to account 456789 immediately" |
| `gift_card_request` | Gift card scam | "Buy 10 iTunes cards, send codes" |
| `credential_request` | Password phishing | "Verify your login credentials here" |
| `sensitive_data_request` | Data theft | "Send employee W-2 forms and payroll" |
| `document_download` | Malicious attachment | "Download this DocuSign document" |
| `link_click` | Phishing link | "Click here to verify account" |
| `urgent_callback` | Phone scam | "Call +1-800-555-0000 immediately" |
| `bank_detail_update` | Bank fraud | "Updated our bank account, please note" |
| `legal_threat` | Legal intimidation | "Lawsuit will be filed in 48 hours" |
| `executive_request` | CEO fraud | "CEO needs this done confidentially" |
| `vpn_or_mfa_reset` | MFA bypass | "Enter your 2FA code to verify" |
| `meeting_request` | Fake meeting | "Join urgent Zoom meeting now" |
| `none` | Legitimate | "Team lunch this Friday at 1pm" |

---

## 🔧 Customization

Want to modify the scripts? Here's the minimal code:

```python
import csv
import requests

# Read CSV
with open('emails.csv') as f:
    emails = list(csv.DictReader(f))

# Classify each email
results = []
for email in emails:
    response = requests.post(
        "http://localhost:8000/classify",
        json={
            "subject": email.get('subject', ''),
            "body": email['body']
        }
    )
    result = response.json()
    results.append({
        'id': email.get('id'),
        'threat': result['request_type'],
        'score': result['confidence_score']
    })

# Save results
with open('output.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, ['id', 'threat', 'score'])
    writer.writeheader()
    writer.writerows(results)
```

---

## 📞 Next Steps

- **Test with sample data:** `python3 classify_from_csv.py sample_emails.csv`
- **Use your own data:** Prepare CSV with `subject` and `body` columns
- **Generate test data:** `python3 generate_test_csv.py`
- **Read detailed docs:** `CSV_USAGE.md`
- **Understand the API:** `USAGE.md`

---

**Ready to classify?** Run: `python3 classify_from_csv.py sample_emails.csv`

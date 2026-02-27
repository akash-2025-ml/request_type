# CSV Email Classification Guide

## Quick Start

### 1. Start the Server
```bash
python3 mailarmor_classifier.py
```

### 2. Classify Emails from CSV
```bash
# Basic usage
python3 classify_from_csv.py sample_emails.csv

# Specify output file
python3 classify_from_csv.py sample_emails.csv --output results.csv

# Include debug information
python3 classify_from_csv.py sample_emails.csv --debug
```

---

## CSV File Format

Your CSV file must have these columns:

| Column | Required | Description |
|--------|----------|-------------|
| `body` | ✅ Yes | Email body text |
| `subject` | ⚠️ Recommended | Email subject line |
| `id` or `email_id` | ❌ Optional | Unique identifier |

### Example CSV:

```csv
id,subject,body
1,Urgent Payment,Please wire transfer $50000 immediately to our new account
2,Team Meeting,Reminder about our weekly sync tomorrow at 10am
3,Gift Card Request,Can you buy 10 Amazon gift cards and send me the codes?
```

### Sample Files Included:

- **`template.csv`** - Empty template to fill in
- **`sample_emails.csv`** - 20 pre-filled test emails (mix of threats and legitimate)

---

## Available Scripts

### Option 1: Full-Featured Script (Recommended)

**`classify_from_csv.py`** - Comprehensive with colors, summary, and statistics

```bash
# Basic usage
python3 classify_from_csv.py input.csv

# Custom output file
python3 classify_from_csv.py input.csv --output my_results.csv

# Include all category scores (debug mode)
python3 classify_from_csv.py input.csv --debug

# Process one-by-one (disable bulk API)
python3 classify_from_csv.py input.csv --no-bulk
```

**Features:**
- ✅ Colored terminal output
- ✅ Progress tracking
- ✅ Summary statistics with charts
- ✅ Bulk processing (up to 100 emails at once)
- ✅ Auto-generates output filename if not specified
- ✅ Shows matched phrases

---

### Option 2: Simple Script

**`simple_csv_classifier.py`** - Minimal, no dependencies

```bash
python3 simple_csv_classifier.py input.csv output.csv
```

**Features:**
- ✅ No external dependencies beyond requests
- ✅ Simple output
- ✅ Easy to understand and modify

---

## Output Format

Results are saved as CSV with these columns:

| Column | Description |
|--------|-------------|
| `id` | Original email ID |
| `subject` | Email subject |
| `body_preview` | First 100 characters of body |
| `request_type` | Detected threat category |
| `confidence_score` | Confidence score (0-100+) |
| `runner_up` | Second-most likely category |
| `runner_up_score` | Runner-up score |
| `matched_phrases` | Phrases that triggered detection |
| `timestamp` | When classification occurred |

### Example Output:

```csv
id,subject,request_type,confidence_score,runner_up,runner_up_score
1,Urgent Payment,wire_transfer,23,invoice_payment,12
2,Team Meeting,none,0,,0
3,Gift Card Request,gift_card_request,26,executive_request,8
```

---

## Example: Complete Workflow

```bash
# Step 1: Start the classifier server
python3 mailarmor_classifier.py

# In another terminal...

# Step 2: Test with sample data
python3 classify_from_csv.py sample_emails.csv

# Step 3: Use your own data
# First, prepare your CSV file
cat > my_emails.csv << 'EOF'
id,subject,body
1,Urgent Request,Please send $10000 via wire transfer today
2,Weekly Report,Attached is the weekly sales report for review
EOF

# Step 4: Classify your emails
python3 classify_from_csv.py my_emails.csv --output my_results.csv

# Step 5: View results
cat my_results.csv
```

---

## Sample Output (Terminal)

```
📂 Reading CSV file: sample_emails.csv
✅ Loaded 20 emails

================================================================================
Starting Classification
================================================================================

🚀 Using bulk classification for faster processing...

[1/20] Email ID: 1
  Subject: Invoice #4521 Payment Due
  🚨 Threat: INVOICE_PAYMENT
  📊 Score: 19
  🥈 Runner-up: wire_transfer (7)

[2/20] Email ID: 2
  Subject: Team Lunch This Friday
  ✅ Threat: NONE
  📊 Score: 0

... (more results) ...

================================================================================
Summary Statistics
================================================================================

📊 Total Emails Processed: 20
🚨 Threats Detected: 13 (65.0%)
✅ Clean Emails: 7 (35.0%)

Threat Breakdown:
--------------------------------------------------
none                      ███████               7 ( 35.0%)
invoice_payment           ██                    2 ( 10.0%)
wire_transfer             ██                    2 ( 10.0%)
gift_card_request         █                     1 (  5.0%)
credential_request        █                     1 (  5.0%)
...

💾 Saving results to: classification_results_20260227_143022.csv
✅ Results saved successfully

✅ Classification Complete!
```

---

## Troubleshooting

### "Server not running" Error
```bash
# Start the server first
python3 mailarmor_classifier.py

# Then run classifier in another terminal
python3 classify_from_csv.py input.csv
```

### "CSV must have 'body' column" Error
Make sure your CSV has a column named `body`. Example:
```csv
subject,body
Test Email,This is the email body text
```

### "ModuleNotFoundError: No module named 'requests'"
```bash
pip install requests
```

### Large CSV Files (>100 emails)
The script automatically handles large files:
- Bulk API is used for ≤100 emails
- For >100 emails, it processes in batches
- Use `--no-bulk` flag to process one-by-one

---

## Performance Tips

1. **Use bulk processing** (default for ≤100 emails)
2. **Run locally** - API calls over network are slower
3. **Filter before classifying** - Only classify suspicious emails
4. **Batch large datasets** - Split 1000s of emails into smaller files

---

## Advanced: Custom Processing

Want to modify the script? Here's the core logic:

```python
import csv
import requests

# Read CSV
with open('emails.csv') as f:
    emails = list(csv.DictReader(f))

# Classify each
for email in emails:
    response = requests.post(
        "http://localhost:8000/classify",
        json={
            "subject": email['subject'],
            "body": email['body']
        }
    )
    result = response.json()
    print(f"{email['id']}: {result['request_type']}")
```

---

## Need More Help?

- Check the main documentation: `USAGE.md`
- View API documentation: http://localhost:8000/docs
- Test individual emails first: `python3 simple_test.py`

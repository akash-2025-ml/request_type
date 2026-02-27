# 🚀 QUICKSTART - CSV Email Classification

## ⚡ 30-Second Start

```bash
# Terminal 1: Start server
python3 mailarmor_classifier.py

# Terminal 2: Classify emails
pip install requests
python3 classify_from_csv.py sample_emails.csv
```

**Done!** Check `classification_results_*.csv` for results.

---

## 📦 What You Got

### 🔧 Main Scripts

| File | Use Case | Command |
|------|----------|---------|
| **`classify_from_csv.py`** | Best option - full features | `python3 classify_from_csv.py input.csv` |
| **`simple_csv_classifier.py`** | Minimal version | `python3 simple_csv_classifier.py in.csv out.csv` |
| **`generate_test_csv.py`** | Create test data | `python3 generate_test_csv.py --count 50` |

### 📄 Sample Files

| File | Description |
|------|-------------|
| **`sample_emails.csv`** | 20 ready-to-test emails (mix of threats & legitimate) |
| **`template.csv`** | Empty template for your own data |

### 📚 Documentation

| File | Content |
|------|---------|
| **`README_CSV.md`** | Complete guide (read this first!) |
| **`CSV_USAGE.md`** | Detailed documentation |
| **`USAGE.md`** | General API usage |

---

## 🎯 Common Tasks

### Task 1: Test with Sample Data
```bash
python3 classify_from_csv.py sample_emails.csv
```

### Task 2: Use Your Own CSV
```bash
# 1. Create CSV with 'subject' and 'body' columns
cat > my_emails.csv << 'EOF'
subject,body
Urgent Payment,Please wire $10000 immediately
Team Meeting,Weekly sync tomorrow at 10am
EOF

# 2. Classify
python3 classify_from_csv.py my_emails.csv --output results.csv
```

### Task 3: Generate Random Test Emails
```bash
# 100 random emails
python3 generate_test_csv.py --count 100 --output test.csv

# Then classify them
python3 classify_from_csv.py test.csv
```

### Task 4: Debug Mode (See All Details)
```bash
python3 classify_from_csv.py sample_emails.csv --debug
```

---

## 📋 CSV Format Required

**Minimum:**
```csv
body
Please wire $50000 to account 123456 immediately
Team lunch this Friday at 1pm
```

**Recommended:**
```csv
subject,body
Urgent Payment,Please wire $50000 to account 123456
Team Lunch,Team lunch Friday at 1pm
```

**With ID:**
```csv
id,subject,body
1,Urgent Payment,Please wire $50000 to account 123456
2,Team Lunch,Team lunch Friday at 1pm
```

---

## 📊 What You Get Back

```csv
id,subject,request_type,confidence_score,runner_up
1,Urgent Payment,wire_transfer,23,invoice_payment
2,Team Lunch,none,0,
```

**Threat categories detected:**
- `invoice_payment` - Fake invoice
- `wire_transfer` - Money transfer scam
- `gift_card_request` - Gift card fraud
- `credential_request` - Password phishing
- `link_click` - Phishing link
- `urgent_callback` - Phone scam
- ...and 8 more (14 total)
- `none` - Legitimate email

---

## 💡 Pro Tips

1. **Start server first** - Always run `python3 mailarmor_classifier.py` before classifying
2. **Use sample data first** - Test with `sample_emails.csv` before your own data
3. **Bulk is faster** - Automatically used for ≤100 emails
4. **Check output** - Results auto-saved to `classification_results_[timestamp].csv`

---

## ❌ If Something Goes Wrong

**"Server not running"**
```bash
# Start server in another terminal
python3 mailarmor_classifier.py
```

**"No module named 'requests'"**
```bash
pip install requests
```

**"CSV must have 'body' column"**
```bash
# Make sure your CSV has 'body' column
head -1 your_file.csv  # Should show "body" somewhere
```

---

## 🎓 Examples

### Example 1: Quick Test
```bash
python3 classify_from_csv.py sample_emails.csv
```

**Output:**
```
✅ Loaded 20 emails
🚨 Threats Detected: 13 (65.0%)
✅ Clean Emails: 7 (35.0%)
💾 Results saved to: classification_results_20260227_143022.csv
```

### Example 2: Your Data
```bash
# Create your CSV
echo "subject,body" > my_emails.csv
echo "Payment,Pay invoice attached" >> my_emails.csv
echo "Meeting,Team sync tomorrow" >> my_emails.csv

# Classify
python3 classify_from_csv.py my_emails.csv

# View results
cat classification_results_*.csv
```

### Example 3: Generate & Classify
```bash
# Generate 50 test emails
python3 generate_test_csv.py --count 50

# Classify them
python3 classify_from_csv.py generated_emails.csv
```

---

## 📞 Need More Help?

- **Complete guide:** `README_CSV.md`
- **API documentation:** Open http://localhost:8000/docs (after starting server)
- **Detailed usage:** `CSV_USAGE.md`

---

## ✅ Checklist

- [ ] Server running? (`python3 mailarmor_classifier.py`)
- [ ] Requests installed? (`pip install requests`)
- [ ] CSV has 'body' column?
- [ ] Ready to classify? (`python3 classify_from_csv.py sample_emails.csv`)

**That's it! You're ready to go!** 🎉

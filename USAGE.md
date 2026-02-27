# Mailarmor Classifier - Usage Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install fastapi uvicorn pydantic
```

### 2. Start the Server
```bash
python3 mailarmor_classifier.py
```

Server runs at: **http://localhost:8000**

---

## Testing Methods

### Method 1: Python Test Script (Easiest)
```bash
# Install requests library
pip install requests

# Run comprehensive tests
python3 test_classifier.py

# Or run simple test
python3 simple_test.py
```

### Method 2: Browser Interface
Open in browser:
- **http://localhost:8000/docs** - Interactive API testing
- **http://localhost:8000/samples** - Get example payloads
- **http://localhost:8000/categories** - List all threat types

### Method 3: cURL Commands

**Test phishing email:**
```bash
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Urgent Payment",
    "body": "Please wire transfer $50,000 immediately",
    "include_debug": true
  }'
```

**Test legitimate email:**
```bash
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Team Meeting",
    "body": "Reminder about our weekly sync tomorrow at 10am",
    "include_debug": false
  }'
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/classify` | POST | Classify single email |
| `/classify/bulk` | POST | Classify up to 100 emails |
| `/categories` | GET | List all threat categories |
| `/samples` | GET | Get sample test payloads |
| `/health` | GET | Server health check |

---

## Request Format

```json
{
  "subject": "Email subject line",
  "body": "Email body content",
  "include_debug": true
}
```

**Parameters:**
- `subject` (optional): Email subject line
- `body` (required): Email body text
- `include_debug` (optional): Include scores for all categories

---

## Response Format

```json
{
  "request_type": "wire_transfer",
  "confidence_score": 23,
  "runner_up": "invoice_payment",
  "runner_up_score": 15,
  "matched_phrases": [
    "[primary] 'wire transfer'",
    "[support] 'immediately'"
  ],
  "all_scores": {
    "wire_transfer": 23,
    "invoice_payment": 15,
    ...
  }
}
```

---

## Threat Categories Detected

1. **invoice_payment** - Fake invoice payment requests
2. **wire_transfer** - Direct money transfer scams
3. **gift_card_request** - Gift card purchase scams
4. **credential_request** - Password/login phishing
5. **sensitive_data_request** - HR/tax/payroll data theft
6. **document_download** - Malicious file download
7. **link_click** - Suspicious link clicking
8. **urgent_callback** - Urgent phone call scams
9. **bank_detail_update** - Bank account change fraud
10. **invoice_verification** - Fake invoice approval
11. **legal_threat** - Legal intimidation scams
12. **executive_request** - CEO/executive impersonation
13. **vpn_or_mfa_reset** - MFA/VPN credential theft
14. **meeting_request** - Fake meeting invites
15. **none** - No threat detected

---

## Example Outputs

### Phishing Detected
```
🚨 Detection Result: WIRE_TRANSFER
📊 Confidence: 23/100

✅ Matched patterns:
   • [primary] 'wire transfer'
   • [primary] 'initiate a transfer'
   • [support] 'immediately'
```

### Legitimate Email
```
🚨 Detection Result: NONE
📊 Confidence: 0/100

✅ Matched patterns:
   (none)
```

---

## Bulk Classification

Test multiple emails at once:

```bash
curl -X POST "http://localhost:8000/classify/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "emails": [
      {"subject": "Invoice", "body": "Pay the invoice attached"},
      {"subject": "Meeting", "body": "Team lunch Friday at 1pm"}
    ]
  }'
```

Max: **100 emails per request**

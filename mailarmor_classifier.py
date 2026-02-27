"""
Mailarmor - Rule-Based Email Request Type Classifier
=====================================================
FastAPI endpoint for classifying email content into threat request categories.
"""

from __future__ import annotations

import re
import html
from typing import Optional
from dataclasses import dataclass, field

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn


# ---------------------------------------------------------------------------
# Rule Engine
# ---------------------------------------------------------------------------

@dataclass
class CategoryRule:
    primary: list[tuple[str, int]]       # (phrase, weight)
    supporting: list[tuple[str, int]]    # (phrase, weight)
    negative: list[tuple[str, int]]      # (phrase, negative weight)
    threshold: int
    regex_patterns: list[tuple[str, int]] = field(default_factory=list)


RULES: dict[str, CategoryRule] = {

    "invoice_payment": CategoryRule(
        primary=[
            ("pay the invoice", 10),
            ("payment due", 9),
            ("outstanding invoice", 9),
            ("remit payment", 10),
            ("settle the amount", 9),
            ("invoice attached", 8),
            ("amount due", 8),
            ("balance due", 8),
            ("kindly make payment", 9),
            ("process the payment", 8),
        ],
        supporting=[
            ("bank details", 4),
            ("wire", 3),
            ("transfer funds", 4),
            ("overdue", 3),
            ("before due date", 3),
            ("attached invoice", 3),
            ("invoice number", 2),
        ],
        negative=[
            ("payment received", -8),
            ("thank you for your payment", -8),
            ("payment confirmed", -7),
            ("receipt", -3),
        ],
        threshold=10,
    ),

    "wire_transfer": CategoryRule(
        primary=[
            ("wire transfer", 10),
            ("transfer funds", 9),
            ("send money", 8),
            ("bank transfer", 9),
            ("transfer the amount", 9),
            ("initiate a transfer", 10),
            ("initiate transfer", 9),
            ("swift transfer", 10),
            ("make a transfer", 9),
        ],
        supporting=[
            ("urgently", 3),
            ("today", 2),
            ("immediately", 3),
            ("account number", 4),
            ("routing number", 4),
            ("iban", 4),
            ("swift code", 4),
            ("beneficiary", 3),
        ],
        negative=[
            ("transfer complete", -6),
            ("transfer confirmed", -6),
        ],
        threshold=10,
    ),

    "gift_card_request": CategoryRule(
        primary=[
            ("gift card", 10),
            ("itunes card", 10),
            ("amazon gift card", 10),
            ("google play card", 10),
            ("steam gift card", 10),
            ("purchase gift cards", 10),
            ("buy gift cards", 10),
            ("e-gift", 8),
            ("buy cards", 7),
        ],
        supporting=[
            ("send the codes", 6),
            ("scratch and send", 6),
            ("keep confidential", 3),
            ("don't tell", 3),
            ("send me the numbers", 4),
            ("pin code", 3),
            ("redemption code", 5),
        ],
        negative=[
            ("gift card balance", -5),
            ("gift card reward", -4),
        ],
        threshold=10,
    ),

    "credential_request": CategoryRule(
        primary=[
            ("send your password", 10),
            ("confirm your credentials", 10),
            ("verify your login", 10),
            ("reset your password", 9),
            ("enter your username", 9),
            ("account verification required", 9),
            ("sign in to verify", 10),
            ("confirm your account", 9),
            ("provide your credentials", 10),
            ("submit your login", 9),
        ],
        supporting=[
            ("account suspended", 4),
            ("unusual activity", 3),
            ("click here to verify", 4),
            ("your email has been suspended", 5),
            ("security alert", 3),
            ("verify your identity", 4),
        ],
        negative=[
            ("password reset complete", -6),
            ("your password has been changed", -6),
        ],
        threshold=10,
    ),

    "sensitive_data_request": CategoryRule(
        primary=[
            ("w-2", 10),
            ("form 16", 10),
            ("tax form", 9),
            ("salary slip", 10),
            ("employee list", 10),
            ("payroll data", 10),
            ("social security number", 10),
            ("pan number", 9),
            ("employee records", 9),
            ("compensation details", 9),
            ("salary details", 9),
        ],
        supporting=[
            ("hr request", 4),
            ("audit", 3),
            ("compliance", 3),
            ("finance team needs", 4),
            ("send us the", 3),
            ("please provide", 3),
        ],
        negative=[],
        threshold=10,
    ),

    "document_download": CategoryRule(
        primary=[
            ("download the document", 10),
            ("open the attachment", 9),
            ("click to download", 10),
            ("review the attached", 8),
            ("access the document", 9),
            ("download now", 8),
            ("open attached file", 9),
            ("view the document", 8),
            ("download file", 8),
        ],
        supporting=[
            ("pdf", 2),
            ("docusign", 4),
            ("shared file", 3),
            ("onedrive", 3),
            ("dropbox", 3),
            ("google drive", 3),
            ("see attached", 3),
            ("attachment", 2),
        ],
        negative=[],
        threshold=8,
    ),

    "link_click": CategoryRule(
        primary=[
            ("click here", 8),
            ("click the link", 9),
            ("follow this link", 9),
            ("click below", 8),
            ("click on the link", 9),
            ("visit our", 7),
            ("go to this link", 9),
            ("access your account at", 9),
            ("log in here", 9),
        ],
        supporting=[
            ("action required", 3),
            ("verify now", 4),
            ("confirm now", 3),
            ("bit.ly", 5),
            ("tinyurl", 5),
            ("link below", 3),
            ("update your account", 3),
        ],
        negative=[
            ("do not click", -8),
            ("never click", -8),
            ("unsubscribe", -2),
        ],
        threshold=9,
        regex_patterns=[
            (r"https?://(?!(?:www\.)?(microsoft|google|apple|amazon)\.com)[^\s]{15,}", 3),
            (r"bit\.ly/|tinyurl\.com|t\.co/|goo\.gl/", 5),
        ],
    ),

    "urgent_callback": CategoryRule(
        primary=[
            ("call us immediately", 10),
            ("call back urgently", 10),
            ("please call", 7),
            ("contact us at", 6),
            ("reach us on", 7),
            ("call now", 8),
            ("dial this number", 9),
            ("phone us", 7),
        ],
        supporting=[
            ("urgent", 3),
            ("immediately", 3),
            ("your account will be closed", 5),
            ("within 24 hours", 3),
            ("failure to respond", 4),
            ("last warning", 4),
        ],
        negative=[],
        threshold=9,
        regex_patterns=[
            (r"(?:call|contact|reach|dial).{0,30}\+?[\d\s\-\(\)]{7,15}", 6),
            (r"\+?1[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", 5),
        ],
    ),

    "bank_detail_update": CategoryRule(
        primary=[
            ("update bank details", 10),
            ("new bank account", 9),
            ("change payment details", 10),
            ("updated account number", 10),
            ("new routing number", 10),
            ("please update your records", 9),
            ("new banking information", 10),
            ("change bank account", 10),
            ("update our banking", 10),
        ],
        supporting=[
            ("effective immediately", 4),
            ("vendor change", 3),
            ("payroll update", 4),
            ("new account details", 4),
            ("please make note", 3),
        ],
        negative=[],
        threshold=10,
    ),

    "invoice_verification": CategoryRule(
        primary=[
            ("verify the invoice", 10),
            ("confirm payment status", 9),
            ("invoice approval needed", 10),
            ("awaiting your confirmation", 9),
            ("payment on hold", 9),
            ("pending invoice", 8),
            ("approve this invoice", 10),
            ("authorize this payment", 10),
        ],
        supporting=[
            ("authorization required", 4),
            ("cfo", 3),
            ("accounts payable", 3),
            ("pending approval", 4),
            ("release payment", 4),
        ],
        negative=[
            ("invoice verified", -6),
            ("payment approved", -5),
        ],
        threshold=10,
    ),

    "legal_threat": CategoryRule(
        primary=[
            ("legal action", 10),
            ("lawsuit", 10),
            ("subpoena", 10),
            ("court order", 10),
            ("failure to comply", 9),
            ("legal proceedings", 10),
            ("summons", 9),
            ("violation notice", 9),
            ("file a lawsuit", 10),
            ("attorney has been instructed", 10),
        ],
        supporting=[
            ("within 48 hours", 4),
            ("failure to respond", 4),
            ("damages", 3),
            ("compliance required", 3),
            ("attorney", 3),
            ("legal department", 3),
        ],
        negative=[],
        threshold=10,
    ),

    "executive_request": CategoryRule(
        primary=[
            ("ceo has requested", 10),
            ("on behalf of the ceo", 10),
            ("per the director", 9),
            ("executive team requires", 10),
            ("the president needs", 9),
            ("board has approved", 9),
            ("as per ceo instructions", 10),
            ("ceo wants you to", 10),
            ("management has approved", 8),
            ("leadership has directed", 9),
        ],
        supporting=[
            ("confidential", 3),
            ("do not discuss", 4),
            ("handle immediately", 4),
            ("bypass normal process", 5),
            ("top priority", 3),
            ("directly to me", 3),
        ],
        negative=[],
        threshold=9,
    ),

    "vpn_or_mfa_reset": CategoryRule(
        primary=[
            ("mfa reset", 10),
            ("two-factor authentication", 9),
            ("2fa code", 10),
            ("authenticator app", 9),
            ("vpn access", 9),
            ("security token", 9),
            ("one-time password", 9),
            ("otp code", 9),
            ("approve the login", 10),
            ("approve sign-in request", 10),
        ],
        supporting=[
            ("new device detected", 4),
            ("unusual sign-in", 4),
            ("your account requires verification", 4),
            ("enter the code", 3),
            ("6-digit code", 4),
            ("verify your device", 4),
        ],
        negative=[],
        threshold=9,
    ),

    "meeting_request": CategoryRule(
        primary=[
            ("join the meeting", 9),
            ("meeting invitation", 8),
            ("you have been invited", 8),
            ("join zoom", 9),
            ("zoom meeting link", 9),
            ("teams meeting", 8),
            ("google meet", 8),
            ("join video conference", 9),
            ("join here for the meeting", 10),
        ],
        supporting=[
            ("click to join", 4),
            ("meeting id", 3),
            ("passcode", 3),
            ("reschedule", 2),
            ("urgent meeting", 4),
            ("calendar invite", 3),
        ],
        negative=[
            ("meeting cancelled", -5),
        ],
        regex_patterns=[
            (r"https?://(?!zoom\.us|teams\.microsoft\.com|meet\.google\.com)[^\s]+(?:zoom|meet|meeting|conference)[^\s]*", 5),
        ],
        threshold=9,
    ),
}


# ---------------------------------------------------------------------------
# Preprocessing
# ---------------------------------------------------------------------------

def preprocess(text: str) -> str:
    """Strip HTML, normalize whitespace, lowercase."""
    # Unescape HTML entities
    text = html.unescape(text)
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text.lower()


def has_negation_before(text: str, phrase: str, window: int = 6) -> bool:
    """Return True if a negation word appears within `window` words before `phrase`."""
    negation_words = {"not", "no", "never", "don't", "do not", "cannot", "can't", "didn't"}
    pattern = re.compile(re.escape(phrase))
    for match in pattern.finditer(text):
        start = match.start()
        preceding = text[:start].split()[-window:]
        if any(neg in " ".join(preceding) for neg in negation_words):
            return True
    return False


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

@dataclass
class ClassificationResult:
    label: str
    score: int
    runner_up: Optional[str]
    runner_up_score: int
    matched_phrases: list[str]
    all_scores: dict[str, int]


def classify(raw_text: str) -> ClassificationResult:
    text = preprocess(raw_text)
    scores: dict[str, int] = {}
    matched: dict[str, list[str]] = {}

    for category, rule in RULES.items():
        score = 0
        hits: list[str] = []

        # Primary phrases
        for phrase, weight in rule.primary:
            if phrase in text and not has_negation_before(text, phrase):
                score += weight
                hits.append(f"[primary] {phrase!r}")

        # Supporting phrases
        for phrase, weight in rule.supporting:
            if phrase in text:
                score += weight
                hits.append(f"[support] {phrase!r}")

        # Negative phrases
        for phrase, weight in rule.negative:
            if phrase in text:
                score += weight  # weight is already negative
                hits.append(f"[negative] {phrase!r} ({weight})")

        # Regex patterns
        for pattern, weight in rule.regex_patterns:
            if re.search(pattern, text):
                score += weight
                hits.append(f"[regex] {pattern!r}")

        scores[category] = score
        matched[category] = hits

    # Filter by threshold
    qualifying = {k: v for k, v in scores.items() if v >= RULES[k].threshold}

    if not qualifying:
        return ClassificationResult(
            label="none",
            score=0,
            runner_up=None,
            runner_up_score=0,
            matched_phrases=[],
            all_scores=scores,
        )

    sorted_cats = sorted(qualifying.items(), key=lambda x: x[1], reverse=True)
    winner_label, winner_score = sorted_cats[0]
    runner_up_label = sorted_cats[1][0] if len(sorted_cats) > 1 else None
    runner_up_score = sorted_cats[1][1] if len(sorted_cats) > 1 else 0

    return ClassificationResult(
        label=winner_label,
        score=winner_score,
        runner_up=runner_up_label,
        runner_up_score=runner_up_score,
        matched_phrases=matched[winner_label],
        all_scores=scores,
    )


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Mailarmor — Request Type Classifier",
    description="Rule-based email request type classification signal for Mailarmor.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class EmailInput(BaseModel):
    subject: Optional[str] = ""
    body: str
    include_debug: bool = False

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "subject": "Urgent: Invoice #4521 Payment Required",
                    "body": "Please pay the invoice attached. The amount due is $5,200. Kindly transfer funds to the bank details provided in the document before the due date.",
                    "include_debug": True,
                }
            ]
        }
    }


class ClassificationResponse(BaseModel):
    request_type: str
    confidence_score: int
    runner_up: Optional[str]
    runner_up_score: int
    matched_phrases: list[str]
    all_scores: Optional[dict[str, int]] = None


class BulkEmailInput(BaseModel):
    emails: list[EmailInput]


class BulkClassificationResponse(BaseModel):
    results: list[dict]


@app.post("/classify", response_model=ClassificationResponse, summary="Classify a single email")
def classify_email(payload: EmailInput):
    """
    Classify an email's request type based on its subject and body.

    Returns the detected request type label, confidence score, and matched rule phrases.
    Set `include_debug: true` to also receive scores for all categories.
    """
    combined_text = f"{payload.subject or ''} {payload.body}"
    result = classify(combined_text)

    return ClassificationResponse(
        request_type=result.label,
        confidence_score=result.score,
        runner_up=result.runner_up,
        runner_up_score=result.runner_up_score,
        matched_phrases=result.matched_phrases,
        all_scores=result.all_scores if payload.include_debug else None,
    )


@app.post("/classify/bulk", response_model=BulkClassificationResponse, summary="Classify multiple emails")
def classify_bulk(payload: BulkEmailInput):
    """
    Classify up to 100 emails in a single request.
    """
    if len(payload.emails) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 emails per bulk request.")

    results = []
    for i, email in enumerate(payload.emails):
        combined_text = f"{email.subject or ''} {email.body}"
        result = classify(combined_text)
        results.append({
            "index": i,
            "request_type": result.label,
            "confidence_score": result.score,
            "runner_up": result.runner_up,
            "runner_up_score": result.runner_up_score,
        })

    return BulkClassificationResponse(results=results)


@app.get("/categories", summary="List all supported request type categories")
def list_categories():
    """Returns all supported request type labels with their descriptions."""
    return {
        "categories": [
            {"value": "invoice_payment",     "description": "Request to pay a fake invoice, often with fake bank details."},
            {"value": "wire_transfer",        "description": "Direct request for a money transfer to attacker-controlled accounts."},
            {"value": "gift_card_request",    "description": "Asking employee to purchase gift cards (common in impersonation attacks)."},
            {"value": "credential_request",   "description": "Asks user to send or reset account login credentials."},
            {"value": "sensitive_data_request","description": "Requests HR/financial info like tax forms, salary slips, or employee lists."},
            {"value": "document_download",    "description": "Requests user to click/download a potentially malicious file."},
            {"value": "link_click",           "description": "Asks user to visit a suspicious link, often disguised as internal services."},
            {"value": "urgent_callback",      "description": "Demands user to call a number urgently — may connect to attacker."},
            {"value": "bank_detail_update",   "description": "Asks to change vendor or payroll bank details to attacker's account."},
            {"value": "invoice_verification", "description": "Pretends to verify a pending invoice or payment as an authority."},
            {"value": "legal_threat",         "description": "Uses legal urgency or false subpoenas to manipulate behavior."},
            {"value": "executive_request",    "description": "Generic directive from CEO or VIP demanding immediate action."},
            {"value": "vpn_or_mfa_reset",     "description": "Tries to capture multi-factor credentials or VPN access."},
            {"value": "meeting_request",      "description": "Fakes calendar invites with malicious links (spear phishing)."},
            {"value": "none",                 "description": "No actionable request detected in the content."},
        ]
    }


@app.get("/samples", summary="Get sample test payloads for each category")
def get_samples():
    """Returns one representative sample email per category for quick testing."""
    return {
        "samples": [
            {
                "category": "invoice_payment",
                "payload": {
                    "subject": "Invoice #INV-4521 — Payment Due",
                    "body": "Dear Finance Team, please find the invoice attached for services rendered in March. The amount due is $12,500. Kindly remit payment to the bank details provided in the attachment before the due date. Please settle the amount at the earliest.",
                    "include_debug": True,
                },
            },
            {
                "category": "wire_transfer",
                "payload": {
                    "subject": "Urgent Wire Transfer Required",
                    "body": "Hi, I need you to initiate a transfer of $45,000 to our new vendor account immediately. Please use the following routing number and account number provided below. This is time sensitive, please transfer funds today.",
                    "include_debug": True,
                },
            },
            {
                "category": "gift_card_request",
                "payload": {
                    "subject": "Quick Favour Needed",
                    "body": "Hey, are you available? I need you to purchase 5 Amazon gift cards worth $200 each for a client reward program. Please buy the cards and send me the redemption codes. Keep this confidential for now, I'll explain later.",
                    "include_debug": True,
                },
            },
            {
                "category": "credential_request",
                "payload": {
                    "subject": "Your Account Has Been Suspended — Action Required",
                    "body": "We have detected unusual activity on your account. Your email has been suspended. Please confirm your account by verifying your login credentials. Sign in to verify your identity here and enter your username and password to restore access.",
                    "include_debug": True,
                },
            },
            {
                "category": "sensitive_data_request",
                "payload": {
                    "subject": "Urgent: Employee W-2 Forms Required for Audit",
                    "body": "Hi, as part of our annual compliance audit, we urgently need the W-2 tax forms for all employees along with the full employee list and salary details. The finance team needs this by end of day. Please send us the documents at your earliest convenience.",
                    "include_debug": True,
                },
            },
            {
                "category": "document_download",
                "payload": {
                    "subject": "Please Review and Sign the Contract",
                    "body": "Hello, please find your contract ready for review via DocuSign. Click to download the document and open the attachment to review all terms. Please open attached file and complete your signature today.",
                    "include_debug": True,
                },
            },
            {
                "category": "link_click",
                "payload": {
                    "subject": "Action Required: Verify Your Microsoft Account",
                    "body": "Your Microsoft 365 account requires immediate attention. Please click here to verify your account: http://microsoft-verify.suspicious-domain.com/verify. Click the link below and confirm now to avoid service interruption.",
                    "include_debug": True,
                },
            },
            {
                "category": "urgent_callback",
                "payload": {
                    "subject": "URGENT: Your Account Will Be Closed",
                    "body": "This is your final notice. Your bank account shows suspicious activity and will be frozen within 24 hours. Please call us immediately at +1-800-555-0199 to prevent account closure. Failure to respond will result in permanent suspension.",
                    "include_debug": True,
                },
            },
            {
                "category": "bank_detail_update",
                "payload": {
                    "subject": "Important: Updated Banking Information",
                    "body": "Please be advised that we have updated our banking information effective immediately. Please update bank details in your system with the new account number and routing number provided. Kindly update your records before processing the next payment.",
                    "include_debug": True,
                },
            },
            {
                "category": "legal_threat",
                "payload": {
                    "subject": "Notice of Legal Action — Immediate Response Required",
                    "body": "You are hereby notified that legal action will be filed against your organization for non-compliance with contract terms. Our attorney has been instructed to initiate legal proceedings unless you respond within 48 hours. Failure to comply will result in a formal lawsuit and damages claim.",
                    "include_debug": True,
                },
            },
            {
                "category": "executive_request",
                "payload": {
                    "subject": "Confidential — Action Needed Immediately",
                    "body": "This is on behalf of the CEO. The CEO has requested that you handle this immediately and process a payment before close of business today. Please keep this confidential and do not discuss with other team members. Leadership has directed this to be top priority.",
                    "include_debug": True,
                },
            },
            {
                "category": "vpn_or_mfa_reset",
                "payload": {
                    "subject": "Action Required: Approve Your MFA Reset",
                    "body": "A new device has been detected signing into your corporate account. Please approve the login by entering the 2FA code sent to your authenticator app. If you did not initiate this, please provide your OTP code to our security team immediately to secure your account.",
                    "include_debug": True,
                },
            },
            {
                "category": "meeting_request",
                "payload": {
                    "subject": "You Have Been Invited to an Urgent Meeting",
                    "body": "You have been invited to an urgent executive meeting. Please join here for the meeting: http://zoom-meeting-login.phishing-site.net/join. Meeting ID: 845-291-0022. Click to join the video conference immediately. This is an urgent meeting — your presence is required.",
                    "include_debug": True,
                },
            },
            {
                "category": "none",
                "payload": {
                    "subject": "Team Lunch This Friday",
                    "body": "Hi everyone, just a reminder that we have a team lunch this Friday at 1pm at the usual restaurant. Please let me know if you can make it. Looking forward to seeing everyone!",
                    "include_debug": True,
                },
            },
        ]
    }


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok", "rules_loaded": len(RULES)}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run("mailarmor_classifier:app", host="0.0.0.0", port=8000, reload=True)

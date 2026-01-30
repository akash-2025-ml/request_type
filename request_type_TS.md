# Technical Specification: Email Request Type Classification System

## 1. System Overview

### 1.1 Purpose
The Request Type Classification System is an AI-powered service that analyzes email content and categorizes emails based on the type of request they contain. The system identifies potentially malicious or suspicious email requests across 16 predefined categories.

### 1.2 Core Functionality
- Accepts email message IDs via REST API
- Retrieves email content from Redis cache
- Applies AI-based classification using DeepSeek-R1 model
- Returns classification results for downstream processing

### 1.3 Technology Stack
- **Language**: Python
- **API Framework**: FastAPI
- **AI Framework**: LangChain
- **LLM Model**: DeepSeek-R1 (via Ollama)
- **Data Store**: Redis
- **Model Hosting**: Ollama server (http://xyz.000.000.000:11434)

## 2. System Architecture

### 2.1 Component Diagram
```
[Client] → [FastAPI Server] → [Classification Engine] → [Ollama Server]
               
```

### 2.2 Module Structure
```
request_type/
├── app.py          # FastAPI application and endpoints
├── auto.py         # Classification agent implementation
├── prompt.py       # AI model prompts
├── redis_1.py      # Redis integration 
└── Request_Type.txt # Functional specification
```

## 3. API Specification

### 3.1 Process Endpoint

**Endpoint**: `POST /process`

**Request Model**:
```python
class InputData(BaseModel):
    Massage_Id: str    # Email message identifier
    Tanent_id: str     # Tenant identifier
    mailbox_id: str    # Mailbox identifier
```

**Response Model**:
```python
class OutputData(BaseModel):
    signal: str        # Fixed value: "request_type"
    value: str         # Classification result (one of 16 categories)
```

**Response Example**:
```json
{
    "signal": "request_type",
    "value": "invoice_payment"
}
```

### 3.2 Health Check Endpoint

**Endpoint**: `GET /`

**Response**:
```json
{
    "message": "FastAPI is running!"
}
```

## 4. Classification Engine

### 4.1 Two-Stage Classification Process

**Stage 1 - Request Detection (agent1)**:
- Determines if email contains any actionable request
- Returns: "request_present" or "none"
- Uses prompt `a1` from prompt.py

**Stage 2 - Request Type Classification (agent2)**:
- Classifies the type of request if present
- Returns: One of 15 category labels
- Uses prompt `a2` from prompt.py

### 4.2 Main Classification Function

```python
def classify_email(email_text: str):
    # Stage 1: Check request presence
    presence_result = agent1(email_text)
    
    if presence_result in ["none", "None"]:
        return "none"
    else:
        # Stage 2: Classify request type
        type_result = agent2(email_text)
        return type_result
```

## 5. Classification Categories

### 5.1 Request Type Categories (14)

| Category | Description |
|----------|-------------|
| **invoice_payment** | Requests to pay attached or referenced invoices, often with fake details |
| **wire_transfer** | Direct money transfer requests to attacker-controlled accounts |
| **gift_card_request** | Urgent requests to purchase and share gift card codes |
| **credential_request** | Requests for usernames, passwords, or authentication codes |
| **sensitive_data_request** | Requests for HR/financial data (tax forms, salary info, etc.) |
| **document_download** | Requests to download potentially malicious documents |
| **link_click** | Urgent requests to click hyperlinks leading to phishing sites |
| **urgent_callback** | Pressure to call a phone number immediately |
| **bank_detail_update** | Requests to change banking or payment information |
| **invoice_verification** | Requests to confirm or validate invoice details |
| **legal_threat** | Intimidation using legal action or violation claims |
| **executive_request** | Impersonation of CEO/executives for urgent tasks |
| **vpn_or_mfa_reset** | Requests to reset VPN or multi-factor authentication |
| **meeting_request** | Meeting invites potentially containing malicious content |

### 5.2 Special Categories (2)

| Category | Description |
|----------|-------------|
| **none** | No actionable request detected in the email |
| **other** | Request present but doesn't match predefined categories |

### 5.3 Classification Priority Rule
When multiple request types are present, prioritize high-risk categories:
- credential_request
- sensitive_data_request
- legal_threat
- bank_detail_update
- document_download

## 6. Data Flow

### 6.1 Request Processing Sequence

1. **API Request Reception**
   - Client sends POST request with Message_Id, Tenant_id, mailbox_id
   - FastAPI validates input data structure

2. **Email Content Retrieval**
   - System calls `get_value(Message_Id)` from redis_1.py
   - Retrieves full email content from Redis cache

3. **Classification Processing**
   - Email content passed to `classify_email()` function
   - Stage 1: Request presence detection via agent1
   - Stage 2: Request type classification via agent2 (if needed)

4. **LLM Processing**
   - LangChain formats messages with SystemMessage (prompt) and HumanMessage (email)
   - Sends to Ollama server for inference
   - Receives classification result

5. **Response Formation**
   - Wraps result in OutputData structure
   - Returns JSON response to client

## 7. Model Configuration

### 7.1 LLM Settings
- **Model**: DeepSeek-R1
- **Server**: Ollama instance at  http://xyz.000.000.000:11434
- **Framework**: LangChain Community LLMs
- **Message Format**: SystemMessage + HumanMessage

### 7.2 Prompt Structure
- **Prompt a1**: Simple request presence detection
- **Prompt a2**: Detailed request type classification
- Both prompts emphasize returning only the label without explanation

## 8. Integration Points

### 8.1 Redis Integration
- Function: `get_value(message_id)` 
- Purpose: Retrieve email content using message ID
- Module: redis_1.py (implementation details not provided)

### 8.2 External Dependencies
- Ollama server for model inference
- Redis server for email storage
- Network connectivity to external Ollama instance

## 9. Deployment Considerations

### 9.1 Environment Requirements
- Python runtime with FastAPI support
- Network access to Ollama server
- Redis server connection
- Sufficient memory for LangChain operations

### 9.2 Configuration Parameters
- Ollama base URL: http://xyz.000.000.000:11434
- Model name: deepseek-r1
- API port: Configurable via FastAPI



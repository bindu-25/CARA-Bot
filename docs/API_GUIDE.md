# API Guide

## Authentication

Currently no authentication required (add in production).

## Endpoints

### Analyze Contract
```http
POST /analyze
Content-Type: multipart/form-data

file: <contract.pdf>
```

**Response:**
```json
{
  "contract_type": "Employment Agreement",
  "parties": ["Company ABC", "John Doe"],
  "dates": ["2024-01-01"],
  "amounts": ["$50,000"],
  "clauses": [...]
}
```

### Assess Risk
```http
POST /assess-risk
Content-Type: multipart/form-data

file: <contract.pdf>
```

### Check Compliance
```http
POST /check-compliance
Content-Type: multipart/form-data

file: <contract.pdf>
```

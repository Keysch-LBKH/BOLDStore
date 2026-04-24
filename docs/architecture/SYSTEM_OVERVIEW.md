# BOLDStore — System Architecture

## High-Level Flow

```
GHL (Events/Webhooks)
        │
        ▼
BOLDStore API (FastAPI)         ◄──── GHL REST API calls (outbound)
 /webhooks/ghl                         N8N REST API calls (outbound)
        │                              Google Drive/Sheets (outbound)
        ▼
 Event Handlers
  ├── sync contacts → Google Sheets
  ├── log events    → Google Sheets (Webhook-Log tab)
  └── trigger       → N8N (via webhook or API)
                             │
                             ▼
                          N8N Workflows
                           (automation logic)
```

## Components

| Component | Role |
|---|---|
| **FastAPI app** (`main.py`) | Receives GHL webhooks, exposes health endpoint |
| **GHL API Client** | Outbound REST calls to GHL LeadConnector API |
| **GHL Webhook Receiver** | Validates signature, routes to handlers |
| **N8N Client** | Triggers N8N workflows, queries executions |
| **Drive Client** | Manages Google Drive folders and docs |
| **Sheets Client** | Reads/writes structured data in Google Sheets |
| **Bootstrap Script** | One-time setup of Drive structure and master Sheet |

## Data Stores

| Store | Purpose |
|---|---|
| Google Sheets — Contacts | Synced GHL contacts |
| Google Sheets — Opportunities | Pipeline/stage tracking |
| Google Sheets — Webhook-Log | Audit trail of all inbound events |
| Google Sheets — Expansion-Tracker | Per-client deployment status |
| Google Drive — Snapshots | GHL snapshot docs, N8N workflow exports |
| Google Drive — SOPs | Standard operating procedures |

## Authentication

| Service | Method |
|---|---|
| GHL | Bearer token (API key) in `Authorization` header |
| GHL Webhooks (inbound) | HMAC-SHA256 signature on raw body |
| N8N | `X-N8N-API-KEY` header |
| Google | Service account JSON key (`service_account.json`) |

## Expansion Model

Each new client gets:
1. GHL snapshot applied to a new sub-account
2. N8N workflows cloned + webhook URLs updated
3. `bootstrap_google.py` run to create a parallel Drive folder tree
4. New row in `Expansion-Tracker` sheet
5. `.env` updated with new `GHL_LOCATION_ID`

# BOLDStore Integration Platform

GHL + N8N + Google Drive/Sheets — raw integration layer.

## Stack

- **Python 3.11+** with FastAPI (webhook receiver + API server)
- **GHL (GoHighLevel)** — REST API client + inbound webhook handler
- **N8N** (self-hosted) — workflow trigger and management client
- **Google Drive/Sheets** — documentation storage and structured data sync

## Quick Start

```bash
# 1. Install dependencies
pip install -e ".[dev]"

# 2. Configure environment
cp .env.example .env
# Fill in .env with your keys

# 3. Bootstrap Google Drive + Sheet (run once)
python scripts/bootstrap_google.py

# 4. Start the server
python main.py
```

API docs available at `http://localhost:8000/docs` (development only).

## Project Structure

```
BOLDStore/
├── main.py                          # FastAPI entry point
├── config/settings.py               # Pydantic settings from .env
├── integrations/
│   ├── ghl/
│   │   ├── api/client.py            # GHL REST API client
│   │   └── webhooks/
│   │       ├── receiver.py          # Signature validation + routing
│   │       └── handlers.py          # Event handler implementations
│   ├── n8n/client.py                # N8N API client
│   └── google/
│       ├── drive/client.py          # Google Drive operations
│       └── sheets/client.py         # Google Sheets read/write
├── docs/
│   ├── snapshots/SNAPSHOT_TEMPLATE.md
│   ├── sops/SOP_TEMPLATE.md
│   └── architecture/SYSTEM_OVERVIEW.md
└── scripts/
    └── bootstrap_google.py          # One-time Drive + Sheet setup
```

## Google Service Account Setup

1. Create a project in Google Cloud Console
2. Enable **Google Drive API** and **Google Sheets API**
3. Create a Service Account and download the JSON key
4. Save as `service_account.json` in the project root (it's in `.gitignore`)
5. Share your Google Drive root folder with the service account email

## GHL Webhook Setup

Register this server as a GHL webhook endpoint:

```python
from integrations.ghl import GHLClient
import asyncio

async def register():
    client = GHLClient()
    await client.create_webhook(
        url="https://YOUR_DOMAIN/webhooks/ghl/",
        events=["ContactCreate", "ContactUpdate", "OpportunityCreate",
                "OpportunityStatusUpdate", "AppointmentCreate", "FormSubmit"],
    )

asyncio.run(register())
```

## Expansion Playbook

See `docs/architecture/SYSTEM_OVERVIEW.md` for the full expansion model.
Each new client deployment: apply GHL snapshot → clone N8N workflows →
run `bootstrap_google.py` → update `.env` → add row to Expansion-Tracker.

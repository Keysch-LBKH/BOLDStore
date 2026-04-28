"""
Create the Ghost Print Co. product pipeline workflow in N8N with a webhook
trigger, then fire a test payload at it.

Usage:
    python scripts/create_ghl_pipeline_workflow.py
"""
import sys
import json
import time
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings

N8N_BASE   = settings.n8n_base_url.rstrip("/")
N8N_API    = f"{N8N_BASE}/api/v1"
TAG_ID     = settings.n8n_boldstore_tag_id
HEADERS    = {"X-N8N-API-KEY": settings.n8n_api_key, "Content-Type": "application/json"}

WEBHOOK_PATH = "ghost-print-item"

# ── Test payload ──────────────────────────────────────────────────────────────
TEST_PAYLOAD = {
    "sku":                "GPC-001",
    "product_name":       "Reaper Flash Tee",
    "category":           "t-shirt",
    "base_colour":        "Washed Black",
    "brand":              "Ghost Print Co.",
    "year":               "2025",
    "price":              "65.00",
    "compare_at_price":   "85.00",
    "sizes_available":    "S,M,L,XL,XXL",
    "available_quantity": "50",
    "raw_notes":          (
        "Traditional tattoo flash reaper design. Heavy 6oz cotton. "
        "Front chest print. White ink on washed black base. "
        "Distressed wash finish."
    ),
    "image_url_1":  "https://drive.google.com/file/d/SAMPLE_IMAGE_1/view",
    "image_url_2":  "",
    "image_url_3":  "",
    "status":       "Draft",
    "contact_id":   "test-contact-001",
    "location_id":  settings.ghl_location_id,
}

# ── Workflow definition ───────────────────────────────────────────────────────
WORKFLOW = {
    "name": "Ghost Print Co. — Product Pipeline",
    "nodes": [
        {
            "id": "node-webhook",
            "name": "GHL Item Submitted",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [250, 300],
            "parameters": {
                "httpMethod": "POST",
                "path": WEBHOOK_PATH,
                "responseMode": "onReceived",
                "responseData": "firstEntryJson",
                "options": {},
            },
            "webhookId": WEBHOOK_PATH,
        },
        {
            "id": "node-set",
            "name": "Map Fields",
            "type": "n8n-nodes-base.set",
            "typeVersion": 3,
            "position": [500, 300],
            "parameters": {
                "mode": "manual",
                "duplicateItem": False,
                "assignments": {
                    "assignments": [
                        {"id": "f1",  "name": "SKU",                "value": "={{ $json.body.sku }}",                "type": "string"},
                        {"id": "f2",  "name": "Product Name",        "value": "={{ $json.body.product_name }}",       "type": "string"},
                        {"id": "f3",  "name": "Category",            "value": "={{ $json.body.category }}",           "type": "string"},
                        {"id": "f4",  "name": "Base Colour",         "value": "={{ $json.body.base_colour }}",        "type": "string"},
                        {"id": "f5",  "name": "Brand",               "value": "={{ $json.body.brand }}",              "type": "string"},
                        {"id": "f6",  "name": "Year",                "value": "={{ $json.body.year }}",               "type": "string"},
                        {"id": "f7",  "name": "Price",               "value": "={{ $json.body.price }}",              "type": "string"},
                        {"id": "f8",  "name": "Compare At Price",    "value": "={{ $json.body.compare_at_price }}",   "type": "string"},
                        {"id": "f9",  "name": "Sizes Available",     "value": "={{ $json.body.sizes_available }}",    "type": "string"},
                        {"id": "f10", "name": "Available Quantity",  "value": "={{ $json.body.available_quantity }}", "type": "string"},
                        {"id": "f11", "name": "Raw Notes",           "value": "={{ $json.body.raw_notes }}",          "type": "string"},
                        {"id": "f12", "name": "Image URL 1",         "value": "={{ $json.body.image_url_1 }}",        "type": "string"},
                        {"id": "f13", "name": "Image URL 2",         "value": "={{ $json.body.image_url_2 }}",        "type": "string"},
                        {"id": "f14", "name": "Image URL 3",         "value": "={{ $json.body.image_url_3 }}",        "type": "string"},
                        {"id": "f15", "name": "Status",              "value": "Draft",                                "type": "string"},
                    ]
                },
                "options": {},
            },
        },
    ],
    "connections": {
        "GHL Item Submitted": {
            "main": [[{"node": "Map Fields", "type": "main", "index": 0}]]
        }
    },
    "settings": {"executionOrder": "v1"},
    "tags": [{"id": TAG_ID}],
}


def get_existing_workflow() -> dict | None:
    r = httpx.get(f"{N8N_API}/workflows", headers=HEADERS, params={"limit": 100})
    r.raise_for_status()
    for wf in r.json().get("data", []):
        if wf["name"] == WORKFLOW["name"]:
            return wf
    return None


def create_workflow() -> dict:
    r = httpx.post(f"{N8N_API}/workflows", headers=HEADERS, json=WORKFLOW)
    if r.status_code not in (200, 201):
        print(f"  [!] {r.status_code}: {r.text}")
        r.raise_for_status()
    return r.json()


def activate_workflow(wf_id: str) -> None:
    r = httpx.post(f"{N8N_API}/workflows/{wf_id}/activate", headers=HEADERS)
    r.raise_for_status()


def fire_test_webhook() -> dict:
    url = f"{N8N_BASE}/webhook/{WEBHOOK_PATH}"
    r = httpx.post(url, json=TEST_PAYLOAD, timeout=15)
    if r.status_code not in (200, 201):
        print(f"  [!] Webhook returned {r.status_code}: {r.text}")
        r.raise_for_status()
    return r.json()


def main():
    print(f"N8N: {N8N_BASE}\n")

    # ── Create or reuse workflow ──────────────────────────────────────────────
    print("Checking for existing workflow...")
    existing = get_existing_workflow()
    if existing:
        wf_id = existing["id"]
        print(f"  Found existing workflow (id: {wf_id})")
    else:
        print("  Creating workflow...")
        wf = create_workflow()
        wf_id = wf["id"]
        print(f"  Created (id: {wf_id})")

    # ── Activate ──────────────────────────────────────────────────────────────
    print("  Activating...")
    activate_workflow(wf_id)
    print("  Active")

    # ── Fire test payload ─────────────────────────────────────────────────────
    webhook_url = f"{N8N_BASE}/webhook/{WEBHOOK_PATH}"
    print(f"\nFiring test payload to: {webhook_url}")
    print(f"Payload:\n{json.dumps(TEST_PAYLOAD, indent=2)}\n")

    time.sleep(1)  # give N8N a moment to register the webhook
    response = fire_test_webhook()
    print(f"Response: {json.dumps(response, indent=2)}")

    print(f"""
Done.

Workflow URL: {N8N_BASE}/workflow/{wf_id}
Webhook URL:  {webhook_url}

Open the workflow in N8N — you should see the test execution with all 15
fields mapped. Next step: add the Google Sheets node to append the row.
""")


if __name__ == "__main__":
    main()

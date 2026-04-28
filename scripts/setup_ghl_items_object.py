"""
Create the 'Items' custom object in GHL with all product pipeline fields.
Run once. Safe to re-run — skips creation if the object already exists.

Usage:
    python scripts/setup_ghl_items_object.py
"""
import sys
import json
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings

BASE = settings.ghl_base_url.rstrip("/")
LOCATION_ID = settings.ghl_location_id
HEADERS = {
    "Authorization": f"Bearer {settings.ghl_api_key}",
    "Content-Type": "application/json",
    "Version": "2021-07-28",
}

# ── Field definitions ─────────────────────────────────────────────────────────
# dataType options: TEXT | LARGE_TEXT | NUMERICAL | DATE | LIST | CHECKBOX | URL
ITEM_FIELDS = [
    {
        "name": "SKU",
        "fieldKey": "sku",
        "dataType": "TEXT",
        "position": 0,
    },
    {
        "name": "Product Name",
        "fieldKey": "product_name",
        "dataType": "TEXT",
        "position": 1,
    },
    {
        "name": "Category",
        "fieldKey": "category",
        "dataType": "LIST",
        "position": 2,
        "options": [
            {"label": "T-Shirt",  "value": "t-shirt"},
            {"label": "Hoodie",   "value": "hoodie"},
            {"label": "Hat",      "value": "hat"},
            {"label": "Tote",     "value": "tote"},
            {"label": "Other",    "value": "other"},
        ],
    },
    {
        "name": "Base Colour",
        "fieldKey": "base_colour",
        "dataType": "TEXT",
        "position": 3,
    },
    {
        "name": "Brand",
        "fieldKey": "brand",
        "dataType": "TEXT",
        "position": 4,
    },
    {
        "name": "Year",
        "fieldKey": "year",
        "dataType": "TEXT",
        "position": 5,
    },
    {
        "name": "Price",
        "fieldKey": "price",
        "dataType": "NUMERICAL",
        "position": 6,
    },
    {
        "name": "Compare At Price",
        "fieldKey": "compare_at_price",
        "dataType": "NUMERICAL",
        "position": 7,
    },
    {
        "name": "Sizes Available",
        "fieldKey": "sizes_available",
        "dataType": "TEXT",
        "position": 8,
    },
    {
        "name": "Available Quantity",
        "fieldKey": "available_quantity",
        "dataType": "NUMERICAL",
        "position": 9,
    },
    {
        "name": "Raw Notes",
        "fieldKey": "raw_notes",
        "dataType": "LARGE_TEXT",
        "position": 10,
    },
    {
        "name": "Image URL 1",
        "fieldKey": "image_url_1",
        "dataType": "TEXT",
        "position": 11,
    },
    {
        "name": "Image URL 2",
        "fieldKey": "image_url_2",
        "dataType": "TEXT",
        "position": 12,
    },
    {
        "name": "Image URL 3",
        "fieldKey": "image_url_3",
        "dataType": "TEXT",
        "position": 13,
    },
    {
        "name": "Status",
        "fieldKey": "status",
        "dataType": "LIST",
        "position": 14,
        "options": [
            {"label": "Draft",            "value": "Draft"},
            {"label": "Pending Approval", "value": "Pending Approval"},
            {"label": "Approved",         "value": "Approved"},
            {"label": "Processing",       "value": "Processing"},
            {"label": "Done",             "value": "Done"},
            {"label": "Error",            "value": "Error"},
        ],
    },
]


def get_existing_objects() -> list[dict]:
    r = httpx.get(
        f"{BASE}/custom-objects/",
        headers=HEADERS,
        params={"locationId": LOCATION_ID},
    )
    if r.status_code != 200:
        print(f"  [!] GET /custom-objects/ returned {r.status_code}: {r.text}")
        return []
    return r.json().get("customObjects", r.json().get("objects", []))


def create_object(fields: list[dict]) -> dict:
    payload = {
        "locationId": LOCATION_ID,
        "name": "Items",
        "description": "Ghost Print Co. product pipeline — one record per item entry.",
        "labels": {
            "singular": "Item",
            "plural": "Items",
        },
        "fields": fields,
    }
    r = httpx.post(f"{BASE}/custom-objects/", headers=HEADERS, json=payload)
    if r.status_code not in (200, 201):
        print(f"  [!] POST /custom-objects/ returned {r.status_code}")
        print(f"  Response: {json.dumps(r.json(), indent=2)}")
        r.raise_for_status()
    return r.json()


def add_fields_to_object(object_id: str, fields: list[dict]) -> None:
    """Fallback: add fields one-by-one if the API requires separate calls."""
    for field in fields:
        r = httpx.post(
            f"{BASE}/custom-objects/{object_id}/fields",
            headers=HEADERS,
            json={**field, "locationId": LOCATION_ID},
        )
        status = "OK" if r.status_code in (200, 201) else f"FAILED ({r.status_code})"
        print(f"    {status}: {field['name']}")
        if r.status_code not in (200, 201):
            print(f"      {r.text}")


def main():
    print(f"Location: {LOCATION_ID}")
    print(f"Base URL: {BASE}\n")

    # ── Check if 'Items' already exists ───────────────────────────────────────
    print("Checking existing custom objects...")
    existing = get_existing_objects()
    existing_names = [o.get("name", "") for o in existing]
    print(f"  Found: {existing_names or 'none'}")

    if "Items" in existing_names:
        obj = next(o for o in existing if o.get("name") == "Items")
        print(f"\n  'Items' already exists (id: {obj.get('id', obj.get('_id', '?'))})")
        print("  Nothing to do. Delete it in GHL first if you want to rebuild.")
        return

    # ── Create the object with fields ─────────────────────────────────────────
    print("\nCreating 'Items' custom object...")
    try:
        result = create_object(ITEM_FIELDS)
        obj_id = result.get("id") or result.get("_id") or result.get("customObject", {}).get("id", "?")
        print(f"  Created (id: {obj_id})")
        print(f"\nFull response:\n{json.dumps(result, indent=2)}")
    except httpx.HTTPStatusError as e:
        # Some GHL accounts need fields added separately after object creation
        print(f"\n  Object creation with inline fields failed — trying two-step approach...")
        payload_no_fields = {
            "locationId": LOCATION_ID,
            "name": "Items",
            "description": "Ghost Print Co. product pipeline — one record per item entry.",
            "labels": {"singular": "Item", "plural": "Items"},
        }
        r = httpx.post(f"{BASE}/custom-objects/", headers=HEADERS, json=payload_no_fields)
        r.raise_for_status()
        result = r.json()
        obj_id = result.get("id") or result.get("_id") or result.get("customObject", {}).get("id", "?")
        print(f"  Object created (id: {obj_id})")
        print("  Adding fields...")
        add_fields_to_object(obj_id, ITEM_FIELDS)

    print("\nDone.")


if __name__ == "__main__":
    main()

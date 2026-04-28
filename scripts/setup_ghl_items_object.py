"""
Create Ghost Print Co. product pipeline custom fields in GHL under a
'Ghost Print Co.' folder. Fields appear in the form builder under Contacts.

Run once. Safe to re-run — skips fields that already exist.

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
# dataType: TEXT | LARGE_TEXT | NUMERICAL | DATE | CHECKBOX | RADIO | TEXTAREA
# | FILE_UPLOAD | DROPDOWN (use picklistOptions for dropdowns)
FOLDER_NAME = "Ghost Print Co."

ITEM_FIELDS = [
    {"name": "GPC: SKU",                "fieldKey": "gpc_sku",                "dataType": "TEXT"},
    {"name": "GPC: Product Name",       "fieldKey": "gpc_product_name",       "dataType": "TEXT"},
    {
        "name": "GPC: Category",
        "fieldKey": "gpc_category",
        "dataType": "DROPDOWN",
        "picklistOptions": ["t-shirt", "hoodie", "hat", "tote", "other"],
    },
    {"name": "GPC: Base Colour",        "fieldKey": "gpc_base_colour",        "dataType": "TEXT"},
    {"name": "GPC: Brand",              "fieldKey": "gpc_brand",              "dataType": "TEXT"},
    {"name": "GPC: Year",               "fieldKey": "gpc_year",               "dataType": "TEXT"},
    {"name": "GPC: Price",              "fieldKey": "gpc_price",              "dataType": "NUMERICAL"},
    {"name": "GPC: Compare At Price",   "fieldKey": "gpc_compare_at_price",   "dataType": "NUMERICAL"},
    {"name": "GPC: Sizes Available",    "fieldKey": "gpc_sizes_available",    "dataType": "TEXT"},
    {"name": "GPC: Available Quantity", "fieldKey": "gpc_available_quantity", "dataType": "NUMERICAL"},
    {"name": "GPC: Raw Notes",          "fieldKey": "gpc_raw_notes",          "dataType": "LARGE_TEXT"},
    {"name": "GPC: Image URL 1",        "fieldKey": "gpc_image_url_1",        "dataType": "TEXT"},
    {"name": "GPC: Image URL 2",        "fieldKey": "gpc_image_url_2",        "dataType": "TEXT"},
    {"name": "GPC: Image URL 3",        "fieldKey": "gpc_image_url_3",        "dataType": "TEXT"},
    {
        "name": "GPC: Status",
        "fieldKey": "gpc_status",
        "dataType": "DROPDOWN",
        "picklistOptions": ["Draft", "Pending Approval", "Approved", "Processing", "Done", "Error"],
    },
]


def get_existing_fields() -> list[dict]:
    r = httpx.get(
        f"{BASE}/custom-fields/",
        headers=HEADERS,
        params={"locationId": LOCATION_ID, "model": "contact"},
    )
    r.raise_for_status()
    return r.json().get("customFields", [])


def get_or_create_folder(existing_fields: list[dict]) -> str | None:
    """Return folderKey of existing GPC folder, or None if folders aren't supported."""
    # Try to list folders
    r = httpx.get(
        f"{BASE}/custom-fields/",
        headers=HEADERS,
        params={"locationId": LOCATION_ID, "model": "contact"},
    )
    folders = r.json().get("folders", [])
    for f in folders:
        if f.get("name") == FOLDER_NAME:
            return f.get("id") or f.get("folderId")

    # Create folder
    r = httpx.post(
        f"{BASE}/custom-fields/folder",
        headers=HEADERS,
        json={"locationId": LOCATION_ID, "name": FOLDER_NAME},
    )
    if r.status_code in (200, 201):
        data = r.json()
        return data.get("id") or data.get("folderId") or data.get("folder", {}).get("id")
    # Folders not supported — fields will be created ungrouped
    return None


def create_field(field_def: dict, folder_id: str | None) -> dict:
    payload = {
        "locationId": LOCATION_ID,
        "name": field_def["name"],
        "fieldKey": field_def["fieldKey"],
        "dataType": field_def["dataType"],
        "model": "contact",
    }
    if folder_id:
        payload["folderId"] = folder_id
    if "picklistOptions" in field_def:
        payload["picklistOptions"] = field_def["picklistOptions"]

    r = httpx.post(f"{BASE}/custom-fields/", headers=HEADERS, json=payload)
    if r.status_code not in (200, 201):
        print(f"    [!] {r.status_code}: {r.text}")
        return {}
    return r.json().get("customField", r.json())


def main():
    print(f"Location: {LOCATION_ID}")
    print(f"Base URL: {BASE}\n")

    # ── Fetch existing fields ─────────────────────────────────────────────────
    print("Fetching existing custom fields...")
    try:
        existing = get_existing_fields()
    except httpx.HTTPStatusError as e:
        print(f"  [!] Failed to fetch fields: {e.response.status_code} — {e.response.text}")
        return

    existing_keys = {f.get("fieldKey", "") for f in existing}
    print(f"  Found {len(existing)} existing fields")

    # ── Get or create folder ──────────────────────────────────────────────────
    print(f"\nSetting up '{FOLDER_NAME}' folder...")
    folder_id = get_or_create_folder(existing)
    print(f"  Folder ID: {folder_id or 'not supported — fields will be ungrouped'}")

    # ── Create fields ─────────────────────────────────────────────────────────
    print("\nCreating fields...")
    created, skipped = 0, 0
    for field in ITEM_FIELDS:
        if field["fieldKey"] in existing_keys:
            print(f"  SKIP (exists): {field['name']}")
            skipped += 1
            continue
        result = create_field(field, folder_id)
        if result:
            fid = result.get("id") or result.get("_id") or "?"
            print(f"  OK: {field['name']}  (id: {fid})")
            created += 1
        else:
            print(f"  FAILED: {field['name']}")

    print(f"\nDone. Created: {created}  Skipped: {skipped}")
    print("\nNext: In GHL go to Sites → Forms and add these fields to a new form.")


if __name__ == "__main__":
    main()

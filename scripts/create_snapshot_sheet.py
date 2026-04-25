"""
Populate a snapshot documentation Google Sheet in the Agency Unbound V2.0 format.
Tabs: Overview, Assets, Modules, Stakeholders.

The service account cannot create Google Sheets (no Drive storage quota),
so YOU must create a blank Google Sheet first:
  1. Go to Drive > Snapshots > GHL-Snapshots folder
  2. Create a new Google Sheet (name it whatever you want — the script sets the title)
  3. Share it with the service account as Editor
  4. Copy the sheet ID from the URL and pass it with --sheet-id

Usage:
    python scripts/create_snapshot_sheet.py --sheet-id <id> --snapshot "My Snapshot Name"
    python scripts/create_snapshot_sheet.py --sheet-id <id>  # uses Ghost Print Co. default
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from google.oauth2 import service_account
import gspread
from googleapiclient.discovery import build

from config import settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HDR_BG = {"red": 0.47, "green": 0.08, "blue": 0.17}
HDR_FG = {"red": 1.0,  "green": 1.0,  "blue": 1.0}


def _fmt_header(sheet_id: int, row: int, num_cols: int) -> list:
    return [{
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": row, "endRowIndex": row + 1,
                      "startColumnIndex": 0, "endColumnIndex": num_cols},
            "cell": {"userEnteredFormat": {
                "backgroundColor": HDR_BG,
                "textFormat": {"foregroundColor": HDR_FG, "bold": True, "fontSize": 8},
                "verticalAlignment": "MIDDLE",
            }},
            "fields": "userEnteredFormat(backgroundColor,textFormat,verticalAlignment)",
        }
    }]


def _freeze(sheet_id: int, rows: int = 2, cols: int = 0) -> list:
    return [{"updateSheetProperties": {
        "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": rows, "frozenColumnCount": cols}},
        "fields": "gridProperties.frozenRowCount,gridProperties.frozenColumnCount",
    }}]


def build_assets_data() -> list[list]:
    """Ghost Print Co. snapshot — premium screenprint streetwear brand."""
    # Name, Asset Type, Module, Description/Function, Set up notes, Updateable, Status, Status Notes
    return [
        ["R1-1.1. User Tag Added -> Assign Contact to User", "Workflow", "Foundation",
         "Assigns new contacts to the brand owner or account rep",
         "Set the 'Assign to User' action to the correct team member.", "FALSE", "Done", ""],
        ["R0. Customer Pipeline", "Pipeline", "Foundation",
         "Tracks contacts from first touch through repeat purchase and VIP. Stages: New Lead → Drop List → First Purchase → Repeat Customer → VIP",
         "Rename stages if needed for brand language.", "FALSE", "", ""],
        ["R0. Brand Store URL", "Custom Value", "Foundation",
         "Stores the online store or Linktree URL used across all email/SMS links",
         "Update to live store URL before going live.", "TRUE", "", ""],
        ["R1. Drop-List OptIn Form", "Form", "Drop List",
         "Captures name, email, and phone from fans opting into drop announcements",
         "Embed on the brand's landing page or link in bio.", "FALSE", "", ""],
        ["R1. Drop-List", "Tag", "Drop List",
         "Applied when a contact opts into drop notifications",
         "Applied via R1-1.0 workflow on form submit.", "TRUE", "", ""],
        ["R1. Ads-Streetwear", "Tag", "Drop List",
         "Identifies contacts arriving from paid social ad campaigns",
         "Connect to Meta/TikTok Ads integration and apply on lead form submit.", "TRUE", "", ""],
        ["R1-1.0. OptIn Submit -> Welcome to Drop List", "Workflow", "Drop List",
         "Triggers on Drop-List form submission; applies R1.Drop-List tag and sends welcome email",
         "Attach trigger to R1.Drop-List OptIn Form.", "FALSE", "", ""],
        ["R1-1.0. Email Welcome to Drop List", "Email Template", "Drop List",
         "Brand intro email with lookbook preview and first-look promise",
         "Update imagery and copy for Ghost Print Co. voice. Keep it short and visual.", "TRUE", "", ""],
        ["R2. Drop Announcement Email", "Email Template", "Product Drops",
         "Full-width styled drop announcement with product photos, price, and buy link",
         "Update product images and link to R0.Brand Store URL for each drop.", "TRUE", "", ""],
        ["R2. Drop Announcement SMS", "SMS Template", "Product Drops",
         "Short-form drop alert: brand name, drop name, link. Under 160 chars.",
         "Edit copy per drop. Link to store or specific product page.", "TRUE", "", ""],
        ["R2-2.0. New Drop -> Notify Drop List", "Workflow", "Product Drops",
         "Manually triggered broadcast to all contacts tagged R1.Drop-List; sends email then SMS",
         "Activate once per drop. Confirm list size before sending.", "FALSE", "", ""],
        ["R2. Waitlist", "Tag", "Product Drops",
         "Applied when a contact requests restock notification after a sold-out drop",
         "Applied by R2-2.1 workflow on waitlist form submit.", "TRUE", "", ""],
        ["R2-2.1. Sold Out -> Add to Waitlist", "Workflow", "Product Drops",
         "Collects waitlist entries after sellout; sends confirmation and notifies on restock",
         "Trigger: Waitlist form submission. Add restock branch when inventory returns.", "FALSE", "", ""],
        ["R3. Order Form 2-Step", "Form", "Purchasing",
         "Two-step checkout form embedded in the drop funnel sales page",
         "Connect to payment integration. Update product SKUs per drop.", "TRUE", "", ""],
        ["R3. Order-Pending", "Tag", "Purchasing",
         "Applied when a contact reaches checkout step 1 but has not completed payment",
         "Applied on step-1 form submit via order form settings.", "FALSE", "", ""],
        ["R3. Order-Paid", "Tag", "Purchasing",
         "Applied when payment is confirmed; triggers fulfillment and post-purchase flows",
         "Triggered by payment confirmation event from order form.", "TRUE", "", ""],
        ["R3-3.0. Order Paid -> Confirmation + Fulfillment Updates", "Workflow", "Purchasing",
         "Sends order confirmation immediately on payment; sends shipping notification when tracking is added",
         "Trigger: Tag = R3.Order-Paid. Add tracking number custom field branch.", "FALSE", "", ""],
        ["R3-3.0. Email Order Confirmation", "Email Template", "Purchasing",
         "Branded order confirmation with item summary, estimated ship time, and support contact",
         "Update brand colours and support email. Keep order details dynamic via custom fields.", "FALSE", "", ""],
        ["R3-3.0. Email Shipping Notification", "Email Template", "Purchasing",
         "Dispatch email with tracking link placeholder and brand messaging",
         "Add tracking number custom field and link. Update estimated delivery copy.", "TRUE", "", ""],
        ["R4. Customer", "Tag", "Retention",
         "Applied after first purchase is confirmed; moves contact into retention sequence",
         "Applied by R3-3.0 workflow after R3.Order-Paid tag fires.", "TRUE", "", ""],
        ["R4. VIP", "Tag", "Retention",
         "Applied after third purchase or qualifying spend threshold; unlocks early access to drops",
         "Set spend threshold in workflow condition. Update copy to reflect VIP perks.", "TRUE", "", ""],
        ["R4-1.0. Post-Purchase -> Review Request + Upsell", "Workflow", "Retention",
         "7 days after purchase sends review request; 14 days sends upsell/next drop teaser",
         "Trigger: Tag = R4.Customer. Adjust timing to match fulfilment window.", "FALSE", "", ""],
        ["R4-1.0. Email Post-Purchase Review Request", "Email Template", "Retention",
         "Styled thank-you with review ask and social share prompt (tag the brand)",
         "Add Instagram handle and review link. Keep it visual — show the product.", "TRUE", "", ""],
    ]


def build_modules_data() -> list[list]:
    return [
        ["R0", "Foundation",     "Universal assets shared across all modules",
         "Customer pipeline\nBrand custom values (store URL)\nUser assignment"],
        ["R1", "Drop List",      "Capture fans and build the pre-launch audience",
         "Opt-in form on landing page or link-in-bio\nWelcome sequence\nAd traffic tagging\nPipeline entry"],
        ["R2", "Product Drops",  "Announce new collections and manage sold-out waitlists",
         "Email + SMS blast to drop list\nDrop announcement templates\nWaitlist capture on sellout\nRestock notification"],
        ["R3", "Purchasing",     "Handle checkout, payment, and fulfillment communication",
         "2-step order form in funnel\nPayment confirmation trigger\nOrder confirmation + shipping notification\nAbandoned checkout recovery"],
        ["R4", "Retention",      "Turn buyers into repeat customers and VIP members",
         "Post-purchase review request\nUpsell sequence\nVIP tier unlock after 3rd purchase\nEarly drop access for VIPs"],
    ]


def build_stakeholders_data() -> list[list]:
    return [
        ["Contact", "Streetwear Fans",       "General audience interested in the brand's aesthetic and drops",
         "Drop notifications, lookbook content, easy checkout"],
        ["Contact", "Tattoo Artists",         "Core demographic — collectors of art-forward premium apparel",
         "Exclusive drops, collab pieces, early VIP access"],
        ["Contact", "Wholesale / Retail Partners", "Shops or studios interested in carrying the brand",
         "Wholesale inquiry flow, bulk pricing, brand assets"],
        ["User",    "Brand Owner",            "Deft — creator, artist, and primary brand voice",
         "Drop scheduling, contact visibility, revenue reporting"],
        ["User",    "Fulfillment Manager",    "Handles order processing and shipping updates",
         "Order tag notifications, tracking number updates"],
        ["Agency",  "Account Manager",        "LBKH Solutions — manages the GHL account and snapshot",
         "Snapshot health, integration status, expansion readiness"],
        ["Agency",  "Tech Support",           "LBKH technical support",
         "Access for troubleshooting integrations and workflows"],
    ]


def populate_snapshot_sheet(sheet_id: str, snapshot_name: str) -> str:
    """Populate an existing Google Sheet with the Agency Unbound snapshot format."""
    creds = service_account.Credentials.from_service_account_file(
        settings.google_service_account_file, scopes=SCOPES
    )
    gc = gspread.authorize(creds)
    sheets_svc = build("sheets", "v4", credentials=creds)

    ss = gc.open_by_key(sheet_id)
    print(f"Opened sheet: {snapshot_name}  ID: {sheet_id}")
    print(f"URL: https://docs.google.com/spreadsheets/d/{sheet_id}/edit")

    ws_overview = ss.sheet1
    ws_overview.update_title("Overview")
    existing = [ws.title for ws in ss.worksheets()]
    ws_assets       = ss.worksheet("Assets")       if "Assets"       in existing else ss.add_worksheet("Assets",       rows=200, cols=8)
    ws_modules      = ss.worksheet("Modules")      if "Modules"      in existing else ss.add_worksheet("Modules",      rows=20,  cols=5)
    ws_stakeholders = ss.worksheet("Stakeholders") if "Stakeholders" in existing else ss.add_worksheet("Stakeholders", rows=20,  cols=4)

    sheet_ids = {
        "Overview":     ws_overview.id,
        "Assets":       ws_assets.id,
        "Modules":      ws_modules.id,
        "Stakeholders": ws_stakeholders.id,
    }

    # Overview
    ws_overview.update("A1", [
        [f"Snapshot Documentation — {snapshot_name}"],
        [""],
        ["Template format: Agency Unbound V2.0 (agencyunbound.com)"],
        ["Owner: LBKH Solutions"],
        ["GHL Location ID:", settings.ghl_location_id],
        [""],
        ["Brand: Ghost Print Co. — Premium screenprint streetwear. Tattoo-culture rooted."],
        [""],
        ["Tabs:"],
        ["  Assets       — Every GHL asset in this snapshot (workflows, tags, forms, etc.)"],
        ["  Modules      — How assets are grouped into functional modules (R0–R4)"],
        ["  Stakeholders — Who interacts with the snapshot and what they need"],
    ], value_input_option="USER_ENTERED")

    # Assets
    asset_headers = ["Name", "Asset Type", "Module", "Description / Function",
                     "Set up notes", "Updateable", "Status", "Status Notes"]
    ws_assets.clear()
    ws_assets.update("A1", [["This table documents every asset in the snapshot"]], value_input_option="USER_ENTERED")
    ws_assets.update("A2", [asset_headers], value_input_option="USER_ENTERED")
    ws_assets.update("A3", build_assets_data(), value_input_option="USER_ENTERED")

    # Modules
    ws_modules.clear()
    ws_modules.update("A1", [["This table divides the snapshot into functional modules"]], value_input_option="USER_ENTERED")
    ws_modules.update("A2", [["Module ID", "Module", "Description", "Scope / Objectives"]], value_input_option="USER_ENTERED")
    ws_modules.update("A3", build_modules_data(), value_input_option="USER_ENTERED")

    # Stakeholders
    ws_stakeholders.clear()
    ws_stakeholders.update("A1", [["This table lists everyone who interacts with the snapshot"]], value_input_option="USER_ENTERED")
    ws_stakeholders.update("A2", [["Type", "Name", "Description", "What they need"]], value_input_option="USER_ENTERED")
    ws_stakeholders.update("A3", build_stakeholders_data(), value_input_option="USER_ENTERED")

    # Formatting
    requests = []
    for tab, num_cols in [("Assets", 8), ("Modules", 4), ("Stakeholders", 4)]:
        requests += _fmt_header(sheet_ids[tab], row=1, num_cols=num_cols)
        requests += _freeze(sheet_ids[tab], rows=2)
    sheets_svc.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body={"requests": requests}).execute()

    print(f"\nDone. Sheet ID: {sheet_id}")
    return sheet_id


def main():
    parser = argparse.ArgumentParser(
        description="Populate a snapshot documentation sheet (Agency Unbound V2.0 format)."
    )
    parser.add_argument("--sheet-id", required=True,
                        help="ID of an existing Google Sheet shared with the service account as Editor.")
    parser.add_argument("--snapshot", default="Ghost Print Co. — BOLDStore Snapshot V1.0",
                        help="Snapshot name shown in the Overview tab.")
    args = parser.parse_args()

    populate_snapshot_sheet(args.sheet_id, args.snapshot)


if __name__ == "__main__":
    main()

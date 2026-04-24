"""
Create a snapshot documentation Google Sheet in Drive.
Mirrors the Agency Unbound V2.0 format with 4 tabs:
  Overview, Assets, Modules, Stakeholders

Usage:
    python scripts/create_snapshot_sheet.py --snapshot "Tattoo Artist V2" --folder-id <drive_folder_id>

Requires:
    - GOOGLE_SERVICE_ACCOUNT_FILE set in .env
    - GOOGLE_DRIVE_ROOT_FOLDER_ID set in .env (used if --folder-id not supplied)
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

# ── colour palette (matches Agency Unbound dark red / yellow) ─────────────────
HDR_BG   = {"red": 0.47, "green": 0.08, "blue": 0.17}   # dark burgundy
HDR_FG   = {"red": 1.0,  "green": 1.0,  "blue": 1.0}
TITLE_BG = {"red": 1.0,  "green": 0.85, "blue": 0.0}    # yellow
TITLE_FG = {"red": 0.0,  "green": 0.0,  "blue": 0.0}


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
    """All 21 snapshot assets pre-loaded for Tattoo Artist V2."""
    return [
        # Name, Asset Type, Module, Description/Function, Set up notes, Updateable, Status, Status Notes
        ["R1-1.1. User Tag Added -> Assign Contact to User", "Workflow", "Foundations",
         "Assigns contacts to a user based on the 'assign to sale'",
         "Assign Sales User to the 'assign to user' action", "FALSE", "Done", "Changed for version 2."],
        ["R1. Ads-1", "Tag", "Lead Capture",
         "Tag applied when a lead comes from paid advertising",
         "Connect to FB/Google Ads integration.", "TRUE", "", ""],
        ["R1. OptIn Form", "Form", "Lead Capture",
         "Opt-in form to capture lead details (name, email, phone)",
         "Embed on landing page 'Opt In Funnel'.", "FALSE", "", ""],
        ["R1-1.0. OptInSubmit -> Deliver Lead Magnet", "Workflow", "Lead Capture",
         "Triggers when opt-in form submitted; adds 'Opt-In Lead' tag",
         "Attach to RE-Form-Optin.", "FALSE", "Issue", ""],
        ["R1. OptIn", "Tag", "Lead Capture",
         "Indicates contact opted in via lead magnet funnel",
         "Applied via workflow RE-WF-OptInSubmit.", "TRUE", "", ""],
        ["R3. Calendar Consultation", "Calendar", "Appointments",
         "Booking calendar for consultations",
         "Integrate with artist's Google calendar.", "FALSE", "", ""],
        ["R2-2.0. Appointment Booked -> Reminder Series", "Workflow", "Appointments",
         "Sends confirmation and reminder emails for booked appointments",
         "Trigger: Appointment Created on RE-Calendar-Consu", "FALSE", "", ""],
        ["R2-2.0. Email Reminder 01", "Email Template", "Appointments",
         "Reminder email for booked calls",
         "Edit the template for client use", "TRUE", "", ""],
        ["R0. Buyer Pipeline", "Pipeline", "Sales",
         "Pipeline for tracking leads from new lead to close. Stages: New Lead → Appointment → Sales Call → Closed",
         "Update stage names for tattoo studio context", "FALSE", "", ""],
        ["R2-2.1. Appointment Complete -> Follow up emails", "Workflow", "Sales",
         "Follow-up automation after sales call; sends SMS + emails",
         "Trigger: Opportunity Stage = 'Sales Call'.", "FALSE", "", ""],
        ["R3. Order 2 Step", "Form", "Sales Funnel",
         "2-step order form for service/product purchase",
         "Embed on Funnel Sales Page.", "TRUE", "", ""],
        ["R3. Order-Pending", "Tag", "Sales Funnel",
         "Applied when contact reaches order form but hasn't paid",
         "Add tag on form submission step 1.", "FALSE", "", ""],
        ["R2-3.0. Appointment Complete -> Payment reminder", "Workflow", "Sales Funnel",
         "Sends reminder to complete payment",
         "Trigger: Tag = RE-Tag-OrderPending.", "FALSE", "", ""],
        ["R3. Order-Paid", "Tag", "Sales Funnel",
         "Applied when order payment completed",
         "Triggered via order form payment confirmation.", "TRUE", "", ""],
        ["R3-4.0. Product Purchased -> Update contact and pipeline", "Workflow", "Sales Funnel",
         "Automation triggered when product is purchased successfully",
         "Trigger: Tag RE-Tag-OrderPaid.", "TRUE", "", ""],
        ["R3-1.0. Email Purchase Confirmation", "Email Template", "Sales Funnel",
         "Purchase confirmation email with client portal access",
         "Attach inside RE-WF-ProductPurchased.", "FALSE", "", ""],
        ["R0. Client Portal URL", "Custom Value", "Client Area",
         "Stores client portal link for purchased users",
         "Custom value used in emails and workflows.", "FALSE", "", ""],
        ["R1. Ads- Property", "Custom Field", "Lead Capture",
         "Stores property/service address of client inquiry",
         "Map to order and opt-in forms.", "FALSE", "", ""],
        ["R1. Desired Move-in Date", "Custom Field", "Appointments",
         "Date field for client's target appointment timeline",
         "Add to forms and consultation intake.", "TRUE", "", ""],
        ["R4-1.0. Product Purchased -> Client Onboarding Sequence", "Workflow", "Client Area",
         "On purchase, sends onboarding instructions and adds tags",
         "Trigger: RE-Tag-OrderPaid.", "FALSE", "", ""],
        ["R4-1.0. Email Onboarding", "Email Template", "Client Area",
         "Email with onboarding steps and client portal login", "", "FALSE", "", ""],
    ]


def create_snapshot_sheet(snapshot_name: str, folder_id: str) -> str:
    creds = service_account.Credentials.from_service_account_file(
        settings.google_service_account_file, scopes=SCOPES
    )
    gc = gspread.authorize(creds)
    drive = build("drive", "v3", credentials=creds)
    sheets_svc = build("sheets", "v4", credentials=creds)

    # ── Create workbook ───────────────────────────────────────────────────────
    ss = gc.create(snapshot_name, folder_id=folder_id)
    sid = ss.id
    print(f"Created sheet: {snapshot_name}  ID: {sid}")
    print(f"URL: https://docs.google.com/spreadsheets/d/{sid}/edit")

    # ── Rename default sheet to Overview and add others ───────────────────────
    ws_overview = ss.sheet1
    ws_overview.update_title("Overview")
    ws_assets      = ss.add_worksheet("Assets",       rows=200, cols=8)
    ws_modules     = ss.add_worksheet("Modules",      rows=20,  cols=5)
    ws_stakeholders = ss.add_worksheet("Stakeholders", rows=20,  cols=4)

    sheet_ids = {
        "Overview":      ws_overview.id,
        "Assets":        ws_assets.id,
        "Modules":       ws_modules.id,
        "Stakeholders":  ws_stakeholders.id,
    }

    # ── Overview tab ──────────────────────────────────────────────────────────
    ws_overview.update("A1", [
        [f"Snapshot Documentation — {snapshot_name}"],
        [""],
        ["Template format: Agency Unbound V2.0 (agencyunbound.com)"],
        ["Owner: LBKH Solutions"],
        ["GHL Location ID:", settings.ghl_location_id],
        [""],
        ["Tabs:"],
        ["  Assets       — Every GHL asset in this snapshot (workflows, tags, forms, etc.)"],
        ["  Modules      — How assets are grouped into functional modules (R0–R4)"],
        ["  Stakeholders — Who interacts with the snapshot and what they need"],
    ], value_input_option="USER_ENTERED")

    # ── Assets tab ────────────────────────────────────────────────────────────
    asset_headers = ["Name", "Asset Type", "Module", "Description / Function",
                     "Set up notes", "Updateable", "Status", "Status Notes"]
    ws_assets.update("A1", [["This table documents every asset in the snapshot"]], value_input_option="USER_ENTERED")
    ws_assets.update("A2", [asset_headers], value_input_option="USER_ENTERED")
    ws_assets.update("A3", build_assets_data(), value_input_option="USER_ENTERED")

    # ── Modules tab ───────────────────────────────────────────────────────────
    ws_modules.update("A1", [["This table divides the snapshot into functional modules"]], value_input_option="USER_ENTERED")
    ws_modules.update("A2", [["Module ID", "Module", "Description", "Scope / Objectives"]], value_input_option="USER_ENTERED")
    ws_modules.update("A3", [
        ["R0", "Foundation",     "All universal assets like custom values",            "Base layer — custom values, pipelines, tags shared across all modules"],
        ["R1", "Opt in Lead",    "Opt in leads from ads, to send lead magnet",         "Funnel page with opt-in form\nFollow up with 3 emails to book sales call\nNotify sales team of new leads\nAdd leads to a pipeline"],
        ["R2", "Sales Calendar", "Simple booking page to book sales calls",            "Calendar booking widget\nNotifications and reminder emails\nNotify sales team\nMove pipeline stage to booked\nCancellation flows\nCharge for no-shows"],
        ["R3", "Purchasing",     "Handles all sales and purchase workflows",           "Purchase the Sales product\nEmail reminders to pay\nRefund policies\nTerms of service"],
        ["R4", "Onboarding",     "Onboarding after sales that orients them to tools",  "Client portal access\nOnboarding email sequence\nTool orientation"],
    ], value_input_option="USER_ENTERED")

    # ── Stakeholders tab ──────────────────────────────────────────────────────
    ws_stakeholders.update("A1", [["This table lists everyone who interacts with the snapshot"]], value_input_option="USER_ENTERED")
    ws_stakeholders.update("A2", [["Type", "Name", "Description", "What they need"]], value_input_option="USER_ENTERED")
    ws_stakeholders.update("A3", [
        ["Contact", "Prospective Clients",  "People inquiring about tattoo services",          "Booking info, pricing, portfolio"],
        ["Contact", "Referral Partners",    "Partners who send client referrals",              "Referral tracking, commission updates"],
        ["User",    "Tattoo Artist",        "Main user — assigned to contacts",                "Booking notifications, client messages"],
        ["User",    "Studio Manager",       "Admin managing bookings and follow-ups",          "Full pipeline visibility, payment status"],
        ["Agency",  "Account Manager",      "LBKH Solutions account manager",                 "Snapshot health, integration status"],
        ["Agency",  "Tech Support",         "LBKH technical support",                         "Access for troubleshooting"],
    ], value_input_option="USER_ENTERED")

    # ── Formatting (header rows + freeze) ─────────────────────────────────────
    requests = []
    for tab, num_cols in [("Assets", 8), ("Modules", 4), ("Stakeholders", 4)]:
        sid_tab = sheet_ids[tab]
        requests += _fmt_header(sid_tab, row=1, num_cols=num_cols)  # row index 1 = row 2
        requests += _freeze(sid_tab, rows=2)

    sheets_svc.spreadsheets().batchUpdate(spreadsheetId=ss.id, body={"requests": requests}).execute()

    print(f"\nDone. Sheet ID: {ss.id}")
    print(f"Add this to your .env:  SNAPSHOT_TATTOO_ARTIST_SHEET_ID={ss.id}")
    return ss.id


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", default="Tattoo Artist Snapshot V2.0 — BOLDStore")
    parser.add_argument("--folder-id", default=None)
    args = parser.parse_args()

    folder_id = args.folder_id or settings.google_drive_root_folder_id
    if not folder_id:
        print("ERROR: supply --folder-id or set GOOGLE_DRIVE_ROOT_FOLDER_ID in .env")
        sys.exit(1)

    create_snapshot_sheet(args.snapshot, folder_id)


if __name__ == "__main__":
    main()

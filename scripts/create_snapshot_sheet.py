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
    """Tattoo Artist V2 snapshot assets — used as the reference template."""
    return [
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

    # Rename / create tabs
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
    ws_modules.update("A3", [
        ["R0", "Foundation",     "All universal assets like custom values",            "Base layer — custom values, pipelines, tags shared across all modules"],
        ["R1", "Opt in Lead",    "Opt in leads from ads, to send lead magnet",         "Funnel page with opt-in form\nFollow up with 3 emails to book sales call\nNotify sales team of new leads\nAdd leads to a pipeline"],
        ["R2", "Sales Calendar", "Simple booking page to book sales calls",            "Calendar booking widget\nNotifications and reminder emails\nNotify sales team\nMove pipeline stage to booked\nCancellation flows\nCharge for no-shows"],
        ["R3", "Purchasing",     "Handles all sales and purchase workflows",           "Purchase the Sales product\nEmail reminders to pay\nRefund policies\nTerms of service"],
        ["R4", "Onboarding",     "Onboarding after sales that orients them to tools",  "Client portal access\nOnboarding email sequence\nTool orientation"],
    ], value_input_option="USER_ENTERED")

    # Stakeholders
    ws_stakeholders.clear()
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
    parser.add_argument("--snapshot", default="BOLDStore — Tattoo Artist V2 Snapshot",
                        help="Snapshot name shown in the Overview tab.")
    args = parser.parse_args()

    populate_snapshot_sheet(args.sheet_id, args.snapshot)


if __name__ == "__main__":
    main()

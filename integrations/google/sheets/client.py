"""Google Sheets client — read/write structured data."""
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build

from config import settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

MIME_SHEET = "application/vnd.google-apps.spreadsheet"


class SheetsClient:
    def __init__(self):
        creds = service_account.Credentials.from_service_account_file(
            settings.google_service_account_file, scopes=SCOPES
        )
        self._gc = gspread.authorize(creds)
        self._drive = build("drive", "v3", credentials=creds)

    # ── Workbook helpers ──────────────────────────────────────────────────────

    def open_by_id(self, sheet_id: str) -> gspread.Spreadsheet:
        return self._gc.open_by_key(sheet_id)

    def create_sheet(self, title: str, folder_id: str | None = None) -> str:
        """Create a Google Sheet via the Drive API and return its ID."""
        meta = {"name": title, "mimeType": MIME_SHEET}
        if folder_id:
            meta["parents"] = [folder_id]
        f = self._drive.files().create(body=meta, fields="id").execute()
        return f["id"]

    # ── Read ──────────────────────────────────────────────────────────────────

    def read_tab(self, sheet_id: str, tab: str) -> list[dict]:
        """Return all rows of a tab as list of dicts (header row = keys)."""
        ws = self.open_by_id(sheet_id).worksheet(tab)
        return ws.get_all_records()

    def read_range(self, sheet_id: str, tab: str, range_: str) -> list[list]:
        ws = self.open_by_id(sheet_id).worksheet(tab)
        return ws.get(range_)

    # ── Write ─────────────────────────────────────────────────────────────────

    def append_row(self, sheet_id: str, tab: str, row: list) -> dict:
        ws = self.open_by_id(sheet_id).worksheet(tab)
        return ws.append_row(row, value_input_option="USER_ENTERED")

    def append_rows(self, sheet_id: str, tab: str, rows: list[list]) -> dict:
        ws = self.open_by_id(sheet_id).worksheet(tab)
        return ws.append_rows(rows, value_input_option="USER_ENTERED")

    def update_cell(self, sheet_id: str, tab: str, row: int, col: int, value) -> dict:
        ws = self.open_by_id(sheet_id).worksheet(tab)
        return ws.update_cell(row, col, value)

    def update_range(self, sheet_id: str, tab: str, range_: str, values: list[list]) -> dict:
        ws = self.open_by_id(sheet_id).worksheet(tab)
        return ws.update(range_, values, value_input_option="USER_ENTERED")

    def clear_tab(self, sheet_id: str, tab: str) -> dict:
        ws = self.open_by_id(sheet_id).worksheet(tab)
        return ws.clear()

    # ── Tab management ────────────────────────────────────────────────────────

    def ensure_tab(self, sheet_id: str, tab: str, headers: list[str] | None = None) -> gspread.Worksheet:
        """Get or create a worksheet tab, optionally writing headers."""
        ss = self.open_by_id(sheet_id)
        try:
            ws = ss.worksheet(tab)
        except gspread.WorksheetNotFound:
            ws = ss.add_worksheet(title=tab, rows=1000, cols=26)
            if headers:
                ws.append_row(headers, value_input_option="USER_ENTERED")
        return ws

    # ── BOLDStore master sheet bootstrap ──────────────────────────────────────

    def bootstrap_master_sheet(self, sheet_id: str | None = None, folder_id: str | None = None) -> str:
        """
        Create (or open existing) master tracking sheet and ensure all tabs exist.
        Returns the sheet ID.
        """
        sid = sheet_id or settings.google_sheets_master_id
        print(f"  [DEBUG] sheet_id arg={repr(sheet_id)}  settings.master_id={repr(settings.google_sheets_master_id)}  sid={repr(sid)}")
        if not sid:
            print("  [DEBUG] No existing sheet ID — creating new sheet via Drive API")
            sid = self.create_sheet("BOLDStore — Master Tracker", folder_id=folder_id)
            print(f"  [DEBUG] create_sheet returned: {repr(sid)}")
        else:
            print(f"  [DEBUG] Using existing sheet ID: {repr(sid)}")
        tabs = {
            "Contacts": ["id", "firstName", "lastName", "email", "phone", "locationId", "createdAt", "tags"],
            "Opportunities": ["id", "name", "contactId", "pipelineId", "stageId", "status", "monetaryValue", "updatedAt"],
            "Snapshots": ["name", "version", "description", "driveLink", "createdAt", "notes"],
            "SOPs": ["title", "category", "version", "driveLink", "lastReviewed", "owner"],
            "N8N-Workflows": ["id", "name", "active", "webhookPath", "description", "lastUpdated"],
            "Webhook-Log": ["timestamp", "event", "contactId", "payload_summary", "status"],
            "Expansion-Tracker": ["clientName", "locationId", "snapshotApplied", "n8nCloned", "driveCloned", "goLiveDate", "notes"],
        }
        for tab, headers in tabs.items():
            self.ensure_tab(sid, tab, headers)
        return sid

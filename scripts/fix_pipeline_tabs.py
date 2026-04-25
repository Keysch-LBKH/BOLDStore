"""
Fix: remove erroneously created Brand Profile and Item Input tabs,
then populate the existing Config and Items tabs correctly.
Run once, then delete this script.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from google.oauth2 import service_account
import gspread

from config import settings
from scripts.create_product_pipeline_sheets import (
    BRAND_PROFILE_ROWS,
    ITEM_INPUT_HEADERS,
    ITEM_INPUT_SAMPLE,
)

SHEET_ID = "1HUajSpYtnnP2iM4vWCR8dJxGeAl947FTzH7SoTNmvOU"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = service_account.Credentials.from_service_account_file(
    settings.google_service_account_file, scopes=SCOPES
)
gc = gspread.authorize(creds)
ss = gc.open_by_key(SHEET_ID)

tabs = {ws.title: ws for ws in ss.worksheets()}
print(f"Existing tabs: {list(tabs.keys())}")

# Delete the two tabs we added by mistake
for bad_tab in ["Brand Profile", "Item Input"]:
    if bad_tab in tabs:
        ss.del_worksheet(tabs[bad_tab])
        print(f"  Deleted: {bad_tab}")

# Refresh tab list
tabs = {ws.title: ws for ws in ss.worksheets()}

# Populate Config tab
if "Config" in tabs:
    ws = tabs["Config"]
    ws.clear()
    ws.update("A1", [["Field", "Value", "Notes"]], value_input_option="USER_ENTERED")
    ws.update("A2", BRAND_PROFILE_ROWS, value_input_option="USER_ENTERED")
    ws.freeze(rows=1)
    ws.format("A1:C1", {
        "backgroundColor": {"red": 0.47, "green": 0.08, "blue": 0.17},
        "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True},
    })
    print("  Populated: Config")
else:
    print("  WARNING: No 'Config' tab found — check the tab name in the sheet")

# Populate Items tab
if "Items" in tabs:
    ws = tabs["Items"]
    ws.clear()
    ws.update("A1", [ITEM_INPUT_HEADERS], value_input_option="USER_ENTERED")
    ws.update("A2", [ITEM_INPUT_SAMPLE], value_input_option="USER_ENTERED")
    ws.freeze(rows=1)
    ws.format("A1:U1", {
        "backgroundColor": {"red": 0.47, "green": 0.08, "blue": 0.17},
        "textFormat": {"foregroundColor": {"red": 1, "green": 1, "blue": 1}, "bold": True},
    })
    # Highlight Status column (K)
    ws.format("K1:K200", {"backgroundColor": {"red": 1.0, "green": 0.95, "blue": 0.8}})
    print("  Populated: Items")
else:
    print("  WARNING: No 'Items' tab found — check the tab name in the sheet")

print("\nDone.")

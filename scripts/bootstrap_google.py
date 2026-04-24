"""
Run once to scaffold Google Drive folders and bootstrap the master Sheet.
Usage:
    python scripts/bootstrap_google.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from integrations.google import DriveClient, SheetsClient


def main():
    print("=== BOLDStore Google Bootstrap ===\n")

    drive = DriveClient()
    sheets = SheetsClient()

    print("Scaffolding Drive folder structure...")
    folder_ids = drive.scaffold_boldstore_structure()
    for name, fid in folder_ids.items():
        link = drive.get_web_link(fid)
        print(f"  {name:<30} {fid}  {link}")

    print("\nBootstrapping master Google Sheet...")
    sid = sheets.bootstrap_master_sheet()
    print(f"  Master sheet ID: {sid}")

    print("\nDone. Copy the IDs above into your .env file.")


if __name__ == "__main__":
    main()

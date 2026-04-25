"""
Run once to scaffold Google Drive folders and bootstrap the master Sheet.
Usage:
    python scripts/bootstrap_google.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import settings
from integrations.google.drive import DriveClient
from integrations.google.sheets import SheetsClient


def main():
    print("=== BOLDStore Google Bootstrap ===\n")

    drive = DriveClient()
    sheets = SheetsClient()

    print("Scaffolding Drive folder structure...")
    folder_ids = drive.scaffold_boldstore_structure()
    for name, fid in folder_ids.items():
        link = f"https://drive.google.com/drive/folders/{fid}"
        print(f"  {name:<30} {fid}  {link}")

    owner = settings.google_drive_owner_email
    if owner:
        print(f"\nSharing folders with {owner}...")
        for name, fid in folder_ids.items():
            if fid:
                drive.share(fid, owner, role="writer")
                print(f"  shared {name}")
    else:
        print("\nSkipping folder sharing — set GOOGLE_DRIVE_OWNER_EMAIL in .env to enable.")

    print("\nBootstrapping master Google Sheet...")
    sid = sheets.bootstrap_master_sheet(folder_id=folder_ids.get("Spreadsheets"))
    print(f"  Master sheet ID: {sid}")

    print("\nDone. Copy the IDs above into your .env file.")


if __name__ == "__main__":
    main()

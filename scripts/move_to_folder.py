"""Move files into a target Drive folder. Run once, then delete."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.google.drive import DriveClient

TARGET_FOLDER = "1_k6hyDeGxfKov5FZ86elHEmVfRuPm1YD"

FILES = {
    "Ghost Print Co. snapshot documentation": "18G2VQoUqXHEdVEST8DeNbGduHRdAhYNLMoE_P0Oh548",
    "Ghost Print Co. Sale Items pipeline":    "1HUajSpYtnnP2iM4vWCR8dJxGeAl947FTzH7SoTNmvOU",
}

drive = DriveClient()
for name, fid in FILES.items():
    drive.move_to_folder(fid, TARGET_FOLDER)
    print(f"  Moved: {name}")

print(f"\nBoth sheets are now in folder: https://drive.google.com/drive/folders/{TARGET_FOLDER}")

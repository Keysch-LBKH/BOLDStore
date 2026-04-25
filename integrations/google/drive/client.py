"""Google Drive client — folder creation, file upload, document management."""
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

from config import settings

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
]

MIME_FOLDER = "application/vnd.google-apps.folder"
MIME_DOC = "application/vnd.google-apps.document"


class DriveClient:
    def __init__(self):
        creds = service_account.Credentials.from_service_account_file(
            settings.google_service_account_file, scopes=SCOPES
        )
        self._svc = build("drive", "v3", credentials=creds)

    # ── Folders ───────────────────────────────────────────────────────────────

    def create_folder(self, name: str, parent_id: str | None = None) -> str:
        """Create a folder and return its ID."""
        meta = {"name": name, "mimeType": MIME_FOLDER}
        if parent_id:
            meta["parents"] = [parent_id]
        f = self._svc.files().create(body=meta, fields="id").execute()
        return f["id"]

    def get_or_create_folder(self, name: str, parent_id: str | None = None) -> str:
        """Return existing folder ID or create it."""
        effective_parent = (parent_id or settings.google_drive_root_folder_id or "").strip()
        if effective_parent:
            parent_clause = f"and '{effective_parent}' in parents "
        else:
            parent_clause = "and 'root' in parents "
            effective_parent = None
        query = f"name='{name}' and mimeType='{MIME_FOLDER}' {parent_clause}and trashed=false"
        results = self._svc.files().list(q=query, fields="files(id,name)").execute()
        files = results.get("files", [])
        if files:
            return files[0]["id"]
        return self.create_folder(name, effective_parent)

    def list_folder(self, folder_id: str) -> list[dict]:
        results = self._svc.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id,name,mimeType,createdTime,modifiedTime)",
        ).execute()
        return results.get("files", [])

    # ── Files ─────────────────────────────────────────────────────────────────

    def create_doc(self, name: str, parent_id: str | None = None) -> str:
        """Create an empty Google Doc and return its ID."""
        meta = {"name": name, "mimeType": MIME_DOC}
        if parent_id:
            meta["parents"] = [parent_id]
        f = self._svc.files().create(body=meta, fields="id").execute()
        return f["id"]

    def upload_text(self, name: str, content: str, parent_id: str | None = None, mime: str = "text/plain") -> str:
        """Upload a plaintext file and return its ID."""
        meta = {"name": name}
        if parent_id:
            meta["parents"] = [parent_id]
        media = MediaIoBaseUpload(io.BytesIO(content.encode()), mimetype=mime)
        f = self._svc.files().create(body=meta, media_body=media, fields="id").execute()
        return f["id"]

    def share(self, file_id: str, email: str, role: str = "writer"):
        """Share a file or folder with an email address. Silently skips if already shared."""
        try:
            self._svc.permissions().create(
                fileId=file_id,
                body={"type": "user", "role": role, "emailAddress": email},
                sendNotificationEmail=False,
            ).execute()
        except Exception as exc:
            if "already" in str(exc).lower():
                return
            raise

    def get_web_link(self, file_id: str) -> str:
        f = self._svc.files().get(fileId=file_id, fields="webViewLink").execute()
        return f.get("webViewLink", "")

    # ── BOLDStore folder scaffold ─────────────────────────────────────────────

    def scaffold_boldstore_structure(self, root_id: str | None = None) -> dict[str, str]:
        """
        Create the canonical BOLDStore folder hierarchy.
        Returns a dict mapping logical names to Drive folder IDs.
        """
        root = root_id or settings.google_drive_root_folder_id
        ids: dict[str, str] = {"root": root}

        top_level = ["Snapshots", "SOPs", "Spreadsheets", "Architecture", "Credentials-Vault"]
        for folder in top_level:
            ids[folder] = self.get_or_create_folder(folder, root)

        # Sub-folders under Snapshots
        for sub in ["GHL-Snapshots", "N8N-Workflows", "Config-Exports"]:
            ids[f"Snapshots/{sub}"] = self.get_or_create_folder(sub, ids["Snapshots"])

        # Store snapshot master folder
        ids["Snapshots/Store Snapshots"] = self.get_or_create_folder("Store Snapshots", ids["Snapshots"])
        ids["Snapshots/Store Snapshots/BOLDStore Master"] = self.get_or_create_folder(
            "BOLDStore Master", ids["Snapshots/Store Snapshots"]
        )

        # Sub-folders under SOPs
        for sub in ["GHL", "N8N", "Google", "Onboarding", "Expansion"]:
            ids[f"SOPs/{sub}"] = self.get_or_create_folder(sub, ids["SOPs"])

        return ids

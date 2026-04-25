from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _strip_comment(v: str) -> str:
    """Strip inline .env comments — some python-dotenv versions don't do this."""
    return v.split("#")[0].strip()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # GHL
    ghl_api_key: str = ""
    ghl_agency_api_key: str = ""
    ghl_location_id: str = ""
    ghl_base_url: str = "https://services.leadconnectorhq.com"
    ghl_webhook_secret: str = ""

    # N8N
    n8n_base_url: str = ""
    n8n_api_key: str = ""
    n8n_boldstore_tag_id: str = "akucO9y04icJCSvB"

    # Google
    google_service_account_file: str = "service_account.json"
    google_drive_root_folder_id: str = ""
    google_drive_owner_email: str = ""
    google_sheets_master_id: str = ""

    # Ghost Print Co. product pipeline (single workbook, multiple tabs)
    ghost_print_pipeline_sheet_id: str = ""

    # App
    app_env: str = "development"
    app_port: int = 8000
    webhook_base_url: str = ""
    log_level: str = "INFO"

    @field_validator(
        "ghl_api_key", "ghl_agency_api_key", "ghl_location_id", "ghl_webhook_secret",
        "n8n_base_url", "n8n_api_key", "n8n_boldstore_tag_id",
        "google_service_account_file", "google_drive_root_folder_id",
        "google_drive_owner_email", "google_sheets_master_id",
        "ghost_print_pipeline_sheet_id",
        "webhook_base_url",
        mode="before",
    )
    @classmethod
    def strip_inline_comments(cls, v: str) -> str:
        return _strip_comment(v) if isinstance(v, str) else v


settings = Settings()

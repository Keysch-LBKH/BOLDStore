from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # Google
    google_service_account_file: str = "service_account.json"
    google_drive_root_folder_id: str = ""
    google_sheets_master_id: str = ""

    # App
    app_env: str = "development"
    app_port: int = 8000
    webhook_base_url: str = ""
    log_level: str = "INFO"


settings = Settings()

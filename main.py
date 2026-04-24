"""BOLDStore — main FastAPI application."""
import structlog
import uvicorn
from fastapi import FastAPI

from config import settings
from integrations.ghl.webhooks import router as ghl_webhook_router

log = structlog.get_logger()

app = FastAPI(
    title="BOLDStore Integration Platform",
    version="0.1.0",
    docs_url="/docs" if settings.app_env != "production" else None,
)

app.include_router(ghl_webhook_router)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.app_port, reload=settings.app_env == "development")

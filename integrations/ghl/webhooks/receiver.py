"""GHL inbound webhook receiver — validates signature, routes to handlers."""
import hashlib
import hmac
import json
from typing import Callable

import structlog
from fastapi import APIRouter, Header, HTTPException, Request

from config import settings

log = structlog.get_logger()
router = APIRouter(prefix="/webhooks/ghl", tags=["GHL Webhooks"])

# Registry: event_type -> list of handler coroutines
_handlers: dict[str, list[Callable]] = {}


def on_event(event_type: str):
    """Decorator to register a handler for a GHL event type."""
    def decorator(fn: Callable):
        _handlers.setdefault(event_type, []).append(fn)
        return fn
    return decorator


def _verify_signature(body: bytes, signature: str) -> bool:
    """GHL signs the raw body with HMAC-SHA256 using the webhook secret."""
    if not settings.ghl_webhook_secret:
        return True  # skip verification if no secret configured (dev mode)
    expected = hmac.new(
        settings.ghl_webhook_secret.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/")
async def receive(
    request: Request,
    x_ghl_signature: str = Header(default=""),
):
    body = await request.body()

    if not _verify_signature(body, x_ghl_signature):
        raise HTTPException(status_code=401, detail="Invalid GHL webhook signature")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = payload.get("type") or payload.get("event")
    log.info("ghl_webhook_received", event_type=event_type)

    for handler in _handlers.get(event_type, []):
        try:
            await handler(payload)
        except Exception:
            log.exception("ghl_webhook_handler_error", event_type=event_type, handler=handler.__name__)

    return {"status": "ok"}

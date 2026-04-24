"""GHL REST API client — wraps the LeadConnector v1 API."""
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings


class GHLClient:
    def __init__(self):
        self._base = settings.ghl_base_url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {settings.ghl_api_key}",
            "Content-Type": "application/json",
            "Version": "2021-07-28",
        }

    # ── internal ─────────────────────────────────────────────────────────────

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _get(self, path: str, params: dict | None = None) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self._base}/{path.lstrip('/')}", headers=self._headers, params=params)
            r.raise_for_status()
            return r.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _post(self, path: str, body: dict) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self._base}/{path.lstrip('/')}", headers=self._headers, json=body)
            r.raise_for_status()
            return r.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _put(self, path: str, body: dict) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.put(f"{self._base}/{path.lstrip('/')}", headers=self._headers, json=body)
            r.raise_for_status()
            return r.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _delete(self, path: str) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.delete(f"{self._base}/{path.lstrip('/')}", headers=self._headers)
            r.raise_for_status()
            return r.json()

    # ── Contacts ─────────────────────────────────────────────────────────────

    async def get_contact(self, contact_id: str) -> dict:
        return await self._get(f"/contacts/{contact_id}")

    async def search_contacts(self, query: str, location_id: str | None = None) -> dict:
        params = {"query": query, "locationId": location_id or settings.ghl_location_id}
        return await self._get("/contacts/search", params=params)

    async def create_contact(self, data: dict) -> dict:
        data.setdefault("locationId", settings.ghl_location_id)
        return await self._post("/contacts/", data)

    async def update_contact(self, contact_id: str, data: dict) -> dict:
        return await self._put(f"/contacts/{contact_id}", data)

    # ── Pipelines / Opportunities ─────────────────────────────────────────────

    async def get_pipelines(self, location_id: str | None = None) -> dict:
        params = {"locationId": location_id or settings.ghl_location_id}
        return await self._get("/opportunities/pipelines", params=params)

    async def get_opportunity(self, opportunity_id: str) -> dict:
        return await self._get(f"/opportunities/{opportunity_id}")

    async def create_opportunity(self, data: dict) -> dict:
        data.setdefault("locationId", settings.ghl_location_id)
        return await self._post("/opportunities/", data)

    async def update_opportunity(self, opportunity_id: str, data: dict) -> dict:
        return await self._put(f"/opportunities/{opportunity_id}", data)

    # ── Conversations ─────────────────────────────────────────────────────────

    async def get_conversations(self, contact_id: str) -> dict:
        params = {"contactId": contact_id, "locationId": settings.ghl_location_id}
        return await self._get("/conversations/search", params=params)

    async def send_message(self, conversation_id: str, message: str, msg_type: str = "SMS") -> dict:
        return await self._post(f"/conversations/{conversation_id}/messages", {
            "type": msg_type,
            "message": message,
        })

    # ── Calendars ─────────────────────────────────────────────────────────────

    async def get_calendars(self, location_id: str | None = None) -> dict:
        params = {"locationId": location_id or settings.ghl_location_id}
        return await self._get("/calendars/", params=params)

    async def get_appointments(self, calendar_id: str, start: str, end: str) -> dict:
        params = {"calendarId": calendar_id, "startTime": start, "endTime": end}
        return await self._get("/calendars/appointments", params=params)

    # ── Webhooks (management) ─────────────────────────────────────────────────

    async def list_webhooks(self, location_id: str | None = None) -> dict:
        params = {"locationId": location_id or settings.ghl_location_id}
        return await self._get("/webhooks/", params=params)

    async def create_webhook(self, url: str, events: list[str], location_id: str | None = None) -> dict:
        return await self._post("/webhooks/", {
            "locationId": location_id or settings.ghl_location_id,
            "url": url,
            "events": events,
        })

    async def delete_webhook(self, webhook_id: str) -> dict:
        return await self._delete(f"/webhooks/{webhook_id}")

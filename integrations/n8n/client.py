"""N8N API client — triggers workflows and manages executions."""
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings


class N8NClient:
    def __init__(self):
        self._base = settings.n8n_base_url.rstrip("/") + "/api/v1"
        self._headers = {
            "X-N8N-API-KEY": settings.n8n_api_key,
            "Content-Type": "application/json",
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _get(self, path: str, params: dict | None = None) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self._base}/{path.lstrip('/')}", headers=self._headers, params=params)
            r.raise_for_status()
            return r.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _post(self, path: str, body: dict | None = None) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{self._base}/{path.lstrip('/')}", headers=self._headers, json=body or {})
            r.raise_for_status()
            return r.json()

    # ── Workflows ─────────────────────────────────────────────────────────────

    async def list_workflows(self, active_only: bool = False) -> dict:
        params = {"active": "true"} if active_only else {}
        return await self._get("/workflows", params=params)

    async def get_workflow(self, workflow_id: str) -> dict:
        return await self._get(f"/workflows/{workflow_id}")

    async def activate_workflow(self, workflow_id: str) -> dict:
        return await self._post(f"/workflows/{workflow_id}/activate")

    async def deactivate_workflow(self, workflow_id: str) -> dict:
        return await self._post(f"/workflows/{workflow_id}/deactivate")

    # ── Executions ────────────────────────────────────────────────────────────

    async def get_execution(self, execution_id: str) -> dict:
        return await self._get(f"/executions/{execution_id}")

    async def list_executions(self, workflow_id: str | None = None, limit: int = 20) -> dict:
        params: dict = {"limit": limit}
        if workflow_id:
            params["workflowId"] = workflow_id
        return await self._get("/executions", params=params)

    # ── Webhook trigger ───────────────────────────────────────────────────────

    async def trigger_webhook(self, webhook_path: str, data: dict) -> dict:
        """Trigger an N8N webhook-triggered workflow directly."""
        url = f"{settings.n8n_base_url.rstrip('/')}/webhook/{webhook_path.lstrip('/')}"
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=data)
            r.raise_for_status()
            return r.json()

    # ── Credentials ───────────────────────────────────────────────────────────

    async def list_credentials(self) -> dict:
        return await self._get("/credentials")

    # ── Health ────────────────────────────────────────────────────────────────

    async def health(self) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{settings.n8n_base_url.rstrip('/')}/healthz")
            r.raise_for_status()
            return r.json()

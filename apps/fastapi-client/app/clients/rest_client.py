import httpx
from app.schema import GibberishPayload, ProcessResult
from app import settings

_client = httpx.AsyncClient()


async def call_rest(payload: GibberishPayload) -> ProcessResult:
    """Send a payload to the REST server and return the processed result."""
    response = await _client.post(
        f"{settings.GO_SERVER_REST_URL}/process",
        json=payload.model_dump(),
        headers={"Authorization": f"Bearer {settings.GO_SERVER_AUTH_TOKEN}"},
    )
    response.raise_for_status()
    return ProcessResult.model_validate(response.json())

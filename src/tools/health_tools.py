import httpx
from src.server import mcp
from src.services.auth_service import FASTAPI_BASE_URL

@mcp.tool()
async def check_backend_health() -> str:
    """Checks if the backend API server is up and responsive."""
    async with httpx.AsyncClient(base_url=FASTAPI_BASE_URL, timeout=5.0) as client:
        try:
            response = await client.get("/healthz")
            return f"System Status: {response.json()}"
        except httpx.RequestError as e:
            return f"Backend unreachable. Error: {e}"
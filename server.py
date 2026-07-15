import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("FastAPI Agent Bridge")

FASTAPI_BASE_URL = "http://localhost:8000"

#tool1
@mcp.tool()
async def check_system_health() ->str:
    '''tests the connection with the fastapi backend'''
    async with httpx.AsyncClient(base_url=FASTAPI_BASE_URL, timeout=5.0) as client:
        try:
            response = await client.get("/healthz")
            if response.status_code == 200:
                return f"Connection successful! Backend response: {response.json()}"
            return f"Failed to connect. Backend returned status code: {response.status_code}"
        except httpx.RequestError as e:
            return f"Connection error. Is the FastAPI app running at {FASTAPI_BASE_URL}? Error: {e}"


#tool2
@mcp.tool()
async def list_api_keys() -> str:
    """    Retrieves a list of all existing API keys generated for the user account.    """
    BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIzZTUwZmNkNS1jNDY3LTQ3ODYtYmI5YS1lYmRkNzYyNThiZWMiLCJyb2xlIjoidXNlciIsImp0aSI6IjIwYTM0N2M2LTQ2YWItNGMxZi05ODU1LWY3Njk4YjYyYTY0MCIsInR5cGUiOiJhY2Nlc3MiLCJleHAiOjE3ODQxNDI3NDd9.Hzo-zc21iS64HkmYC1Yo7Ks6Y3qpz3vcR5Vz8NXdLxw"
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}"
    }

    async with httpx.AsyncClient(base_url=FASTAPI_BASE_URL, headers=headers) as client:
        try:
            response = await client.get("/api_f/v1/api-keys/")
            if response.status_code == 200:
                return f"Active API Keys:\n{response.json()}"
            return f"Backend returned error {response.status_code}: {response.text}"
            
        except httpx.RequestError as e:
            return f"Network communication error: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
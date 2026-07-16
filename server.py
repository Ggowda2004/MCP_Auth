import httpx
from mcp.server.fastmcp import FastMCP
import json
import os

mcp = FastMCP("FastAPI Agent Bridge")

FASTAPI_BASE_URL = "http://localhost:8000"
TOKEN_FILE = ".mcp_tokens.json"

async def get_authenticated_client() -> httpx.AsyncClient:

    if not os.path.exists(TOKEN_FILE):
        raise RuntimeError("No tokens found. Please run login_cli.py first.")
    
    with open(TOKEN_FILE, "r") as f:
        tokens = json.load(f)
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    client = httpx.AsyncClient(base_url=FASTAPI_BASE_URL, timeout=5.0)
    client.headers.update({"Authorization":f"Bearer {access_token}"})

    profile_check = await client.get("/auth_f/v1/auth/me")
    if profile_check.status_code == 401:
        print("Access token expired. Attempting automatic refresh...")
        refresh_response = await client.post(
            "/auth_f/v1/auth/refresh", 
            json={"refresh_token": refresh_token} # Adjust schema to match your backend refresh expectation
        )

        if refresh_response.status_code == 200:
            new_tokens = refresh_response.json()
            access_token = new_tokens.get("access_token")
            refresh_token = new_tokens.get("refresh_token", refresh_token)


            with open(TOKEN_FILE, "w") as f:
                json.dump({"access_token": access_token, "refresh_token": refresh_token}, f)

            client.headers.update({"Authorization": f"Bearer {access_token}"})
            print("Token successfully refreshed and saved!")
        else:
            await client.aclose()
            raise RuntimeError("Session expired completely. Please run login_cli.py again.")
            
    return client




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
    try:
            async with get_authenticated_client() as client:
                response = await client.get("/api_f/v1/api-keys/")
            if response.status_code == 200:
                return f"Active API Keys:\n{response.json()}"
            return f"Backend returned error {response.status_code}: {response.text}"
            
    except httpx.RequestError as e:
        return f"Network communication error: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
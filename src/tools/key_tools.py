import os
import json
import httpx
from src.server import mcp
from src.services.auth_service import FASTAPI_BASE_URL, TOKEN_FILE, get_valid_access_token
from src.services.gui_service import launch_login_window

@mcp.tool()
async def trigger_desktop_login() -> str:
    """Launches a secure graphical window on the user's desktop to log in."""
    success = launch_login_window()
    return "🎉 Success! Session restored." if success else "❌ Login cancelled."

@mcp.tool()
async def list_api_keys() -> str:
    """Retrieves a list of all existing API keys generated for the user account."""
    try:
        token = await get_valid_access_token()
        async with httpx.AsyncClient(base_url=FASTAPI_BASE_URL, timeout=5.0) as client:
            response = await client.get("/api_f/v1/api-keys/", headers={"Authorization": f"Bearer {token}"})
            return f"Active API Keys:\n{response.json()}" if response.status_code == 200 else f"Error: {response.text}"
    except Exception as e:
        return f"Failure: {str(e)}"

@mcp.tool()
async def create_api_key(key_name: str) -> str:
    """Generates and returns a brand new API key for the user account."""
    try:
        token = await get_valid_access_token()
        async with httpx.AsyncClient(base_url=FASTAPI_BASE_URL, timeout=5.0) as client:
            response = await client.post(
                "/api_f/v1/api-keys/", 
                headers={"Authorization": f"Bearer {token}"}, 
                json={"name": key_name}
            )
            return f"Successfully created key:\n{response.json()}" if response.status_code == 201 else f"Error: {response.text}"
    except Exception as e:
        return f"Failure: {str(e)}"

@mcp.tool()
async def delete_api_key(key_id: str) -> str:
    """Permanently revokes and deletes an existing API key using its unique ID."""
    try:
        token = await get_valid_access_token()
        async with httpx.AsyncClient(base_url=FASTAPI_BASE_URL, timeout=5.0) as client:
            response = await client.delete(
                f"/api_f/v1/api-keys/{key_id}", 
                headers={"Authorization": f"Bearer {token}"}
            )
            return f"Successfully revoked key: {key_id}" if response.status_code == 204 else f"Error: {response.text}"
    except Exception as e:
        return f"Failure: {str(e)}"

@mcp.tool()
async def logout_user() -> str:
    """Safely logs the user out of the backend system and destroys all local session credentials."""
    try:
        if not os.path.exists(TOKEN_FILE):
            return "Already logged out."
        try:
            access_token = await get_valid_access_token()
            with open(TOKEN_FILE, "r") as f:
                refresh_token = json.load(f).get("refresh_token")
            async with httpx.AsyncClient(base_url=FASTAPI_BASE_URL, timeout=5.0) as client:
                await client.post(
                    "/auth_f/v1/auth/logout", 
                    headers={"Authorization": f"Bearer {access_token}"}, 
                    cookies={"refresh_token": refresh_token}
                )
        except Exception:
            pass
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        return "🎉 Success! Logged out and local cache wiped clean."
    except Exception as e:
        return f"Error: {str(e)}"

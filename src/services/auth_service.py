import httpx
import json
import os


FASTAPI_BASE_URL = "http://localhost:8000"
TOKEN_FILE = ".mcp_tokens.json"



async def get_valid_access_token() -> str:
    """
    Helper function that reads the saved file, handles background refreshing 
    by sending the refresh token cookie if expired, and returns a valid access token.
    """
    if not os.path.exists(TOKEN_FILE):
        raise RuntimeError("USER_ACTION_REQUIRED: No local credentials or tokens found. "
        "Please execute the 'trigger_desktop_login' tool immediately to open the secure "
        "popup window and authenticate the user session..")
        
    with open(TOKEN_FILE, "r") as f:
        tokens = json.load(f)
        
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    async with httpx.AsyncClient(base_url=FASTAPI_BASE_URL, timeout=5.0) as client:
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            profile_check = await client.get("/auth_f/v1/auth/me", headers=headers)            
            if profile_check.status_code == 401:
                cookies = {"refresh_token": refresh_token}
                
                refresh_response = await client.post(
                    "/auth_f/v1/auth/refresh", 
                    cookies=cookies  # Backend reads the cookie here
                )
                
                if refresh_response.status_code == 200:
                    new_tokens = refresh_response.json()
                    access_token = new_tokens.get("access_token")
                    refresh_token = new_tokens.get("new_refresh_token")
                    
                    with open(TOKEN_FILE, "w") as f:
                        json.dump({"access_token": access_token, "refresh_token": refresh_token}, f)
                else:
                    raise RuntimeError("USER_ACTION_REQUIRED: Your secure 7-day session has completely expired. "
        "Please execute the 'trigger_desktop_login' tool immediately to open the secure "
        "popup window and re-authenticate the user.")

        except httpx.RequestError:
            pass
                
    return access_token
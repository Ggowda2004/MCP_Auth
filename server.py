import httpx
from mcp.server.fastmcp import FastMCP
import json
import os

mcp = FastMCP("FastAPI Agent Bridge")

FASTAPI_BASE_URL = "http://localhost:8000"
TOKEN_FILE = ".mcp_tokens.json"

async def get_valid_access_token() -> str:
    """
    Helper function that reads the saved file, handles background refreshing 
    by sending the refresh token cookie if expired, and returns a valid access token.
    """
    if not os.path.exists(TOKEN_FILE):
        raise RuntimeError("No tokens found. Please run login_cli.py first.")
        
    with open(TOKEN_FILE, "r") as f:
        tokens = json.load(f)
        
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    async with httpx.AsyncClient(base_url=FASTAPI_BASE_URL, timeout=5.0) as client:
        # 1. Use the access token header to check profile health
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            profile_check = await client.get("/auth_f/v1/auth/me", headers=headers)
            
            # 2. If access token is expired, trigger the refresh
            if profile_check.status_code == 401:
                
                # NEW: Format the refresh token as a cookie dictionary
                cookies = {"refresh_token": refresh_token}
                
                # Call refresh endpoint passing the cookies dictionary
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
                    backend_error_text = refresh_response.text
        
                    raise RuntimeError(
                        f"REFRESH_FAILED_BY_BACKEND (Status {refresh_response.status_code}):\n"
                        f"Exact Backend Message: {backend_error_text}\n\n"
                        f"Please run login_cli.py to manually reset."
                    )
        except httpx.RequestError:
            pass
                
    return access_token




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
    """
    Retrieves a list of all existing API keys generated for the user account.
    """
    try:
        token = await get_valid_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        async with httpx.AsyncClient(base_url=FASTAPI_BASE_URL, timeout=5.0) as client:
            response = await client.get("/api_f/v1/api-keys/", headers=headers)
            
            if response.status_code == 200:
                return f"Active API Keys:\n{response.json()}"
            return f"Backend returned error {response.status_code}: {response.text}"
            
    except Exception as e:
        return f"Authentication or connection failure: {str(e)}"



#tool3
@mcp.tool()
async def create_api_key(key_name:str)-> str:
    '''
    Generates and returns a new api key'''

    try:
        token = await get_valid_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"name": key_name} 

        async with httpx.AsyncClient(base_url=FASTAPI_BASE_URL, timeout=5.0) as client:
            response = await client.post("/api_f/v1/api-keys/", headers=headers, json=payload)

            if response.status_code in [200, 201]:
                return f"Successfully created new key:\n{response.json()}"
            return f"Failed to create key. Status: {response.status_code}, Detail: {response.text}"
    except Exception as e:
        return f"Error executing tool: {str(e)}"


#tool4
@mcp.tool()
async def delete_api_key(key_id:str) -> str:
    '''Used to delete a api key'''
    try:
        token = await get_valid_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        async with httpx.AsyncClient(base_url=FASTAPI_BASE_URL, timeout=5.0) as client:
            response = await client.delete(f"/api_f/v1/api-keys/{key_id}", headers=headers)

            if response.status_code == 204:
                return f"Successfully revoked a key:\n{key_id}"
            return f"Failed to delete key. Status: {response.status_code}, Detail: {response.text}"
    except Exception as e:
        return f"Error executing tool: {str(e)}"    
    
            
#tool5
@mcp.tool()
async def logout_user():
    '''Logout the user'''
    try:
        if not os.path.exists(TOKEN_FILE):
            return "You are already logged out. No active session file was found."

        with open(TOKEN_FILE, "r") as f:
            tokens = json.load(f)
        
        try:
            #fix
            access_token = await get_valid_access_token()
            refresh_token = tokens.get("refresh_token")

            headers = {"Authorization": f"Bearer {access_token}"}
            cookies = {"refresh_token": refresh_token}

            async with httpx.AsyncClient(base_url=FASTAPI_BASE_URL, timeout=5.0) as client:
                response = await client.post("/auth_f/v1/auth/logout", headers=headers, cookies=cookies)

                if response.status_code == 200:
                    backend_msg = "Backend server session terminated successfully."
                else:
                    backend_msg = f"Backend returned status {response.status_code}, forcing local cleanup anyway."
            
        except Exception as auth_err:
            # If get_valid_access_token fails because the 7 days are up, we can't notify the backend,
            # but we should still proceed and force a local logout!
            backend_msg = f"Backend session already dead or unreachable ({str(auth_err)}). Proceeding with local logout."

        os.remove(TOKEN_FILE)
        return f"🎉 Success! {backend_msg} Your local `.mcp_tokens.json` file has been deleted. You are now logged out."
    except Exception as e:
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        return f"Logged out with local override. Local tokens cleared. (Details: {str(e)})"


import tkinter as tk
from tkinter import messagebox

# --- TOOL 6: SECURE INTERACTIVE DESKTOP LOGIN ---
@mcp.tool()
async def trigger_desktop_login() -> str:
    """
    Launches a secure graphical window on the user's desktop to log in.
    Use this immediately when the session is expired or missing.
    """
    # 1. Create a hidden state holder to pass data out of the window thread
    login_result = {"success": False, "error": None}

    def submit_login():
        email = email_entry.get()
        password = password_entry.get()

        if not email or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        # 2. Call your existing FastAPI login endpoint right here
        try:
            url = f"{FASTAPI_BASE_URL}/auth_f/v1/auth/login"
            payload = {"username": email, "password": password}
            
            # Form submission or JSON body matching your login_cli.py setup
            response = httpx.post(url, data=payload, timeout=5.0)
            
            if response.status_code == 200:
                tokens = response.json()
                
                # 3. Write securely to your working disk storage
                with open(TOKEN_FILE, "w") as f:
                    json.dump({
                        "access_token": tokens.get("access_token"),
                        "refresh_token": tokens.get("refresh_token")
                    }, f, indent=4)
                
                login_result["success"] = True
                root.destroy() # Close the window on success
            else:
                messagebox.showerror("Login Failed", f"Backend error ({response.status_code}): {response.text}")
        except Exception as e:
            messagebox.showerror("Network Error", f"Could not reach backend: {str(e)}")

    # 4. Build the actual native UI window layout
    root = tk.Tk()
    root.title("Secure MCP Authenticator")
    root.geometry("350x200")
    root.resizable(False, False)
    root.attributes("-topmost", True) # Force window to pop up over Claude Desktop

    # UI Fields
    tk.Label(root, text="FastAPI Backend Secure Login", font=("Arial", 12, "bold")).pack(pady=10)
    
    tk.Label(root, text="Email:").pack()
    email_entry = tk.Entry(root, width=30)
    email_entry.pack()

    tk.Label(root, text="Password:").pack()
    password_entry = tk.Entry(root, show="*", width=30) # Mask character input for security
    password_entry.pack()

    tk.Button(root, text="Login & Connect", command=submit_login, bg="green", fg="white").pack(pady=15)

    # 5. Start the native window event loop (Hangs until window is closed or success)
    root.mainloop()

    if login_result["success"]:
        return "🎉 Success! The user logged in securely via the desktop window. Session restored."
    return "❌ Login cancelled or failed. The user closed the window without authenticating."



if __name__ == "__main__":
    mcp.run(transport="stdio")
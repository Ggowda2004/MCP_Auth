import json
import os
import httpx

FASTAPI_BASE_URL = "http://localhost:8000"
TOKEN_FILE = ".mcp_tokens.json"

def run_login():
    print("--- MCP Project Local Login Setup ---")
    email = input("Enter email: ")
    password = input("Enter password: ")

    # 1. Hit your real login endpoint
    url = f"{FASTAPI_BASE_URL}/auth_f/v1/auth/login"
    payload = {"username": email, "password": password} # Adjust keys to match your backend schemas

    try:
        response = httpx.post(url, data=payload, timeout=5.0) # Use json=payload if your backend expects JSON instead of Form data
        
        if response.status_code == 200:
            tokens = response.json()
            
            # 2. Extract tokens (Adjust keys based on your real backend response names)
            token_data = {
                "access_token": tokens.get("access_token"),
                "refresh_token": tokens.get("refresh_token")
            }

            # 3. Save to a secure local file hidden from the AI
            with open(TOKEN_FILE, "w") as f:
                json.dump(token_data, f, indent=4)
                
            print("\n🎉 Success! Tokens saved locally. Your MCP server can now authenticate automatically.")
        else:
            print(f"\n❌ Login failed ({response.status_code}): {response.text}")
            
    except httpx.RequestError as e:
        print(f"\n❌ Could not connect to FastAPI backend: {e}")

if __name__ == "__main__":
    run_login()

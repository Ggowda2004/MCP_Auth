import json
import httpx
import tkinter as tk
from tkinter import messagebox
from src.services.auth_service import FASTAPI_BASE_URL, TOKEN_FILE

def launch_login_window() -> bool:
    """Renders a secure Tkinter GUI login modal on top of active desktop layers."""
    login_result = {"success": False}
    def submit_login():
        email = email_entry.get()
        password = password_entry.get()
        if not email or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        try:
            url = f"{FASTAPI_BASE_URL}/auth_f/v1/auth/login"
            response = httpx.post(url, data={"username": email, "password": password}, timeout=5.0)
            
            if response.status_code == 200:
                tokens = response.json()
                with open(TOKEN_FILE, "w") as f:
                    json.dump({
                        "access_token": tokens.get("access_token"), 
                        "refresh_token": tokens.get("refresh_token")
                    }, f, indent=4)
                login_result["success"] = True
                root.destroy()
            else:
                messagebox.showerror("Login Failed", f"Backend error ({response.status_code})")
        except Exception as e:
            messagebox.showerror("Network Error", f"Could not reach backend: {str(e)}")

    root = tk.Tk()
    root.title("Secure MCP Authenticator")
    root.geometry("350x200")
    root.resizable(False, False)
    root.attributes("-topmost", True)

    tk.Label(root, text="FastAPI Backend Secure Login", font=("Arial", 12, "bold")).pack(pady=10)
    tk.Label(root, text="Email:").pack()
    email_entry = tk.Entry(root, width=30)
    email_entry.pack()
    tk.Label(root, text="Password:").pack()
    password_entry = tk.Entry(root, show="*", width=30)
    password_entry.pack()
    tk.Button(root, text="Login & Connect", command=submit_login, bg="green", fg="white").pack(pady=15)
    root.mainloop()

    return login_result["success"]
# 🔌 Enterprise FastAPI Model Context Protocol (MCP) Bridge

A highly secure, completely decoupled, and modular Model Context Protocol (MCP) server built with Python and the official `mcp` SDK. This bridge acts as an intelligent proxy layer for your core FastAPI backend—enabling LLM interfaces (like Claude Desktop) to safely interact with production endpoints using state-of-the-art token rotation, secure local storage, and desktop-native interactive authentication.

---

## 🏗️ Architectural Overview

This repository utilizes a **Server-Tools-Service** architecture to strictly isolate the AI model from raw application code, business workflows, and sensitive security components.

```
       ┌────────────────────────┐
       │ Claude Desktop / LLM   │
       └───────────┬────────────┘
                    │
                    ▼ (Standard input/output - stdio JSON Protocol)
┌────────────────────────────────────────────────────────┐
│ Standalone MCP Bridge Environment                      │
│                                                          │
│  ┌────────────────────────┐                             │
│  │     main.py Engine     │                             │
│  └───────────┬────────────┘                             │
│              │ (Imports & Registers)                    │
│              ▼                                          │
│  ┌────────────────────────┐                             │
│  │   src/tools/ Layer     │◀─── Reads / Writes ───┐      │
│  │ (Exposes Docs to AI)   │                        │      │
│  └───────────┬────────────┘                        ▼      │
└──────────────┼───────────────────────────┌────────────────┐
               │ (Executes Logic)           │ .mcp_tokens    │
               ▼                            │  (Hidden disk  │
┌────────────────────────┐                  │   credentials) │
│  src/services/ Layer   │──────────────────└────────────────┘
│ (HTTPX & Tkinter GUI)  │
└──────────────┬─────────┘
               │
               ▼ (Asynchronous network operations with Cookie/Header injection)
       ┌────────────────────────┐
       │  Live FastAPI Backend  │ (e.g., http://localhost:8000)
       └────────────────────────┘
```

### Key Design Pillars

- **Decoupled System Identity** — Runs completely independent of your main FastAPI codebase, preventing dependency bloat and minimizing code collision.
- **AI-Blind Authentication** — The LLM never handles passwords, user logins, or active JWT parameters.
- **State-Aware Token Rotation** — Automatically manages short-lived access headers alongside rotated, secure `SameSite=Lax` refresh cookies.
- **Proactive LLM Loop Interaction** — Uses standardized error tokens (`USER_ACTION_REQUIRED`) embedded directly into script handlers to trigger conversational state transitions smoothly.

---

## 📁 Repository Directory Matrix

```
fastapi-mcp-bridge/
├── .mcp_tokens.json       # [AUTOMATED] Cross-platform hidden token credentials cache
├── pyproject.toml         # Python workspace environment settings managed via `uv`
├── main.py                # High-utility orchestration entry point
└── src/
    ├── __init__.py
    ├── server.py           # Unified single-instantiation home for FastMCP configurations
    ├── services/           # Pure logic engines (Zero MCP logic allowed here)
    │   ├── __init__.py
    │   ├── auth_service.py # Handles HTTPX requests, file interactions, and rotation loops
    │   └── gui_service.py  # Builds the Tkinter system overlay window forms
    └── tools/              # AI Interaction Layer (Zero UI/Core file logic here)
        ├── __init__.py
        ├── health_tools.py # Baseline server diagnostic utilities
        └── key_tools.py    # Enterprise API key asset management & logout operations
```

## 📝 Core MCP Integration Notes(only for developer) (Read Before Modifying for refernece only)

Keep these three architectural quirks in mind when maintaining or scaling this decoupled project:

### 1. File Visibility (`.mcp_tokens.json`)
* **Behavior:** The dot (`.`) prefix transforms this file into a hidden file on macOS and Linux filesystems.
* **Purpose:** This is a standard industry convention used to keep the root project workspace clean and prevent configuration files (like `.env`) from cluttering your standard folder view. 

### 2. Standard Output Restrictions (`print()` Hazard)
* **Behavior:** **NEVER** use standard `print()` statements anywhere inside your MCP execution thread files (`main.py`, `src/tools/*`, `src/services/*`).
* **Why:** The Model Context Protocol uses the standard input/output stream (`stdio`) to send raw JSON packets to the AI client or inspector. Standard `print()` statements output unformatted text directly into that stream, causing a JSON protocol syntax collision that instantly crashes the connection.
* **Debugging Workaround:** Use your tools to return data arrays directly onto your browser UI viewport screen, or utilize `sys.stderr` streams if you need deep system tracing logs.

### 3. Headless Cookie Extraction (`SameSite=Lax` Bypass)
* **Behavior:** Your FastAPI backend uses cookie attributes like `SameSite="lax"`. Your separate MCP Python framework (`httpx`) completely ignores this restriction.
* **Why:** The `SameSite` browser security matrix strictly governs standard client-side web browser tab engines to prevent cross-site identity theft vectors. A headless network engine script like `httpx` is not a browser; it interacts with cookie arrays directly as simple header attributes, bypassing the standard cross-site checks completely.

---

## 🚀 Installation & System Configuration

### 1. Prerequisites

Ensure you have the ultra-fast Python package compiler **`uv`** and **Node.js** (for testing tools) installed on your system.

### 2. Standard Workspace Setup

Clone your repository folder and compile all necessary packages inside an isolated environment:

```bash
# Navigate to the bridge directory
cd fastapi-mcp-bridge

# Sync project and download core dependencies automatically
uv pip install mcp httpx
```

---

## 🧪 Development, Testing, and Local Diagnostics

To inspect the parameters, inputs, and schemas exactly how the AI will see them, utilize the official Model Context Protocol system inspector tool.

**Fast execution bypass (Global Setup):**

Avoid long `npx` online bundle installations by tracking the engine globally:

```bash
# Install once globally
npm install -g @modelcontextprotocol/inspector

# Boot your project instantly
mcp-inspector uv run python main.py
```

Open the generated web engine in your browser profile to test live operations!

---

## 🔐 Comprehensive Security Flow Matrix

### 1. Initial / Expired Authentication Loop (Secure Popups)

When operations run for the first time, or after your secure 7-day refresh lifecycle terminates, a dedicated exceptions loop executes:

```python
# From src/services/auth_service.py
if not os.path.exists(TOKEN_FILE):
    raise RuntimeError(
        "USER_ACTION_REQUIRED: No local credentials or tokens found. "
        "Please execute the 'trigger_desktop_login' tool immediately to open the secure "
        "popup window and authenticate the user session."
    )
```

**Flow:**

1. The data tool raises a `RuntimeError` matching the text format above.
2. The AI reads the keyword `USER_ACTION_REQUIRED` and interprets the detailed description string.
3. The AI autonomously calls `trigger_desktop_login()`.
4. A native graphical Tkinter login window pops up on your computer desktop over your AI interface.
5. The password field utilizes standard security masks (`show="*"`) to avoid local exposure.
6. The credentials safely hit `/auth_f/v1/auth/login`, and write new hashes directly to `.mcp_tokens.json`. The AI is completely blind to your credentials.

### 2. State-Aware Token Rotation

Your FastAPI backend rotates the refresh token cookie on every access refresh, validating unique, non-reusable `jti` variables via a Redis blacklist cache layer. `src/services/auth_service.py` intercepts this automatically:

```
[Access Token Expired] ──► [Tool intercepts 401] ──► [Sends Refresh Cookie] ──► [Backend Generates New JTI Payload] ──► [Writes Fresh Token File to Disk]
```

---

## ⚙️ Integrating with Client Platforms (Claude Desktop Setup)

To use your completed modular agent bridge natively inside your chat conversations, connect the configuration definitions to your system client application file.

### Open configuration file destination

| Platform | Path |
|---|---|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |

### Update file block definitions

Append your directory inside the key values structure precisely:

```json
{
  "mcpServers": {
    "fastapi-enterprise-bridge": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/your/fastapi-mcp-bridge",
        "run",
        "python",
        "main.py"
      ]
    }
  }
}
```

> ⚠️ **Crucial Reference:** Double-check that your directory path is formatted as an absolute system link.

Restart your Claude Desktop client application from your machine tray completely to instantiate the tools!

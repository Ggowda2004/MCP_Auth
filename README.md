npx @modelcontextprotocol/inspector uv run python server.py -> 
1. Why .mcp_tokens.json instead of mcp_tokens.json?The dot (.) at the beginning makes it a hidden file on macOS and Linux systems.It keeps your project directory looking clean by hiding configuration metadata from standard views (like when running a simple ls command or looking at your file explorer). It is an industry convention used for configuration files (like .env, .gitignore, or .babelrc). You can safely rename it to standard mcp_tokens.json if you prefer it to be visible.

Because MCP uses stdio to communicate with the inspector using raw JSON objects, any normal print() statements in your code will break the JSON protocol and crash the inspector

samesite="lax", a standard Python script can bypass this without issues. SameSite only restricts web browsers from sharing cookies across different domain names; 
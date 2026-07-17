from src.server import mcp
#importing the tool files here will trigger the decorators and registers them to the server object
import src.tools.health_tools 
import src.tools.key_tools  

if __name__ == "__main__":
    mcp.run(transport="stdio")

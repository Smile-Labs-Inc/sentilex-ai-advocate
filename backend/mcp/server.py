from mcp.server.fastmcp import FastMCP
import os
mcp = FastMCP("SriLankaLawReader")
# Update directory to point to markdown-laws
# recursive search might be needed if you have subdirectories, but currently it is flat
ACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "markdown-laws")
@mcp.tool()
def get_act_content(act_name: str):
    """Reads the content of a specific Sri Lankan Act from local storage.
    
    Args:
        act_name: The name of the file without extension (e.g. '09-2022_E')
    """
    # Sanitize input to prevent directory traversal
    safe_name = os.path.basename(act_name)
    file_path = os.path.join(ACTS_DIR, f"{safe_name}.md") # Changed to .md
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding="utf8") as f:
            return f.read()
    return f"Act not found: {safe_name}.md in {ACTS_DIR}"
# Recommended: Add a list tool so LLMs know what files are available
@mcp.tool()
def list_available_acts():
    """Lists all available Sri Lankan Acts in the library."""
    if not os.path.exists(ACTS_DIR):
        return "Laws directory not found."
    
    files = [f.replace('.md', '') for f in os.listdir(ACTS_DIR) if f.endswith('.md')]
    return "\n".join(files)
if __name__ == "__main__":
    mcp.run(transport="stdio")
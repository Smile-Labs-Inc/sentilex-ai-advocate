from mcp.server.fastmcp import FastMCP
import os

mcp = FastMCP("SriLankaLawReader")
ACTS_DIR = "./data/Law_pdfs"

@mcp.tool()
def get_act_content(act_name: str):
    """Reads the content of a specific Sri Lankan Act from local storage."""
    file_path = os.path.join(ACTS_DIR, f"{act_name}.txt")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding="utf8") as f:
            return f.read()
    return "Act not found. Please ensure the filename is correct."

if __name__ == "__main__":
    mcp.run(transport="stdio")

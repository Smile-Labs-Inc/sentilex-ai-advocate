from mcp.server.fastmcp import FastMCP
import os
import json
from typing import List, Dict, Any, Optional

try:
    from index_engine import AntigravityIndex
except ImportError:
    # Fallback for relative import if run as a module
    from .index_engine import AntigravityIndex

mcp = FastMCP("SriLankaLawReader")

# Path Configuration
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
ACTS_DIR = os.path.join(DATA_DIR, "markdown-laws")
INDEX_DIR = os.path.join(DATA_DIR, "index")

# Initialize and Load Index
indexer = AntigravityIndex({"index_dir": INDEX_DIR})
# Try loading existing index
try:
    indexer.load()
    print(f"Loaded index from {INDEX_DIR}")
except Exception as e:
    print(f"Warning: Could not load index from {INDEX_DIR}: {e}")

@mcp.tool()
def get_act_content(act_name: str):
    """Reads the content of a specific Sri Lankan Act from local storage.
    
    Args:
        act_name: The name of the file without extension (e.g. '09-2022_E')
    """
    # Sanitize input to prevent directory traversal
    safe_name = os.path.basename(act_name)
    file_path = os.path.join(ACTS_DIR, f"{safe_name}.md") 
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding="utf8") as f:
            return f.read()
    return f"Act not found: {safe_name}.md in {ACTS_DIR}"

@mcp.tool()
def get_section_content(section_id: str) -> str:
    """
    Retrieves the full text of a specific legal section/chunk by its ID.
    
    Args:
        section_id: The unique identifier for the section (e.g., 'file:09-2024::sec-3-objectives').
    """
    if section_id in indexer.chunks:
        chunk = indexer.chunks[section_id]
        # Return structured or raw text
        heading = chunk.get("heading", "Untitled Section")
        text = chunk.get("text_plain", "")
        return f"## {heading}\n\n{text}"
    
    return f"Section ID '{section_id}' not found in index."

@mcp.tool()
def list_available_acts():
    """Lists all available Sri Lankan Acts in the library."""
    if not os.path.exists(ACTS_DIR):
        return "Laws directory not found."
    
    files = [f.replace('.md', '') for f in os.listdir(ACTS_DIR) if f.endswith('.md')]
    return "\n".join(files)

@mcp.tool()
def search_laws(query: str, filters: Optional[str] = None, limit: int = 10) -> str:
    """
    Performs a hybrid search (keyword + semantic) on the legal corpus.
    
    Args:
        query: The search query string.
        filters: Optional JSON string of filters (e.g., '{"jurisdiction": "Sri Lanka", "clause_type": "prohibition"}').
        limit: Maximum number of results to return.
    """
    parsed_filters = None
    if filters:
        try:
            parsed_filters = json.loads(filters)
        except json.JSONDecodeError:
            return "Error: Invalid JSON format for filters."

    results = indexer.search_hybrid(query=query, filters=parsed_filters, k=limit)
    
    # Format results for readability
    output = []
    for res in results:
        meta = res.get("metadata", {})
        file_id = meta.get("file_id", "unknown")
        section = meta.get("section_id", "unknown")
        text_snippet = res.get("text_plain", "")[:200] + "..."
        score = res.get("score", 0.0)
        output.append(f"[{score:.2f}] File: {file_id}, Section: {section}\nPreview: {text_snippet}\n")
    
    return "\n".join(output) if output else "No results found."

@mcp.tool()
def get_similar_chunks(chunk_id: str, limit: int = 5) -> str:
    """
    Finds chunks similar to a given chunk ID based on vector similarity.
    
    Args:
        chunk_id: The ID of the chunk to compare against.
        limit: Number of similar chunks to return.
    """
    if chunk_id not in indexer.vectors:
        return f"Error: Chunk ID '{chunk_id}' not found in index."
    
    vector = indexer.vectors[chunk_id]
    # search with empty query but provided vector
    results = indexer.search_hybrid(query="", k=limit, vector=vector)
    
    output = []
    for res in results:
        if res.get("chunk_id") == chunk_id:
            continue # Skip self
            
        meta = res.get("metadata", {})
        text_snippet = res.get("text_plain", "")[:150] + "..."
        score = res.get("score", 0.0)
        output.append(f"[{score:.2f}] ID: {res.get('chunk_id')}\nText: {text_snippet}\n")
        
    return "\n".join(output) if output else "No similar chunks found."

@mcp.resource("graph://entities")
def get_entity_graph() -> str:
    """Returns the full entity relationship graph as a JSON string."""
    return json.dumps(indexer.graph, indent=2)

@mcp.tool()
def query_graph(node_id: str, depth: int = 1) -> str:
    """
    Traverses the entity graph starting from a node.
    
    Args:
        node_id: The starting node ID.
        depth: Traversal depth (default 1).
    """
    if node_id not in indexer.graph["nodes"]:
        return f"Node '{node_id}' not found in graph."
    
    subgraph = {
        "nodes": {node_id: indexer.graph["nodes"][node_id]},
        "edges": []
    }
    
    # Simple BFS for depth
    current_level = {node_id}
    visited = {node_id}
    
    for _ in range(depth):
        next_level = set()
        for edge in indexer.graph["edges"]:
            s, t = edge["source"], edge["target"]
            if s in current_level or t in current_level:
                subgraph["edges"].append(edge)
                if s not in visited:
                    visited.add(s)
                    next_level.add(s)
                    subgraph["nodes"][s] = indexer.graph["nodes"].get(s, {})
                if t not in visited:
                    visited.add(t)
                    next_level.add(t)
                    subgraph["nodes"][t] = indexer.graph["nodes"].get(t, {})
        current_level = next_level
        
    return json.dumps(subgraph, indent=2)

if __name__ == "__main__":
    mcp.run(transport="stdio")

"""
MCP Client Adapter

This module provides a bridge between the Research Agent and the local MCP Server (AntigravityIndex).
It mimics the interface expected by the Research Agent while directly accessing the
underlying indexer for efficiency in this local deployment.
"""

import logging
from typing import List, Dict, Any, Optional
from schemas.messages import LegalSource

# Import the indexer directly from the server module
# This works because we are in the same process/environment
try:
    from .server import indexer
except ImportError:
    # Fallback if running from a different context
    try:
        from mcp_server.server import indexer
    except ImportError:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from mcp_server.server import indexer

logger = logging.getLogger(__name__)

class MCPClientError(Exception):
    """Custom exception for MCP client errors."""
    pass

class MCPClient:
    """
    Adapter to interact with the Legal Knowledge Graph (MCP Server).
    """

    def __init__(self):
        self.indexer = indexer

    def health_check(self) -> bool:
        """
        Check if the MCP server (index) is responsive.
        
        Returns:
            True if the index is loaded and accessible.
        """
        try:
            # Simple check: do we have chunks?
            return len(self.indexer.chunks) > 0
        except Exception as e:
            logger.error(f"MCP Health Check Failed: {e}")
            return False

    def query_legal_sources(self, query: str, max_sources: int = 5) -> List[LegalSource]:
        """
        Query the legal knowledge graph for relevant sources.

        Args:
            query: The search query.
            max_sources: Maximum number of sources to return.

        Returns:
            List of LegalSource objects.

        Raises:
            MCPClientError: If the query fails.
        """
        try:
            # Use the hybrid search directly from the indexer
            results = self.indexer.search_hybrid(query=query, k=max_sources)
            
            legal_sources = []
            for res in results:
                metadata = res.get("metadata", {})
                
                # Extract fields for LegalSource
                # Fallback to defaults if missing
                law_name = metadata.get("file_id", "Unknown Law")
                section_id = metadata.get("section_id", "Unknown Section")
                
                # The search result 'text_plain' is the content we want
                text = res.get("text_plain", "")
                
                # Add score to metadata for transparency
                source_metadata = metadata.copy()
                source_metadata["score"] = res.get("score", 0.0)
                source_metadata["chunk_id"] = res.get("chunk_id")

                legal_sources.append(LegalSource(
                    law_name=law_name,
                    section=section_id,
                    text=text,
                    metadata=source_metadata
                ))
                
            return legal_sources

        except Exception as e:
            logger.error(f"Error querying MCP: {e}")
            raise MCPClientError(f"Failed to query legal sources: {str(e)}")

_client_instance = None

def get_mcp_client() -> MCPClient:
    """
    Get or create the singleton MCP client instance.
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = MCPClient()
    return _client_instance

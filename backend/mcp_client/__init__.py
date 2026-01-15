"""MCP client package for legal knowledge retrieval."""

from .client import MCPClient, MCPClientError, get_mcp_client

__all__ = ["MCPClient", "MCPClientError", "get_mcp_client"]

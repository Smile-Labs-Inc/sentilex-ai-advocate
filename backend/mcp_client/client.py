"""
MCP Client Wrapper

This is the ONLY gateway to legal knowledge in the system.
All legal text must come from MCP - no external knowledge, no guessing.

The MCP service is assumed to be running locally and provides Sri Lankan legal texts.
"""

import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime

from schemas.messages import LegalSource


class MCPClientError(Exception):
    """Raised when MCP communication fails."""
    pass


class MCPClient:
    """
    Wrapper for the Model Context Protocol (MCP) service.

    This client:
    - Communicates with local MCP server
    - Returns VERBATIM legal text only
    - Does NOT interpret or summarize
    - Does NOT have fallback to general knowledge
    - Fails explicitly if MCP is unavailable
    """

    def __init__(self, mcp_host: str = None, mcp_port: int = None):
        """
        Initialize MCP client.

        Args:
            mcp_host: MCP server host (default: localhost)
            mcp_port: MCP server port (default: 3000)
        """
        self.mcp_host = mcp_host or os.getenv("MCP_HOST", "localhost")
        self.mcp_port = mcp_port or int(os.getenv("MCP_PORT", "3000"))
        self.base_url = f"http://{self.mcp_host}:{self.mcp_port}"

    def query_legal_sources(
        self,
        query: str,
        max_sources: int = 5,
        law_filter: Optional[List[str]] = None
    ) -> List[LegalSource]:
        """
        Query MCP for legal sources.

        This is a RETRIEVAL-ONLY operation. No reasoning happens here.

        Args:
            query: Legal question or topic to search
            max_sources: Maximum number of sources to return
            law_filter: Optional list of law names to restrict search

        Returns:
            List of LegalSource objects containing verbatim legal text

        Raises:
            MCPClientError: If MCP is unavailable or query fails
        """
        try:
            # TODO: Replace with actual MCP client SDK call
            # For now, this is a mock implementation showing the interface

            # In production, this would be something like:
            # from mcp_sdk import MCPClient as SDK
            # response = SDK.query(query, max_results=max_sources, filters=law_filter)

            # MOCK IMPLEMENTATION FOR DEMONSTRATION
            # In real system, this would call the MCP service
            sources = self._mock_mcp_query(query, max_sources, law_filter)

            return sources

        except Exception as e:
            raise MCPClientError(f"MCP query failed: {str(e)}")

    def get_specific_section(
        self,
        law_name: str,
        section: str
    ) -> Optional[LegalSource]:
        """
        Retrieve a specific section of a law.

        Args:
            law_name: Name of the law (e.g., "Penal Code")
            section: Section number or identifier

        Returns:
            LegalSource if found, None otherwise

        Raises:
            MCPClientError: If MCP is unavailable
        """
        try:
            # TODO: Replace with actual MCP client SDK call
            # response = SDK.get_section(law_name, section)

            # MOCK IMPLEMENTATION
            source = self._mock_get_section(law_name, section)
            return source

        except Exception as e:
            raise MCPClientError(f"MCP section retrieval failed: {str(e)}")

    def verify_citation(
        self,
        law_name: str,
        section: str
    ) -> bool:
        """
        Verify that a citation exists in MCP.

        Used by the Validation Agent to detect hallucinations.

        Args:
            law_name: Name of the law
            section: Section number or identifier

        Returns:
            True if citation exists, False otherwise
        """
        try:
            source = self.get_specific_section(law_name, section)
            return source is not None
        except MCPClientError:
            return False

    def health_check(self) -> bool:
        """
        Check if MCP service is available.

        Returns:
            True if MCP is reachable, False otherwise
        """
        try:
            # TODO: Implement actual health check
            # response = requests.get(f"{self.base_url}/health")
            # return response.status_code == 200
            return True  # Mock: assume healthy
        except:
            return False

    # ========== MOCK IMPLEMENTATIONS (REPLACE IN PRODUCTION) ==========

    def _mock_mcp_query(
        self,
        query: str,
        max_sources: int,
        law_filter: Optional[List[str]]
    ) -> List[LegalSource]:
        """
        Mock MCP query for demonstration.

        In production, this would be replaced with actual MCP SDK calls.
        """
        # This is a placeholder showing the expected data structure
        mock_sources = [
            LegalSource(
                law_name="Penal Code of Sri Lanka",
                section="296",
                text=(
                    "Section 296: Whoever does any act with such intention or knowledge "
                    "and under such circumstances that if he by that act caused death "
                    "he would be guilty of culpable homicide not amounting to murder, "
                    "shall be punished with imprisonment of either description for a term "
                    "which may extend to three years, or with fine, or with both."
                ),
                metadata={
                    "enacted": "1883",
                    "amended": "2006",
                    "chapter": "XVI - Of Offences Affecting the Human Body"
                }
            ),
            LegalSource(
                law_name="Penal Code of Sri Lanka",
                section="299",
                text=(
                    "Section 299: Whoever causes death by doing an act with the intention "
                    "of causing death, or with the intention of causing such bodily injury "
                    "as is likely to cause death, or with the knowledge that he is likely "
                    "by such act to cause death, commits the offence of culpable homicide."
                ),
                metadata={
                    "enacted": "1883",
                    "chapter": "XVI - Of Offences Affecting the Human Body"
                }
            )
        ]

        # Filter by law if requested
        if law_filter:
            mock_sources = [
                s for s in mock_sources if s.law_name in law_filter]

        return mock_sources[:max_sources]

    def _mock_get_section(
        self,
        law_name: str,
        section: str
    ) -> Optional[LegalSource]:
        """
        Mock section retrieval for demonstration.

        In production, this would be replaced with actual MCP SDK calls.
        """
        # Simulate lookup
        if "Penal Code" in law_name and section == "299":
            return LegalSource(
                law_name="Penal Code of Sri Lanka",
                section="299",
                text=(
                    "Section 299: Whoever causes death by doing an act with the intention "
                    "of causing death, or with the intention of causing such bodily injury "
                    "as is likely to cause death, or with the knowledge that he is likely "
                    "by such act to cause death, commits the offence of culpable homicide."
                ),
                metadata={
                    "enacted": "1883",
                    "chapter": "XVI - Of Offences Affecting the Human Body"
                }
            )
        return None


# Singleton instance
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """
    Get the global MCP client instance.

    This ensures a single connection pool across the application.
    """
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client

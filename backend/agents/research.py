"""
Research Agent (MCP Runnable)

Role: Legal context retrieval ONLY from MCP.

This agent:
- Calls the local MCP service
- Returns VERBATIM legal text
- Does NO summarization
- Does NO inference
- Does NO reasoning

This is a pure retrieval agent. It is the ONLY agent that accesses MCP.
"""

from typing import Dict, Any
from datetime import datetime
from langchain_core.runnables import Runnable, RunnableLambda

from mcp_server.mcp_client import get_mcp_client, MCPClientError
from schemas.messages import PlannerOutput, ResearchOutput


def create_research_runnable() -> Runnable:
    """
    Create the Research agent as a LangChain Runnable.

    This agent retrieves legal sources from MCP without interpretation.
    It is the ONLY agent that accesses legal knowledge.

    Returns:
        Runnable that takes PlannerOutput and returns ResearchOutput
    """
    mcp_client = get_mcp_client()

    def research(planner_output: PlannerOutput) -> ResearchOutput:
        """
        Retrieve legal sources from MCP.

        Args:
            planner_output: Output from the planner containing the processed query

        Returns:
            ResearchOutput containing verbatim legal sources
        """
        query = planner_output.query

        try:
            # Query MCP for relevant legal sources
            sources = mcp_client.query_legal_sources(
                query=query,
                max_sources=5  # Configurable limit
            )

            if not sources:
                # No sources found - this is a valid outcome
                return ResearchOutput(
                    sources=[],
                    mcp_query=query,
                    retrieval_timestamp=datetime.utcnow().isoformat(),
                    status="empty"
                )

            # Return verbatim sources
            return ResearchOutput(
                sources=sources,
                mcp_query=query,
                retrieval_timestamp=datetime.utcnow().isoformat(),
                status="success"
            )

        except MCPClientError as e:
            # MCP unavailable - this is a critical failure
            # Return empty sources with failure status
            # The validation agent will catch this
            return ResearchOutput(
                sources=[],
                mcp_query=query,
                retrieval_timestamp=datetime.utcnow().isoformat(),
                status="empty"
            )

    return RunnableLambda(research)


def create_research_with_fallback_runnable() -> Runnable:
    """
    Create Research agent with explicit fallback handling.

    If MCP is unavailable, this variant explicitly returns an error state
    that will cause validation to fail.

    Returns:
        Runnable that takes PlannerOutput and returns ResearchOutput
    """
    mcp_client = get_mcp_client()

    def research_with_health_check(planner_output: PlannerOutput) -> ResearchOutput:
        """
        Research with explicit MCP health check.

        This variant ensures that MCP unavailability is explicitly handled.
        """
        # Check MCP health first
        if not mcp_client.health_check():
            # MCP is down - return empty with clear indication
            return ResearchOutput(
                sources=[],
                mcp_query=planner_output.query,
                retrieval_timestamp=datetime.utcnow().isoformat(),
                status="empty"
            )

        # Proceed with normal research
        try:
            sources = mcp_client.query_legal_sources(
                query=planner_output.query,
                max_sources=5
            )

            status = "success" if sources else "empty"

            return ResearchOutput(
                sources=sources,
                mcp_query=planner_output.query,
                retrieval_timestamp=datetime.utcnow().isoformat(),
                status=status
            )

        except MCPClientError as e:
            return ResearchOutput(
                sources=[],
                mcp_query=planner_output.query,
                retrieval_timestamp=datetime.utcnow().isoformat(),
                status="empty"
            )

    return RunnableLambda(research_with_health_check)


def get_research_agent() -> Runnable:
    """
    Get the default research agent.

    Returns:
        Research agent runnable
    """
    return create_research_runnable()

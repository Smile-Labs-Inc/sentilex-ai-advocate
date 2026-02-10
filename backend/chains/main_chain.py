"""
Main Chain - Multi-Agent Legal Reasoning Pipeline

This orchestrates the complete flow:
Input → Planner → Research → Reasoning → Validation → Branch → Output

CRITICAL ARCHITECTURE:
- All communication is Planner-mediated (through the chain)
- Agents are Runnables, NOT AgentExecutors
- Validation determines if output is safe
- If validation fails → refusal
- If validation passes → synthesized output

This chain is the core of the court-admissible system.
"""

from typing import Dict, Any, Union
from langchain_core.runnables import (
    Runnable,
    RunnableLambda,
    RunnablePassthrough,
    RunnableBranch
)

from agents import (
    get_planner,
    get_research_agent,
    get_reasoning_agent,
    get_validation_agent,
    get_synthesizer_agent,
    get_refusal_agent
)
from schemas.messages import (
    UserQuery,
    PlannerOutput,
    ResearchOutput,
    ReasoningOutput,
    ValidationOutput,
    SynthesizerOutput,
    RefusalOutput
)


def create_main_chain() -> Runnable:
    """
    Create the main multi-agent chain with validation branching.

    Flow:
        UserQuery
        → Planner (routing)
        → Research (MCP retrieval)
        → Reasoning (legal analysis)
        → Validation (gatekeeper)
        → Branch:
            - If validation fails → Refusal
            - If validation passes → Synthesizer

    Returns:
        Runnable chain that takes UserQuery and returns SynthesizerOutput or RefusalOutput
    """
    audit_logger = get_audit_logger()

    # Get all agent runnables
    planner = get_planner()
    research = get_research_agent()
    reasoning = get_reasoning_agent()
    validation = get_validation_agent()
    synthesizer = get_synthesizer_agent()
    refusal = get_refusal_agent()

    # State accumulation helpers
    # These lambdas accumulate state as it flows through the pipeline

    def add_planner_output(state: Dict[str, Any]) -> Dict[str, Any]:
        """Add planner output to state and log."""
        user_query = state["user_query"]
        planner_output = planner.invoke(user_query)

        # Audit log
        audit_logger.log_agent_execution(
            agent="planner",
            input_data=user_query.dict(),
            output_data=planner_output.dict()
        )

        return {
            "user_query": user_query,
            "planner_output": planner_output
        }

    def add_research_output(state: Dict[str, Any]) -> Dict[str, Any]:
        """Add research output to state and log."""
        planner_output = state["planner_output"]
        research_output = research.invoke(planner_output)

        # Audit log
        audit_logger.log_agent_execution(
            agent="research",
            input_data=planner_output.dict(),
            output_data=research_output.dict()
        )

        return {
            **state,
            "research_output": research_output
        }

    def add_reasoning_output(state: Dict[str, Any]) -> Dict[str, Any]:
        """Add reasoning output to state and log."""
        research_output = state["research_output"]
        reasoning_output = reasoning.invoke(research_output)

        # Audit log
        audit_logger.log_agent_execution(
            agent="reasoning",
            input_data=research_output.dict(),
            output_data=reasoning_output.dict()
        )

        return {
            **state,
            "reasoning_output": reasoning_output
        }

    def add_validation_output(state: Dict[str, Any]) -> Dict[str, Any]:
        """Add validation output to state and log."""
        research_output = state["research_output"]
        reasoning_output = state["reasoning_output"]

        validation_output = validation.invoke(
            (research_output, reasoning_output))

        # Audit log
        audit_logger.log_agent_execution(
            agent="validation",
            input_data={
                "research": research_output.dict(),
                "reasoning": reasoning_output.dict()
            },
            output_data=validation_output.dict()
        )

        return {
            **state,
            "validation_output": validation_output
        }

    def synthesize_success(state: Dict[str, Any]) -> SynthesizerOutput:
        """Synthesize successful output and log."""
        research_output = state["research_output"]
        reasoning_output = state["reasoning_output"]
        validation_output = state["validation_output"]

        synthesizer_output = synthesizer.invoke(
            (research_output, reasoning_output, validation_output)
        )

        # Audit log
        audit_logger.log_agent_execution(
            agent="synthesizer",
            input_data={
                "research": research_output.dict(),
                "reasoning": reasoning_output.dict(),
                "validation": validation_output.dict()
            },
            output_data=synthesizer_output.dict()
        )

        return synthesizer_output

    def synthesize_refusal(state: Dict[str, Any]) -> RefusalOutput:
        """Synthesize refusal output and log."""
        validation_output = state["validation_output"]

        refusal_output = refusal.invoke(validation_output)

        # Audit log
        audit_logger.log_agent_execution(
            agent="refusal",
            input_data=validation_output.dict(),
            output_data=refusal_output.dict()
        )

        return refusal_output

    def route_validation(state: Dict[str, Any]) -> str:
        """
        Determine routing based on validation status.

        This is the critical branching point:
        - If validation fails → refusal path
        - If validation passes/warns → success path
        """
        validation_output = state["validation_output"]

        if validation_output.status == "fail":
            return "refusal"
        else:
            # Both "pass" and "warn" proceed to output
            # Warnings are shown in the synthesized output
            return "success"

    # Build the chain with explicit state passing
    chain = (
        # Initialize state with user query
        RunnableLambda(lambda user_query: {"user_query": user_query})

        # Planner
        | RunnableLambda(add_planner_output)

        # Research
        | RunnableLambda(add_research_output)

        # Reasoning
        | RunnableLambda(add_reasoning_output)

        # Validation
        | RunnableLambda(add_validation_output)

        # Branch based on validation
        | RunnableBranch(
            # (condition, runnable) pairs
            (lambda state: route_validation(state) == "refusal",
             RunnableLambda(synthesize_refusal)),

            (lambda state: route_validation(state) == "success",
             RunnableLambda(synthesize_success)),

            # Default (should never reach, but safety)
            RunnableLambda(synthesize_refusal)
        )
    )

    return chain


def create_simple_chain() -> Runnable:
    """
    Create a simplified chain without state accumulation.

    This is a more readable version showing the core flow.
    Use this for understanding, but prefer create_main_chain() for production.

    Returns:
        Runnable chain
    """
    # Get agents
    planner = get_planner()
    research = get_research_agent()
    reasoning = get_reasoning_agent()
    validation = get_validation_agent()
    synthesizer = get_synthesizer_agent()
    refusal = get_refusal_agent()

    # Simple linear chain (no branching in this version)
    simple_chain = (
        planner
        | research
        | reasoning
        # Placeholder for validation input
        | (lambda reasoning_out: (None, reasoning_out))
        # Note: Actual validation requires both research and reasoning outputs
        # This simplified version doesn't show the full branching
    )

    return simple_chain


def invoke_chain(user_query: UserQuery) -> Union[SynthesizerOutput, RefusalOutput]:
    """
    Invoke the main chain with a user query.

    This is the primary entry point for processing legal queries.

    Args:
        user_query: The user's legal question

    Returns:
        Either a synthesized answer or a refusal message
    """
    chain = create_main_chain()
    result = chain.invoke(user_query)
    return result


def invoke_chain_with_tracing(
    user_query: UserQuery,
    trace_name: str = "legal_query"
) -> Union[SynthesizerOutput, RefusalOutput]:
    """
    Invoke the chain with LangSmith tracing enabled.

    This is useful for debugging and auditing individual queries.

    Args:
        user_query: The user's legal question
        trace_name: Name for the trace

    Returns:
        Either a synthesized answer or a refusal message
    """
    from langsmith import traceable

    @traceable(name=trace_name)
    def traced_invoke(query: UserQuery):
        return invoke_chain(query)

    return traced_invoke(user_query)


# Export the main factory function
get_main_chain = create_main_chain

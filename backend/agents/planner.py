"""
Planner Agent (Orchestrator Runnable)

Role: Control flow ONLY. No legal reasoning. No MCP access.

This agent determines the execution path but does NOT perform any legal analysis.
It is a deterministic routing mechanism, not an intelligent agent.
"""

from typing import Dict, Any
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from schemas.messages import UserQuery, PlannerOutput


# Prompt template for the planner
# Note: This is intentionally simple and focused on routing logic only
PLANNER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal system planner. Your ONLY job is to determine execution flow.

You do NOT:
- Perform legal analysis
- Access legal databases
- Answer legal questions

You DO:
- Route queries to the appropriate execution pipeline
- Validate that queries are answerable
- Assign confidence to routing decisions

Standard execution path for all legal queries:
1. research - Retrieve legal sources from MCP
2. reason - Apply legal reasoning to sources
3. validate - Check for hallucinations and errors
4. synthesize - Format final output

Output your decision as JSON with this structure:
{{
    "steps": ["research", "reason", "validate", "synthesize"],
    "query": "<processed query>",
    "confidence": <0.0 to 1.0>
}}

Query processing rules:
- Preserve original legal terminology
- Do NOT answer the question
- Do NOT infer legal meaning
- If query is unclear, set confidence < 0.5"""),
    ("user", "{question}")
])


def create_planner_runnable(llm: ChatOpenAI = None) -> Runnable:
    """
    Create the Planner agent as a LangChain Runnable.

    The planner is deterministic and does NOT perform legal reasoning.
    It simply routes queries through the standard pipeline.

    Args:
        llm: Language model for query processing (optional, uses default if None)

    Returns:
        Runnable that takes UserQuery and returns PlannerOutput
    """

    if llm is None:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0,
        )

    def process_input(user_query: UserQuery) -> Dict[str, Any]:
        """Convert UserQuery to prompt input."""
        return {
            "question": user_query.question,
            "case_context": user_query.case_context or "None provided"
        }

    def parse_output(ai_message) -> PlannerOutput:
        """Parse LLM output into PlannerOutput schema."""
        import json

        content = ai_message.content

        # Extract JSON from response
        try:
            # Try to parse as JSON
            if isinstance(content, str):
                # Handle markdown code blocks
                if "```json" in content:
                    content = content.split("```json")[
                        1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()

                data = json.loads(content)
            else:
                data = content

            return PlannerOutput(
                steps=data["steps"],
                query=data["query"],
                confidence=data["confidence"]
            )
        except Exception as e:
            # Fallback: return standard routing with low confidence
            return PlannerOutput(
                steps=["research", "reason", "validate", "synthesize"],
                query=user_query.question,
                confidence=0.3  # Low confidence due to parsing error
            )

    # Build the runnable chain
    planner_chain = (
        RunnableLambda(process_input)
        | PLANNER_PROMPT
        | llm
        | RunnableLambda(parse_output)
    )

    return planner_chain


def create_deterministic_planner() -> Runnable:
    """
    Create a fully deterministic planner that requires NO LLM.

    This is the recommended approach for production court-admissible systems.
    All legal queries follow the same path: research → reason → validate → synthesize.

    Returns:
        Runnable that takes UserQuery and returns PlannerOutput
    """
    def deterministic_plan(user_query: UserQuery) -> PlannerOutput:
        """
        Deterministic planning: ALL queries follow the same pipeline.

        This eliminates LLM non-determinism from the control flow.
        """
        # Simple validation: ensure query is not empty
        confidence = 1.0 if len(user_query.question.strip()) > 10 else 0.4

        return PlannerOutput(
            steps=["research", "reason", "validate", "synthesize"],
            query=user_query.question.strip(),
            confidence=confidence
        )

    return RunnableLambda(deterministic_plan)


# Default planner (use deterministic for production)
def get_planner() -> Runnable:
    """
    Get the default planner runnable.

    Uses deterministic planner for maximum court admissibility.
    """
    return create_deterministic_planner()

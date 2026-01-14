"""
Legal Reasoning Agent

Role: Apply law to question using ONLY provided MCP sources.

This agent:
- Uses ONLY the legal sources provided by the Research Agent
- Must explicitly state limitations
- Must cite all sources used
- Must NOT invent legal content
- Must NOT use external legal knowledge

The reasoning chain is NOT exposed to users (to prevent jailbreaking).
Only the final analysis is shown.
"""

from typing import Dict, Any, Tuple
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from schemas.messages import ResearchOutput, ReasoningOutput, LegalSource


# Prompt template for legal reasoning
# This is CRITICAL: it must enforce strict source adherence
REASONING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a legal reasoning engine for Sri Lankan law.

CRITICAL RULES (violating these will result in validation failure):

1. Use ONLY the legal sources provided below. Do NOT use external legal knowledge.
2. If sources are insufficient, you MUST say so explicitly in limitations.
3. Every legal statement MUST be cited to a provided source.
4. Do NOT invent case law, precedents, or legal interpretations.
5. Do NOT make assumptions about facts not stated in the query.
6. Be explicit about uncertainty and limitations.

Your output MUST follow this structure:

ANALYSIS:
- Apply the provided legal sources to the question
- Cite each source used: [Law Name, Section X]
- State the legal conclusion that can be drawn
- Use clear, professional legal language

LIMITATIONS:
- State what CANNOT be concluded from available sources
- Identify missing legal context
- Note any ambiguities in the query
- List any assumptions made

CITATIONS USED:
- List each source identifier used in format: "Law Name - Section X"

Example:
ANALYSIS:
Based on Section 299 of the Penal Code of Sri Lanka, culpable homicide is defined as causing death with intention to cause death or bodily injury likely to cause death [Penal Code, Section 299]. The act described in the query involves...

LIMITATIONS:
The provided sources do not address the specific question of intent in cases of medical negligence. Additional sources on medical malpractice law would be needed to fully answer this question.

CITATIONS USED:
- Penal Code of Sri Lanka - Section 299
- Penal Code of Sri Lanka - Section 296"""),
    ("user", """Query: {query}

Provided Legal Sources:
{sources}

Apply these sources to answer the query. Remember: use ONLY these sources.""")
])


def create_reasoning_runnable(llm: ChatOpenAI = None) -> Runnable:
    """
    Create the Legal Reasoning agent as a LangChain Runnable.

    This agent applies legal reasoning using ONLY provided MCP sources.

    Args:
        llm: Language model for reasoning (should be capable model like GPT-4)

    Returns:
        Runnable that takes ResearchOutput and returns ReasoningOutput
    """
    # Use a capable model for legal reasoning
    if llm is None:
        llm = ChatOpenAI(
            model="gpt-4o",  # Use capable model for legal reasoning
            temperature=0.0,  # Deterministic
        )

    def prepare_reasoning_input(research_output: ResearchOutput) -> Dict[str, Any]:
        """
        Prepare input for the reasoning prompt.

        Formats legal sources for presentation to the LLM.
        """
        # Format sources for the prompt
        formatted_sources = []
        for idx, source in enumerate(research_output.sources, 1):
            formatted_sources.append(
                f"{idx}. {source.law_name} - Section {source.section}\n"
                f"   Text: {source.text}\n"
            )

        sources_text = "\n".join(
            formatted_sources) if formatted_sources else "No sources available."

        return {
            "query": research_output.mcp_query,
            "sources": sources_text
        }

    def parse_reasoning_output(ai_message, research_output: ResearchOutput) -> ReasoningOutput:
        """
        Parse LLM output into ReasoningOutput schema.

        Extracts analysis, limitations, and citations from the structured response.
        """
        content = ai_message.content

        # Parse structured output
        analysis = ""
        limitations = ""
        citations_used = []

        # Simple parsing (in production, use more robust parsing or structured output)
        if "ANALYSIS:" in content:
            parts = content.split("LIMITATIONS:")
            analysis_part = parts[0].split("ANALYSIS:")[1].strip()
            analysis = analysis_part

            if len(parts) > 1:
                limitations_part = parts[1].split("CITATIONS USED:")[0].strip()
                limitations = limitations_part

                if "CITATIONS USED:" in content:
                    citations_part = content.split(
                        "CITATIONS USED:")[1].strip()
                    # Extract citations (simple line-based parsing)
                    citations_used = [
                        line.strip().lstrip("-").strip()
                        for line in citations_part.split("\n")
                        if line.strip() and not line.strip().startswith("Example")
                    ]
        else:
            analysis = content
            limitations = "Unable to parse structured limitations."

        # Calculate confidence based on source availability
        confidence = 0.8 if research_output.sources else 0.2

        return ReasoningOutput(
            analysis=analysis,
            limitations=limitations,
            citations_used=citations_used,
            confidence=confidence,
            reasoning_chain=None  # Not exposed to prevent chain-of-thought leakage
        )

    # Build the runnable chain with state passing
    def reasoning_chain(research_output: ResearchOutput) -> ReasoningOutput:
        """Execute reasoning and parse output."""
        # Prepare input
        prompt_input = prepare_reasoning_input(research_output)

        # Generate reasoning
        prompt = REASONING_PROMPT.format_messages(**prompt_input)
        ai_message = llm.invoke(prompt)

        # Parse output
        return parse_reasoning_output(ai_message, research_output)

    return RunnableLambda(reasoning_chain)


def create_structured_reasoning_runnable(llm: ChatOpenAI = None) -> Runnable:
    """
    Create reasoning agent with structured output (JSON mode).

    This variant uses OpenAI's structured output for more reliable parsing.

    Args:
        llm: Language model with JSON mode support

    Returns:
        Runnable that takes ResearchOutput and returns ReasoningOutput
    """
    import json

    if llm is None:
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.0,
            model_kwargs={"response_format": {"type": "json_object"}}
        )

    # Simplified prompt for JSON output
    json_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a legal reasoning engine for Sri Lankan law.

Output your reasoning as JSON with this structure:
{{
    "analysis": "Your legal analysis using ONLY provided sources with citations",
    "limitations": "What cannot be concluded from available sources",
    "citations_used": ["Law Name - Section X", ...]
}}

RULES:
- Use ONLY the provided legal sources
- Cite every legal statement
- Explicitly state limitations
- Do NOT invent legal content"""),
        ("user", "Query: {query}\n\nLegal Sources:\n{sources}")
    ])

    def structured_reasoning(research_output: ResearchOutput) -> ReasoningOutput:
        """Execute reasoning with structured output."""
        # Format sources
        formatted_sources = "\n".join([
            f"- {s.law_name}, Section {s.section}: {s.text}"
            for s in research_output.sources
        ]) if research_output.sources else "No sources available."

        # Invoke LLM
        prompt = json_prompt.format_messages(
            query=research_output.mcp_query,
            sources=formatted_sources
        )
        ai_message = llm.invoke(prompt)

        # Parse JSON
        try:
            data = json.loads(ai_message.content)
            return ReasoningOutput(
                analysis=data.get("analysis", ""),
                limitations=data.get("limitations", ""),
                citations_used=data.get("citations_used", []),
                confidence=0.8 if research_output.sources else 0.2,
                reasoning_chain=None
            )
        except json.JSONDecodeError:
            # Fallback
            return ReasoningOutput(
                analysis="Reasoning output parsing failed.",
                limitations="Unable to process reasoning due to output format error.",
                citations_used=[],
                confidence=0.1,
                reasoning_chain=None
            )

    return RunnableLambda(structured_reasoning)


def get_reasoning_agent() -> Runnable:
    """
    Get the default reasoning agent.

    Returns:
        Legal reasoning agent runnable
    """
    return create_reasoning_runnable()

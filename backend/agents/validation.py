"""
Validation / Compliance Agent

Role: Gatekeeper - detect hallucinations, verify citations, block unsafe output.

This agent:
- Detects hallucinations (legal content not from MCP sources)
- Ensures all citations exist in provided sources
- Assigns confidence scores
- BLOCKS output if validation fails

If status == "fail", the system MUST STOP and return a refusal message.

This is the most critical agent for court admissibility.
"""

from typing import Dict, Any, List, Tuple
from langchain_core.runnables import Runnable, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate

from mcp_client import get_mcp_client
from schemas.messages import (
    ResearchOutput,
    ReasoningOutput,
    ValidationOutput,
    ValidationIssue
)
from .llm_factory import get_llm


# Validation prompt template
VALIDATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a validation engine for legal AI outputs.

Your job is to detect errors, hallucinations, and unsafe outputs.

You will receive:
1. Original legal sources from MCP
2. The reasoning analysis that used those sources
3. Citations claimed by the reasoning agent

Your validation checks:

1. CITATION VERIFICATION
   - Every legal statement must cite a provided source
   - Every citation must reference an actual source in the list
   - Verify section numbers match

2. HALLUCINATION DETECTION
   - Detect any legal content NOT from provided sources
   - Flag any case law or precedents not in sources
   - Flag any legal interpretations without source backing

3. CONSISTENCY CHECK
   - Ensure citations_used list matches citations in analysis
   - Verify all sources mentioned exist in source list

4. LIMITATION CHECK
   - Ensure limitations section acknowledges knowledge gaps
   - Verify agent admits when sources are insufficient

Output your validation as JSON:
{{
    "status": "pass" | "warn" | "fail",
    "issues": [
        {{
            "severity": "critical" | "warning" | "info",
            "type": "hallucination" | "missing_citation" | "inconsistency" | "other",
            "description": "Clear description of the issue",
            "location": "Where in the analysis this occurs"
        }}
    ],
    "confidence": 0.0 to 1.0,
    "all_citations_verified": true | false,
    "no_hallucination_detected": true | false
}}

CRITICAL: Any "critical" severity issue MUST result in status "fail"."""),
    ("user", """Legal Sources:
{sources}

Reasoning Analysis:
{analysis}

Stated Limitations:
{limitations}

Citations Used:
{citations_used}

Validate this output.""")
])


def create_validation_runnable(llm=None) -> Runnable:
    """
    Create the Validation agent as a LangChain Runnable.

    This agent is the gatekeeper that prevents hallucinations and errors
    from reaching users.

    Args:
        llm: Language model for validation analysis

    Returns:
        Runnable that takes (ResearchOutput, ReasoningOutput) and returns ValidationOutput
    """
    if llm is None:
        llm = get_llm(
            model="gpt-4o",  # Use capable model for critical validation
            temperature=0.0,
        )

    mcp_client = get_mcp_client()

    def validate(
        inputs: Tuple[ResearchOutput, ReasoningOutput]
    ) -> ValidationOutput:
        """
        Validate reasoning output against research sources.

        Args:
            inputs: Tuple of (ResearchOutput, ReasoningOutput)

        Returns:
            ValidationOutput with pass/warn/fail status
        """
        research_output, reasoning_output = inputs

        # Step 1: Rule-based validation (deterministic)
        rule_based_issues = []

        # Check 1: Are there any sources?
        if not research_output.sources:
            rule_based_issues.append(
                ValidationIssue(
                    severity="critical",
                    type="missing_sources",
                    description="No legal sources were retrieved from MCP. Cannot provide legal analysis.",
                    location="research"
                )
            )

        # Check 2: Are citations claimed?
        if not reasoning_output.citations_used:
            rule_based_issues.append(
                ValidationIssue(
                    severity="warning",
                    type="missing_citation",
                    description="No citations were explicitly listed.",
                    location="citations_used"
                )
            )

        # Check 3: Verify each claimed citation exists in sources
        all_citations_verified = True
        source_identifiers = {
            f"{s.law_name} - Section {s.section}"
            for s in research_output.sources
        }

        for citation in reasoning_output.citations_used:
            # Fuzzy match: check if citation references any source
            citation_verified = any(
                source_id.lower() in citation.lower() or citation.lower() in source_id.lower()
                for source_id in source_identifiers
            )

            if not citation_verified:
                all_citations_verified = False
                rule_based_issues.append(
                    ValidationIssue(
                        severity="critical",
                        type="hallucination",
                        description=f"Citation '{citation}' does not match any provided source.",
                        location="citations_used"
                    )
                )

        # Check 4: Is analysis substantive?
        if len(reasoning_output.analysis) < 50:
            rule_based_issues.append(
                ValidationIssue(
                    severity="warning",
                    type="insufficient_analysis",
                    description="Analysis is too brief to be substantive.",
                    location="analysis"
                )
            )

        # Check 5: Are limitations stated?
        if len(reasoning_output.limitations) < 20:
            rule_based_issues.append(
                ValidationIssue(
                    severity="warning",
                    type="missing_limitations",
                    description="Limitations are not adequately stated.",
                    location="limitations"
                )
            )

        # Step 2: LLM-based validation (hallucination detection)
        llm_issues = []
        try:
            # Format sources for validation
            formatted_sources = "\n".join([
                f"- {s.law_name}, Section {s.section}"
                for s in research_output.sources
            ]) if research_output.sources else "No sources"

            # Invoke validation LLM
            prompt = VALIDATION_PROMPT.format_messages(
                sources=formatted_sources,
                analysis=reasoning_output.analysis,
                limitations=reasoning_output.limitations,
                citations_used=", ".join(reasoning_output.citations_used)
            )

            ai_message = llm.invoke(prompt)

            # Parse validation output
            import json
            validation_data = json.loads(ai_message.content)

            # Extract LLM-detected issues
            for issue_data in validation_data.get("issues", []):
                llm_issues.append(
                    ValidationIssue(
                        severity=issue_data.get("severity", "warning"),
                        type=issue_data.get("type", "other"),
                        description=issue_data.get("description", ""),
                        location=issue_data.get("location")
                    )
                )
        except Exception as e:
            # If LLM validation fails, add a warning but continue
            llm_issues.append(
                ValidationIssue(
                    severity="warning",
                    type="validation_error",
                    description=f"LLM validation failed: {str(e)}",
                    location="validation"
                )
            )

        # Combine all issues
        all_issues = rule_based_issues + llm_issues

        # Determine final status
        critical_issues = [i for i in all_issues if i.severity == "critical"]
        warning_issues = [i for i in all_issues if i.severity == "warning"]

        if critical_issues:
            status = "fail"
            confidence = 0.0
        elif warning_issues:
            status = "warn"
            confidence = 0.5
        else:
            status = "pass"
            confidence = 0.9

        # Detect hallucinations (no critical hallucination issues)
        hallucination_issues = [
            i for i in all_issues
            if i.type == "hallucination" and i.severity == "critical"
        ]
        no_hallucination_detected = len(hallucination_issues) == 0

        return ValidationOutput(
            status=status,
            issues=all_issues,
            confidence=confidence,
            all_citations_verified=all_citations_verified,
            no_hallucination_detected=no_hallucination_detected
        )

    return RunnableLambda(validate)


def create_rule_based_validation_runnable() -> Runnable:
    """
    Create a purely rule-based validation agent (no LLM).

    This is more deterministic and suitable for production systems
    where every decision must be explainable.

    Returns:
        Runnable that takes (ResearchOutput, ReasoningOutput) and returns ValidationOutput
    """
    def rule_based_validate(
        inputs: Tuple[ResearchOutput, ReasoningOutput]
    ) -> ValidationOutput:
        """Pure rule-based validation."""
        research_output, reasoning_output = inputs

        issues = []

        # Rule 1: Must have sources
        if not research_output.sources:
            issues.append(
                ValidationIssue(
                    severity="critical",
                    type="missing_sources",
                    description="No legal sources retrieved. Cannot provide legal analysis without sources.",
                    location="research"
                )
            )

        # Rule 2: Must have citations
        if not reasoning_output.citations_used and research_output.sources:
            issues.append(
                ValidationIssue(
                    severity="critical",
                    type="missing_citation",
                    description="No citations provided despite having sources available.",
                    location="citations_used"
                )
            )

        # Rule 3: Citation verification
        source_identifiers = {
            f"{s.law_name} - Section {s.section}".lower()
            for s in research_output.sources
        }

        all_citations_verified = True
        for citation in reasoning_output.citations_used:
            # Check if citation matches any source
            matches = any(
                source_id in citation.lower() or citation.lower() in source_id
                for source_id in source_identifiers
            )

            if not matches:
                all_citations_verified = False
                issues.append(
                    ValidationIssue(
                        severity="critical",
                        type="hallucination",
                        description=f"Citation '{citation}' not found in provided sources.",
                        location="citations_used"
                    )
                )

        # Rule 4: Analysis length check
        if len(reasoning_output.analysis) < 50:
            issues.append(
                ValidationIssue(
                    severity="warning",
                    type="insufficient_analysis",
                    description="Analysis appears too brief.",
                    location="analysis"
                )
            )

        # Rule 5: Limitations check
        if len(reasoning_output.limitations) < 20:
            issues.append(
                ValidationIssue(
                    severity="info",
                    type="missing_limitations",
                    description="Limitations section is brief. Consider more explicit statement of constraints.",
                    location="limitations"
                )
            )

        # Determine status
        critical_issues = [i for i in issues if i.severity == "critical"]
        if critical_issues:
            status = "fail"
            confidence = 0.0
        elif [i for i in issues if i.severity == "warning"]:
            status = "warn"
            confidence = 0.6
        else:
            status = "pass"
            confidence = 0.95

        no_hallucination_detected = not any(
            i.type == "hallucination" and i.severity == "critical"
            for i in issues
        )

        return ValidationOutput(
            status=status,
            issues=issues,
            confidence=confidence,
            all_citations_verified=all_citations_verified,
            no_hallucination_detected=no_hallucination_detected
        )

    return RunnableLambda(rule_based_validate)


def get_validation_agent() -> Runnable:
    """
    Get the default validation agent.

    Uses rule-based validation for maximum determinism and explainability.

    Returns:
        Validation agent runnable
    """
    return create_rule_based_validation_runnable()

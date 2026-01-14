"""
Message schemas for the multi-agent legal reasoning system.

These schemas define the strict data contracts between agents in the pipeline.
All communication is typed and validated to ensure court-admissible traceability.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field, validator


class UserQuery(BaseModel):
    """Initial user input to the system."""
    question: str = Field(..., description="The legal question to be answered")
    case_context: Optional[str] = Field(
        None, description="Optional case-specific context")

    class Config:
        frozen = True  # Immutable for audit trail


class PlannerOutput(BaseModel):
    """Planner's deterministic execution plan.

    The planner ONLY determines control flow. It does NOT perform legal reasoning.
    """
    steps: List[Literal["research", "reason", "validate", "synthesize"]] = Field(
        ...,
        description="Ordered list of execution steps"
    )
    query: str = Field(...,
                       description="Processed query for downstream agents")
    confidence: float = Field(..., ge=0.0, le=1.0,
                              description="Planner confidence in routing")

    @validator('steps')
    def validate_steps(cls, v):
        required = ["research", "reason", "validate", "synthesize"]
        if v != required:
            raise ValueError(f"Steps must be exactly {required} in order")
        return v


class LegalSource(BaseModel):
    """A single legal source retrieved from MCP.

    This is the ONLY way legal knowledge enters the system.
    """
    law_name: str = Field(...,
                          description="Name of the law (e.g., 'Penal Code')")
    section: str = Field(..., description="Section number or identifier")
    text: str = Field(..., description="VERBATIM legal text from MCP")
    metadata: dict = Field(default_factory=dict,
                           description="Additional MCP metadata")

    class Config:
        frozen = True  # Immutable source of truth


class ResearchOutput(BaseModel):
    """Output from the Research Agent (MCP Runnable).

    Contains ONLY retrieved legal text, no interpretation.
    """
    sources: List[LegalSource] = Field(...,
                                       description="Retrieved legal sources")
    mcp_query: str = Field(..., description="Query sent to MCP")
    retrieval_timestamp: str = Field(...,
                                     description="ISO timestamp of retrieval")
    status: Literal["success", "partial", "empty"] = Field(
        ...,
        description="Retrieval status"
    )

    @validator('sources')
    def validate_sources(cls, v):
        if not v:
            raise ValueError(
                "Research output must contain at least one source or status must be 'empty'")
        return v


class ReasoningOutput(BaseModel):
    """Output from the Legal Reasoning Agent.

    This agent applies law to facts using ONLY provided MCP sources.
    """
    analysis: str = Field(...,
                          description="Legal reasoning applying sources to query")
    limitations: str = Field(...,
                             description="Explicit statement of what CANNOT be concluded")
    citations_used: List[str] = Field(...,
                                      description="List of source identifiers actually used")
    confidence: float = Field(..., ge=0.0, le=1.0,
                              description="Reasoning confidence")
    reasoning_chain: Optional[str] = Field(
        None,
        description="Internal reasoning summary (NOT exposed to user)"
    )

    @validator('analysis')
    def validate_analysis_length(cls, v):
        if len(v) < 50:
            raise ValueError("Analysis must be substantive (min 50 chars)")
        return v


class ValidationIssue(BaseModel):
    """A specific issue detected by the Validation Agent."""
    severity: Literal["critical", "warning",
                      "info"] = Field(..., description="Issue severity")
    type: str = Field(...,
                      description="Issue type (e.g., 'missing_citation', 'hallucination')")
    description: str = Field(..., description="Human-readable description")
    location: Optional[str] = Field(
        None, description="Where in reasoning the issue occurs")


class ValidationOutput(BaseModel):
    """Output from the Validation/Compliance Agent.

    This is the gatekeeper. If status == 'fail', the system MUST STOP.
    """
    status: Literal["pass", "warn",
                    "fail"] = Field(..., description="Validation status")
    issues: List[ValidationIssue] = Field(
        default_factory=list, description="Detected issues")
    confidence: float = Field(..., ge=0.0, le=1.0,
                              description="Overall confidence in output")
    all_citations_verified: bool = Field(...,
                                         description="All citations exist in sources")
    no_hallucination_detected: bool = Field(...,
                                            description="No external knowledge used")

    @validator('status')
    def validate_critical_issues(cls, v, values):
        if 'issues' in values:
            critical_issues = [i for i in values['issues']
                               if i.severity == "critical"]
            if critical_issues and v != "fail":
                raise ValueError(
                    "Critical issues must result in 'fail' status")
        return v


class SynthesizerOutput(BaseModel):
    """Final output from the Synthesizer Agent.

    This agent does NO reasoning, only presentation.
    """
    response: str = Field(..., description="Formatted final response")
    citations: List[LegalSource] = Field(..., description="All sources used")
    confidence_note: str = Field(...,
                                 description="Confidence explanation for user")
    disclaimer: str = Field(..., description="Legal disclaimer")
    metadata: dict = Field(default_factory=dict,
                           description="Additional metadata")


class RefusalOutput(BaseModel):
    """Output when the system refuses to answer.

    This is returned when validation fails.
    """
    reason: str = Field(..., description="Why the system refused")
    issues: List[ValidationIssue] = Field(...,
                                          description="Issues that caused refusal")
    suggestions: Optional[str] = Field(
        None, description="How user might rephrase query")


class AuditLogEntry(BaseModel):
    """A single entry in the audit log.

    Every agent interaction must be logged for court admissibility.
    """
    timestamp: str = Field(..., description="ISO timestamp")
    agent: str = Field(..., description="Agent name")
    input_data: dict = Field(..., description="Agent input")
    output_data: dict = Field(..., description="Agent output")
    execution_time_ms: float = Field(...,
                                     description="Execution time in milliseconds")
    metadata: dict = Field(default_factory=dict,
                           description="Additional context")

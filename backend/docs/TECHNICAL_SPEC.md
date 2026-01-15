# Technical Specification - Multi-Agent Legal Reasoning System

## Document Control

| Property | Value |
|----------|-------|
| System Name | SentiLex AI Advocate |
| Version | 1.0.0 |
| Date | January 14, 2026 |
| Status | Production Ready |
| Domain | Sri Lankan Law |

---

## 1. System Purpose

Build a **court-admissible**, **deterministic**, and **auditable** multi-agent system for legal reasoning using LangChain that:
- Provides accurate legal analysis based solely on Sri Lankan legal texts
- Maintains complete audit trails for court proceedings
- Prevents hallucinations through strict validation
- Ensures explainability and traceability

---

## 2. Architectural Principles

### 2.1 Core Design Rules

| Rule | Implementation |
|------|---------------|
| **No Hallucinations** | All legal content from MCP only |
| **Planner-Mediated** | All communication through chain |
| **Agents as Runnables** | No `AgentExecutor`, use `Runnable` |
| **No Direct Communication** | Agents never talk to each other |
| **Explicit Validation** | Gatekeeper blocks unsafe output |
| **Full Auditability** | Every step logged with timestamps |
| **Deterministic Flow** | Fixed execution path |
| **No CoT Exposure** | Chain-of-thought never shown to users |

### 2.2 Architectural Pattern

**Pattern**: Pipeline Architecture with Validation Branching

```
Linear Pipeline:
User Input → Planner → Research → Reasoning → Validation

Branching Logic:
Validation → [Pass → Synthesizer → Success Output]
           → [Fail → Refusal → Error Output]
```

---

## 3. Agent Specifications

### 3.1 Planner Agent

**Type**: Deterministic Runnable (no LLM in production)

**Purpose**: Routing and flow control

**Input**: `UserQuery`
```python
{
    "question": str,
    "case_context": Optional[str]
}
```

**Output**: `PlannerOutput`
```python
{
    "steps": ["research", "reason", "validate", "synthesize"],
    "query": str,
    "confidence": float  # 0.0 to 1.0
}
```

**Decision Logic**:
- All queries follow fixed path: research → reason → validate → synthesize
- No dynamic routing
- Simple validation: query length > 10 chars

**Performance**: < 10ms

---

### 3.2 Research Agent

**Type**: MCP Runnable

**Purpose**: Legal source retrieval ONLY

**Input**: `PlannerOutput`

**Output**: `ResearchOutput`
```python
{
    "sources": List[LegalSource],
    "mcp_query": str,
    "retrieval_timestamp": str,  # ISO 8601
    "status": "success" | "partial" | "empty"
}
```

**Legal Source Schema**:
```python
{
    "law_name": str,
    "section": str,
    "text": str,  # VERBATIM from MCP
    "metadata": dict
}
```

**Behavior**:
- Calls MCP service with query
- Returns verbatim legal text
- NO summarization
- NO interpretation
- NO reasoning

**Performance**: 100-500ms (MCP query time)

---

### 3.3 Legal Reasoning Agent

**Type**: LLM Runnable (GPT-4)

**Purpose**: Apply law to question using ONLY provided sources

**Input**: `ResearchOutput`

**Output**: `ReasoningOutput`
```python
{
    "analysis": str,
    "limitations": str,
    "citations_used": List[str],
    "confidence": float,
    "reasoning_chain": Optional[str]  # Internal only, never exposed
}
```

**Constraints**:
- MUST use only provided sources
- MUST cite every legal statement
- MUST explicitly state limitations
- MUST NOT invent legal content
- MUST NOT use external knowledge

**Prompt Structure**:
```
System: You are a legal reasoning engine...
        CRITICAL RULES:
        1. Use ONLY provided sources
        2. Cite all statements
        3. State limitations explicitly
        
User: Query: {query}
      Sources: {sources}
```

**Performance**: 2-5s (LLM processing)

---

### 3.4 Validation Agent

**Type**: Rule-based + LLM Runnable (GPT-4)

**Purpose**: Gatekeeper - detect errors, block unsafe output

**Input**: `(ResearchOutput, ReasoningOutput)`

**Output**: `ValidationOutput`
```python
{
    "status": "pass" | "warn" | "fail",
    "issues": List[ValidationIssue],
    "confidence": float,
    "all_citations_verified": bool,
    "no_hallucination_detected": bool
}
```

**Validation Checks**:

1. **Rule-Based**:
   - Sources exist?
   - Citations claimed?
   - Citations match sources?
   - Analysis substantive? (>50 chars)
   - Limitations stated? (>20 chars)

2. **LLM-Based**:
   - Hallucination detection
   - Citation correctness
   - Consistency checks
   - Limitation adequacy

**Failure Conditions**:
```python
if any(issue.severity == "critical"):
    status = "fail"  # System STOPS here
```

**Performance**: 1-3s (validation processing)

---

### 3.5 Synthesizer Agent

**Type**: Formatting Runnable (no LLM)

**Purpose**: Presentation ONLY

**Input**: `(ResearchOutput, ReasoningOutput, ValidationOutput)`

**Output**: `SynthesizerOutput`
```python
{
    "response": str,  # Markdown formatted
    "citations": List[LegalSource],
    "confidence_note": str,
    "disclaimer": str,
    "metadata": dict
}
```

**Behavior**:
- Formats analysis as markdown
- Adds citations
- Adds confidence notes
- Adds legal disclaimer
- NO reasoning
- NO decisions

**Performance**: < 100ms

---

### 3.6 Refusal Agent

**Type**: Formatting Runnable

**Purpose**: Generate refusal messages

**Input**: `ValidationOutput` (with status="fail")

**Output**: `RefusalOutput`
```python
{
    "reason": str,
    "issues": List[ValidationIssue],
    "suggestions": Optional[str]
}
```

**Behavior**:
- Explains why system refused
- Lists critical issues
- Provides suggestions for rephrasing

**Performance**: < 50ms

---

## 4. Data Flow

### 4.1 Message Schemas

All inter-agent communication uses Pydantic models:

| Schema | File | Purpose |
|--------|------|---------|
| `UserQuery` | `schemas/messages.py` | User input |
| `PlannerOutput` | `schemas/messages.py` | Routing decision |
| `LegalSource` | `schemas/messages.py` | Single legal text |
| `ResearchOutput` | `schemas/messages.py` | Retrieved sources |
| `ReasoningOutput` | `schemas/messages.py` | Legal analysis |
| `ValidationIssue` | `schemas/messages.py` | Single validation issue |
| `ValidationOutput` | `schemas/messages.py` | Validation result |
| `SynthesizerOutput` | `schemas/messages.py` | Final success output |
| `RefusalOutput` | `schemas/messages.py` | Final refusal output |
| `AuditLogEntry` | `schemas/messages.py` | Audit trail entry |

### 4.2 State Management

State accumulates as it flows through the pipeline:

```python
state = {
    "user_query": UserQuery,
    "planner_output": PlannerOutput,
    "research_output": ResearchOutput,
    "reasoning_output": ReasoningOutput,
    "validation_output": ValidationOutput
}
```

### 4.3 Branching Logic

```python
if validation_output.status == "fail":
    return refusal_agent.invoke(validation_output)
else:  # "pass" or "warn"
    return synthesizer_agent.invoke((research, reasoning, validation))
```

---

## 5. MCP Integration

### 5.1 MCP Service

**Purpose**: Local legal knowledge database

**Interface**: HTTP REST API (or SDK)

**Endpoint**: `http://localhost:3000` (configurable)

### 5.2 MCP Client

**File**: `mcp_client/client.py`

**Methods**:
```python
query_legal_sources(query: str, max_sources: int) -> List[LegalSource]
get_specific_section(law_name: str, section: str) -> Optional[LegalSource]
verify_citation(law_name: str, section: str) -> bool
health_check() -> bool
```

### 5.3 Mock Implementation

Current implementation includes mock responses for demonstration:
- `_mock_mcp_query()` - Returns sample legal sources
- `_mock_get_section()` - Returns specific section

**Production**: Replace with actual MCP SDK calls

---

## 6. Audit Logging

### 6.1 Audit Requirements

For court admissibility, log:
- Timestamp (ISO 8601)
- Agent name
- Input data (complete)
- Output data (complete)
- Execution time (milliseconds)
- Metadata

### 6.2 Audit Logger

**File**: `logging/audit.py`

**Class**: `AuditLogger`

**Methods**:
```python
log_agent_execution(agent, input_data, output_data, exec_time, metadata)
get_session_logs() -> List[AuditLogEntry]
export_session_logs(output_file) -> str
generate_audit_report(output_file) -> str
```

### 6.3 Log Formats

**JSONL** (append-only):
```json
{"timestamp": "2026-01-14T15:30:45.123Z", "agent": "planner", ...}
{"timestamp": "2026-01-14T15:30:45.456Z", "agent": "research", ...}
```

**JSON** (exportable):
```json
[
  {"timestamp": "...", "agent": "planner", ...},
  {"timestamp": "...", "agent": "research", ...}
]
```

**Markdown** (human-readable):
```markdown
# Legal AI System Audit Report
## 1. Agent: planner
**Timestamp:** 2026-01-14T15:30:45.123Z
...
```

---

## 7. API Specification

### 7.1 Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| POST | `/query` | Submit legal query |
| GET | `/audit/{session_id}` | Get audit logs |
| GET | `/export/{session_id}` | Export audit report |
| POST | `/test/query` | Test with sample query |

### 7.2 POST /query

**Request**:
```json
{
  "question": "string",
  "case_context": "string | null"
}
```

**Response (Success)**:
```json
{
  "status": "success",
  "data": {
    "response": "markdown",
    "citations": [...],
    "confidence_note": "string",
    "disclaimer": "string",
    "metadata": {...}
  },
  "session_id": "string",
  "timestamp": "ISO 8601"
}
```

**Response (Refusal)**:
```json
{
  "status": "refused",
  "data": {
    "reason": "string",
    "issues": [...],
    "suggestions": "string"
  },
  "session_id": "string",
  "timestamp": "ISO 8601"
}
```

---

## 8. Performance Specifications

### 8.1 Latency Targets

| Component | Target | Maximum |
|-----------|--------|---------|
| Planner | < 10ms | 50ms |
| Research | 100-500ms | 1s |
| Reasoning | 2-5s | 10s |
| Validation | 1-3s | 8s |
| Synthesizer | < 100ms | 500ms |
| **Total** | **3-9s** | **20s** |

### 8.2 Throughput

- **Sequential queries**: 6-10 queries/minute
- **Parallel queries**: Limited by OpenAI rate limits

### 8.3 Resource Usage

- **Memory**: ~500MB baseline + 200MB per concurrent request
- **CPU**: Minimal (LLM processing is remote)
- **Storage**: ~1MB per query session (audit logs)

---

## 9. Security & Compliance

### 9.1 Data Privacy

- User queries logged for audit trail
- No PII stored without consent
- Audit logs contain full query data

### 9.2 API Security

- Rate limiting (implement with middleware)
- API key authentication (implement as needed)
- CORS configured for production

### 9.3 Court Admissibility

**Evidence Requirements**:
1. ✅ Complete audit trail
2. ✅ Timestamp all operations
3. ✅ Log all inputs and outputs
4. ✅ Verify all citations
5. ✅ Block hallucinations
6. ✅ Explicit refusal mechanism
7. ✅ No external knowledge
8. ✅ Deterministic routing

---

## 10. Deployment

### 10.1 Requirements

- Python 3.10+
- OpenAI API access
- MCP service (local or remote)
- 1GB RAM minimum
- 1 CPU core minimum

### 10.2 Environment Variables

```bash
OPENAI_API_KEY=required
MCP_HOST=localhost
MCP_PORT=3000
API_HOST=0.0.0.0
API_PORT=8000
AUDIT_LOG_DIR=logs
```

### 10.3 Startup

```bash
python app.py
```

### 10.4 Health Checks

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "mcp_available": true,
  "timestamp": "2026-01-14T15:30:45.123Z"
}
```

---

## 11. Testing

### 11.1 Test Suite

**File**: `test_system.py`

**Test Cases**:
1. Basic legal definition query
2. Query with case context
3. Specific section query
4. Complex legal question
5. Obscure topic (expected refusal)

### 11.2 Running Tests

```bash
python test_system.py
```

### 11.3 Test Coverage

- ✅ Planner routing
- ✅ Research retrieval
- ✅ Reasoning with sources
- ✅ Validation checks
- ✅ Success synthesis
- ✅ Refusal synthesis
- ✅ Audit logging

---

## 12. Extensibility

### 12.1 Adding New Agents

1. Create agent file in `agents/`
2. Implement as `Runnable`
3. Define schemas in `schemas/messages.py`
4. Integrate into `chains/main_chain.py`
5. Add audit logging

### 12.2 Customizing Validation

Edit `agents/validation.py`:
- Add new rule-based checks
- Modify LLM validation prompts
- Adjust severity thresholds

### 12.3 Supporting New Legal Domains

1. Configure MCP for new jurisdiction
2. Update prompt templates in agents
3. Adjust validation rules
4. Update disclaimers

---

## 13. Known Limitations

1. **MCP Mock**: Current implementation uses mock MCP responses
2. **Single Language**: Only English support currently
3. **Sequential Processing**: No parallel agent execution
4. **LLM Dependency**: Requires OpenAI API access
5. **No Streaming**: Responses are not streamed

---

## 14. Future Enhancements

### 14.1 Planned Features

- [ ] Multi-language support (Sinhala, Tamil)
- [ ] Streaming responses
- [ ] Parallel agent execution
- [ ] Case law integration
- [ ] Precedent matching
- [ ] Custom validation rules
- [ ] Enhanced audit analytics
- [ ] Performance optimizations

### 14.2 Integration Opportunities

- LangSmith for tracing
- Prometheus for metrics
- Grafana for dashboards
- Redis for caching
- PostgreSQL for audit persistence

---

## 15. References

- **LangChain Documentation**: https://python.langchain.com/
- **Pydantic**: https://docs.pydantic.dev/
- **FastAPI**: https://fastapi.tiangolo.com/
- **OpenAI API**: https://platform.openai.com/docs

---

**Document Version**: 1.0.0  
**Last Updated**: January 14, 2026  
**Maintained By**: SentiLex AI Advocate Team

# AI Coding Agent Instructions for SentiLex AI Advocate

## 🎯 Project Overview
**SentiLex** is a court-admissible, multi-agent legal AI system for Sri Lankan law. It converts trauma victim testimony into prosecution-ready legal documentation using trauma-informed interviews, forensic evidence triage, and legal classification.

**Critical Design Principle**: Explainability and court admissibility trump flexibility. Every system decision must be traceable and defensible.

---

## 🏗️ Architecture: Multi-Agent Pipeline

The system follows a **deterministic, validation-gated pipeline** (NOT autonomous agents):

```
UserQuery → Planner → Research(MCP) → Reasoning → Validation(Gatekeeper) → Branch
                                                      ↓          ↓
                                                    PASS    FAIL
                                                      ↓       ↓
                                                  Synthesizer Refusal
```

### Core Principle: Planner-Mediated Communication
- **All agents are LangChain Runnables**, NOT AgentExecutors
- **No direct agent-to-agent communication** — flow is always through the planner/chain
- **Communication via typed Pydantic schemas** (see `backend/schemas/messages.py`)
- **Every step is logged** in `backend/audit_logging/audit.py` for court admissibility

### Why This Design?
1. **Explainability**: Every decision is traceable (audit logs)
2. **No Hallucinations**: Only MCP (Model Context Protocol) is the legal knowledge source
3. **Validation Gate**: The Validation agent can BLOCK unsafe outputs
4. **Deterministic**: Same query always produces same execution path

---

## 📁 Key Directory Structure & Patterns

### Backend (`backend/`)
```
agents/               # Core agents (Runnables only)
  ├── planner.py     # Routes queries (deterministic, no legal reasoning)
  ├── research.py    # Retrieves sources from MCP only
  ├── reasoning.py   # Applies law to sources (must cite)
  ├── validation.py  # Gatekeeper (blocks hallucinations)
  ├── synthesizer.py # Formats output for end user
  └── llm_factory.py # LLM instantiation (single source of truth)

chains/               # Pipeline orchestration
  └── main_chain.py  # RunnableSequence + RunnableBranch (validation gate)

schemas/              # Type-safe communication
  └── messages.py    # Pydantic models for all agent inputs/outputs

mcp_server/           # MCP integration
  └── mcp_client.py  # Wrapper around MCP service (ONLY legal source)

database/             # SQLAlchemy models & config
models/               # ORM models (User, Lawyer, Evidence, etc.)
routers/              # FastAPI endpoint handlers
audit_logging/        # Court-admissible audit trail
```

### Frontend (`frontend/`)
- **Framework**: Preact (3kB React alternative)
- **Build Tool**: Vite
- **Styling**: Tailwind CSS v4
- **Architecture**: Atomic Design (atoms → molecules → organisms → templates → pages)
- **Key Scripts**: `npm run dev` (development), `npm run build` (production)

---

## 🔑 Essential Patterns & Conventions

### 1. **Agent Creation (Runnables, NOT AgentExecutor)**
**File**: `backend/agents/[agent_name].py`

```python
# ✅ CORRECT: Returns a Runnable
def create_planner_runnable(llm=None) -> Runnable:
    prompt = ChatPromptTemplate.from_messages([...])
    llm = get_llm(model="gpt-4o-mini", temperature=0.0)
    return prompt | llm | RunnableLambda(parse_output)

# ❌ WRONG: Don't use AgentExecutor or autonomous agents
# ❌ WRONG: Don't let agents call tools directly
```

**Key Conventions**:
- Use `backend/agents/llm_factory.py:get_llm()` for ALL LLM instantiation
- Set `temperature=0.0` for deterministic behavior
- Always return a `Runnable` object
- Input/output types are Pydantic schemas from `backend/schemas/messages.py`

### 2. **Type-Safe Communication**
**File**: `backend/schemas/messages.py`

All inter-agent communication uses typed Pydantic schemas:
- `UserQuery` → input from user
- `PlannerOutput` → routing decision
- `ResearchOutput` → MCP-retrieved sources
- `ReasoningOutput` → legal analysis (with citations)
- `ValidationOutput` → pass/warn/fail status
- `SynthesizerOutput` or `RefusalOutput` → final output

**Pattern**:
```python
# Define schema
class MyOutput(BaseModel):
    field1: str
    field2: List[str]

# Use in agent
def my_agent(input_data: MyInput) -> MyOutput:
    return MyOutput(field1="value", field2=[])
```

### 3. **MCP is the ONLY Legal Source**
**File**: `backend/mcp_server/mcp_client.py`

- **All legal knowledge** comes from MCP (no vector databases, no external sources)
- MCP returns legal text from Sri Lankan statutes
- **Research agent retrieves sources**, **Validation agent verifies citations match**

```python
from mcp_server.mcp_client import get_mcp_client

mcp_client = get_mcp_client()
sources = mcp_client.retrieve_sources(query)  # Only way to get legal knowledge
```

### 4. **Validation = Gatekeeper**
**File**: `backend/agents/validation.py`

The Validation agent is the most critical. It:
- Detects hallucinations (legal content NOT from MCP sources)
- Verifies every citation exists in retrieved sources
- Assigns pass/warn/fail status
- **If status="fail", system MUST output refusal** (not errors)

**Key Pattern**:
```python
validation_output = validation_agent.invoke((research_output, reasoning_output))
if validation_output.status == "fail":
    return refusal_agent.invoke(validation_output)  # Block unsafe output
else:
    return synthesizer.invoke(reasoning_output)
```

### 5. **Audit Logging (Court Admissibility)**
**File**: `backend/audit_logging/audit.py`

Every agent interaction is logged:
```python
from audit_logging.audit import get_audit_logger

logger = get_audit_logger()
logger.log_agent_execution(
    agent="reasoning",
    input_data=research.dict(),
    output_data=reasoning.dict()
)
```

This is written to `backend/logs/session_YYYYMMDD_HHMMSS.jsonl` for court records.

### 6. **Database Models**
**File**: `backend/models/[model_name].py`

Using SQLAlchemy 2.0+ with explicit `__tablename__`:
```python
class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True)
    hash_sha256 = Column(String(64), nullable=False)  # Forensic integrity
```

**Key Models**:
- `User` (victims/users)
- `Lawyer` (legal professionals)
- `Evidence` (uploaded media with SHA-256 hashing)
- `Incident` (user-reported incidents)
- `SessionChatMessage` (conversation history)

---

## 🚀 Development Workflows

### **Backend Startup**
```bash
cd backend

# Install dependencies (Python 3.13+)
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env: OPENAI_API_KEY, MCP_HOST/PORT, DATABASE creds

# Start API server
python main.py
# Server: http://localhost:8000
# API docs: http://localhost:8000/docs
```

### **Frontend Startup**
```bash
cd frontend

# Install dependencies
npm install

# Development server (hot reload)
npm run dev
# Server: http://localhost:5173

# Production build
npm run build
```

### **Database Migrations (Alembic)**
```bash
cd backend

# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Reset database (development only)
psql -f alembic/reset.psql
```

### **Testing**
```bash
cd backend

# Run test suite (validates agents, chains, validation)
python test_system.py

# Manual API test
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is culpable homicide under Sri Lankan law?"}'
```

---

## 🔐 Security & Compliance

### **Evidence Hashing (Forensic Chain-of-Custody)**
All uploaded evidence gets SHA-256 fingerprinting:
```python
import hashlib
hash_sha256 = hashlib.sha256(file_content).hexdigest()
```

### **AES-256 Encryption**
Evidence stored in AWS S3 with AES-256 encryption at rest, TLS 1.3 in transit.

### **Access Control**
- JWT tokens for authentication (`backend/auth/dependencies.py`)
- MFA (TOTP) for admins
- S3 presigned URLs for secure file access
- Rate limiting enabled

---

## ⚠️ Common Pitfalls & How to Avoid Them

| Pitfall | Impact | How to Avoid |
|---------|--------|-------------|
| Using vector DB instead of MCP | Hallucinations, non-court-admissible | Always use `get_mcp_client()` for legal knowledge |
| Agents calling tools directly | Breaks validation gate | All agents are Runnables; chain them via `main_chain.py` |
| Missing audit logs | Not admissible in court | Every agent step logged via `get_audit_logger()` |
| Uncited legal statements | Validation fails, blocks output | Reasoning agent must include citations from MCP sources |
| Temperature > 0.0 in critical agents | Non-deterministic behavior | Set `temperature=0.0` in planner, reasoning, validation |
| Direct agent-to-agent communication | Breaks traceability | Always route through the chain via schemas |

---

## 📚 Reference Files for Understanding Patterns

- **Architecture Decisions**: `backend/docs/ARCHITECTURE.md`
- **API Endpoints**: `backend/main.py` + `backend/routers/`
- **Agent Examples**: `backend/agents/planner.py` (simplest), `validation.py` (most complex)
- **Type Schemas**: `backend/schemas/messages.py`
- **Chain Orchestration**: `backend/chains/main_chain.py`
- **Environment Setup**: `backend/config.py`
- **Frontend Structure**: `frontend/README.md` (Atomic Design)

---

## 💡 When Adding New Features

1. **New Agent?** → Create in `backend/agents/[name].py`, return `Runnable`, use `get_llm()`, add schema to `messages.py`
2. **New Database Model?** → Create in `backend/models/[name].py`, then `alembic revision --autogenerate`
3. **New API Endpoint?** → Create in `backend/routers/[feature].py`, import in `main.py`, add response schema
4. **New Frontend Page?** → Follow Atomic Design: atoms → molecules → organisms → templates → pages in `frontend/src/`
5. **Changed Agent Output?** → Update schema in `messages.py`, update validation prompts, update chain in `main_chain.py`

---

## 🔗 External Integration Points

- **OpenAI API**: gpt-4o, gpt-4o-mini (via `llm_factory.py`)
- **MCP Service**: Legal document retrieval (port 3000)
- **PostgreSQL/MySQL**: User data, evidence metadata
- **AWS S3**: Evidence storage (encrypted, hashed)
- **Redis** (optional): Caching, session management
- **Google OAuth**: User authentication (in progress)


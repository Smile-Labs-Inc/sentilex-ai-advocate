# SentiLex AI Advocate - Backend

## 🏛️ Multi-Agent Legal Reasoning System

A court-admissible, multi-agent legal AI system built with LangChain for Sri Lankan law.

### ✨ Key Features

- ✅ **No Hallucinations** - Only uses MCP legal sources
- ✅ **Full Audit Trail** - Every agent interaction logged
- ✅ **Citation Verification** - All legal statements must cite sources
- ✅ **Gatekeeper Validation** - Blocks unsafe outputs

The API will be available at:

- **API**: http://localhost:8001
- **Docs**: http://localhost:8001/docs
- **Health**: http://localhost:8001/health

### 4. Test the System

```bash
# Run test suite
python test_system.py

# Or test via API
curl -X POST http://localhost:8001/test/query
```

---

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete system architecture and design
- **[API Docs](http://localhost:8001/docs)** - Interactive API documentation (when server is running)
- **Code Documentation** - All agents and modules are fully documented

---

## 🏗️ Architecture

### Multi-Agent Pipeline

```
User Query → Planner → Research (MCP) → Reasoning → Validation → Branch
                                                                    ↓
                                                        Pass → Synthesizer
                                                        Fail → Refusal
```

### Core Components

| Component        | Role           | File                                             |
| ---------------- | -------------- | ------------------------------------------------ |
| **Planner**      | Routing logic  | [`agents/planner.py`](agents/planner.py)         |
| **Research**     | MCP retrieval  | [`agents/research.py`](agents/research.py)       |
| **Reasoning**    | Legal analysis | [`agents/reasoning.py`](agents/reasoning.py)     |
| **Validation**   | Gatekeeper     | [`agents/validation.py`](agents/validation.py)   |
| **Synthesizer**  | Presentation   | [`agents/synthesizer.py`](agents/synthesizer.py) |
| **Main Chain**   | Orchestration  | [`chains/main_chain.py`](chains/main_chain.py)   |
| **MCP Client**   | Legal sources  | [`mcp_client/client.py`](mcp_client/client.py)   |
| **Audit Logger** | Court trail    | [`logging/audit.py`](logging/audit.py)           |

---

## 🔌 API Endpoints

### POST /query

Submit a legal query and get analysis or refusal.

**Request:**

```json
{
  "question": "What is culpable homicide under Sri Lankan law?",
  "case_context": "Optional context"
}
```

**Response:**

```json
{
  "status": "success",
  "data": {
    "response": "# Legal Analysis...",
    "confidence_note": "✅ High confidence...",
    "citations": [...]
  },
  "session_id": "20260114_153045",
  "timestamp": "2026-01-14T15:30:45Z"
}
```

### GET /health

Check system and MCP service health.

### GET /audit/{session_id}

Retrieve audit logs for a session.

### GET /export/{session_id}

Export audit report (JSON or Markdown).

---

## 🧪 Testing

### Run Test Suite

```bash
python test_system.py
```

### Manual Testing

```bash
# Test endpoint
curl -X POST http://localhost:8001/test/query

# Custom query
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Your legal question here"}'
```

---

## 📊 Project Structure

```
backend/
├── agents/              # All agent Runnables
│   ├── planner.py      # Routing
│   ├── research.py     # MCP retrieval
│   ├── reasoning.py    # Legal analysis
│   ├── validation.py   # Gatekeeper
│   └── synthesizer.py  # Presentation
├── chains/             # Pipeline orchestration
│   └── main_chain.py   # Main flow
├── schemas/            # Type-safe schemas
│   └── messages.py     # Pydantic models
├── mcp_client/         # MCP integration
│   └── client.py       # MCP wrapper
├── logging/            # Audit trail
│   └── audit.py        # Logging system
├── app.py              # FastAPI app
├── test_system.py      # Test suite
└── requirements.txt    # Dependencies
```

---

## ⚙️ Configuration

### Required Environment Variables

```bash
OPENAI_API_KEY=your_key_here  # Required
```

### Optional Configuration

```bash
MCP_HOST=localhost      # MCP service host
MCP_PORT=3000          # MCP service port
API_HOST=0.0.0.0       # API bind address
API_PORT=8001          # API port
AUDIT_LOG_DIR=logs     # Log directory
```

---

## 🔐 Security & Compliance

### Court Admissibility Features

1. **Audit Trail**: Every agent execution logged with timestamps
2. **Citation Verification**: All legal statements must cite sources
3. **Hallucination Detection**: Validation blocks unsourced content
4. **No External Knowledge**: Only MCP sources used
5. **Deterministic Flow**: Fixed execution path
6. **Explicit Refusal**: System refuses unsafe queries

### Audit Logs

All logs are stored in:

- **JSONL**: `logs/session_{id}.jsonl` (append-only)
- **JSON**: `logs/export_{id}.json` (exportable)
- **Markdown**: `logs/report_{id}.md` (human-readable)

---

## 📈 Performance

**Expected Latencies:**

- Planner: < 10ms (deterministic)
- Research: 100-500ms (MCP query)
- Reasoning: 2-5s (LLM analysis)
- Validation: 1-3s (verification)
- Synthesizer: < 100ms (formatting)
- **Total: 3-9 seconds**

---

## 🤝 Development

### Adding a New Agent

1. Create agent file in `agents/`
2. Implement as LangChain `Runnable`
3. Define schemas in `schemas/messages.py`
4. Integrate into `chains/main_chain.py`
5. Add audit logging

### Code Standards

- Use type hints
- Document all functions
- Follow PEP 8
- Write Pydantic schemas for all data

---

## 📝 License

See [LICENSE](../LICENSE) file.

---

## 🆘 Support

- **Documentation**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **API Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health
- **Audit Logs**: `GET /audit/{session_id}`

---

**Built with ❤️ for court-admissible legal AI**

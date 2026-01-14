# Quick Start Guide - SentiLex AI Advocate

## 📋 Prerequisites

- Python 3.10 or higher
- OpenAI API key
- Terminal/Command Prompt

---

## 🚀 Installation (5 minutes)

### Step 1: Navigate to Backend

```bash
cd backend
```

### Step 2: Run Setup Script

```bash
python setup.py
```

This will:
- ✅ Check Python version
- ✅ Create .env file
- ✅ Install all dependencies
- ✅ Create necessary directories
- ✅ Verify project structure

### Step 3: Configure API Key

Open `.env` file and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Get an API key from: https://platform.openai.com/api-keys

---

## ▶️ Running the System

### Start the Server

```bash
python app.py
```

You should see:
```
SentiLex AI Advocate - Legal Reasoning System
============================================================
✓ Multi-agent architecture initialized
✓ Audit logging enabled
✓ MCP client configured
✓ Logs directory: logs
✓ MCP service available (or warning if not available)
============================================================

Starting server on 0.0.0.0:8000
Docs: http://0.0.0.0:8000/docs
```

### Access the API

Open your browser:
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🧪 Testing

### Quick Test

```bash
# In a new terminal (keep server running)
curl -X POST http://localhost:8000/test/query
```

### Full Test Suite

```bash
python test_system.py
```

This runs 5 test cases and generates audit reports.

---

## 💻 Using the API

### Example 1: Basic Legal Query

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the definition of culpable homicide under Sri Lankan law?"
  }'
```

### Example 2: Query with Context

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the legal penalties?",
    "case_context": "A person caused death with intention but without premeditation"
  }'
```

### Example 3: Using Python

```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={
        "question": "What does Section 299 of the Penal Code say?",
        "case_context": None
    }
)

result = response.json()
print(result["status"])  # 'success' or 'refused'
print(result["data"]["response"])  # The legal analysis
```

---

## 📊 Understanding Responses

### Success Response

```json
{
  "status": "success",
  "data": {
    "response": "# Legal Analysis\n\n## Analysis\n...",
    "confidence_note": "✅ High confidence in this analysis...",
    "disclaimer": "IMPORTANT LEGAL NOTICE...",
    "citations": [
      {
        "law_name": "Penal Code of Sri Lanka",
        "section": "299",
        "text": "Section 299: Whoever causes death..."
      }
    ],
    "metadata": {
      "sources_count": 2,
      "validation_status": "pass",
      "confidence": 0.9
    }
  },
  "session_id": "20260114_153045",
  "timestamp": "2026-01-14T15:30:45.123Z"
}
```

### Refusal Response

```json
{
  "status": "refused",
  "data": {
    "reason": "Cannot provide analysis due to:\n• No legal sources retrieved",
    "issues": [
      {
        "severity": "critical",
        "type": "missing_sources",
        "description": "No legal sources were retrieved from MCP"
      }
    ],
    "suggestions": "• Try rephrasing your question..."
  },
  "session_id": "20260114_153045",
  "timestamp": "2026-01-14T15:30:45.123Z"
}
```

---

## 📁 Audit Logs

### View Session Logs

```bash
# Get current session ID from any query response
curl http://localhost:8000/audit/20260114_153045
```

### Export Audit Report

```bash
# JSON format
curl http://localhost:8000/export/20260114_153045?format=json

# Markdown format
curl http://localhost:8000/export/20260114_153045?format=markdown
```

Logs are also automatically saved in the `logs/` directory:
- `logs/session_{id}.jsonl` - Append-only log
- `logs/export_{id}.json` - Full JSON export
- `logs/report_{id}.md` - Human-readable report

---

## 🔧 Configuration

### Environment Variables

Edit `.env` file:

```bash
# Required
OPENAI_API_KEY=sk-your-key

# Optional (with defaults)
MCP_HOST=localhost
MCP_PORT=3000
API_HOST=0.0.0.0
API_PORT=8000
AUDIT_LOG_DIR=logs
```

### Change Server Port

```bash
# In .env
API_PORT=9000

# Or override when running
export API_PORT=9000
python app.py
```

---

## 🐛 Troubleshooting

### Issue: "Module not found"

```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "OpenAI API key not configured"

```bash
# Check .env file exists and has your key
cat .env | grep OPENAI_API_KEY
```

### Issue: "MCP service not available"

This is expected if you don't have MCP running locally. The system will use mock data for demonstration.

To check MCP status:
```bash
curl http://localhost:8000/health
```

### Issue: "Port already in use"

```bash
# Change port in .env
API_PORT=9000

# Or kill process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

---

## 📚 Next Steps

1. **Read the Architecture**
   - Open `ARCHITECTURE.md` for complete system design
   - View `SYSTEM_DIAGRAM.md` for visual diagrams

2. **Explore the Code**
   - `agents/` - All agent implementations
   - `chains/main_chain.py` - Main orchestration
   - `app.py` - API endpoints

3. **Customize the System**
   - Add new agents
   - Modify validation rules
   - Extend schemas

4. **Deploy to Production**
   - Set up proper MCP service
   - Configure monitoring
   - Enable LangSmith tracing

---

## 🆘 Getting Help

- **Health Check**: http://localhost:8000/health
- **API Documentation**: http://localhost:8000/docs
- **Architecture Guide**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **System Diagram**: [SYSTEM_DIAGRAM.md](SYSTEM_DIAGRAM.md)

---

## 📝 Quick Reference

| Task | Command |
|------|---------|
| Setup | `python setup.py` |
| Start Server | `python app.py` |
| Run Tests | `python test_system.py` |
| Test Query | `curl -X POST http://localhost:8000/test/query` |
| View Docs | Open http://localhost:8000/docs |
| Health Check | `curl http://localhost:8000/health` |
| Stop Server | Press `Ctrl+C` |

---

**You're all set! 🎉**

Start the server with `python app.py` and begin querying the system!

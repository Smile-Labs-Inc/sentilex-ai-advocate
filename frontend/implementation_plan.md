### **Incident Reporting System - Full Implementation Plan**

#### **Overview**
This plan details the implementation of a production-ready Incident Reporting System featuring incident management, evidence attachment, persistent case memory, and a conversational AI interface. The system leverages **Google Gemini** (via LangChain) for AI capabilities and stores data locally for the initial phase.

***

### **Phase 1: Database & Backend Modeling**
*Focus: Setting up the data structure and SQLAlchemy models to support new features.*

#### **Task 1.1: Create Chat Message Model**
- **Action**: Create `backend/models/chat_message.py`.
- **Details**: Implement the `ChatMessage` class with fields for `incident_id`, `role` (user/assistant/system), `content`, and timestamps.
- **Reference**: See code snippet in `[NEW] chat_message.py` from the proposal.

#### **Task 1.2: Create Evidence Model**
- **Action**: Create `backend/models/evidence.py`.
- **Details**: Implement the `Evidence` class with fields for `incident_id`, `file_name`, `file_path`, `file_type`, `file_size`, and `uploaded_at`.
- **Reference**: See code snippet in `[NEW] evidence.py` from the proposal.

#### **Task 1.3: Update Incident Model & Init**
- **Action**: Modify `backend/models/incident.py` and `backend/models/__init__.py`.
- **Details**:
    - Add `relationship` properties to the `Incident` class to link it with `ChatMessage` and `Evidence` (cascade delete enabled).
    - Register new models in `__init__.py` to ensure Alembic detects them.

#### **Task 1.4: Database Migration**
- **Action**: Generate and apply Alembic migrations.
- **Commands**:
  ```bash
  alembic revision --autogenerate -m "Add chat messages and evidence tables"
  alembic upgrade head
  ```

***

### **Phase 2: Backend Logic & AI Agents**
*Focus: Implementing the core business logic, file handling, and AI memory integration.*

#### **Task 2.1: Implement Case Memory Agent**
- **Action**: Create `backend/agents/case_memory.py`.
- **Details**:
    - Implement `get_case_memory_chain` to load history from the DB into `ConversationBufferMemory`.
    - Initialize `ChatGoogleGenerativeAI` with `gemini-1.5-flash` (or your preferred model).
    - Implement `chat_with_case` to handle the read/write loop (User Msg → LLM → Save both to DB).

#### **Task 2.2: Implement Evidence Handling Logic**
- **Action**: Create utility functions for file storage (if not already present).
- **Details**: Ensure a local directory (e.g., `uploaded_evidence/`) exists. Implement safe file naming and saving logic.

#### **Task 2.3: Update API Routers**
- **Action**: Modify `backend/routers/incidents.py`.
- **Details**:
    - `POST /incidents/{id}/messages`: Call `chat_with_case`.
    - `GET /incidents/{id}/messages`: Return list of messages.
    - `POST /incidents/{id}/evidence`: specific logic to handle `UploadFile`, save to disk, and create `Evidence` DB record.
    - `GET /incidents/{id}/evidence`: Return list of file metadata.

***

### **Phase 3: Frontend Integration**
*Focus: Connecting the UI to the new backend endpoints.*

#### **Task 3.1: Update Service Layer**
- **Action**: Modify `frontend/src/services/incident.ts`.
- **Details**: Add TypeScript interfaces (`ChatMessageResponse`, `EvidenceResponse`) and fetch functions (`sendChatMessage`, `getChatMessages`, `uploadEvidence`).

#### **Task 3.2: Update Incident Workspace Hook**
- **Action**: Modify `frontend/src/hooks/useIncidentWorkspace.ts`.
- **Details**:
    - Replace any mock data with calls to the new service functions.
    - Implement state management for `chatHistory` and `evidenceList`.
    - Ensure the "Onboarding Wizard" correctly triggers the `createIncident` API call upon completion.

#### **Task 3.3: UI Component Binding**
- **Action**: Update `IncidentWorkspacePage`, `AIChatSection`, and `EvidenceSection`.
- **Details**:
    - Bind the "Send" button in Chat to `sendChatMessage`.
    - Bind the "Upload" button in Evidence to `uploadEvidence`.
    - Ensure real data renders in the lists.

***

### **Phase 4: Verification & Testing**
*Focus: Ensuring reliability and correctness.*

#### **Task 4.1: Automated Testing**
- **Action**: Add unit and integration tests.
- **Details**:
    - Check for existing tests using `find . -name "*test*"`.
    - Write a test for `case_memory.py` ensuring context is maintained.
    - Write API tests for uploading a file and verifying it exists on disk.

#### **Task 4.2: Manual End-to-End Test**
- **Action**: Perform a full user walkthrough.
- **Steps**:
    1.  Start Backend (`uvicorn main:app --reload`) and Frontend (`npm run dev`).
    2.  Create a new incident via Wizard.
    3.  Send a message: "Summarize this case." -> Verify AI responds with context.
    4.  Upload a PDF/Image -> Verify it appears in the list.
    5.  Restart servers -> Verify data persists.

***

### **Summary of Artifacts**

| Action | File Path | Description |
| :--- | :--- | :--- |
| **[NEW]** | `backend/models/chat_message.py` | DB Model for chat history |
| **[NEW]** | `backend/models/evidence.py` | DB Model for file metadata |
| **[NEW]** | `backend/agents/case_memory.py` | LangChain agent with persistent memory |
| **[MOD]** | `backend/models/incident.py` | Added relationships |
| **[MOD]** | `backend/routers/incidents.py` | Added API endpoints |
| **[MOD]** | `frontend/src/services/incident.ts` | Added API client methods |
| **[MOD]** | `frontend/src/hooks/useIncidentWorkspace.ts` | Connected UI state to Real API |
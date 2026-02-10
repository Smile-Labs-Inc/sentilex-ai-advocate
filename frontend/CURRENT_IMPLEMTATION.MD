# Sentilex AI Advocate - Technical Audit & Completion Roadmap

**Document Version:** 1.0  
**Last Updated:** 2026-02-08  
**Status:** In Development

---

## 📋 Table of Contents

1. [System Inventory & Status](#system-inventory--status)
2. [Frontend-Backend API Mapping](#frontend-backend-api-mapping)
3. [Missing Handshake List](#missing-handshake-list)
4. [Full User Walkthrough](#full-user-walkthrough)
5. [Final Completion Checklist](#final-completion-checklist)

---

## 🔍 System Inventory & Status

### Frontend Pages Overview

| Page                   | Route                 | Current State           | Backend Integration                 | Notes                                                  |
| ---------------------- | --------------------- | ----------------------- | ----------------------------------- | ------------------------------------------------------ |
| **Auth**               | `/` (default)         | ✅ Fully Integrated     | `/auth/*`                           | Login, Register, OAuth working                         |
| **Dashboard**          | `/dashboard`          | ⚠️ Partially Integrated | `/incidents/`, `/api/chat/stats`    | Static UI with mock data, needs real incident fetching |
| **New Incident**       | `/new-incident`       | ✅ Fully Integrated     | `/incidents/`                       | Wizard creates incident via API                        |
| **Incident Workspace** | `/incident-workspace` | ✅ Fully Integrated     | `/incidents/{id}/*`                 | Chat, evidence upload, incident creation working       |
| **Incident Detail**    | `/incident-detail`    | ⚠️ Static UI Only       | `/incidents/{id}`                   | No API calls implemented                               |
| **Lawyer Finder**      | `/lawyers`            | ✅ Fully Integrated     | `/lawyers/`                         | Search and list functionality working                  |
| **Evidence Vault**     | `/evidence`           | ✅ Fully Integrated     | `/evidence/*`                       | Filtering, deletion, global view working               |
| **Lawbook**            | `/lawbook`            | ✅ Fully Integrated     | `/lawbook/*`                        | Query, laws list, content fetch working                |
| **AI Chat**            | `/ai-chat`            | ⚠️ Partially Integrated | `/api/chat/*`                       | UI ready, needs session management                     |
| **Settings**           | `/settings`           | ⚠️ Partially Integrated | `/auth/me`, `/auth/change-password` | Profile update needs full implementation               |
| **Verify Email**       | `/verify-email`       | ✅ Fully Integrated     | `/auth/verify-email`                | Email verification working                             |

### Legend

- ✅ **Fully Integrated**: Page has complete backend communication
- ⚠️ **Partially Integrated**: Some features work, others need backend connection
- ❌ **Static UI Only**: No backend integration yet

---

## 🔗 Frontend-Backend API Mapping

### Authentication System

#### Frontend Service: `services/auth.ts`

| Frontend Method       | Backend Endpoint        | HTTP Method | Status     | Data Schema                                |
| --------------------- | ----------------------- | ----------- | ---------- | ------------------------------------------ |
| `register()`          | `/auth/register`        | POST        | ✅ Working | `RegisterRequest` → `RegistrationResponse` |
| `login()`             | `/auth/login`           | POST        | ✅ Working | `LoginRequest` → `LoginResponse`           |
| `logout()`            | `/auth/logout`          | POST        | ✅ Working | Bearer token required                      |
| `refreshToken()`      | `/auth/refresh`         | POST        | ✅ Working | `{refresh_token}` → `{access_token}`       |
| `getCurrentUser()`    | `/auth/me`              | GET         | ✅ Working | Returns `UserProfile`                      |
| `updateProfile()`     | `/auth/me`              | PATCH       | ✅ Working | `Partial<UserProfile>`                     |
| `verifyEmail()`       | `/auth/verify-email`    | POST        | ✅ Working | `{token}`                                  |
| `changePassword()`    | `/auth/change-password` | POST        | ✅ Working | `{current_password, new_password}`         |
| `setupMFA()`          | `/auth/mfa/setup`       | POST        | ✅ Working | Returns QR code & backup codes             |
| `enableMFA()`         | `/auth/mfa/enable`      | POST        | ✅ Working | `{code}`                                   |
| `getActiveSessions()` | `/auth/sessions`        | GET         | ✅ Working | Returns session list                       |
| `revokeSession()`     | `/auth/sessions/{id}`   | DELETE      | ✅ Working | Session ID required                        |

**Environment Variables Required:**

- `VITE_API_URL` (default: `http://127.0.0.1:8000`)
- JWT stored in: `localStorage.sentilex_auth_token`

---

### Incident Management System

#### Frontend Service: `services/incident.ts`

| Frontend Method             | Backend Endpoint                        | HTTP Method | Status     | Data Schema                                  |
| --------------------------- | --------------------------------------- | ----------- | ---------- | -------------------------------------------- |
| `createIncident()`          | `/incidents/`                           | POST        | ✅ Working | `IncidentCreate` → `IncidentResponse`        |
| `getIncidents()`            | `/incidents/`                           | GET         | ✅ Working | Query param: `status_filter`                 |
| `getIncident()`             | `/incidents/{id}`                       | GET         | ✅ Working | Returns `IncidentResponse`                   |
| `sendIncidentChatMessage()` | `/incidents/{id}/messages`              | POST        | ✅ Working | `{content}` → `IncidentChatExchangeResponse` |
| `getIncidentChatMessages()` | `/incidents/{id}/messages`              | GET         | ✅ Working | Returns message array                        |
| `uploadEvidence()`          | `/incidents/{id}/evidence`              | POST        | ✅ Working | FormData with files                          |
| `getIncidentEvidence()`     | `/incidents/{id}/evidence`              | GET         | ✅ Working | Returns evidence list                        |
| `deleteEvidence()`          | `/incidents/{id}/evidence/{evidenceId}` | DELETE      | ✅ Working | -                                            |

**Backend Routes:** `routers/incidents.py`

**Missing Endpoints:**

- ❌ `PATCH /incidents/{id}` - Update incident (exists in backend, not used in frontend)
- ❌ `DELETE /incidents/{id}` - Delete incident (exists in backend, not used in frontend)

---

### Evidence Management System (Global)

#### Frontend Service: `services/evidence.ts`

| Frontend Method  | Backend Endpoint | HTTP Method | Status     | Data Schema                                    |
| ---------------- | ---------------- | ----------- | ---------- | ---------------------------------------------- |
| `getAllEvidence` | `/evidence/`     | GET         | ✅ Working | Query params: filters → `EvidenceListResponse` |
| `getEvidence`    | `/evidence/{id}` | GET         | ✅ Working | Returns `EvidenceResponse`                     |
| `deleteEvidence` | `/evidence/{id}` | DELETE      | ✅ Working | -                                              |

**Backend Routes:** `routers/evidence.py`

---

### Document Generation System

#### Frontend Service: `services/documents.ts`

| Frontend Method          | Backend Endpoint                                     | HTTP Method | Status     | Return Type |
| ------------------------ | ---------------------------------------------------- | ----------- | ---------- | ----------- |
| `exportPoliceStatement`  | `/documents/incidents/{id}/export/police-statement`  | GET         | ✅ Working | Blob (PDF)  |
| `exportCERTReport`       | `/documents/incidents/{id}/export/cert-report`       | GET         | ✅ Working | Blob (PDF)  |
| `exportEvidenceManifest` | `/documents/incidents/{id}/export/evidence-manifest` | GET         | ✅ Working | Blob (PDF)  |
| `exportCaseFile`         | `/documents/incidents/{id}/export/case-file`         | GET         | ✅ Working | Blob (ZIP)  |

**Backend Routes:** `routers/documents.py`

---

### Lawyer Management System

#### Frontend Service: `services/lawyers.tsx`

| Frontend Method    | Backend Endpoint           | HTTP Method | Status     | Data Schema                                  |
| ------------------ | -------------------------- | ----------- | ---------- | -------------------------------------------- |
| `searchLawyers()`  | `/lawyers/`                | GET         | ✅ Working | Query params: `district`, `specialty`        |
| `register()`       | `/lawyers/register`        | POST        | ✅ Working | `LawyerRegisterRequest`                      |
| `login()`          | `/lawyers/login`           | POST        | ✅ Working | `LawyerLoginRequest` → `LawyerLoginResponse` |
| `getMyProfile()`   | `/lawyers/me`              | GET         | ✅ Working | Returns `LawyerProfile`                      |
| `updateProfile()`  | `/lawyers/me`              | PUT         | ✅ Working | `Partial<LawyerProfile>`                     |
| `changePassword()` | `/lawyers/change-password` | POST        | ✅ Working | `{current_password, new_password}`           |
| `verifyEmail()`    | `/lawyers/verify-email`    | POST        | ✅ Working | `{token}`                                    |
| `getSessions()`    | `/lawyers/sessions`        | GET         | ✅ Working | Returns session list                         |

**Backend Routes:** `routers/lawyers.py`

---

### Lawbook System

#### Frontend Service: `services/lawbook.tsx`

| Frontend Method     | Backend Endpoint   | HTTP Method | Status     | Data Schema                      |
| ------------------- | ------------------ | ----------- | ---------- | -------------------------------- |
| `fetchLaws()`       | `/lawbook/`        | GET         | ✅ Working | Returns `{laws: Law[]}`          |
| `fetchLawContent()` | `/lawbook/{lawId}` | GET         | ✅ Working | Returns `{content: string}`      |
| `submitQuery()`     | `/lawbook/query`   | POST        | ✅ Working | `QueryRequest` → `QueryResponse` |

**Backend Routes:** `routers/lawbook.py`

---

### Chat System (Session-Based)

#### Frontend Service: **MISSING** ❌

| Frontend Method    | Backend Endpoint          | HTTP Method | Status        | Data Schema                                |
| ------------------ | ------------------------- | ----------- | ------------- | ------------------------------------------ |
| ❌ Not implemented | `/api/chat/send`          | POST        | Backend Ready | `ChatSendMessage` → `ChatExchangeResponse` |
| ❌ Not implemented | `/api/chat/history`       | GET         | Backend Ready | Returns chat history                       |
| ❌ Not implemented | `/api/chat/sessions`      | GET         | Backend Ready | Returns session list                       |
| ❌ Not implemented | `/api/chat/sessions/{id}` | GET         | Backend Ready | Returns session with messages              |
| ❌ Not implemented | `/api/chat/sessions/{id}` | PATCH       | Backend Ready | Update session (rename)                    |
| ❌ Not implemented | `/api/chat/sessions/{id}` | DELETE      | Backend Ready | Delete session                             |
| ❌ Not implemented | `/api/chat/stats`         | GET         | Backend Ready | Returns chat statistics                    |

**Backend Routes:** `routers/chat.py`

**Config Endpoints Defined But Not Used:**

```typescript
CHAT: {
    SEND: '/api/chat/send',
    HISTORY: '/api/chat/history',
    SESSIONS: '/api/chat/sessions',
    SESSION: (id: string) => `/api/chat/sessions/${id}`,
    DELETE_SESSION: (id: string) => `/api/chat/sessions/${id}`,
    UPDATE_SESSION: (id: string) => `/api/chat/sessions/${id}`,
    STATS: '/api/chat/stats',
}
```

---

### Google OAuth

#### Frontend Service: `services/auth.ts`

| Frontend Method               | Backend Endpoint        | HTTP Method | Status     |
| ----------------------------- | ----------------------- | ----------- | ---------- |
| `getGoogleLoginUrl()`         | `/auth/google/login`    | GET         | ✅ Working |
| (Callback handled by backend) | `/auth/google/callback` | GET         | ✅ Working |

**Backend Routes:** `routers/google_oauth.py`

---

### Legal Queries

#### Backend Endpoint Available

| Backend Endpoint | HTTP Method | Status           | Frontend Usage          |
| ---------------- | ----------- | ---------------- | ----------------------- |
| `/legal-queries` | POST        | ✅ Backend Ready | ❌ Not used in frontend |
| `/legal-queries` | GET         | ✅ Backend Ready | ❌ Not used in frontend |

**Backend Routes:** `routers/legal_queries.py`

---

### Case Agent

#### Backend Endpoint Available

| Backend Endpoint      | HTTP Method | Status           | Frontend Usage          |
| --------------------- | ----------- | ---------------- | ----------------------- |
| `/case-agent/analyze` | POST        | ✅ Backend Ready | ❌ Not used in frontend |

**Backend Routes:** `routers/case_agent.py`

---

### Payments

#### Backend Endpoint Available

| Backend Endpoint          | HTTP Method | Status           | Frontend Usage          |
| ------------------------- | ----------- | ---------------- | ----------------------- |
| `/payments/create-order`  | POST        | ✅ Backend Ready | ❌ Not used in frontend |
| `/payments/capture-order` | POST        | ✅ Backend Ready | ❌ Not used in frontend |

**Backend Routes:** `routers/payments.py`

**Frontend Config Has:**

```typescript
PAYPAL_CLIENT_ID: ENV.PAYPAL_CLIENT_ID;
```

---

## ❌ Missing Handshake List (Tasks to Completion)

### 🔴 Critical - Blocking User Flows

#### 1. **Dashboard Page - Real Data Integration**

**Location:** `frontend/src/pages/Dashboard/Dashboard.tsx`

**Problem:** Dashboard uses mock data from `useDashboardData` hook instead of fetching real incidents.

**Required Changes:**

- Create `services/dashboard.ts` with:
  ```typescript
  async function getDashboardStats(): Promise<DashboardStats>;
  async function getUserIncidents(): Promise<Incident[]>;
  ```
- Update `hooks/useDashboardData.ts` to call:
  - `GET /incidents/` - Fetch user's incidents
  - `GET /api/chat/stats` - Fetch chat statistics (if implemented)
- **Data Schema Needed:**
  ```typescript
  interface DashboardStats {
    totalIncidents: number;
    activeIncidents: number;
    resolvedIncidents: number;
    totalMessages: number;
  }
  ```

**Auth Headers:** ✅ Already implemented (Bearer token)

---

#### 2. **AI Chat Page - Complete Implementation**

**Location:** `frontend/src/pages/AIChat/AIChat.tsx`

**Problem:** Page exists but has no service layer to communicate with `/api/chat/*` endpoints.

**Required Changes:**

- Create `services/chat.ts` with methods:
  ```typescript
  async function sendChatMessage(
    message: string,
    sessionId?: string,
  ): Promise<ChatExchangeResponse>;
  async function getChatSessions(): Promise<ChatSession[]>;
  async function getChatSession(
    sessionId: string,
  ): Promise<ChatSessionWithMessages>;
  async function createChatSession(title: string): Promise<ChatSession>;
  async function updateChatSession(
    sessionId: string,
    title: string,
  ): Promise<void>;
  async function deleteChatSession(sessionId: string): Promise<void>;
  async function getChatStats(): Promise<ChatStats>;
  ```

**Data Schemas Needed:**

```typescript
interface ChatSendMessage {
  message: string;
  session_id?: string;
}

interface ChatExchangeResponse {
  user_message: ChatMessage;
  assistant_message: ChatMessage;
  session_id: string;
}

interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

interface ChatStats {
  total_sessions: number;
  total_messages: number;
  total_user_messages: number;
  total_assistant_messages: number;
}
```

**Auth Headers:** ✅ Bearer token required

---

#### 3. **Incident Detail Page - Backend Integration**

**Location:** `frontend/src/pages/IncidentDetail/IncidentDetail.tsx`

**Problem:** Page receives incident as prop but doesn't fetch from backend or allow updates.

**Required Changes:**

- Add API call to fetch incident by ID: `GET /incidents/{id}`
- Add update functionality: `PATCH /incidents/{id}` (backend endpoint exists)
- Add delete functionality: `DELETE /incidents/{id}` (backend endpoint exists)

**Data Schema for Update:**

```typescript
interface IncidentUpdate {
  title?: string;
  description?: string;
  status?: "draft" | "submitted" | "under_review" | "resolved";
  // ... other fields
}
```

---

#### 4. **Evidence Vault Page - Complete Implementation**

**Location:** `frontend/src/pages/EvidenceVault/EvidenceVault.tsx`

**Problem:** Page is static UI only, no backend integration.

**Required Changes:**

- Fetch all evidence across all incidents: Need new backend endpoint
  - **Missing Backend:** `GET /evidence/` - Get all evidence for current user
  - Alternative: Loop through incidents and fetch evidence for each
- Display evidence with filtering/search
- Allow evidence download (need backend endpoint for file serving)

**Data Schema:**

```typescript
interface EvidenceVaultItem {
  id: number;
  incident_id: number;
  incident_title: string;
  file_name: string;
  file_type: string;
  file_size: number;
  uploaded_at: string;
}
```

**Missing Backend Endpoint:**

```python
@router.get("/evidence/all")
async def get_all_user_evidence(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
)
```

---

#### 5. **Settings Page - Complete Profile Management**

**Location:** `frontend/src/pages/Settings/Settings.tsx`

**Problem:** Partial implementation, needs full integration with auth endpoints.

**Required Changes:**

- Implement profile update form calling `PATCH /auth/me`
- Implement password change calling `POST /auth/change-password`
- Implement MFA management:
  - `POST /auth/mfa/setup`
  - `POST /auth/mfa/enable`
  - `POST /auth/mfa/disable`
  - `GET /auth/mfa/status`
- Implement session management:
  - `GET /auth/sessions`
  - `DELETE /auth/sessions/{id}`

**All endpoints exist, just need UI integration.**

---

### 🟡 Medium Priority - Enhanced Features

#### 6. **Case Agent Integration**

**Backend:** `routers/case_agent.py` - `/case-agent/analyze`

**Problem:** Backend has AI case analysis endpoint but frontend doesn't use it.

**Potential Use Cases:**

- Add "Analyze Case" button in Incident Workspace
- Automatically analyze incident after creation
- Show AI-generated case summary

**Data Schema:**

```typescript
interface CaseAnalysisRequest {
  incident_id: number;
  additional_context?: string;
}

interface CaseAnalysisResponse {
  summary: string;
  identified_laws: LawViolation[];
  recommendations: string[];
  confidence_score: number;
}
```

---

#### 7. **Legal Queries System**

**Backend:** `routers/legal_queries.py` - `/legal-queries`

**Problem:** Backend has legal query storage but frontend doesn't use it.

**Potential Use Cases:**

- Save lawbook queries for later reference
- View query history
- Share queries with lawyers

**Data Schema:**

```typescript
interface LegalQueryCreate {
  question: string;
  context?: string;
}

interface LegalQueryResponse {
  id: number;
  user_id: number;
  question: string;
  answer: string;
  created_at: string;
}
```

---

#### 8. **Payment Integration**

**Backend:** `routers/payments.py` - `/payments/*`

**Problem:** PayPal integration exists in backend but not used in frontend.

**Potential Use Cases:**

- Pay for lawyer consultations
- Premium features
- Document certification fees

**Required:**

- Create `services/payments.ts`
- Add PayPal button component
- Integrate with lawyer finder or premium features

**Config Already Has:**

```typescript
PAYPAL_CLIENT_ID: ENV.PAYPAL_CLIENT_ID;
```

---

### 🟢 Low Priority - Nice to Have

#### 9. **Lawyer Verification Admin Panel**

**Backend:** `routers/lawyer_verification.py`

**Problem:** Admin endpoints exist but no admin UI.

**Endpoints:**

- `GET /admin/lawyers/pending`
- `POST /admin/lawyers/{id}/verify`
- `POST /admin/lawyers/{id}/reject`

**Requires:**

- Admin authentication flow
- Admin dashboard page
- Lawyer verification UI

---

#### 10. **Document Storage Service**

**Backend:** `models/DocumentStorageService.py`

**Problem:** Backend has document storage model but no API endpoints.

**Potential Use:**

- Store legal documents
- Generate PDF reports
- Archive incident reports

---

## 🚶 Full User Walkthrough (The Journey)

### Happy Path: New User Registration → Incident Report → Lawyer Consultation

#### 1. **User Registration & Email Verification**

```
User lands on → / (redirects to Auth page)
├─ User clicks "Sign Up"
├─ Fills registration form
├─ Frontend calls → POST /auth/register
│  └─ Backend creates user, sends verification email
├─ User receives email with token
├─ User clicks link → /verify-email?token=xxx
├─ Frontend calls → POST /auth/verify-email
│  └─ Backend marks email as verified
└─ User redirected to → /dashboard
```

**Data Flow:**

```typescript
RegisterRequest {
  email: string,
  password: string,
  full_name: string
}
→ Backend validates, creates user
→ Returns RegistrationResponse {
  message: "Registration successful",
  user_id: number
}
```

**Error Handling:**

- If email exists: Backend returns `400` with `{detail: "Email already registered"}`
- Frontend shows toast notification
- If verification fails: Backend returns `400` with `{detail: "Invalid or expired token"}`

---

#### 2. **User Login**

```
User lands on → / (Auth page)
├─ User enters credentials
├─ Frontend calls → POST /auth/login
│  └─ Backend validates credentials, generates JWT
├─ Frontend stores tokens in localStorage
├─ Frontend calls → GET /auth/me
│  └─ Backend returns user profile
└─ User redirected to → /dashboard
```

**Data Flow:**

```typescript
LoginRequest { email, password }
→ Backend validates
→ Returns LoginResponse {
  access_token: string,
  refresh_token: string,
  token_type: "bearer",
  user_id: number,
  email: string,
  full_name: string
}
```

**Error Handling:**

- If credentials invalid: Backend returns `401` with `{detail: "Invalid credentials"}`
- If email not verified: Backend returns `403` with `{detail: "Email not verified"}`
- Frontend shows error toast

---

#### 3. **Dashboard - First View**

```
User lands on → /dashboard
├─ Frontend calls → GET /incidents/ (with Bearer token)
│  └─ Backend returns empty array (new user)
├─ Dashboard shows "New User" view with CTA
├─ Mock stats displayed (needs real data integration)
└─ User clicks "Report New Incident"
   └─ Navigates to → /new-incident
```

**Current Issue:** ⚠️ Dashboard uses mock data, needs real API integration

---

#### 4. **Create Incident Report**

```
User on → /new-incident
├─ Wizard Step 1: Incident Type
│  └─ User selects type (cyberbullying, harassment, etc.)
├─ Wizard Step 2: Basic Information
│  └─ User enters title, description, date, location
├─ Wizard Step 3: Additional Details
│  └─ User enters platforms, perpetrator info
├─ User clicks "Complete"
├─ Frontend calls → POST /incidents/
│  └─ Backend creates incident, returns incident_id
└─ User redirected to → /incident-workspace
```

**Data Flow:**

```typescript
IncidentCreate {
  incident_type: 'cyberbullying',
  title: 'Harassment on social media',
  description: 'Detailed description...',
  date_occurred: '2026-02-08',
  location: 'Colombo, Sri Lanka',
  jurisdiction: 'Sri Lanka',
  platforms_involved: 'Facebook, Instagram',
  perpetrator_info: 'Username: @harasser123'
}
→ Backend creates incident
→ Returns IncidentResponse {
  id: 123,
  user_id: 456,
  status: 'submitted',
  created_at: '2026-02-08T18:53:15Z',
  ...
}
```

**Error Handling:**

- If unauthorized: Backend returns `401`, frontend redirects to login
- If validation fails: Backend returns `422` with field errors
- Frontend shows validation errors inline

---

#### 5. **Incident Workspace - AI Analysis & Evidence Upload**

```
User on → /incident-workspace
├─ Incident created (ID stored in state)
├─ AI Analysis starts automatically (mock, 2-second delay)
├─ Timeline shows "Incident Reported" event
├─ After analysis:
│  ├─ Timeline shows "AI Analysis Complete"
│  └─ Identified laws displayed (mock data)
├─ User uploads evidence:
│  ├─ Selects files
│  ├─ Frontend calls → POST /incidents/{id}/evidence
│  │  └─ Backend saves files, returns evidence metadata
│  └─ Timeline updated with "Evidence Uploaded" event
├─ User chats with AI:
│  ├─ Types message
│  ├─ Frontend calls → POST /incidents/{id}/messages
│  │  └─ Backend processes with AI, returns response
│  └─ Chat UI updates with both messages
└─ User clicks "Submit to Police"
   └─ Incident status updated (currently local only)
```

**Data Flow - Evidence Upload:**

```typescript
FormData with files
→ POST /incidents/123/evidence
→ Backend saves to uploaded_evidence/
→ Returns EvidenceResponse[] {
  id: 789,
  incident_id: 123,
  file_name: 'screenshot.png',
  file_path: 'uploaded_evidence/xxx.png',
  file_type: 'image/png',
  file_size: 245678,
  uploaded_at: '2026-02-08T19:00:00Z'
}
```

**Data Flow - AI Chat:**

```typescript
{ content: 'What laws apply to my case?' }
→ POST /incidents/123/messages
→ Backend:
  1. Saves user message
  2. Calls AI chain with incident context
  3. Saves AI response
→ Returns IncidentChatExchangeResponse {
  user_message: { id, role: 'user', content, created_at },
  assistant_message: { id, role: 'assistant', content, created_at }
}
```

**Error Handling:**

- If file too large: Backend returns `413` with `{detail: "File too large"}`
- If AI fails: Backend returns `500`, frontend shows fallback message
- If unauthorized: Backend returns `401`, frontend redirects to login

---

#### 6. **Find Lawyer**

```
User clicks "Find Lawyers" from workspace
├─ Navigates to → /lawyers
├─ Frontend calls → GET /lawyers/?specialty=cyber-crime
│  └─ Backend returns filtered lawyer list
├─ User views lawyer profiles
├─ User clicks "Contact" (future: payment integration)
└─ User can filter by district, specialty
```

**Data Flow:**

```typescript
GET /lawyers/?specialty=cyber-crime&district=Colombo
→ Backend queries database
→ Returns Lawyer[] {
  id, name, specialties, rating, reviews_count,
  availability, experience_years, email, phone,
  district, verification_status, is_active
}
```

---

#### 7. **Lawbook Research**

```
User navigates to → /lawbook
├─ Frontend calls → GET /lawbook/
│  └─ Backend returns list of available laws
├─ User selects a law
├─ Frontend calls → GET /lawbook/{lawId}
│  └─ Backend returns law content (markdown)
├─ User submits query
├─ Frontend calls → POST /lawbook/query
│  └─ Backend processes with AI, returns analysis
└─ User views citations and legal analysis
```

**Data Flow - Query:**

```typescript
QueryRequest {
  question: 'What is the penalty for cyberbullying?',
  case_context: 'My incident details...'
}
→ POST /lawbook/query
→ Backend:
  1. Retrieves relevant laws from vector DB
  2. Processes with AI reasoning chain
  3. Validates with legal validator
→ Returns QueryResponse {
  status: 'success',
  data: {
    response: 'Based on the Computer Crimes Act...',
    confidence_note: 'High confidence (92%)',
    disclaimer: 'This is not legal advice...',
    metadata: { retrieval_timestamp, sources_count, ... },
    citations: [{ law_name, section, text }, ...]
  },
  session_id: 'uuid',
  timestamp: '2026-02-08T19:30:00Z'
}
```

---

#### 8. **Session Management & Logout**

```
User clicks profile → Settings
├─ Frontend calls → GET /auth/sessions
│  └─ Backend returns active sessions
├─ User views sessions (device, IP, last activity)
├─ User revokes a session
├─ Frontend calls → DELETE /auth/sessions/{id}
│  └─ Backend invalidates session
└─ User clicks "Logout"
   ├─ Frontend calls → POST /auth/logout
   │  └─ Backend blacklists token
   ├─ Frontend clears localStorage
   └─ User redirected to → / (Auth page)
```

---

### Error Scenarios

#### Scenario 1: Token Expiration During Session

```
User performs action → Frontend calls API with expired token
├─ Backend returns → 401 Unauthorized
├─ Frontend intercepts error
├─ Frontend calls → POST /auth/refresh
│  └─ Backend validates refresh token, returns new access token
├─ Frontend retries original request with new token
└─ If refresh fails:
   ├─ Frontend clears tokens
   └─ Redirects to login page
```

**Current Issue:** ⚠️ Token refresh logic needs implementation in frontend

---

#### Scenario 2: Network Failure

```
User submits form → Frontend calls API
├─ Network error (timeout, no connection)
├─ Frontend catches error
├─ Shows toast: "Network error. Please try again."
└─ User can retry action
```

---

#### Scenario 3: Validation Error

```
User submits incident with missing required field
├─ Frontend calls → POST /incidents/
├─ Backend returns → 422 Unprocessable Entity
│  └─ { detail: [{ loc: ['body', 'title'], msg: 'field required' }] }
├─ Frontend parses validation errors
└─ Shows inline error messages on form fields
```

---

## ✅ Final Completion Checklist

### 🔐 Authentication (95% Complete)

- [x] User registration
- [x] Email verification
- [x] Login/Logout
- [x] JWT token management
- [x] Google OAuth integration
- [x] Password reset flow
- [x] MFA setup & enable
- [ ] **Token auto-refresh on expiration** (needs implementation)
- [ ] **Session timeout warning** (nice to have)

---

### 📋 Incident Management (85% Complete)

- [x] Create incident via wizard
- [x] Incident creation API integration
- [x] Evidence upload
- [x] Incident chat with AI
- [x] Chat message persistence
- [x] Evidence listing
- [x] Evidence deletion
- [ ] **Fetch incidents on Dashboard** (critical)
- [ ] **Update incident details** (backend ready, frontend missing)
- [ ] **Delete incident** (backend ready, frontend missing)
- [ ] **Incident status workflow** (draft → submitted → under_review → resolved)
- [ ] **Download evidence files** (needs backend endpoint)

---

### 💬 Chat System (30% Complete)

- [x] Incident-specific chat (working)
- [ ] **General AI chat page** (UI exists, no backend integration)
- [ ] **Chat session management** (backend ready, frontend missing)
- [ ] **Chat history sidebar** (backend ready, frontend missing)
- [ ] **Session rename** (backend ready, frontend missing)
- [ ] **Session deletion** (backend ready, frontend missing)
- [ ] **Chat statistics** (backend ready, frontend missing)

---

### ⚖️ Lawyer System (90% Complete)

- [x] Lawyer search & filter
- [x] Lawyer registration
- [x] Lawyer login
- [x] Lawyer profile management
- [x] Email verification for lawyers
- [x] Session management for lawyers
- [ ] **Lawyer-client messaging** (not implemented)
- [ ] **Lawyer booking system** (not implemented)
- [ ] **Payment integration** (backend ready, frontend missing)

---

### 📚 Lawbook System (100% Complete)

- [x] List available laws
- [x] View law content
- [x] Submit legal queries
- [x] AI-powered legal analysis
- [x] Citations & references
- [x] Confidence scoring
- [x] Legal disclaimers

---

### 📊 Dashboard & Analytics (40% Complete)

- [x] Dashboard UI
- [x] Stats grid component
- [x] Activity feed component
- [ ] **Real incident data fetching** (critical)
- [ ] **Real statistics** (currently mock data)
- [ ] **Chart data from backend** (currently mock)
- [ ] **Recent activity from backend** (currently mock)

---

### 🔧 Settings & Profile (60% Complete)

- [x] View profile
- [x] Update profile API
- [ ] **Profile update UI** (needs full implementation)
- [ ] **Password change UI** (needs implementation)
- [ ] **MFA management UI** (backend ready, UI missing)
- [ ] **Session management UI** (backend ready, UI missing)
- [ ] **Notification preferences** (not implemented)

---

### 🗄️ Evidence Vault (10% Complete)

- [x] Evidence vault page UI
- [ ] **Fetch all user evidence** (needs backend endpoint)
- [ ] **Evidence filtering** (needs implementation)
- [ ] **Evidence search** (needs implementation)
- [ ] **Evidence download** (needs backend endpoint)
- [ ] **Evidence preview** (needs implementation)

---

### 🤖 Advanced AI Features (20% Complete)

- [x] Incident chat AI
- [x] Lawbook query AI
- [ ] **Case agent analysis** (backend ready, frontend missing)
- [ ] **Automatic law identification** (currently mock)
- [ ] **Evidence analysis** (not implemented)
- [ ] **Timeline auto-generation** (partially mock)

---

### 💳 Payment System (0% Complete)

- [ ] **PayPal integration** (backend ready, frontend missing)
- [ ] **Create payment order** (backend ready)
- [ ] **Capture payment** (backend ready)
- [ ] **Payment history** (not implemented)
- [ ] **Lawyer consultation payments** (not implemented)

---

### 🛡️ Admin Features (0% Complete)

- [ ] **Admin login** (backend ready)
- [ ] **Lawyer verification UI** (backend ready)
- [ ] **Admin dashboard** (not implemented)
- [ ] **User management** (not implemented)
- [ ] **System analytics** (not implemented)

---

## 📝 Priority Implementation Order

### Phase 1: Critical Fixes (Week 1)

1. ✅ **Dashboard real data integration** - Fetch incidents from `/incidents/`
2. ✅ **Token auto-refresh** - Implement refresh logic in auth service
3. ✅ **Incident detail page** - Add fetch, update, delete functionality

### Phase 2: Core Features (Week 2)

4. ✅ **AI Chat page** - Complete session-based chat implementation
5. ✅ **Settings page** - Full profile, password, MFA, session management
6. ✅ **Evidence vault** - Backend endpoint + frontend integration

### Phase 3: Enhanced Features (Week 3)

7. ✅ **Case agent integration** - Add analyze button in workspace
8. ✅ **Legal queries** - Save and view query history
9. ✅ **Payment integration** - PayPal for lawyer consultations

### Phase 4: Admin & Polish (Week 4)

10. ✅ **Admin panel** - Lawyer verification UI
11. ✅ **Error handling** - Comprehensive error boundaries
12. ✅ **Loading states** - Better UX for async operations
13. ✅ **Testing** - Unit and integration tests

---

## 🔑 Environment Variables Checklist

### Frontend (.env)

```bash
VITE_API_URL=http://127.0.0.1:8000
VITE_FRONTEND_URL=http://localhost:5173
VITE_ENABLE_GOOGLE_AUTH=true
VITE_PAYPAL_CLIENT_ID=your_paypal_client_id
```

### Backend (.env)

```bash
SECRET_KEY=your-secret-key-min-32-chars
DATABASE_URL=postgresql://user:pass@localhost/sentilex_db
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
OPENAI_API_KEY=your_openai_key
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_secret
```

---

## 🎯 Success Metrics

### Current Completion Status

- **Authentication:** 95% ✅
- **Incident Management:** 85% ⚠️
- **Lawyer System:** 90% ✅
- **Lawbook:** 100% ✅
- **Chat System:** 30% ❌
- **Dashboard:** 40% ❌
- **Evidence Vault:** 10% ❌
- **Payments:** 0% ❌
- **Admin:** 0% ❌

### Overall Project Completion: **~60%**

---

## 📞 Next Steps

1. **Review this document** with the team
2. **Prioritize missing features** based on business needs
3. **Assign tasks** from the completion checklist
4. **Create backend endpoints** for missing functionality (Evidence Vault, etc.)
5. **Implement frontend services** for existing backend endpoints (Chat, Case Agent, etc.)
6. **Add comprehensive error handling** and loading states
7. **Write tests** for critical user flows
8. **Deploy to staging** for user testing

---

**Document maintained by:** Development Team  
**Last audit:** 2026-02-08  
**Next review:** After Phase 1 completion

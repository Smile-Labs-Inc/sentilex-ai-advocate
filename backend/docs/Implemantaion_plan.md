# Elite Sri Lankan Court-Admissible AI System
## 2026 University Competition Project Plan

**Objective:** Build a legally-compliant, forensically-secure, and admissible AI system for processing sensitive legal cases in Sri Lankan courts.

---

## Executive Summary

This project addresses five critical gaps that prevent AI systems from being accepted in Sri Lankan legal proceedings:

1. **Chain of Custody** - Forensic integrity through tamper-proof metadata
2. **Multi-Agent Legal Nuance** - Specialized agents for legal accuracy and compliance
3. **Zero-Knowledge Privacy** - Trauma data handling without identity linkage
4. **Warm Handoff** - Intelligent referral and resource routing
5. **Offline-First Architecture** - Resilient trauma intake for low-connectivity areas

---

## Project Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│  (React Frontend + Whisper + Offline Storage)                │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│              INTELLIGENT PROCESSING LAYER                    │
│  (LangGraph Multi-Agent Orchestration)                       │
│  ├─ Supervisor Agent                                        │
│  ├─ Researcher Agent                                        │
│  ├─ Legal Auditor Agent                                     │
│  └─ Glossary Agent (Sinhala/Tamil)                          │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│              KNOWLEDGE & COMPLIANCE LAYER                    │
│  (RAG with Sri Lankan Legal Corpus)                          │
│  ├─ Sri Lanka Penal Code                                    │
│  ├─ Online Safety Act 2021                                  │
│  └─ Procedural Law Database                                 │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│            FORENSIC & SECURITY LAYER                         │
│  (Cryptography + Zero-Knowledge Architecture)                │
│  ├─ SHA-256 Hashing Engine                                  │
│  ├─ AES Encryption                                          │
│  ├─ Anonymous ID Generation (UUID)                          │
│  ├─ PII Redaction Sub-Agent                                 │
│  └─ Digital Receipt Generator                               │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│              DATA & INTEGRATION LAYER                        │
│  (AWS S3 + PostgreSQL + Referral APIs)                       │
│  ├─ Encrypted S3 Vault                                      │
│  ├─ Identity-Separate Database                              │
│  ├─ Police Bureau API (Tell IGP)                            │
│  └─ NGO Directory Service                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase Breakdown: 8 Core Tasks

### TASK 1: The Vault - Forensic Infrastructure & Integrity
**Duration:** 1 week | **Goal:** Implement cryptographic foundation for court admissibility

#### Subtasks:

**1.1 - Tamper-Proof Metadata System**
- [ ] Design manifest schema: `{ GPS_location, device_ID, timestamp, file_hash }`
- [ ] Implement SHA-256 hashing of entire manifest string
- [ ] Store manifest in tamper-proof log (write-once append database)
- [ ] Create versioning system for audit trail

**1.2 - Digital Receipt Generation**
- [ ] Build receipt template with:
  - Original file hash
  - Manifest hash
  - Timestamp of receipt generation
  - Unique receipt ID
- [ ] Implement QR code encoding for physical/digital sharing
- [ ] Create receipt verification endpoint (for CID/courts to re-hash and validate)
- [ ] Export receipt as PDF and JSON formats

**1.3 - AWS S3 Vault Architecture**
- [ ] Configure S3 bucket with server-side encryption (SSE-KMS)
- [ ] Implement bucket versioning for immutable storage
- [ ] Setup access logging and CloudTrail auditing
- [ ] Create IAM policies with principle of least privilege
- [ ] Deploy S3 object lock for compliance mode (90-day retention minimum)

**1.4 - AES Encryption Pipeline**
- [ ] Implement AES-256-GCM encryption for all uploaded files
- [ ] Generate unique encryption keys per user
- [ ] Store encryption keys in AWS Secrets Manager (separate from S3)
- [ ] Create encrypt/decrypt utility functions with error handling

**1.5 - Chain of Custody Ledger**
- [ ] Design PostgreSQL table schema for custody events
- [ ] Implement immutable logging (append-only, no updates)
- [ ] Create endpoints to retrieve full custody chain for any file
- [ ] Generate custody chain PDF report for court submission

---

### TASK 2: Voice & Vibe - Accessibility & Frontend
**Duration:** 1 week | **Goal:** Build trauma-informed, multilingual intake UI

#### Subtasks:

**2.1 - React Frontend Architecture**
- [ ] Setup React 19 + TypeScript project structure
- [ ] Implement responsive design for mobile-first (primary access from phones)
- [ ] Create trauma-informed UI design system (calm colors, large buttons, minimal distractions)
- [ ] Build progressive disclosure forms (show fields step-by-step, not all at once)

**2.2 - Whisper Integration (Sinhala/Tamil Optimization)**
- [ ] Integrate OpenAI Whisper for real-time transcription
- [ ] Optimize model loading for Sinhala and Tamil languages
- [ ] Implement confidence score detection (flag low-confidence sections for review)
- [ ] Create manual transcript correction UI (allow user to fix transcription)
- [ ] Add speaker diarization (if multiple voices present)

**2.3 - Offline-First Sync Architecture**
- [ ] Implement IndexedDB for local encrypted storage
- [ ] Build service worker for offline functionality
- [ ] Create sync queue system (when connection restored, push queued data)
- [ ] Add visual indicators for sync status (saved locally, pending upload, synced)
- [ ] Implement conflict resolution if offline edits conflict with server

**2.4 - Local Encryption Buffer**
- [ ] Use TweetNaCl.js for client-side AES encryption (before upload)
- [ ] Generate per-session encryption key (derive from user's first input)
- [ ] Store encrypted transcript locally with expiration (clear after 7 days if unsent)
- [ ] Create "Data Loss Prevention" warnings

**2.5 - Multi-Language Support (Sinhala/Tamil)**
- [ ] Implement i18n library (react-i18next)
- [ ] Create translation files for all UI components
- [ ] Add RTL support for potential future Arabic/Urdu
- [ ] Build language selector with persistent preference

**2.6 - Accessibility Compliance**
- [ ] Ensure WCAG 2.1 AA compliance (screen readers, keyboard navigation)
- [ ] Add alt text for all images
- [ ] Implement focus indicators for keyboard users
- [ ] Test with VoiceOver (macOS/iOS) and NVDA (Windows)

---

### TASK 3: The Brain - Multi-Agent Orchestration
**Duration:** 1 week | **Goal:** Build intelligent agent system with legal oversight

#### Subtasks:

**3.1 - LangGraph Supervisor Agent**
- [x] Design supervisor flow in LangGraph
- [x] Implement routing logic to delegate to specialist agents
- [x] Create prompt for supervisor to understand task categorization
- [x] Build error recovery (if agents fail, retry with different approach)
- [x] Implement reasoning trace logging for explainability

**3.2 - Researcher Agent**
- [x] Build agent to analyze case facts and extract key information
- [x] Create prompts for structured extraction (parties, allegations, timeline)
- [x] Implement fact validation against RAG knowledge base
- [x] Generate "Problem Category" recommendations (e.g., "Sexual Abuse under Penal Code 363")
- [x] Output structured JSON with extracted facts

**3.3 - Legal Auditor Agent** (Specialized Compliance Check)
- [x] Create auditor agent with single responsibility: audit Researcher's work
- [x] Build prompts to check:
- [x]   Is the categorization legally sound under Sri Lankan law?
- [x]   Are there alternative legal interpretations?
- [x]   Does the categorization comply with Online Safety Act 2021?
- [x]   Are there jurisdictional concerns?
- [x] Implement rejection with detailed reasoning (explain why category might be wrong)
- [x] Create "confidence score" for each audit (0-100%)
- [x] If confidence < 70%, escalate to human lawyer review

**3.4 - Glossary Agent (Legal Terminology Compliance)**
- [/] Build Sinhala/Tamil legal terminology database
  - Example: "Sexual Abuse" → Sinhala: "කාමुක අපයෝජනය" (precise legal term)
  - Example: "Harassment" → Tamil: "தொல்லை" (vs informal words)
- [/] Create agent to detect informal language in transcript
- [/] Implement term mapping (convert informal → formal legal terminology)
- [/] Generate "Terminology Report" showing all replacements
- [/] Validate terminology against Online Safety Act glossary

**3.5 - Agent Communication Protocol**
- [x] Design message passing format between agents (JSON schema)
- [x] Implement tool calling for agent-to-agent queries
- [x] Create shared context manager (all agents access same facts)
- [x] Build agent health monitoring (log execution time, success rate)
- [x] Implement circuit breaker (if agent fails 3x, notify admin)

**3.6 - Reasoning & Explainability**
- [x] Log all agent decisions with reasoning (why did Auditor reject this?)
- [x] Create debug mode to visualize agent flow
- [x] Generate "Decision Trail" PDF (show all agent interactions)
- [x] Implement human-in-the-loop review UI (lawyer can override/approve)

---

### TASK 4: The Librarian - RAG Knowledge System
**Duration:** 1 week | **Goal:** Build specialized legal knowledge base

#### Subtasks:

**4.1 - Sri Lankan Legal Corpus Ingestion**
- [x] Collect and digitize:
  - Sri Lanka Penal Code (sections relevant to Online Safety Act)
  - Online Safety Act 2021 (full text)
  - Supreme Court precedent cases (minimum 50 landmark cases)
  - Procedural law guidelines (e.g., how to file a complaint)
- [x] Convert PDFs to structured text with section references
- [x] Create semantic chunking (split by legal concepts, not arbitrary lengths)

**4.2 - Vector Embedding & Retrieval**
- [x] Use OpenAI embeddings (or open-source alternative like BGE)
- [x] Create vector database (Pinecone, Weaviate, or Supabase pgvector)
- [x] Implement semantic search for legal queries
- [x] Build metadata filters (search by act, section, year, etc.)
- [x] Create hybrid search (keyword + semantic) for accuracy

**4.3 - RAG Pipeline for Legal Queries**
- [x] Build retrieval pipeline: `Query → Embedding → Vector Search → Reranking`
- [x] Implement reranking using cross-encoder (e.g., `ms-marco-MiniLM-L-12-v2`)
- [x] Create context window manager (include top 5-10 relevant sections)
- [x] Implement citation tracking (every answer includes source section numbers)
- [x] Build confidence scoring (low confidence → escalate to human lawyer)

**4.4 - Precedent Case Database**
- [/] Scrape Sri Lankan Supreme/Court of Appeal decisions from LatestLK or legal databases
- [/] Structure cases: `{ case_name, year, parties, allegation_category, court_decision, relevant_sections }`
- [/] Implement case similarity search (find similar past cases to current fact pattern)
- [/] Create "precedent matching" feature (highlight relevant case law)

**4.5 - Online Safety Act Mapping**
- [/] Create jurisdiction mapping:
  - Sections 4-8: Online Harassment & Cyberbullying
  - Sections 9-12: Child Sexual Exploitation Material (CSEM)
  - Sections 13-15: Non-consensual intimate images
- [/] Build decision tree for categorization (which section applies?)
- [/] Implement legal consequence database (what is the punishment range?)

**4.6 - Knowledge Base Update Protocol**
- [/] Design quarterly update schedule
- [/] Create version control for legal corpus
- [/] Implement deprecation markers for outdated sections
- [/] Build notification system when precedent changes

---

### TASK 5: The Clerk - PDF Report Generation
**Duration:** 1 week | **Goal:** Generate court-admissible police statement documents

#### Subtasks:

**5.1 - C-Form (Police Statement) PDF Generator**
- [ ] Understand C-Form template from CID/Sri Lanka Police
- [ ] Create dynamic PDF template with:
  - Complainant details (anonymized or named, user choice)
  - Incident description (from transcript + AI categorization)
  - Alleged offense (legal categorization from Researcher Agent)
  - Case category (from Online Safety Act mapping)
  - Evidence list (uploaded files, metadata hashes)
- [ ] Implement digital signature placeholder (for lawyer to sign later)
- [ ] Add footer with "Generated on [date] using AI Legal Assistant v2.0"

**5.2 - Metadata & Evidence Annex**
- [ ] Create detailed evidence annex including:
  - File hash (SHA-256)
  - Digital receipt QR code
  - Chain of custody timeline
  - Encryption certificate proof
- [ ] Implement tamper-evident design (watermark: "FORENSICALLY SECURED")
- [ ] Generate integrity verification guide (how CID can verify authenticity)

**5.3 - Multi-Format Export**
- [ ] PDF export (for courts, lawyers, filing)
- [ ] JSON export (for digital record systems)
- [ ] XML export (for integration with official justice portals)
- [ ] Implement format validation before export

**5.4 - Lawyer Review & Annotation Interface**
- [ ] Build UI for lawyers to review AI-generated report
- [ ] Allow in-document editing (change facts, add legal commentary)
- [ ] Implement version tracking (show original vs. lawyer-edited)
- [ ] Create "Audit Trail" (all lawyer edits logged and timestamped)
- [ ] Add lawyer e-signature integration

**5.5 - Report Versioning & Archive**
- [ ] Implement immutable report versioning
- [ ] Store all versions in tamper-proof archive
- [ ] Create "Report History" UI (show all edits, who made them, when)
- [ ] Implement retention policy (keep for 7 years per SOP)

**5.6 - PDF Security**
- [ ] Implement PDF encryption (password-protected for sensitive cases)
- [ ] Add metadata encryption (prevent reading of embedded details)
- [ ] Create "Print to PDF" security warnings (warn if user prints to insecure printer)
- [ ] Implement expiring document links (reports accessible for 30 days, then require re-authentication)

---

### TASK 6: The Bridge - Referral & Integration Layer
**Duration:** 1 week | **Goal:** Build intelligent routing to authorities and support organizations

#### Subtasks:

**6.1 - Geo-Fencing & Location-Based Routing**
- [ ] Integrate Google Maps API or local Sri Lankan mapping service
- [ ] Build geo-fencing for Police Women & Children's Bureau locations
  - Colombo Metropolitan Bureau
  - Regional bureaus (8 across Sri Lanka)
  - Contact details, operating hours, specialties
- [ ] Create NGO directory with coordinates:
  - The LEADS Foundation
  - Women's Need Collective
  - CERI (Center for Empowerment and Research for Equality)
  - Sarvodaya Women's Development
- [ ] Implement distance calculation and sorting (closest services first)
- [ ] Generate "Nearest Resources" card with:
  - Organization name, distance, phone, hours
  - Directions link (Apple Maps/Google Maps)
  - Languages spoken

**6.2 - Dynamic Referral Logic**
- [ ] Build referral rules engine:
  - If allegation = child abuse → prioritize child-specialized bureaus
  - If allegation = sexual abuse → prioritize women bureaus
  - If allegation = cyberbullying → standard cyber crime units
- [ ] Implement confidence-based routing:
  - High confidence case → direct to specialized bureau
  - Low confidence → suggest multiple options
  - Edge case → suggest general legal aid

**6.3 - Direct API Integration (Tell IGP Portal Webhook)**
- [ ] Research Tell IGP portal API specifications
- [ ] Design webhook payload schema:
  ```json
  {
    "case_id": "UUID",
    "category": "Online Safety Act - Section X",
    "severity": "high|medium|low",
    "hashed_evidence": "SHA-256-HASH",
    "digital_receipt_id": "RECEIPT-ID",
    "complainant_anonymous_id": "UUID",
    "jurisdiction": "Colombo|Kandy|etc",
    "timestamp": "ISO-8601"
  }
  ```
- [ ] Implement OAuth 2.0 authentication with Tell IGP
- [ ] Build retry logic (if webhook fails, queue for manual retry)
- [ ] Create webhook logging and audit trail
- [ ] Implement "Push Status Tracker" (user can see if report reached Tell IGP)

**6.4 - Sri Lanka CERT Integration**
- [ ] Research Sri Lanka CERT reporting procedures
- [ ] If case involves cybersecurity threat → auto-trigger CERT notification
- [ ] Create incident classification for CERT (ransomware, DDoS, data breach, etc.)
- [ ] Implement secure channel for CERT handoff

**6.5 - Warm Handoff Communication**
- [ ] Build "Introduction Letter" template (from AI system to receiving bureau)
  - Explains case summary
  - Lists evidence hashes
  - Provides next steps for complainant
- [ ] Create SMS/WhatsApp notifications (send to complainant after submission)
  - Confirmation of submission
  - Bureau details + directions
  - Expected timeline (when bureau will contact)
- [ ] Implement follow-up reminders (1 week, 2 weeks, 1 month after submission)

**6.6 - NGO Resource Hub**
- [ ] Build comprehensive NGO database:
  - Services offered (counseling, legal aid, safe house, etc.)
  - Eligibility criteria
  - Operating hours
  - Languages
  - Free/paid services
  - Ratings/reviews from users (opt-in)
- [ ] Implement "One-Click Referral" (send NGO details + user consent to organization)
- [ ] Create partnership agreements template (for NGO participation)

---

### TASK 7: Stress Test - Security & Accuracy Validation
**Duration:** 1 week | **Goal:** Ensure system resilience and legal accuracy

#### Subtasks:

**7.1 - Vulnerability Testing (Simulated Breach Scenario)**
- [ ] Design breach simulation scenarios:
  - S3 bucket exposure (can hacker access raw files?)
  - Database injection attack (can hacker modify case data?)
  - Man-in-the-middle (can hacker intercept transcript?)
  - Insider threat (can staff member exfiltrate data?)
- [ ] Implement penetration testing:
  - Use OWASP Top 10 checklist
  - Test authentication bypass
  - Test authorization bypass (can user A see user B's case?)
  - Test data exfiltration
- [ ] Run chaos engineering tests:
  - Database down → does system gracefully fail?
  - S3 down → is data recoverable?
  - Whisper API timeout → does system retry?
- [ ] Generate vulnerability report with remediation timeline

**7.2 - Encryption & Key Management Audit**
- [ ] Verify AES-256 implementation (no weak ciphers)
- [ ] Audit key rotation policy (rotate keys every 90 days)
- [ ] Test key recovery (can we decrypt old data with new keys?)
- [ ] Verify S3-KMS integration (keys are truly separate from data)
- [ ] Run key derivation tests (ensure IVs are random, not reused)

**7.3 - Chain of Custody Integrity Check**
- [ ] Simulate file tampering (modify file after upload)
- [ ] Verify hash mismatch detection
- [ ] Test receipt verification (re-hash file, compare to receipt)
- [ ] Verify metadata integrity (can attacker modify manifest?)
- [ ] Test custody ledger immutability (can attacker delete entries?)

**7.4 - AI Accuracy & Legal Compliance Testing**
- [ ] Create test dataset: 50+ case scenarios with known correct categorizations
- [ ] Test Researcher Agent accuracy:
  - Fact extraction accuracy > 95%
  - Legal categorization accuracy > 90%
  - Category confidence > 75% threshold
- [ ] Test Legal Auditor Agent:
  - Does it catch incorrect categorizations? (sensitivity > 85%)
  - False positive rate < 10% (minimize lawyer escalations)
- [ ] Test Glossary Agent:
  - Sinhala/Tamil terminology accuracy > 95%
  - No informal language in final reports
- [ ] Generate "AI Accuracy Report" for competition

**7.5 - Offline Sync Stress Testing**
- [ ] Test long offline periods (7+ days)
- [ ] Verify data consistency after sync
- [ ] Test conflict resolution (offline edits vs server edits)
- [ ] Verify encryption persists through sync
- [ ] Test with poor connectivity (simulate 2G speed)

**7.6 - Performance & Load Testing**
- [ ] Test concurrent users (100+ simultaneous uploads)
- [ ] Measure response times:
  - Whisper transcription < 2 minutes per 10 minutes audio
  - Agent analysis < 30 seconds
  - PDF generation < 10 seconds
- [ ] Test database query performance (index optimization)
- [ ] Run memory leak detection
- [ ] Generate performance report with bottleneck analysis

**7.7 - Legal Compliance Checklist**
- [ ] Verify GDPR-like compliance (Sri Lanka Data Protection regulations)
- [ ] Check Online Safety Act compliance:
  - Are we handling CSEM securely? (no storage, immediate report to authorities)
  - Are we complying with age verification?
  - Are we complying with data retention minimization?
- [ ] Audit lawyer privilege (attorney-client privilege for lawyer-submitted cases?)
- [ ] Verify police confidentiality (no data shared without authorization)

---

### TASK 8: Pitch Polish - Presentation & Competition Finalization
**Duration:** 1 week | **Goal:** Prepare competition-ready presentation and documentation

#### Subtasks:

**8.1 - Forensic Admissibility Presentation**
- [ ] Create 15-minute pitch deck covering:
  - **The Problem:** Why current AI systems fail in court
  - **The Solution Architecture:** 5 pillars explained clearly
  - **Technical Depth:** Show actual code/screenshots
  - **Legal Compliance:** How we meet Sri Lankan requirements
  - **Real-World Impact:** Demo walkthrough
  - **Competitive Edge:** Why this beats other approaches
- [ ] Develop talking points for each slide
- [ ] Create backup slides for Q&A deep dives

**8.2 - Live Demo Preparation**
- [ ] Build demo scenario (realistic case, not dummy data)
- [ ] Pre-record fallback demo (if live demo fails)
- [ ] Practice demo flow (under 5 minutes):
  1. User uploads voice testimony (show Whisper transcription)
  2. Researcher Agent categorizes (show JSON output)
  3. Legal Auditor validates (show audit reasoning)
  4. PDF generates (show C-Form with hashes)
  5. Referral generated (show nearest bureau routing)
- [ ] Prepare talking points for each demo step
- [ ] Test demo on competition day hardware (laptop, wifi quality)

**8.3 - Technical Documentation**
- [ ] Create README.md with:
  - Project overview
  - Architecture diagram
  - Deployment instructions
  - API documentation
  - Configuration guide
- [ ] Write API docs for lawyer portal and Tell IGP webhook
- [ ] Create user manual (both complainant and lawyer perspectives)
- [ ] Build admin guide (system monitoring, escalations)
- [ ] Document legal compliance checklist

**8.4 - Competitive Differentiation Document**
- [ ] Create one-pager highlighting:
  - Chain of custody forensic capabilities (unique to this system)
  - Multi-agent legal auditing (not just LLM generation)
  - Zero-knowledge privacy architecture (trauma-informed)
  - Sinhala/Tamil legal terminology (local nuance)
  - Offline-first resilience (addresses rural connectivity)
- [ ] Compare to alternatives (ChatGPT lawyer, generic legal AI, etc.)
- [ ] Highlight "2026 advancement" (what makes this next-gen?)

**8.5 - Deployment & Infrastructure**
- [ ] Finalize deployment strategy:
  - Frontend: Vercel (optimal for React)
  - Backend: Railway or DigitalOcean (your preference)
  - Database: PostgreSQL on managed service
  - Vectordb: Pinecone or self-hosted Weaviate
  - S3: AWS or DigitalOcean Spaces
- [ ] Set up monitoring (Sentry for errors, DataDog for performance)
- [ ] Create runbook for production incidents
- [ ] Document scaling plan (if system gets 1M users, how does it scale?)

**8.6 - Pitch Dry Run & Feedback**
- [ ] Schedule practice presentation with:
  - Your supervisor (legal perspective)
  - A technical mentor (architecture feedback)
  - A peer (clarity and engagement feedback)
- [ ] Collect feedback and iterate
- [ ] Time the pitch (must fit competition time limit)
- [ ] Practice handling interruptions and tough questions
- [ ] Record yourself and review (fix pacing, clarity, confidence)

**8.7 - Submission Package**
- [ ] Create final submission including:
  - Pitch deck (PDF + PowerPoint)
  - Live demo access (GitHub repo + deployed instance)
  - Technical documentation
  - Legal compliance report
  - Performance metrics & test results
  - Team bios (highlight your competitive programming background)
- [ ] Create "Quick Start" guide (judge can deploy locally in 5 minutes)
- [ ] Include video walkthrough (3-minute YouTube video)

**8.8 - Final Checklist Before Submission**
- [ ] [ ] All secrets removed from GitHub (no API keys exposed)
- [ ] [ ] README.md is clear and complete
- [ ] [ ] Demo works without manual setup
- [ ] [ ] All dependencies are pinned to specific versions
- [ ] [ ] Documentation is proofread (no typos)
- [ ] [ ] Legal terminology validated by lawyer/mentor
- [ ] [ ] Performance metrics documented
- [ ] [ ] Accessibility tested (WCAG compliance)
- [ ] [ ] All 5 pillars are visibly implemented (not just promised)

---

## Technology Stack

### Frontend
- **React 19** with TypeScript
- **TailwindCSS** for styling (or shadcn/ui for components)
- **Whisper Web** for client-side transcription (Sinhala/Tamil optimized)
- **Service Workers** for offline functionality
- **IndexedDB** for local storage

### Backend
- **Node.js + NestJS** (or Express for rapid development)
- **PostgreSQL** for relational data
- **Pinecone/Weaviate** for vector embeddings
- **AWS S3** for file storage
- **AWS Secrets Manager** for key management

### AI/ML
- **LangGraph** for multi-agent orchestration
- **LangChain** for RAG pipeline
- **OpenAI API** (GPT-4, Whisper, Embeddings)
- **Cross-encoder** for document reranking

### Security & Compliance
- **AES-256-GCM** for encryption
- **SHA-256** for hashing
- **TweetNaCl.js** for client-side crypto
- **AWS KMS** for key management
- **OAuth 2.0** for API authentication

### DevOps
- **Docker** for containerization
- **GitHub Actions** for CI/CD
- **Vercel** for frontend deployment
- **Railway/DigitalOcean** for backend deployment
- **Sentry** for error tracking
- **DataDog** for monitoring

---

## Success Metrics & KPIs

| Metric | Target | Why It Matters |
|--------|--------|-----------------|
| **Legal Categorization Accuracy** | > 90% | Core to court admissibility |
| **Chain of Custody Integrity** | 100% | Non-negotiable for forensics |
| **Offline Sync Success Rate** | > 99% | No data loss in rural areas |
| **PDF Generation Time** | < 10 seconds | User experience critical |
| **Judge Confidence Score** | > 8/10 | Subjective but important for competition |
| **Whisper Transcription Accuracy** | > 95% (Sinhala/Tamil) | Language-specific challenge |
| **System Uptime** | > 99.5% | Reliability in emergency use |
| **Encryption Key Rotation** | 100% compliance | Security requirement |

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Legal Categorization Wrong** | Medium | High | Legal Auditor Agent + lawyer review layer |
| **Data Breach** | Low | Critical | AES-256 + KMS + zero-knowledge architecture |
| **S3 Outage** | Low | High | Multi-region backup + local encryption buffer |
| **Whisper API Rate Limit** | Medium | Medium | Queue system + fallback manual transcription |
| **Offline Sync Conflicts** | Medium | Medium | Conflict resolution protocol + user notification |
| **Lawyer Portal Not Ready** | High | Medium | Build lawyer portal in parallel from Task 2 |
| **Tell IGP API Not Available** | Medium | Medium | Design for future integration (webhook-ready) |
| **Poor Demo Performance** | Medium | High | Pre-record fallback demo |

---

## Timeline Summary

```
Week 1: The Vault (Cryptography Foundation)
├─ 1.1 Metadata System
├─ 1.2 Digital Receipt
├─ 1.3 S3 Vault
├─ 1.4 AES Encryption
└─ 1.5 Custody Ledger

Week 2: Voice & Vibe (Frontend + Offline)
├─ 2.1 React Architecture
├─ 2.2 Whisper Integration
├─ 2.3 Offline Sync
├─ 2.4 Local Encryption
├─ 2.5 i18n Support
└─ 2.6 Accessibility

Week 3: The Brain (Multi-Agent System)
├─ 3.1 Supervisor Agent
├─ 3.2 Researcher Agent
├─ 3.3 Legal Auditor Agent
├─ 3.4 Glossary Agent
├─ 3.5 Communication Protocol
└─ 3.6 Explainability

Week 4: The Librarian (RAG System)
├─ 4.1 Legal Corpus Ingestion
├─ 4.2 Vector Embeddings
├─ 4.3 RAG Pipeline
├─ 4.4 Precedent Database
├─ 4.5 Online Safety Act Mapping
└─ 4.6 Update Protocol

Week 5: The Clerk (PDF Generation)
├─ 5.1 C-Form Generator
├─ 5.2 Evidence Annex
├─ 5.3 Multi-Format Export
├─ 5.4 Lawyer Review UI
├─ 5.5 Versioning
└─ 5.6 PDF Security

Week 6: The Bridge (Referral System)
├─ 6.1 Geo-Fencing
├─ 6.2 Dynamic Routing
├─ 6.3 Tell IGP Webhook
├─ 6.4 CERT Integration
├─ 6.5 Warm Handoff
└─ 6.6 NGO Hub

Week 7: Stress Test (Security & Validation)
├─ 7.1 Breach Simulation
├─ 7.2 Encryption Audit
├─ 7.3 Integrity Check
├─ 7.4 AI Accuracy Testing
├─ 7.5 Offline Testing
├─ 7.6 Performance Testing
└─ 7.7 Compliance Checklist

Week 8: Pitch Polish (Final Presentation)
├─ 8.1 Pitch Deck
├─ 8.2 Live Demo
├─ 8.3 Documentation
├─ 8.4 Differentiation
├─ 8.5 Deployment
├─ 8.6 Dry Runs
├─ 8.7 Submission Package
└─ 8.8 Final Checklist
```

---

## Why This Wins: Competitive Advantage

### 1. **Legal Defensibility**
You're not just showing a "cool AI." You're showing a system designed **from first principles** to be admissible in a Sri Lankan court. The chain of custody alone is sophisticated enough to be a paper on its own.

### 2. **Local Nuance Mastery**
While competitors build generic legal AI, you're handling Sinhala/Tamil terminology, Online Safety Act 2021 specifics, and Sri Lankan Police procedures. This is **not replicable by international teams**.

### 3. **Privacy as a Feature**
The zero-knowledge architecture shows you understand trauma survivors' fears. The offline-first design shows you understand rural Sri Lanka. This is **emotionally intelligent engineering**.

### 4. **Multi-Agent Sophistication**
A Legal Auditor Agent is something you'd see at a top law firm's legal tech stack, not at a university competition. This shows **enterprise-grade thinking**.

### 5. **End-to-End Journey**
From intake → analysis → PDF → referral → follow-up. You're not stopping at analysis. You're **completing the victim's justice journey**.

### 6. **Forensic Credibility**
If a real CID officer can re-verify your digital receipt 6 months later, you've crossed from "neat project" to **infrastructure for justice**. That's what judges remember.

---

## Success Pattern

**This project pattern mirrors real legal tech companies:**
- Palantir (chain of custody + explainability)
- Westlaw (RAG + legal precedent)
- LawGeex (multi-agent legal review)
- **You're combining all three + trauma-informed design.**

---

**Made for Excellence. Made for Impact. Made for Justice.**
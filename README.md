# Sentilex | Agentic Legal Advocate ⚖️

Sentilex is an autonomous digital advocate designed to bridge the gap between trauma and justice for victims in Sri Lanka. Purpose-built for the 2026 legal landscape, it addresses "procedural paralysis" by using agentic AI to conduct multilingual, empathetic interviews and convert raw testimony into structured, prosecution-ready legal documentation.

## 🌟 Key Features

- 🎙️ **Trauma-Informed Interviewing**: Multilingual (Sinhala, Tamil, English) NLP that guides victims through high-stress incident reporting.
- ⚖️ **Intelligent Legal Classification**: Automatically maps incidents against the Computer Crimes Act No. 24 of 2007 and the Online Safety Act.
- 🔐 **Forensic-Grade Evidence Triage**: Implements SHA-256 cryptographic hashing and digital fingerprinting for screenshots/videos to ensure CID-acceptable chain-of-custody.
- 📄 **"Ready-to-File" Documentation**: Generates professional Police Statements (C-Form equivalents) and technical reports for Sri Lanka CERT.

## 🛠️ Technology Stack

| Layer            | Technology                 |
| ---------------- | -------------------------- |
| Frontend         | React (Vite), Tailwind CSS |
| Backend          | FastAPI (Python)           |
| AI Orchestration | LangGraph, LangChain       |
| Database/Cache   | PostgreSQL, Redis          |
| Storage          | Amazon S3 (Encrypted)      |
| Validation       | Pydantic, LangSmith        |

## 🏗️ Architecture & Security

Designed for the 2026 standards of data privacy:

- **Encryption**: AES-256 at rest and TLS 1.3 in transit.
- **Verification**: Every piece of evidence undergoes SHA-256 hashing to create a tamper-proof audit trail for court admissibility.
- **Access**: Secure management via Multi-Factor Authentication (MFA) and S3 Presigned URLs.

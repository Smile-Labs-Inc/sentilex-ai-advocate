<div align="center">
  <img src="images/law-auction-svgrepo-com (1).svg" alt="Sentilex Scale Logo" width="120" height="120" />
  
  # Sentilex AI Advocate 
  
  **Autonomous Legal Support & Forensic Evidence Management System**
  
  *"Bridging the Gap Between Trauma and Justice"*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![Platform](https://img.shields.io/badge/platform-web-blue)]()
[![Docker](https://img.shields.io/badge/docker-ready-blue)]()
[![Live Demo](https://img.shields.io/badge/demo-online-green)](https://sentilex.smilelabs.online/)

<div align="center">
  <h3>
    <a href="https://sentilex.smilelabs.online/">🌐 Visit Live Site</a>
  </h3>
</div>

</div>

---

## 🏛️ Vision

**Sentilex** is a pioneering multi-agent AI system designed to democratize legal access in Sri Lanka. It serves as a first-response legal advocate, conducting empathetic, trauma-aware interviews with victims, securing forensic-grade evidence via cryptographic hashing, and instantly generating court-admissible documentation compliant with the **Computer Crimes Act No. 24 of 2007** and **Online Safety Act No. 9 of 2024**.

---

## 🚀 Key Features

### 🕊️ Trauma-Aware Legal Interviewing

AI-powered empathetic conversations guide victims through incident reporting. The system uses **intent-based routing** to adapt responses for emergencies, legal guidance, and evidence collection without requiring prior legal knowledge.

### ⚖️ Intelligent Legal Analysis (RAG)

Retrieves and cites relevant provisions from Sri Lankan Law. Uses a **Model Context Protocol (MCP)** with full audit trails to prevent hallucinations, ensuring advice is legally sound and contextually accurate.

### 🔐 Forensic-Grade Evidence Vault

Processes uploaded files with **SHA-256 cryptographic hashing** and metadata tracking (timestamps, S3 keys) to create a tamper-proof, court-admissible chain of custody.

### 📄 Professional Document Generation

Automatically generates submission-ready **Police Statements** and **CERT Technical Reports**, complete with structured incident narratives and evidence inventories.

### 🛡️ Verified Lawyer Directory

A searchable database of verified legal professionals. Includes a rigid verification workflow where lawyers upload NICs and Attorney Certificates for admin validation.

---

## 🛠️ Technology Stack

<div align="center">

**Frontend**
<br>
![Preact](https://img.shields.io/badge/Preact-673AB7?style=for-the-badge&logo=preact&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![VisX](https://img.shields.io/badge/VisX-000000?style=for-the-badge&logo=d3.js&logoColor=white)
![Motion](https://img.shields.io/badge/Motion-000000?style=for-the-badge&logo=framer&logoColor=white)

**Backend & AI**
<br>
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-FF4B4B?style=for-the-badge&logo=langchain&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google%20gemini&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)

**Infrastructure & DevOps**
<br>
![DigitalOcean](https://img.shields.io/badge/DigitalOcean-0080FF?style=for-the-badge&logo=digitalocean&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![AWS S3](https://img.shields.io/badge/AWS%20S3-569A31?style=for-the-badge&logo=amazon-s3&logoColor=white)

</div>

---

## 🏗️ System Architecture

Sentilex employs a **secure, containerized microservices architecture**:

1.  **Entry Point:** Traffic is routed through **Cloudflare** to an **Nginx Reverse Proxy**.
2.  **Application Layer:** Dockerized containers for **Frontend (Preact)** and **Backend (FastAPI)**.
3.  **Authentication:** Robust IAM system handling Users, Lawyers, and Admins with **JWT**, **OAuth (Google)**, and **MFA (TOTP)**.
4.  **Data Layer:** **PostgreSQL** handles relational data (Users, Incidents), while **AWS S3** stores encrypted evidence.
5.  **AI Engine:** A multi-agent system powered by **LangGraph** handles intent classification, legal reasoning, and safety validation.
6.  **Real-Time Updates:** **WebSocket** server pushes notifications (e.g., verification status) instantly to clients.

---

## ⚡ Quick Start with Docker

Run the entire application with a single command.

### Prerequisites

- Docker & Docker Compose

### 🚀 Launch

1.  **Clone the repository**

    ```bash
    git clone https://github.com/Smile-Labs-Inc/sentilex-ai-advocate.git
    cd sentilex-ai-advocate
    ```

2.  **Environment Setup**
    Create a `.env` file from the example.

    ```bash
    cp .env.example .env
    ```

3.  **Start Services**
    ```bash
    docker compose up -d --build
    ```

The application will be available at:

- **Frontend:** `http://localhost:8080`
- **API Docs:** `http://localhost:8001/docs`

---

## 🤝 Contributing

We welcome contributions! Please see `CONTRIBUTING.md` for details on how to submit pull requests, report issues, and suggest improvements.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built with ❤️ by Smile Labs Inc. for a Safer Digital Sri Lanka.</sub>
</div>

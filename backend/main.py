from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
from typing import Optional, Union, Dict, Any
import traceback
from contextlib import asynccontextmanager
from database.config import check_db_connection, Base, engine

# Import all models to ensure they're registered with SQLAlchemy
from models.user import User
from models.lawyers import Lawyer
from models.admin import Admin
from models.session_chat import SessionChatMessage, ChatSession
from models.token_blacklist import TokenBlacklist
from models.login_attempt import LoginAttempt
from models.active_session import ActiveSession

from schemas.messages import UserQuery, SynthesizerOutput, RefusalOutput
from chains import invoke_chain

from routers import lawyers
from routers import google_oauth
from routers import auth
from routers import admin_auth
from routers import lawbook
from routers import lawyer_verification
from routers import payments
from routers import legal_queries
from routers import incidents
from routers import case_agent
from routers import chat
from mcp_server.mcp_client import get_mcp_client




# Import OpenAI exceptions for better error handling
try:
    from openai import RateLimitError, APIError, AuthenticationError
except ImportError:
    # Fallback if openai not installed
    RateLimitError = Exception
    APIError = Exception
    AuthenticationError = Exception

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup Logic ---
    print("Checking database connection...")
    if check_db_connection():
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        print("Database is online and tables verified.")
    else:
        print("CRITICAL: Database connection failed.")
        
    # Check MCP availability
    try:
        mcp_client = get_mcp_client()
        if mcp_client.health_check():
            print("MCP service available")
        else:
            print("WARNING: MCP service not available")
    except Exception as e:
        print(f"WARNING: Could not connect to MCP service: {e}")
    yield  # The app runs while this is held

    # --- Shutdown Logic (Optional) ---
    # print("Shutting down...")

# Pass the lifespan to the FastAPI constructor
app = FastAPI(
    title="Sentilex AI Advocate Backend",
    description="Backend for the legally-compliant, forensically-secure AI system.",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(lawyers.router)
app.include_router(auth.router)
app.include_router(admin_auth.router)
app.include_router(google_oauth.router)
app.include_router(lawbook.router)
app.include_router(lawyer_verification.router)
app.include_router(legal_queries.router)
app.include_router(incidents.router)
app.include_router(case_agent.router)
app.include_router(chat.router)
app.include_router(payments.router)


# Session Middleware for OAuth (must be added before CORS)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production-min-32-chars")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Sentilex AI Advocate Backend Running"}


@app.get("/health")
async def health_check():
    mcp_status = False
    try:
        mcp_client = get_mcp_client()
        mcp_status = mcp_client.health_check()
    except:
        pass
        
    return {
        "status": "healthy",
        "mcp_available": mcp_status,
        "database": "connected" # implicit if we got here without error usually, or could check again
    }

def main():
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()

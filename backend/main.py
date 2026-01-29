from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
from typing import Optional, Union, Dict, Any
import traceback
from contextlib import asynccontextmanager
from database.config import check_db_connection, Base, engine


from schemas.messages import UserQuery, SynthesizerOutput, RefusalOutput
from chains import invoke_chain

from routers import lawyers
from routers import google_oauth
from routers import auth
from routers import lawbook




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
app.include_router(google_oauth.router)
app.include_router(lawbook.router)


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
    return {"status": "healthy"}

def main():
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)


if __name__ == "__main__":
    main()

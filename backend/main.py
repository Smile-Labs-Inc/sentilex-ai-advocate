from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
from typing import Optional, Union, Dict, Any
import traceback

from schemas.messages import UserQuery, SynthesizerOutput, RefusalOutput
from chains import invoke_chain

# Import OpenAI exceptions for better error handling
try:
    from openai import RateLimitError, APIError, AuthenticationError
except ImportError:
    # Fallback if openai not installed
    RateLimitError = Exception
    APIError = Exception
    AuthenticationError = Exception

load_dotenv()

app = FastAPI(
    title="Sentilex AI Advocate Backend",
    description="Backend for the legally-compliant, forensically-secure AI system.",
    version="0.1.0"
)

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


class QueryRequest(BaseModel):
    question: str
    case_context: Optional[str] = None


@app.post("/query")
async def submit_query(request: QueryRequest):
    """
    Submit a legal query to the multi-agent system.

    This endpoint processes the query through:
    1. Planner - Determines execution flow
    2. Research - Retrieves legal sources
    3. Reasoning - Applies legal reasoning
    4. Validation - Checks for errors
    5. Synthesizer - Formats final output
    """
    try:
        # Create UserQuery
        user_query = UserQuery(
            question=request.question,
            case_context=request.case_context or ""
        )

        # Invoke the multi-agent chain
        result = invoke_chain(user_query)

        # Format response based on result type
        if isinstance(result, SynthesizerOutput):
            return {
                "status": "success",
                "response": result.response,
                "confidence_note": result.confidence_note,
                "disclaimer": result.disclaimer,
                "citations": [
                    {
                        "law_name": source.law_name,
                        "section": source.section,
                        "text": source.text
                    }
                    for source in result.citations
                ]
            }
        elif isinstance(result, RefusalOutput):
            return {
                "status": "refused",
                "reason": result.reason,
                "issues": [
                    {
                        "severity": issue.severity,
                        "type": issue.type,
                        "message": issue.message
                    }
                    for issue in result.issues
                ]
            }
    except RateLimitError as e:
        error_detail = str(e)
        print(f"OpenAI Rate Limit Error: {error_detail}")
        raise HTTPException(
            status_code=429,
            detail={
                "error": "OpenAI API quota exceeded",
                "message": "The OpenAI API key has exceeded its quota. Please check your billing details at https://platform.openai.com/account/billing",
                "type": "rate_limit_error"
            }
        )
    except AuthenticationError as e:
        error_detail = str(e)
        print(f"OpenAI Authentication Error: {error_detail}")
        raise HTTPException(
            status_code=401,
            detail={
                "error": "OpenAI authentication failed",
                "message": "Invalid OpenAI API key. Please check your .env file.",
                "type": "authentication_error"
            }
        )
    except APIError as e:
        error_detail = str(e)
        print(f"OpenAI API Error: {error_detail}")
        raise HTTPException(
            status_code=502,
            detail={
                "error": "OpenAI API error",
                "message": f"The OpenAI API returned an error: {str(e)}",
                "type": "api_error"
            }
        )
    except Exception as e:
        error_detail = traceback.format_exc()
        print(f"Error in /query endpoint: {error_detail}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error",
                "message": str(e),
                "type": "unknown_error"
            }
        )


def main():
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)


if __name__ == "__main__":
    main()

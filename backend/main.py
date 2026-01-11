from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

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

def main():
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)

if __name__ == "__main__":
    main()

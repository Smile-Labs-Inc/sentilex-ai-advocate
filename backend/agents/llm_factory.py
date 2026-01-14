"""
LLM Factory - Unified LLM Provider Selection

Supports switching between OpenAI and Google Gemini based on environment configuration.
"""

import os
from typing import Optional


def get_llm(model: Optional[str] = None, temperature: float = 0.0):
    """
    Get an LLM instance based on environment configuration.
    
    Args:
        model: Model name (optional, uses defaults based on provider)
        temperature: Temperature setting (default: 0.0 for deterministic output)
        
    Returns:
        LLM instance (ChatOpenAI or ChatGoogleGenerativeAI)
    """
    use_gemini = os.getenv("USE_GEMINI", "false").lower() == "true"
    
    if use_gemini:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            # Use the standard Gemini model names
            # For free tier, "gemini-pro" is usually available
            # Map all models to gemini-pro for compatibility
            gemini_model = "gemini-pro"
            
            print(f"Using Gemini model: {gemini_model}")
            
            return ChatGoogleGenerativeAI(
                model=gemini_model,
                temperature=temperature,
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                convert_system_message_to_human=True  # Gemini doesn't support system messages natively
            )
        except ImportError:
            print("WARNING: langchain-google-genai not installed. Falling back to OpenAI.")
            print("Install with: pip install langchain-google-genai")
    
    # Default to OpenAI
    from langchain_openai import ChatOpenAI
    
    default_model = model or "gpt-4o-mini"
    
    return ChatOpenAI(
        model=default_model,
        temperature=temperature
    )

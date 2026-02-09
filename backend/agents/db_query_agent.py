"""
DB Query Agent - Read-Only SQL Agent for User Context

Provides secure, RLS-protected database access for retrieving user context.
"""

import os
from langchain_community.utilities import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

from langchain_core.prompts import PromptTemplate
from urllib.parse import quote_plus


def get_agent_db(user_id: int) -> SQLDatabase:
    """
    Create a read-only database connection with RLS context.
    
    The connection uses agent_user role and sets app.current_user_id
    for Row-Level Security enforcement.
    """
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "sentilex_db")
    
    # Agent credentials (read-only role)
    agent_password = os.getenv("AGENT_DB_PASSWORD", "secure_agent_pass")
    
    # Set RLS context via connection options
    uri = (
        f"postgresql+psycopg2://agent_user:{quote_plus(agent_password)}"
        f"@{db_host}:{db_port}/{db_name}"
        f"?options=-c%20app.current_user_id%3D{user_id}"
    )
    
    return SQLDatabase.from_uri(
        uri,
        include_tables=["users", "incidents", "incident_chat_messages"]
    )


# Security-focused SQL agent prompt
DB_QUERY_PROMPT = PromptTemplate.from_template("""
You are a read-only database analyst retrieving user profile and case context for case agents.

SAFE TABLES ONLY (permission denied on others):
- users (profile, preferences, expertise)
- incidents (case metadata for this user only) 
- incident_chat_messages (conversation history for this user/incident)

SECURITY RULES:
- SELECT queries ONLY. No INSERT, UPDATE, DELETE, ALTER, DROP, CREATE.
- RLS is enforced: you only see data for user_id = {user_id}
- LIMIT 20 maximum. Use LIMIT 5 for summaries.
- If "permission denied" or no rows: respond "No accessible data for this user."

USER CONTEXT QUERY: {input}
USER ID: {user_id}

Format response as JSON:
{{{{
    "user_profile": "name, email, preferences",
    "relevant_cases": ["case summaries"],
    "preferences": "language, district"
}}}}

SQL Query:""")


def create_db_query_agent(user_id: int):
    """
    Create a read-only SQL agent for user context retrieval.
    
    Uses RLS-protected connection and security-focused prompting.
    """
    db = get_agent_db(user_id)
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type="tool-calling",
        prefix=DB_QUERY_PROMPT.format(user_id=user_id, input="{{input}}"),
        max_iterations=3,
    )
    
    return agent


def get_user_context(user_id: int, query: str = None) -> dict:
    """
    Convenience function to get user context.
    
    Args:
        user_id: The user ID to query context for
        query: Optional specific query, defaults to full profile
        
    Returns:
        Dict with user profile, cases, and preferences
    """
    if query is None:
        query = f"Get profile, preferences, and summary of past cases for user_id {user_id}"
    
    agent = create_db_query_agent(user_id)
    
    try:
        result = agent.invoke({"input": query})
        return {"output": result.get("output", ""), "error": None}
    except Exception as e:
        return {"output": "", "error": str(e)}

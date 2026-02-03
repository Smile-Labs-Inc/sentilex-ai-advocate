"""
Case Agent Graph - LangGraph Workflow with Memory Layers

Complete flow with per-incident memory, global user memory, and DB context.
"""

from typing import TypedDict, Annotated, List, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage

from database import get_db
from agents.memory import IncidentChatHistory, UserGlobalChatHistory
from agents.db_query_agent import get_user_context
from models.chat_message import ChatMessage


class CaseAgentState(TypedDict):
    """State for the case agent workflow."""
    messages: Annotated[List[AnyMessage], "add"]
    incident_id: int
    user_id: int
    user_context: str  # from DB query
    incident_history: List[AnyMessage]  # per-incident memory
    global_user_history: List[AnyMessage]  # global user memory


def load_memories_node(state: CaseAgentState) -> dict:
    """Load both incident + global user history from database."""
    db = next(get_db())
    try:
        incident_history = IncidentChatHistory(state["incident_id"], db).messages
        global_history = UserGlobalChatHistory(state["user_id"], db).messages
        
        return {
            "incident_history": incident_history,
            "global_user_history": global_history,
        }
    finally:
        db.close()


def db_user_context_node(state: CaseAgentState) -> dict:
    """Query DB for user profile/preferences via RLS-protected agent."""
    result = get_user_context(state["user_id"])
    
    return {"user_context": result.get("output", "No user context available")}


def legal_reasoning_node(state: CaseAgentState) -> dict:
    """Run the main legal chain with full context injected."""
    from chains.main_chain import create_main_chain
    from schemas.messages import UserQuery
    chain = create_main_chain()
    
    # Build context summary from histories
    incident_context = "\n".join([
        f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
        for m in state.get("incident_history", [])[-20:]  # Last 20 messages
    ])
    
    global_context = "\n".join([
        m.content for m in state.get("global_user_history", [])[-20:]
    ])
    
    # Get the user's question from messages
    user_question = state["messages"][-1].content if state["messages"] else ""
    
    # Create enriched query with all context
    enriched_query = UserQuery(
        question=user_question,
        case_context=f"""
JURISDICTION: Sri Lanka
USER PROFILE:
{state.get('user_context', 'No profile available')}

INCIDENT HISTORY:
{incident_context or 'No previous messages in this incident'}

USER PATTERNS:
{global_context or 'No global history available'}
"""
    )
    
    try:
        result = chain.invoke(enriched_query)
        response_content = str(result.answer if hasattr(result, 'answer') else result)
    except Exception as e:
        response_content = f"I apologize, but I encountered an error processing your request: {str(e)}"
    
    return {"messages": [AIMessage(content=response_content)]}


def save_memories_node(state: CaseAgentState) -> dict:
    """Save new messages to incident history (which includes user_id for global queries)."""
    db = next(get_db())
    try:
        # Get the last user message and AI response
        messages_to_save = state["messages"][-2:] if len(state["messages"]) >= 2 else state["messages"]
        
        # Save to incident history with user_id
        # This automatically enables global user queries via user_id filter
        for msg in messages_to_save:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            chat_msg = ChatMessage(
                incident_id=state["incident_id"],
                user_id=state["user_id"],
                role=role,
                content=msg.content
            )
            db.add(chat_msg)
        
        db.commit()
    finally:
        db.close()
    
    return state


def build_case_agent_graph():
    """Build and compile the case agent LangGraph workflow."""
    workflow = StateGraph(CaseAgentState)

    # Add nodes
    workflow.add_node("load_memories", load_memories_node)
    workflow.add_node("db_user_context", db_user_context_node)
    workflow.add_node("legal_reasoning", legal_reasoning_node)
    workflow.add_node("save_memories", save_memories_node)

    # Set entry point and edges
    workflow.set_entry_point("load_memories")
    workflow.add_edge("load_memories", "db_user_context")
    workflow.add_edge("db_user_context", "legal_reasoning")
    workflow.add_edge("legal_reasoning", "save_memories")
    workflow.add_edge("save_memories", END)

    # Per-incident persistence via checkpointer
    checkpointer = MemorySaver()
    
    return workflow.compile(checkpointer=checkpointer)


# Export compiled agent
case_agent = build_case_agent_graph()


def invoke_case_agent(
    incident_id: int,
    user_id: int,
    message: str
) -> dict:
    """
    Invoke the case agent with a user message.
    
    Args:
        incident_id: The incident this conversation belongs to
        user_id: The authenticated user's ID
        message: The user's message
        
    Returns:
        Dict with response and user context used
    """
    config = {
        "configurable": {
            "thread_id": f"incident_{incident_id}",  # per-incident checkpoints
        }
    }
    
    result = case_agent.invoke(
        {
            "messages": [HumanMessage(content=message)],
            "incident_id": incident_id,
            "user_id": user_id,
            "user_context": "",
            "incident_history": [],
            "global_user_history": [],
        },
        config=config,
    )
    
    return {
        "response": result["messages"][-1].content if result["messages"] else "",
        "user_context_used": result.get("user_context", ""),
    }

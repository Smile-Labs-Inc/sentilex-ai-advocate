"""
Case Agent Graph - Intent-Based Routing Architecture for Sentilex

Smart LangGraph workflow with:
- Intent classification (Router Node)
- Conditional edges based on query type
- Specialized agents: Conversational, Emergency, Legal, Synthesizer
- Trauma-informed, empathetic responses
"""

import os
from enum import Enum
from typing import TypedDict, Annotated, List, Optional, Literal
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from database import get_db
from agents.memory import IncidentChatHistory, UserGlobalChatHistory
from agents.db_query_agent import get_user_context
from models.incident_chat import IncidentChatMessage


# =============================================================================
# Intent Classification Schema
# =============================================================================

class UserIntent(str, Enum):
    """Possible user intents for routing."""
    GREETING = "greeting"              # Hello, hi, thanks, bye
    SMALL_TALK = "small_talk"          # How are you, weather, general chat
    LEGAL_TRIAGE = "legal_triage"      # Questions about laws, rights, violations
    EVIDENCE_GUIDANCE = "evidence"     # How to upload/collect/hash evidence
    CASE_STATUS = "case_status"        # Questions about this specific incident
    EMERGENCY = "emergency"            # Active harm, ongoing attacks, immediate danger
    GENERAL_HELP = "general_help"      # How to use app, what can you do


class IntentClassification(BaseModel):
    """Structured output for intent classification."""
    intent: UserIntent = Field(
        ..., 
        description="The classified intent of the user's message"
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Confidence score for the classification"
    )
    urgency_level: Literal["high", "normal"] = Field(
        default="normal",
        description="High if emergency or time-sensitive"
    )
    reasoning: str = Field(
        default="",
        description="Brief explanation for the classification"
    )


# =============================================================================
# State Definition
# =============================================================================

class CaseAgentState(TypedDict):
    """Extended state for the case agent workflow with intent routing."""
    messages: Annotated[List[AnyMessage], "add"]
    incident_id: int
    user_id: int
    
    # Intent classification
    intent: Optional[UserIntent]
    confidence: float
    urgency_level: str
    
    # Context data
    user_context: str
    context_data: dict  # Stores DB/SQL results
    incident_history: List[AnyMessage]
    global_user_history: List[AnyMessage]
    
    # Processing data
    agent_output: str  # Raw agent output before synthesis


# =============================================================================
# Intent Classification (Router Node)
# =============================================================================

def get_router_llm():
    """Get lightweight LLM for routing."""
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )


def router_node(state: CaseAgentState) -> dict:
    """Classify user intent and decide routing path."""
    last_message = state["messages"][-1].content if state["messages"] else ""
    
    llm = get_router_llm()
    
    # Create structured output with Pydantic
    structured_llm = llm.with_structured_output(IntentClassification)
    
    prompt = f"""You are an intent classifier for a legal aid platform in Sri Lanka that helps cybercrime victims.

Classify the user's message into ONE of these intents:
- GREETING: Greetings like "hello", "hi", "thanks", "bye"
- SMALL_TALK: General chat not related to legal matters
- LEGAL_TRIAGE: Questions about laws, legal rights, Computer Crimes Act, Online Safety Act
- EVIDENCE: Questions about evidence collection, uploading files, screenshots, hashing
- CASE_STATUS: Questions about their specific incident/case details
- EMERGENCY: Active ongoing harm, cyberattacks in progress, immediate danger
- GENERAL_HELP: Questions about how to use the platform

User's message: "{last_message}"

Consider the context:
- This is a Sri Lankan legal aid platform for cybercrime victims
- Urgency is HIGH if there's ongoing harm or time-sensitive danger
- Default to LEGAL_TRIAGE if unsure between legal options
"""

    try:
        result = structured_llm.invoke(prompt)
        return {
            "intent": result.intent,
            "confidence": result.confidence,
            "urgency_level": result.urgency_level,
        }
    except Exception as e:
        # Default to legal_triage if classification fails
        return {
            "intent": UserIntent.LEGAL_TRIAGE,
            "confidence": 0.5,
            "urgency_level": "normal",
        }


# =============================================================================
# Specialized Nodes
# =============================================================================

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


def conversational_node(state: CaseAgentState) -> dict:
    """Handle greetings, small talk, and general help - lightweight, no DB calls."""
    last_message = state["messages"][-1].content if state["messages"] else ""
    intent = state.get("intent", UserIntent.GREETING)
    
    llm = get_router_llm()
    
    prompt = f"""You are a friendly, empathetic legal assistant for Sentilex, a platform helping cybercrime victims in Sri Lanka.

Respond to the user in a warm, trauma-informed manner. Keep it brief and supportive.

User's Intent: {intent.value}
User's Message: "{last_message}"

Guidelines:
- For GREETING: Warm welcome, offer to help with their case
- For SMALL_TALK: Brief friendly response, gently redirect to how you can help
- For GENERAL_HELP: Explain what you can do (legal guidance, evidence tips, case tracking)

Remember: Many users may be in distress. Be calm, supportive, and professional.
Keep response under 100 words unless more detail is needed."""

    try:
        response = llm.invoke(prompt)
        return {"agent_output": response.content}
    except Exception:
        return {"agent_output": "Hello! I'm here to help you with your case. How can I assist you today?"}


def emergency_node(state: CaseAgentState) -> dict:
    """Immediate advice for active cybercrimes - prioritize safety."""
    last_message = state["messages"][-1].content if state["messages"] else ""
    
    llm = get_router_llm()
    
    prompt = f"""You are an emergency response assistant for Sentilex, helping cybercrime victims in Sri Lanka.

The user may be experiencing an ACTIVE cybercrime or immediate danger.

User's Message: "{last_message}"

Provide IMMEDIATE, actionable advice:

1. **Immediate Safety First**
   - If in physical danger: Call 119 (Police Emergency)
   - Disconnect from compromised networks/devices if safe to do so

2. **Report Active Cyberattacks**
   - SL CERT (Cyber Emergency): +94 11 2 691 692
   - Police Cyber Crime Division: +94 11 2 421 111
   - Website: cert.gov.lk

3. **Preserve Evidence**
   - Take screenshots NOW before content is removed
   - Don't delete any messages or communications
   - Note the time and date

4. **Next Steps**
   - We'll help you document everything properly
   - Guide you through the formal reporting process

Be CALM, CLEAR, and REASSURING. This person may be panicking.
Keep it concise but complete on emergency contacts."""

    try:
        response = llm.invoke(prompt)
        return {"agent_output": response.content}
    except Exception:
        return {
            "agent_output": (
                "🚨 **Emergency Resources:**\n\n"
                "- **Police Emergency:** 119\n"
                "- **SL CERT (Cyber Emergency):** +94 11 2 691 692\n"
                "- **Police Cyber Crime Division:** +94 11 2 421 111\n\n"
                "If you're in immediate danger, please call 119 first. "
                "I'm here to help you document and report this incident."
            )
        }


def db_context_node(state: CaseAgentState) -> dict:
    """Query DB for user profile and incident details."""
    result = get_user_context(state["user_id"])
    
    # Get incident details from database
    db = next(get_db())
    try:
        from models.incident import Incident
        incident = db.query(Incident).filter(Incident.id == state["incident_id"]).first()
        
        incident_details = {}
        if incident:
            incident_details = {
                "title": incident.title,
                "type": incident.incident_type.value if incident.incident_type else "",
                "description": incident.description,
                "status": incident.status.value if incident.status else "",
                "date_occurred": str(incident.date_occurred) if incident.date_occurred else "",
                "jurisdiction": incident.jurisdiction or "",
                "platforms": incident.platforms_involved or "",
            }
    finally:
        db.close()
    
    return {
        "user_context": result.get("output", "No user context available"),
        "context_data": {
            "user_profile": result.get("output", ""),
            "incident": incident_details,
        }
    }


def legal_reasoning_node(state: CaseAgentState) -> dict:
    """Legal analysis for triage and evidence guidance."""
    from chains.main_chain import create_main_chain
    from schemas.messages import UserQuery
    
    chain = create_main_chain()
    
    # Build context from histories
    incident_context = "\n".join([
        f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}"
        for m in state.get("incident_history", [])[-15:]
    ])
    
    user_question = state["messages"][-1].content if state["messages"] else ""
    incident_data = state.get("context_data", {}).get("incident", {})
    
    # Create enriched query
    enriched_query = UserQuery(
        question=user_question,
        case_context=f"""
JURISDICTION: Sri Lanka
INCIDENT TYPE: {incident_data.get('type', 'Unknown')}
INCIDENT DESCRIPTION: {incident_data.get('description', 'No description')}
USER PROFILE: {state.get('user_context', 'No profile')}
CONVERSATION HISTORY:
{incident_context or 'No previous messages'}
"""
    )
    
    try:
        result = chain.invoke(enriched_query)
        response = str(result.answer if hasattr(result, 'answer') else result)
        return {"agent_output": response}
    except Exception as e:
        error_msg = str(e)
        
        # Provide helpful fallback for legal queries
        if state.get("intent") == UserIntent.EVIDENCE_GUIDANCE:
            return {
                "agent_output": (
                    "For collecting evidence of cybercrimes in Sri Lanka:\n\n"
                    "1. **Screenshots**: Capture all relevant content with timestamps\n"
                    "2. **Save URLs**: Document exact web addresses\n"
                    "3. **Messages**: Export chat logs if possible\n"
                    "4. **Witnesses**: Note anyone who saw the content\n"
                    "5. **Timeline**: Record when incidents occurred\n\n"
                    "You can upload evidence files through the Evidence tab. "
                    "All files are encrypted for your protection."
                )
            }
        else:
            return {
                "agent_output": (
                    "Based on your query about Sri Lankan law, I can help guide you through "
                    "the relevant provisions of the Computer Crimes Act No. 24 of 2007 and "
                    "the Online Safety Act No. 9 of 2024.\n\n"
                    "Could you tell me more specifically what aspect of your case you'd like help with?"
                )
            }


def synthesizer_node(state: CaseAgentState) -> dict:
    """Final node: Format all outputs into empathetic, trauma-informed response."""
    agent_output = state.get("agent_output", "")
    intent = state.get("intent", UserIntent.GENERAL_HELP)
    incident_data = state.get("context_data", {}).get("incident", {})
    
    llm = get_router_llm()
    
    prompt = f"""You are the final response synthesizer for Sentilex, a trauma-informed legal aid platform for cybercrime victims in Sri Lanka.

**Your Mission**: Take the agent's output and format it into a warm, professional, human-readable response.

**Agent Output to Format:**
{agent_output}

**User's Intent**: {intent.value}
**Incident Type**: {incident_data.get('type', 'Unknown')}

**Formatting Guidelines:**
1. **Tone**: Empathetic, calm, supportive - never clinical or robotic
2. **Acknowledge their situation**: Show understanding of their distress
3. **Clear structure**: Use bullet points for action items
4. **Encourage next steps**: Always give them something concrete to do next
5. **Maintain hope**: Remind them that they're taking the right steps

**Trauma-Informed Principles:**
- Validate their experience
- Emphasize they're not alone
- Focus on empowerment, not victimization
- Keep language simple and clear

Format the response for readability but don't add information not in the agent output.
Keep it concise - under 200 words unless detailed legal guidance is needed."""

    try:
        response = llm.invoke(prompt)
        return {"messages": [AIMessage(content=response.content)]}
    except Exception:
        # Fallback: use agent output directly if synthesis fails
        return {"messages": [AIMessage(content=agent_output)]}


def save_memories_node(state: CaseAgentState) -> dict:
    """Save new messages to incident history."""
    db = next(get_db())
    try:
        messages_to_save = state["messages"][-2:] if len(state["messages"]) >= 2 else state["messages"]
        
        for msg in messages_to_save:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            chat_msg = IncidentChatMessage(
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


# =============================================================================
# Conditional Routing
# =============================================================================

def route_by_intent(state: CaseAgentState) -> str:
    """Route to appropriate node based on classified intent."""
    intent = state.get("intent", UserIntent.LEGAL_TRIAGE)
    urgency = state.get("urgency_level", "normal")
    
    # Emergency always takes priority
    if intent == UserIntent.EMERGENCY or urgency == "high":
        return "emergency"
    
    # Simple intents - no DB needed
    if intent in [UserIntent.GREETING, UserIntent.SMALL_TALK, UserIntent.GENERAL_HELP]:
        return "conversational"
    
    # Complex intents - need DB context
    return "db_context"


def route_after_db_context(state: CaseAgentState) -> str:
    """Route after DB context is loaded."""
    intent = state.get("intent", UserIntent.LEGAL_TRIAGE)
    
    if intent == UserIntent.CASE_STATUS:
        # Case status just needs DB data, go to synthesis
        return "synthesizer"
    
    # Legal triage and evidence guidance need legal reasoning
    return "legal_reasoning"


# =============================================================================
# Graph Builder
# =============================================================================

def build_case_agent_graph():
    """Build the intent-routing LangGraph workflow."""
    workflow = StateGraph(CaseAgentState)
    
    # Add all nodes
    workflow.add_node("load_memories", load_memories_node)
    workflow.add_node("router", router_node)
    workflow.add_node("conversational", conversational_node)
    workflow.add_node("emergency", emergency_node)
    workflow.add_node("db_context", db_context_node)
    workflow.add_node("legal_reasoning", legal_reasoning_node)
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("save_memories", save_memories_node)
    
    # Entry point
    workflow.set_entry_point("load_memories")
    
    # Load memories -> Router
    workflow.add_edge("load_memories", "router")
    
    # Router -> Conditional edges based on intent
    workflow.add_conditional_edges(
        "router",
        route_by_intent,
        {
            "conversational": "conversational",
            "emergency": "emergency",
            "db_context": "db_context",
        }
    )
    
    # Conversational/Emergency -> Synthesizer -> Save
    workflow.add_edge("conversational", "synthesizer")
    workflow.add_edge("emergency", "synthesizer")
    
    # DB Context -> Conditional (Case Status vs Legal)
    workflow.add_conditional_edges(
        "db_context",
        route_after_db_context,
        {
            "synthesizer": "synthesizer",
            "legal_reasoning": "legal_reasoning",
        }
    )
    
    # Legal Reasoning -> Synthesizer
    workflow.add_edge("legal_reasoning", "synthesizer")
    
    # Synthesizer -> Save -> END
    workflow.add_edge("synthesizer", "save_memories")
    workflow.add_edge("save_memories", END)
    
    # Compile with checkpointer
    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)


# =============================================================================
# Export
# =============================================================================

case_agent = build_case_agent_graph()


def invoke_case_agent(incident_id: int, user_id: int, message: str) -> dict:
    """
    Invoke the case agent with a user message.
    
    Args:
        incident_id: The incident this conversation belongs to
        user_id: The authenticated user's ID
        message: The user's message
        
    Returns:
        Dict with response and routing metadata
    """
    config = {
        "configurable": {
            "thread_id": f"incident_{incident_id}",
        }
    }
    
    result = case_agent.invoke(
        {
            "messages": [HumanMessage(content=message)],
            "incident_id": incident_id,
            "user_id": user_id,
            "intent": None,
            "confidence": 0.0,
            "urgency_level": "normal",
            "user_context": "",
            "context_data": {},
            "incident_history": [],
            "global_user_history": [],
            "agent_output": "",
        },
        config=config,
    )
    
    return {
        "response": result["messages"][-1].content if result["messages"] else "",
        "intent": result.get("intent", "").value if result.get("intent") else "unknown",
        "confidence": result.get("confidence", 0.0),
        "urgency_level": result.get("urgency_level", "normal"),
    }

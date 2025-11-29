import time, uuid
from gemini_client import chat_model
from memory_redis import get_session_window, save_session_window

# import new agents
from agents.intake_agent import route
from agents.rag_agent import run_rag
from agents.action_agent import run_action
from agents.validator_agent import validate


def run_agent(user_id, session_id, user_text):

    # 1. Load memory (redis → dynamo fallback)
    window = get_session_window(session_id)

    # 2. Route to agent
    agent = route(user_text)     # 'rag' or 'action'
    print(f"action :{agent}")
    # 3. Execute agent
    if agent == "rag":
        response_text = run_rag(window, user_text)
        context_for_validator = "RAG context used."
    else:
        response_text = run_action(window, user_text)
        context_for_validator = "Tool-based action."

    # 4. Validate output
    verdict = validate(response_text, context_for_validator)
    if verdict == "retry":
        # fallback to safer short answer
        response_text = "I am unable to fully confirm this. Let me fetch accurate info."

    # 5. Save message in memory
    msg = {
        "message_id": str(uuid.uuid4()),
        "role": "assistant",
        "text": response_text,
        "timestamp": time.time()
    }

    save_session_window(session_id, window + [msg])

    return response_text

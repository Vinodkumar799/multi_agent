# agents/intake_agent.py
import google.generativeai as genai
from gemini_client import chat_model

def route(user_text):
    """
    Routes query to appropriate agent.
    """
    system_prompt = """
    You are a routing agent.
    Decide whether this user message requires:
    - 'rag' (for answering from documents relate to companies, Managements,Datasecurity,Inventory, FAQs, logs)
    - 'action' (create ticket, update DB, call API)
    Respond ONLY with: rag or action.
    """

    resp = chat_model.generate_content(system_prompt + "\nUser: " + user_text)
    route = resp.text.strip().lower()
    print(f"route reply : {route}")
    if "action" in route:
        return "action"
    return "rag"

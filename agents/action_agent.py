# agents/action_agent.py
import json
from gemini_client import chat_model

def run_action(window, user_text):
    """
    Example tools: create_ticket, update_order, notify_email
    """
    tools_prompt = """
    You are the Action Agent.
    Convert the user request into a structured action.

    If user says: 'open ticket', output:
    {
      "action": "create_ticket",
      "payload": { "issue": "refund delayed", "priority": "high" }
    }

    Only return valid JSON.
    """

    resp = chat_model.generate_content(tools_prompt + "\n\nUser: " + user_text)
    action_json = resp.text.strip()

    try:
        parsed = json.loads(action_json)
    except:
        parsed = {"action": "unknown", "payload": {"error": "parse_failed"}}

    # Here you integrate real API calls --------------------------------------
    # Example:
    if parsed["action"] == "create_ticket":
        ticket_id = "TCK-" + str(time.time()).replace(".", "")
        return f"Ticket created successfully with ID {ticket_id}"

    return "Action completed."

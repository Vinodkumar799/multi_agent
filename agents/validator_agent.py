# agents/validator_agent.py
from gemini_client import chat_model

def validate(answer, context):
    print(f"ans , context :", answer, context)
    """
    Check hallucination,grounding, Adult Information, Personal Information.
    """
    prompt = f"""
    You are a validation agent.
    Check if the answer is safe, grounded and useful.

    Context:
    {context}

    Answer:
    {answer}

    If valid respond "valid".
    If not, respond "retry" ang give reason.
    """
    resp = chat_model.generate_content(prompt)
    print(f"validator res : {resp}")
    return resp.text.strip().lower()

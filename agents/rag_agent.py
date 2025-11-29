# agents/rag_agent.py
from retriever import retrieve_context
from prompts import build_prompt
from gemini_client import chat_model

def run_rag(window, user_text):
    context = retrieve_context(user_text)
    print(context)
    prompt = build_prompt(window, context, user_text)

    resp = chat_model.generate_content(prompt)
    return resp.text

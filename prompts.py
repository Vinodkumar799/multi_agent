def build_prompt(history, context, user_message):
    return f"""
You are a Customer Support AI.

CONTEXT from internal docs:
{context}

CONVERSATION HISTORY:
{history}

USER MESSAGE:
{user_message}

Your answer must use internal evidence only.
"""

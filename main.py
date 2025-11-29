from fastapi import FastAPI
from pydantic import BaseModel
from orchestrator import run_agent

app = FastAPI()

class Query(BaseModel):
    user_id: str
    session_id: str
    message: str

@app.post("/chat")
def chat(q: Query):
    answer = run_agent(q.user_id, q.session_id, q.message)
    return {"answer": answer}

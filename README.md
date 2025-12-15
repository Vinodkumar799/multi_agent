Overview
This project is a production-style AI Customer Support Assistant built using a multi-agent architecture.
The system answers customer queries using internal documents, logs, and conversation history, and can also perform real-world actions through tool calling.

The solution demonstrates:

Multi-agent orchestration

Retrieval Augmented Generation (RAG)

Short-term and long-term memory

Tool calling and action execution

Guardrails and validation

Integration with APIs, databases, and file systems

FastAPI backend with a Streamlit chat UI

Use Case
Customer Support Assistant

Answer customer questions using internal knowledge (FAQs, docs, logs)

Remember past conversations

Decide whether to answer or perform an action

Create support tickets or trigger workflows when required

Ensure safe and grounded responses

High-Level Architecture

User (Streamlit Chat UI)
|
v
FastAPI Backend (/chat)
|
v
Intake Agent (Router)
|
+--> RAG Agent (Docs / Logs / FAQs)
|
+--> Action Agent (Tool Calls / APIs)
|
v
Validator Agent (Safety & Grounding)
|
v
Memory Layer (Redis + DynamoDB)
|
v
Final Response

Agents Overview

Intake Agent (Routing Agent)

Understands user intent

Routes requests to the correct agent:

RAG Agent for informational queries

Action Agent for operational requests

RAG Agent

Uses Retrieval Augmented Generation

Retrieves relevant context from:

Internal documents

Logs

FAQs

Uses a vector database (Pinecone / FAISS / Chroma)

Combines retrieved context with conversation memory

Action Agent

Executes real-world actions:

Create support tickets

Call external APIs

Update databases

Uses structured tool calling

Validator Agent (Guardrails)

Prevents hallucinations

Ensures responses are grounded in retrieved context

Enforces safety and response quality

Memory Architecture

Memory Type Purpose
Redis Short-term conversation window
DynamoDB Long-term persistent memory
Session ID Maintains user conversation continuity

Retrieval Augmented Generation (RAG) Flow

Documents are embedded and stored in a vector database

User query is converted to an embedding

Relevant documents are retrieved

Retrieved context is injected into the LLM prompt

This ensures accurate and grounded answers.

Tech Stack

LLM: Google Gemini

Backend: FastAPI

Frontend: Streamlit

Vector DB: Pinecone / FAISS / Chroma

Memory: Redis + DynamoDB

Language: Python 3.10+

Project Structure

.
├── agents
│ ├── intake_agent.py
│ ├── rag_agent.py
│ ├── action_agent.py
│ └── validator_agent.py
│
├── tools
│ ├── retriever.py
│ ├── memory_redis.py
│ ├── memory_dynamo.py
│ └── ticket_api.py
│
├── api
│ └── main.py (FastAPI application)
│
├── ui
│ └── app.py (Streamlit chat UI)
│
├── data
│ └── sample_docs
│
├── requirements.txt
├── README.md
└── .gitignore

Setup and Run Instructions

Install dependencies
pip install -r requirements.txt

Environment Variables
Create a .env file (do NOT commit this file):

GEMINI_API_KEY=your_gemini_key
PINECONE_API_KEY=your_pinecone_key
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=ap-south-1
REDIS_URL=redis://localhost:6379

Start FastAPI Backend
uvicorn api.main:app --reload --port 8000

API documentation will be available at:
http://localhost:8000/docs

Start Streamlit UI
streamlit run ui/app.py


This project is designed for demo and assignment purposes

The architecture can be extended with additional agents and tools

from argparse import Namespace
from pinecone import Pinecone
from google import genai
from google.genai import types
from config import PINECONE_API_KEY, PINECONE_INDEX
import numpy as np
from dotenv import load_dotenv
import os 

load_dotenv()
# Load API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)
pc=Pinecone(api_key="XXXXXXXX")
index = pc.Index(host="https://demo-c6y0d3v.svc.aped-4627-b74a.pinecone.io")
def embed(text: str):
    
    res=[np.array(e.values) for e in client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=1536)).embeddings
]
    return res[0]

def retrieve_context(query: str, top_k=5):
    vec = embed(query).tolist()
    results = index.query(namespace="company-policies",vector=vec, top_k=top_k, include_metadata=True)
    print(f"rag results : {results.matches}")
    return [match["metadata"]["snippet"] for match in results.matches]

# pip install "pinecone[grpc]"
from pinecone.grpc import PineconeGRPC as Pinecone



# To get the unique host for an index, 
# see https://docs.pinecone.io/guides/manage-data/target-an-index
index = pc.Index(host="INDEX_HOST")
from google import genai
from google.genai import types
import numpy as np
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT", None)
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "support-index")

MAX_SENTENCES = int(os.getenv("MAX_SENTENCES", 5))  # semantic chunk: number of sentences
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 1))  # number of overlapping sentences
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 32))
EMBED_MODEL = "gemini-embedding-001"

from google import genai

print(GEMINI_API_KEY)
pc = Pinecone(api_key="")
client = genai.Client(api_key=GEMINI_API_KEY)
pc=Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
index = pc.Index(host="")


res=[np.array(e.values) for e in client.models.embed_content(
    model="gemini-embedding-001",
    contents="Informatins about Access Management and Controls",
    config=types.EmbedContentConfig(output_dimensionality=1536)
).embeddings]


res=index.query(
    namespace="company-policies",
    vector=res[0],
    top_k=5,
    include_values=False,
    include_metadata=True
)

documents_for_rerank = []
for d in res.matches:
    documents_for_rerank.append({
        "id": d["id"],
        "text": d["metadata"]["snippet"]  # OR store full chunk in metadata if needed
    })
result = pc.inference.rerank(
    model="bge-reranker-v2-m3",
    query="Information about Access Management and Controls",
    documents=documents_for_rerank,
    top_n=2,
    return_documents=True,
    parameters={
        "truncate": "END"
    }
)

contents = [item.document.text for item in result.data]
print(f"contents :{contents}")

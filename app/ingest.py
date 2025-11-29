
import os
import time
import json
import uuid
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from datetime import datetime
from tqdm import tqdm

# PDF reader
from PyPDF2 import PdfReader
# Gemini & Pinecone clients
from google.genai import types
import google.generativeai as genai
from pinecone import Pinecone

# Semantic chunking
import spacy
nlp = spacy.load("en_core_web_sm")  # make sure spacy model is installed: python -m spacy download en_core_web_sm

# --- Config ---
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENVIRONMENT", None)
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "support-index")

MAX_SENTENCES = int(os.getenv("MAX_SENTENCES", 5))  # semantic chunk: number of sentences
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 1))  # number of overlapping sentences
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 32))
EMBED_MODEL = "gemini-embedding-001"
from google import genai

client = genai.Client(api_key=GEMINI_API_KEY)
# Initialize Gemini
if not GEMINI_API_KEY:
    raise RuntimeError("Set GEMINI_API_KEY in .env")

# Initialize Pinecone
if not PINECONE_API_KEY:
    raise RuntimeError("Set PINECONE_API_KEY in .env")
pc=Pinecone(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
index_list = pc.list_indexes()
print("pc index :", index_list)

index = pc.Index(PINECONE_INDEX)

# --- Utilities ---


def read_pdf(path: Path) -> str:
    text_chunks = []
    try:
        reader = PdfReader(str(path))
        for p in reader.pages:
            try:
                text = p.extract_text()
            except Exception:
                text = ""
            if text:
                text_chunks.append(text)
    except Exception as e:
        print(f"[WARN] Could not read PDF {path}: {e}")
    return "\n".join(text_chunks)


def read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def read_json_chat(path: Path) -> str:
    try:
        j = json.loads(path.read_text(encoding="utf-8"))
        msgs = []
        if isinstance(j, list):
            for m in j:
                role = m.get("role") or m.get("from") or "user"
                content = m.get("content") or m.get("message") or m.get("text") or ""
                msgs.append(f"{role}: {content}")
        elif isinstance(j, dict):
            arr = j.get("messages") or j.get("chat") or []
            for m in arr:
                role = m.get("role") or m.get("from") or "user"
                content = m.get("content") or m.get("message") or m.get("text") or ""
                msgs.append(f"{role}: {content}")
        else:
            msgs = [str(j)]
        return "\n".join(msgs)
    except Exception:
        return ""


def text_from_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return read_pdf(path)
    if suffix in {".txt", ".md", ".log"}:
        return read_text_file(path)
    if suffix in {".json"}:
        return read_json_chat(path)
    return read_text_file(path)


def semantic_chunk_text(text: str, max_sentences: int = MAX_SENTENCES, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into semantic chunks based on sentences.
    overlap = number of sentences to repeat between chunks
    """
    if not text:
        return []

    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    chunks = []
    start = 0
    while start < len(sentences):
        end = start + max_sentences
        chunk = sentences[start:end]
        if chunk:
            chunks.append(" ".join(chunk))
        start += max_sentences - overlap  # move forward but keep overlap
    return chunks


def embed_texts(texts: List[str]) -> List[List[float]]:
    embeddings = []
    for t in texts:
        import numpy as np
        for attempt in range(3):
            try:
                res = [np.array(e.values) for e in client.models.embed_content(
    model="gemini-embedding-001",
    contents=t,
    config=types.EmbedContentConfig(output_dimensionality=1536)
).embeddings]
                
                print(f"res is : {res}")
                embeddings.append(res[0])
                break
            except Exception as e:
                wait = 1 + attempt * 2
                print(f"[WARN] embed failed (attempt {attempt+1}) - wait {wait}s - {e}")
                time.sleep(wait)
        else:
            print("[ERROR] embedding failed permanently, inserting zero vector.")
            embeddings.append([0.0] * 1536)
    return embeddings


def make_metadata(file_path: Path, source: str, chunk_idx: int, chunk_text: str) -> Dict:
    return {
        "source": source,
        "filepath": str(file_path.parent),
        "filename": file_path.name,
        "chunk_index": chunk_idx,
        "ingested_at": datetime.utcnow().isoformat(),
        "snippet": (chunk_text[:500] + "...") if len(chunk_text) > 500 else chunk_text
    }


def upsert_batch_to_pinecone(items: List[Dict]):
    to_upsert = [(it["id"], it["values"], it["metadata"]) for it in items]
    try:
        index.upsert(vectors=to_upsert,namespace="company-policies")
    except Exception as e:
        print(f"[ERROR] Pinecone upsert failed: {e}")
        time.sleep(3)
        index.upsert(vectors=to_upsert)


def ingest_file(file_path: Path, source_tag: str):
    """
    Ingest a single file (PDF/TXT/MD/JSON) with semantic chunking.
    """
    print(f"\n[INFO] Ingesting file: {file_path} as source={source_tag}")
    try:
        text = text_from_file(file_path)
        if not text.strip():
            print(f"[WARN] Empty file: {file_path}")
            return

        chunks = semantic_chunk_text(text)
        batch = []
        for idx, chunk in enumerate(chunks):
            uid = f"{file_path.name}__{idx}__{uuid.uuid4().hex[:8]}"
            metadata = make_metadata(file_path, source_tag, idx, chunk)
            batch.append({"id": uid, "values": None, "metadata": metadata, "text": chunk})

            if len(batch) >= BATCH_SIZE:
                texts = [b["text"] for b in batch]
                embs = embed_texts(texts)
                items = [{"id": b["id"], "values": emb, "metadata": b["metadata"]} for b, emb in zip(batch, embs)]
                upsert_batch_to_pinecone(items)
                batch = []

        # Flush remaining batch
        if batch:
            texts = [b["text"] for b in batch]
            embs = embed_texts(texts)
            items = [{"id": b["id"], "values": emb, "metadata": b["metadata"]} for b, emb in zip(batch, embs)]
            upsert_batch_to_pinecone(items)

        print(f"[DONE] Ingested {len(chunks)} semantic chunks from {file_path}")

    except Exception as e:
        print(f"[ERROR] Failed to ingest {file_path}: {e}")


def main():
    base = Path("app/data/docs")
    if not base.exists():
        raise RuntimeError("Folder 'data/docs/' not found. Put your PDFs there.")

    # Get all PDFs in the folder
    pdf_files = [p for p in base.glob("*.pdf") if p.is_file()]
    if not pdf_files:
        print("[INFO] No PDF files found in 'data/docs/'.")
        return

    print(f"[INFO] Found {len(pdf_files)} PDFs in 'data/docs/'.")

    # Ingest each PDF
    for file_path in pdf_files:
        ingest_file(file_path, source_tag="docs")

    print("\n[ALL DONE] Semantic chunking ingestion completed.")


if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()

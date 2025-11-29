import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

AWS_REGION = os.getenv("AWS_REGION")
DDB_ENDPOINT = os.getenv("DDB_ENDPOINT")
REDIS_URL = os.getenv("REDIS_URL")

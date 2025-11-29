import redis
import json
from config import REDIS_URL

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def get_session_window(session_id: str):
    data = r.get(f"window:{session_id}")
    return json.loads(data) if data else []

def save_session_window(session_id: str, messages: list):
    r.set(f"window:{session_id}", json.dumps(messages))

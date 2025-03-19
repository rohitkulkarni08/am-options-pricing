import redis
import json
from config import REDIS_HOST, REDIS_PORT

cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def cache_data(ticker, data):
    cache.setex(f"stock:{ticker}", 3600, json.dumps(data))

def fetch_from_cache(ticker):
    data = cache.get(f"stock:{ticker}")
    return json.loads(data) if data else None

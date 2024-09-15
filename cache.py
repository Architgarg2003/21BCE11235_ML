import os
import redis
import pickle
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Connect to Redis using environment variables
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))

try:
    cache = redis.Redis(host=redis_host, port=redis_port)
    # Test the connection
    if cache.ping():
        logging.info(f"Connected to Redis at {redis_host}:{redis_port}")
except redis.ConnectionError as e:
    logging.error(f"Failed to connect to Redis: {str(e)}")
    raise

# Cache document embeddings
def cache_set(doc_id, embeddings):
    """
    Cache the document embeddings using the document ID as the key.
    
    Args:
    - doc_id (str): Unique identifier for the document.
    - embeddings (any): The document embeddings to be cached.
    """
    try:
        cache.set(doc_id, pickle.dumps(embeddings))
        logging.info(f"Cached embeddings for doc_id: {doc_id}")
    except Exception as e:
        logging.error(f"Error caching embeddings for doc_id {doc_id}: {str(e)}")

# Retrieve cached embeddings
def cache_get(doc_id):
    """
    Retrieve cached document embeddings by document ID.
    
    Args:
    - doc_id (str): Unique identifier for the document.
    
    Returns:
    - Unpickled embeddings if found in cache, else None.
    """
    try:
        cached = cache.get(doc_id)
        if cached:
            return pickle.loads(cached)
        logging.info(f"No cached embeddings found for doc_id: {doc_id}")
        return None
    except pickle.UnpicklingError as e:
        logging.error(f"Error unpickling cached embeddings for doc_id {doc_id}: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Error retrieving cached embeddings for doc_id {doc_id}: {str(e)}")
        return None

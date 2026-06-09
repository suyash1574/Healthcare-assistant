import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

BASE_DIR       = os.path.dirname(os.path.dirname(__file__))
DATA_DIR       = os.path.join(BASE_DIR, "data")
VECTOR_STORE_DIR = os.path.join(BASE_DIR, "vector_store")

COLLECTION_NAME    = "healthcare_docs"
EMBEDDING_MODEL    = "all-MiniLM-L6-v2"
LLM_MODEL          = "llama-3.3-70b-versatile"
CHUNK_SIZE         = 500
CHUNK_OVERLAP      = 50
TOP_K_RESULTS      = 3
SIMILARITY_THRESHOLD = 0.3

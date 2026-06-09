import os
from dotenv import load_dotenv

# Load .env from parent directory (shared keys)
_parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(_parent_dir, ".env"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

BASE_DIR         = os.path.dirname(os.path.dirname(__file__))
DATA_DIR         = os.path.join(BASE_DIR, "data")
VECTOR_STORE_DIR = os.path.join(BASE_DIR, "vector_store")

COLLECTION_NAME     = "healthcare_docs"
EMBEDDING_MODEL     = "all-MiniLM-L6-v2"
CHUNK_SIZE          = 500
CHUNK_OVERLAP       = 50
TOP_K_RESULTS       = 3
SIMILARITY_THRESHOLD = 0.3

# LLM provider configs (priority order: Groq -> Nvidia -> OpenRouter free models)
LLM_PROVIDERS = [
    # Primary: Groq
    {
        "name": "Groq",
        "api_key": GROQ_API_KEY,
        "model": "llama-3.3-70b-versatile",
        "base_url": None,
    },
    # Fallback 1: Nvidia NIM
    {
        "name": "Nvidia NIM",
        "api_key": NVIDIA_API_KEY,
        "model": "meta/llama-3.3-70b-instruct",
        "base_url": "https://integrate.api.nvidia.com/v1",
    },
    # Fallback 2+: OpenRouter free models
    {
        "name": "OpenRouter - Llama 4 Maverick",
        "api_key": OPENROUTER_API_KEY,
        "model": "meta-llama/llama-4-maverick:free",
        "base_url": "https://openrouter.ai/api/v1",
    },
    {
        "name": "OpenRouter - DeepSeek V3",
        "api_key": OPENROUTER_API_KEY,
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "base_url": "https://openrouter.ai/api/v1",
    },
    {
        "name": "OpenRouter - DeepSeek R1",
        "api_key": OPENROUTER_API_KEY,
        "model": "deepseek/deepseek-r1:free",
        "base_url": "https://openrouter.ai/api/v1",
    },
    {
        "name": "OpenRouter - Qwen 2.5 72B",
        "api_key": OPENROUTER_API_KEY,
        "model": "qwen/qwen-2.5-72b-instruct:free",
        "base_url": "https://openrouter.ai/api/v1",
    },
    {
        "name": "OpenRouter - Qwen3 235B",
        "api_key": OPENROUTER_API_KEY,
        "model": "qwen/qwen3-235b-a22b:free",
        "base_url": "https://openrouter.ai/api/v1",
    },
    {
        "name": "OpenRouter - Gemma 4 26B",
        "api_key": OPENROUTER_API_KEY,
        "model": "google/gemma-4-26b-a4b-instruct:free",
        "base_url": "https://openrouter.ai/api/v1",
    },
    {
        "name": "OpenRouter - Nvidia Nemotron 30B",
        "api_key": OPENROUTER_API_KEY,
        "model": "nvidia/nemotron-3-nano-30b-a3b:free",
        "base_url": "https://openrouter.ai/api/v1",
    },
    {
        "name": "OpenRouter - Phi-4 Reasoning",
        "api_key": OPENROUTER_API_KEY,
        "model": "microsoft/phi-4-reasoning-plus:free",
        "base_url": "https://openrouter.ai/api/v1",
    },
    # Last resort: random free model via OpenRouter auto-router
    {
        "name": "OpenRouter - Free Auto",
        "api_key": OPENROUTER_API_KEY,
        "model": "openrouter/free",
        "base_url": "https://openrouter.ai/api/v1",
    },
]

import os
from pathlib import Path

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:8080/v1")
LLM_MODEL = os.getenv(
    "LLM_MODEL", "qwen-4b-vl"
)  # llama-server ignores it; llama-swap/LiteLLM use it
LLM_API_KEY = os.getenv("LLM_API_KEY", "none")
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "300"))
DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
IMAGE_MAX_EDGE = int(os.getenv("IMAGE_MAX_EDGE", "1024"))

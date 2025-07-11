# llm_service/config.py
# @docs
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MODEL_PATH: str = os.getenv("MODEL_PATH", "/path/to/your/model.gguf")
    MODEL_N_CTX: int = int(os.getenv("MODEL_N_CTX", 2048))
    MODEL_N_GPU_LAYERS: int = int(os.getenv("MODEL_N_GPU_LAYERS", 0)) # 0 for CPU, -1 for all layers on GPU

    # API settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", 8000))

    # Generation parameters (defaults)
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", 0.7))
    DEFAULT_MAX_TOKENS: int = int(os.getenv("DEFAULT_MAX_TOKENS", 512))
    DEFAULT_TOP_P: float = float(os.getenv("DEFAULT_TOP_P", 0.95))
    # Add other llama.cpp parameters as needed, e.g., top_k, repeat_penalty

settings = Settings()

# Example of how to use:
# from llm_service.config import settings
# print(settings.MODEL_PATH)

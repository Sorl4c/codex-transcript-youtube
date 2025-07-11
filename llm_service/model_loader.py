# llm_service/model_loader.py
# @docs
from llama_cpp import Llama
from .config import settings
from .logger import logger # Use centralized logger

class ModelManager:
    _instance = None
    _llm = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ModelManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def load_model(self):
        if self._llm is None:
            try:
                logger.info(f"Loading model from: {settings.MODEL_PATH}")
                logger.info(f"Context size (n_ctx): {settings.MODEL_N_CTX}")
                logger.info(f"GPU layers (n_gpu_layers): {settings.MODEL_N_GPU_LAYERS}")
                self._llm = Llama(
                    model_path=settings.MODEL_PATH,
                    n_ctx=settings.MODEL_N_CTX,
                    n_gpu_layers=settings.MODEL_N_GPU_LAYERS,
                    verbose=True # Or configure as needed
                )
                logger.info("Model loaded successfully.")
            except Exception as e:
                logger.error(f"Error loading model: {e}", exc_info=True)
                self._llm = None # Ensure llm is None if loading failed
                raise
        return self._llm

    def get_model(self) -> Llama:
        if self._llm is None:
            self.load_model() # Attempt to load if not already loaded
        if self._llm is None:
            # This case means loading failed and an error was already logged.
            # We should not proceed with a None model.
            raise RuntimeError("Model could not be loaded. Check logs for details.")
        return self._llm

# Global instance of the model manager
model_manager = ModelManager()

def get_llm_instance() -> Llama:
    """Provides access to the singleton Llama instance."""
    return model_manager.get_model()

# You might want to pre-load the model when the application starts.
# This can be done in main.py (FastAPI startup event).

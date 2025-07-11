import unittest
import os
from unittest.mock import patch, mock_open, MagicMock
import tempfile

# Adjust the import path based on your project structure
# This assumes test_core.py is in ia/tests/ and core.py is in ia/
from ..core import (
    load_prompt_template,
    create_text_splitter,
    initialize_llm,
    map_summarize_chunk,
    reduce_summaries,
    FALLBACK_MAP_PROMPT_TEMPLATE,
    FALLBACK_REDUCE_PROMPT_TEMPLATE
)

# Sobrescribir la ruta por defecto para usar los modelos reales
DEFAULT_MODEL_PATH = "/mnt/c/local/modelos/tinyllama.gguf"  # Usando tinyllama.gguf por defecto

# Mock Llama and LangchainLlamaCpp as they are heavy dependencies
# and we don't want to actually load models during unit tests.
class MockLlama:
    def __init__(self, model_path: str, **kwargs):
        self.model_path = model_path
        self.kwargs = kwargs
        if not os.path.exists(model_path) and model_path != "dummy_invalid_path.gguf":
             # Simplified check for tests; real lib would error more specifically
            if model_path != "ia/models/llama-3-8b-instruct-q5_k_m.gguf": # Allow default path for some tests
                 # For specific tests that expect an error, we might not want to raise here
                 # but let the test assert the warning. For general mock, this is fine.
                 pass # Let it pass for mock, actual error handled by lib

    def __call__(self, prompt: str, **kwargs):
        return {"choices": [{"text": f"Mock summary for: {prompt[:20]}..."}]}

    def create_completion(self, prompt: str, **kwargs):
        return {"choices": [{"text": f"Mock completion for: {prompt[:20]}..."}]}

class MockLangchainLlamaCpp:
    def __init__(self, model_path: str, **kwargs):
        self.model_path = model_path
        self.kwargs = kwargs
        if not os.path.exists(model_path) and model_path != "dummy_invalid_path.gguf":
            pass # Let it pass for mock

    def __call__(self, prompt: str, **kwargs):
        # Langchain's __call__ might be different, this is a simplified mock
        return f"Mock Langchain summary for: {prompt[:20]}..."


class TestCoreUtilities(unittest.TestCase):
    def setUp(self):
        # Apply patches for all tests in this class
        self.llama_patcher = patch('llama_cpp.Llama', MockLlama)
        self.langchain_patcher = patch('langchain_community.llms.LlamaCpp', MockLangchainLlamaCpp)
        self.mock_llama = self.llama_patcher.start()
        self.mock_langchain = self.langchain_patcher.start()
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.mock_prompt_dir = os.path.join(self.temp_dir.name, 'prompts')
        os.makedirs(self.mock_prompt_dir, exist_ok=True)
        
        # Set up dummy prompt files
        self.dummy_map_prompt_content = "This is a dummy map prompt: {text}"
        self.dummy_reduce_prompt_content = "This is a dummy reduce prompt: {text}"

        self.map_prompt_file_path = os.path.join(self.mock_prompt_dir, "map.txt")
        self.reduce_prompt_file_path = os.path.join(self.mock_prompt_dir, "reduce.txt")

        with open(self.map_prompt_file_path, "w") as f:
            f.write(self.dummy_map_prompt_content)
        with open(self.reduce_prompt_file_path, "w") as f:
            f.write(self.dummy_reduce_prompt_content)
        
        # Use real model for tests
        self.dummy_model_file = DEFAULT_MODEL_PATH
        
        # Verify model file exists
        if not os.path.exists(self.dummy_model_file):
            raise FileNotFoundError(f"No se encontró el archivo del modelo en {self.dummy_model_file}")
    
    def tearDown(self):
        # Stop all patches
        self.llama_patcher.stop()
        self.langchain_patcher.stop()
        # Clean up temporary directory
        self.temp_dir.cleanup()

    # --- Tests for load_prompt_template ---
    def test_load_prompt_template_success(self):
        prompt = load_prompt_template(self.map_prompt_file_path, "fallback")
        self.assertEqual(prompt, self.dummy_map_prompt_content)

    def test_load_prompt_template_file_not_found_uses_fallback(self):
        non_existent_file = os.path.join(self.mock_prompt_dir, "non_existent.txt")
        fallback_content = "This is a fallback prompt."
        prompt = load_prompt_template(non_existent_file, fallback_content)
        self.assertEqual(prompt, fallback_content)

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists', return_value=True)
    def test_load_prompt_template_read_error_uses_fallback(self, mock_exists, mock_file):
        mock_file.side_effect = IOError("Failed to read")
        file_path = "any_path.txt"
        fallback_content = "Fallback due to read error."
        prompt = load_prompt_template(file_path, fallback_content)
        self.assertEqual(prompt, fallback_content)

    # --- Tests for create_text_splitter ---
    def test_create_text_splitter_default_params(self):
        splitter = create_text_splitter()
        self.assertIsNotNone(splitter)
        # Accessing private attributes for testing purposes, not ideal but common for config checks
        self.assertEqual(splitter._chunk_size, 1000)  # Updated to match actual default in core.py
        self.assertEqual(splitter._chunk_overlap, 100)  # Updated to match actual default in core.py

    def test_create_text_splitter_custom_params(self):
        chunk_size = 500
        chunk_overlap = 50
        splitter = create_text_splitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.assertIsNotNone(splitter)
        self.assertEqual(splitter._chunk_size, chunk_size)
        self.assertEqual(splitter._chunk_overlap, chunk_overlap)

    # --- Tests for initialize_llm ---
    def test_initialize_llm_native_success(self):
        llm = initialize_llm(model_path=self.dummy_model_file, pipeline_type="native", n_ctx=1024)
        self.assertIsInstance(llm, MockLlama)
        self.assertEqual(llm.model_path, self.dummy_model_file)
        self.assertIn("n_ctx", llm.kwargs)
        self.assertEqual(llm.kwargs["n_ctx"], 1024)

    # Class-level patch handles MockLangchainLlamaCpp
    def test_initialize_llm_langchain_success(self):
        llm_params = {"temperature": 0.5, "max_tokens": 100}
        llm = initialize_llm(
            model_path=self.dummy_model_file,
            pipeline_type="langchain",
            **llm_params
        )
        self.assertIsInstance(llm, MockLangchainLlamaCpp)
        self.assertEqual(llm.model_path, self.dummy_model_file)
        self.assertIn("temperature", llm.kwargs)
        self.assertEqual(llm.kwargs["temperature"], 0.5)

    @patch('builtins.print') # To capture print statements (warnings)
    def test_initialize_llm_model_not_found_warning(self, mock_print):
        # Test with a path that the mock won't consider 'existing' by default
        # but also not the specific DEFAULT_MODEL_PATH if it's special-cased in mock
        invalid_path = "dummy_invalid_path.gguf"
        
        # We expect a ValueError because the pipeline_type is invalid, but first a warning
        with self.assertRaises(ValueError):
            initialize_llm(model_path=invalid_path, pipeline_type="invalid_type")
        mock_print.assert_any_call(f"WARNING: Model file not found at '{invalid_path}'. LLM initialization will likely fail.")

    def test_initialize_llm_invalid_pipeline_type(self):
        with self.assertRaises(ValueError) as context:
            initialize_llm(model_path="any_model.gguf", pipeline_type="non_existent_pipeline")
        self.assertIn("Unsupported pipeline_type", str(context.exception))

    # --- Tests for map_summarize_chunk ---
    # Class-level patch handles MockLlama
    def test_map_summarize_chunk(self):
        mock_llm_instance = MockLlama(model_path=self.dummy_model_file)
        text_chunk = "This is a piece of text to be summarized."
        prompt_template = "Summarize: {text}"
        generation_params = {}
        summary = map_summarize_chunk(mock_llm_instance, text_chunk, prompt_template, generation_params)
        # The mock returns "Mock summary for: {prompt[:20]}..."
        self.assertTrue(summary.startswith("Mock summary for: Summarize: This is a"), 
                      f"Unexpected summary format: {summary}")

    # --- Tests for reduce_summaries ---
    # Class-level patch handles MockLlama
    def test_reduce_summaries(self):
        mock_llm_instance = MockLlama(model_path=self.dummy_model_file)
        summaries = ["First summary.", "Second summary.", "Third summary."]
        prompt_template = "Combine: {text}"
        generation_params = {}
        combined_summary = reduce_summaries(mock_llm_instance, summaries, prompt_template, generation_params)
        # The mock returns "Mock summary for: {prompt[:20]}..."
        self.assertTrue(combined_summary.startswith("Mock summary for: Combine: First"), 
                      f"Unexpected combined summary format: {combined_summary}")

if __name__ == '__main__':
    unittest.main()

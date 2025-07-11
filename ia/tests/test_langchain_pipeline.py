import unittest
import os
import sys

# Add project root to sys.path to allow importing 'ia' module
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from ia.langchain_pipeline import summarize_text_langchain
from ia.core import DEFAULT_MODEL_PATH, FALLBACK_MAP_PROMPT_TEMPLATE, FALLBACK_REDUCE_PROMPT_TEMPLATE

# A very short sample text for testing
SAMPLE_TEXT = """
Artificial intelligence is a rapidly evolving field. Its applications span various industries,
including healthcare, finance, and transportation. Ethical considerations are paramount.
"""

class TestLangchainPipeline(unittest.TestCase):

    @unittest.skipIf(not os.path.exists(DEFAULT_MODEL_PATH),
                     f"Model file not found at {DEFAULT_MODEL_PATH}. Skipping Langchain pipeline tests.")
    def test_summarize_text_langchain_basic(self):
        """Test basic summarization with the Langchain pipeline."""
        print(f"\nRunning test_summarize_text_langchain_basic using model: {DEFAULT_MODEL_PATH}")
        
        # Using fallback prompts directly for simplicity in this basic test
        # and to avoid dependency on prompt file existence for this unit test.
        # llm_kwargs for the Langchain LlamaCpp constructor
        test_llm_kwargs = {
            "temperature": 0.1,
            "max_tokens": 150, # Max tokens for the summary
            "n_ctx": 512,      # Context window for this test
            "n_gpu_layers": 0, # Force CPU for this test to avoid CI/GPU issues
            "verbose": False   # Keep LlamaCpp quiet for tests
        }

        try:
            summary = summarize_text_langchain(
                text_content=SAMPLE_TEXT,
                model_path=DEFAULT_MODEL_PATH,
                # map_prompt_template_str=FALLBACK_MAP_PROMPT_TEMPLATE, # summarize_text_langchain loads prompts
                # reduce_prompt_template_str=FALLBACK_REDUCE_PROMPT_TEMPLATE,
                llm_kwargs=test_llm_kwargs,
                chunk_size=300, # Smaller chunk for small sample text
                chunk_overlap=30
            )
            
            self.assertIsInstance(summary, str)
            self.assertTrue(len(summary) > 0, "Summary should not be empty.")
            self.assertNotIn("Failed to generate summary", summary, "Summary should not be an error message.")
            self.assertNotIn("Input text was empty", summary, "Summary should not indicate empty input.")
            print(f"Langchain Pipeline Test Summary (first 100 chars): {summary[:100]}...")

        except Exception as e:
            self.fail(f"summarize_text_langchain raised an exception: {e}")

    def test_summarize_empty_text_langchain(self):
        """Test Langchain pipeline with empty input text."""
        print("\nRunning test_summarize_empty_text_langchain...")
        test_llm_kwargs = {"n_gpu_layers": 0, "verbose": False}
        summary = summarize_text_langchain(
            text_content="", 
            model_path=DEFAULT_MODEL_PATH, # Model path still needed for LLM init by Langchain
            llm_kwargs=test_llm_kwargs
        )
        self.assertIsInstance(summary, str)
        # Depending on implementation, it might return a specific message or an empty string
        self.assertTrue(
            summary == "Input text was empty or too short to create document chunks." or summary == "",
            f"Unexpected summary for empty text: {summary}"
        )
        print(f"Langchain Pipeline Test Summary for empty text: '{summary}'")

if __name__ == '__main__':
    unittest.main()

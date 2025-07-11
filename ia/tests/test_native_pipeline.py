import unittest
import os
import sys

# Add project root to sys.path to allow importing 'ia' module
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from ia.native_pipeline import summarize_text_native
from ia.core import DEFAULT_MODEL_PATH

# A very short sample text for testing
SAMPLE_TEXT = """
Traditional software development follows a waterfall model. Agile methodologies, however, 
offer more flexibility and iterative progress. Scrum and Kanban are popular Agile frameworks.
"""

class TestNativePipeline(unittest.TestCase):

    @unittest.skipIf(not os.path.exists(DEFAULT_MODEL_PATH),
                     f"Model file not found at {DEFAULT_MODEL_PATH}. Skipping Native pipeline tests.")
    def test_summarize_text_native_basic(self):
        """Test basic summarization with the Native pipeline."""
        print(f"\nRunning test_summarize_text_native_basic using model: {DEFAULT_MODEL_PATH}")
        
        test_llm_constructor_kwargs = {
            "n_ctx": 512,      # Context window for this test
            "n_gpu_layers": 0, # Force CPU for this test to avoid CI/GPU issues
            # verbose is now a direct param to summarize_text_native, not in constructor_kwargs for that function
        }
        test_generation_params = {
            "temperature": 0.1,
            "max_tokens": 150 # Max tokens for the summary
        }

        try:
            summary = summarize_text_native(
                text_content=SAMPLE_TEXT,
                model_path=DEFAULT_MODEL_PATH,
                llm_constructor_kwargs=test_llm_constructor_kwargs,
                generation_params=test_generation_params,
                verbose=False, # Keep LlamaCpp quiet for tests via summarize_text_native's verbose param
                chunk_size=300, 
                chunk_overlap=30
            )
            
            self.assertIsInstance(summary, str)
            self.assertTrue(len(summary) > 0, "Summary should not be empty.")
            self.assertNotIn("Failed to generate summary", summary, "Summary should not be an error message.")
            self.assertNotIn("Input text was empty", summary, "Summary should not indicate empty input.")
            print(f"Native Pipeline Test Summary (first 100 chars): {summary[:100]}...")

        except Exception as e:
            self.fail(f"summarize_text_native raised an exception: {e}")

    def test_summarize_empty_text_native(self):
        """Test Native pipeline with empty input text."""
        print("\nRunning test_summarize_empty_text_native...")
        test_llm_constructor_kwargs = {"n_gpu_layers": 0}
        summary = summarize_text_native(
            text_content="", 
            model_path=DEFAULT_MODEL_PATH, # Model path still needed if llm_instance is not passed
            llm_constructor_kwargs=test_llm_constructor_kwargs,
            verbose=False
        )
        self.assertIsInstance(summary, str)
        self.assertEqual(summary, "Input text was empty or too short to create document chunks.",
                         f"Unexpected summary for empty text: {summary}")
        print(f"Native Pipeline Test Summary for empty text: '{summary}'")

if __name__ == '__main__':
    unittest.main()

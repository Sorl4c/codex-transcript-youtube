# tests/test_langchain_pipeline.py

import os
import pytest
from unittest.mock import patch, MagicMock, call

from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document

# Assuming 'ia' is in PYTHONPATH, which is typical if tests are run from project root
from ia.langchain_pipeline import (
    initialize_llm,
    summarize_text_langchain,
    DEFAULT_MODEL_PATH,
    MAP_PROMPT_TEMPLATE,
    REDUCE_PROMPT_TEMPLATE,
)

# Define the paths to mock based on their usage in langchain_pipeline.py
LLAMA_CPP_PATH = "ia.langchain_pipeline.LlamaCpp"
LOAD_SUMMARIZE_CHAIN_PATH = "ia.langchain_pipeline.load_summarize_chain"
RECURSIVE_SPLITTER_PATH = "ia.langchain_pipeline.RecursiveCharacterTextSplitter"
OS_PATH_EXISTS_PATH = "os.path.exists"
PROMPT_TEMPLATE_PATH = "ia.langchain_pipeline.PromptTemplate"
DOCUMENT_PATH = "ia.langchain_pipeline.Document"


@pytest.fixture
def mock_llm_instance(monkeypatch):
    mock_llm = MagicMock()
    monkeypatch.setattr(LLAMA_CPP_PATH, MagicMock(return_value=mock_llm))
    return mock_llm


@pytest.fixture
def mock_chain_instance(monkeypatch):
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = {"output_text": "mock summary"}
    monkeypatch.setattr(LOAD_SUMMARIZE_CHAIN_PATH, MagicMock(return_value=mock_chain))
    return mock_chain


class TestInitializeLlm:
    DUMMY_MODEL_PATH = "/fake/model.gguf"

    @patch(OS_PATH_EXISTS_PATH, return_value=True)
    @patch(LLAMA_CPP_PATH)
    def test_initialize_llm_model_exists(self, mock_llama_cpp_class, mock_exists):
        """Test LLM initialization when model file exists."""
        llm_kwargs = {"temperature": 0.5, "n_gpu_layers": 10}
        initialize_llm(self.DUMMY_MODEL_PATH, **llm_kwargs)

        mock_exists.assert_called_once_with(self.DUMMY_MODEL_PATH)
        expected_call_kwargs = {
            "model_path": self.DUMMY_MODEL_PATH,
            "n_gpu_layers": 10,
            "n_batch": 512,
            "verbose": False,
            "temperature": 0.5,
            "max_tokens": 512,
            "top_p": 0.9,
            "n_ctx": 2048,
        }
        mock_llama_cpp_class.assert_called_once_with(**expected_call_kwargs)

    @patch(OS_PATH_EXISTS_PATH, return_value=False)
    @patch(LLAMA_CPP_PATH)
    def test_initialize_llm_model_not_exists_warning(self, mock_llama_cpp_class, mock_exists, capsys):
        """Test LLM initialization prints warning if model file doesn't exist."""
        initialize_llm(self.DUMMY_MODEL_PATH)

        mock_exists.assert_called_once_with(self.DUMMY_MODEL_PATH)
        captured = capsys.readouterr()
        assert f"WARNING: Model file not found at '{self.DUMMY_MODEL_PATH}'" in captured.out
        # LlamaCpp should still be called, letting it handle the error internally
        mock_llama_cpp_class.assert_called_once()


class TestSummarizeTextLangchain:
    SAMPLE_TEXT = "This is a sample text for summarization. It is long enough to be split into multiple chunks hopefully. We need to test the map reduce functionality."
    SHORT_TEXT = "Short text."

    @patch(OS_PATH_EXISTS_PATH, return_value=True) # For DEFAULT_MODEL_PATH check
    @patch(RECURSIVE_SPLITTER_PATH)
    def test_summarize_text_langchain_happy_path(
        self, mock_splitter_class, mock_exists, mock_llm_instance, mock_chain_instance
    ):
        """Test the main summarization flow with mocks."""
        mock_text_splitter = MagicMock()
        mock_text_splitter.split_text.return_value = ["chunk1", "chunk2"]
        mock_splitter_class.return_value = mock_text_splitter

        # Mock Document creation
        with patch(DOCUMENT_PATH, side_effect=lambda page_content: Document(page_content=page_content)) as mock_doc_init:
            summary = summarize_text_langchain(self.SAMPLE_TEXT, model_path=DEFAULT_MODEL_PATH)

        assert summary == "mock summary"
        mock_exists.assert_called_with(DEFAULT_MODEL_PATH) # Called by initialize_llm
        mock_splitter_class.assert_called_once_with(
            chunk_size=1000, chunk_overlap=100, length_function=len, is_separator_regex=False
        )
        mock_text_splitter.split_text.assert_called_once_with(self.SAMPLE_TEXT)
        
        # Check Document instantiation
        expected_doc_calls = [call(page_content='chunk1'), call(page_content='chunk2')]
        mock_doc_init.assert_has_calls(expected_doc_calls)

        mock_chain_instance.invoke.assert_called_once()
        args, _ = mock_chain_instance.invoke.call_args
        assert "input_documents" in args[0]
        assert len(args[0]["input_documents"]) == 2
        assert args[0]["input_documents"][0].page_content == "chunk1"

    @patch(OS_PATH_EXISTS_PATH, return_value=True)
    def test_summarize_text_langchain_empty_input(self, mock_exists, mock_llm_instance):
        """Test summarization with empty input text."""
        # No need to mock splitter or chain if docs are empty
        summary = summarize_text_langchain("", model_path=DEFAULT_MODEL_PATH)
        assert summary == "Input text was empty or too short to create document chunks."
        mock_exists.assert_called_with(DEFAULT_MODEL_PATH)

    @patch(OS_PATH_EXISTS_PATH, return_value=True)
    @patch(RECURSIVE_SPLITTER_PATH)
    def test_summarize_text_langchain_short_input_one_chunk(
        self, mock_splitter_class, mock_exists, mock_llm_instance, mock_chain_instance
    ):
        """Test summarization with short text resulting in one chunk."""
        mock_text_splitter = MagicMock()
        mock_text_splitter.split_text.return_value = ["short text chunk"]
        mock_splitter_class.return_value = mock_text_splitter

        with patch(DOCUMENT_PATH, side_effect=lambda page_content: Document(page_content=page_content)) as mock_doc_init:
            summary = summarize_text_langchain(self.SHORT_TEXT, model_path=DEFAULT_MODEL_PATH)

        assert summary == "mock summary"
        mock_text_splitter.split_text.assert_called_once_with(self.SHORT_TEXT)
        mock_doc_init.assert_called_once_with(page_content='short text chunk')
        mock_chain_instance.invoke.assert_called_once()
        args, _ = mock_chain_instance.invoke.call_args
        assert len(args[0]["input_documents"]) == 1

    @patch(OS_PATH_EXISTS_PATH, return_value=True)
    @patch(LOAD_SUMMARIZE_CHAIN_PATH)
    @patch(PROMPT_TEMPLATE_PATH) # Mock PromptTemplate class
    def test_summarize_text_langchain_uses_correct_prompts(
        self, mock_prompt_template_class, mock_load_chain, mock_exists, mock_llm_instance
    ):
        """Test that correct prompt templates are used."""
        # To capture the instances of PromptTemplate
        map_prompt_instance = MagicMock()
        reduce_prompt_instance = MagicMock()
        mock_prompt_template_class.side_effect = [map_prompt_instance, reduce_prompt_instance]
        
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = {"output_text": "mock summary"}
        mock_load_chain.return_value = mock_chain

        summarize_text_langchain(self.SAMPLE_TEXT, model_path=DEFAULT_MODEL_PATH)

        expected_prompt_calls = [
            call(template=MAP_PROMPT_TEMPLATE, input_variables=["text"]),
            call(template=REDUCE_PROMPT_TEMPLATE, input_variables=["text"])
        ]
        mock_prompt_template_class.assert_has_calls(expected_prompt_calls)

        mock_load_chain.assert_called_once()
        _, kwargs = mock_load_chain.call_args
        assert kwargs["map_prompt"] == map_prompt_instance
        assert kwargs["combine_prompt"] == reduce_prompt_instance
        assert kwargs["chain_type"] == "map_reduce"

    @patch(OS_PATH_EXISTS_PATH, return_value=True)
    @patch(LLAMA_CPP_PATH) # To inspect its call from initialize_llm
    def test_summarize_text_langchain_passes_llm_kwargs(
        self, mock_llama_cpp_class, mock_exists, mock_chain_instance # mock_chain_instance for load_summarize_chain
    ):
        """Test that llm_kwargs are passed to initialize_llm."""
        custom_llm_kwargs = {"temperature": 0.99, "n_ctx": 4096, "verbose": True}
        
        # Mock the LlamaCpp instance returned by initialize_llm
        mock_llm_returned_by_init = MagicMock()
        mock_llama_cpp_class.return_value = mock_llm_returned_by_init

        summarize_text_langchain(self.SAMPLE_TEXT, model_path=DEFAULT_MODEL_PATH, llm_kwargs=custom_llm_kwargs)

        expected_init_kwargs = {
            "model_path": DEFAULT_MODEL_PATH,
            "n_gpu_layers": -1,
            "n_batch": 512,
            **custom_llm_kwargs # Custom kwargs should override defaults or be added
        }
        # Default values that are not overridden by custom_llm_kwargs
        if "max_tokens" not in custom_llm_kwargs: expected_init_kwargs["max_tokens"] = 512
        if "top_p" not in custom_llm_kwargs: expected_init_kwargs["top_p"] = 0.9
        
        mock_llama_cpp_class.assert_called_once_with(**expected_init_kwargs)
        
        # Ensure the mocked LLM instance is passed to load_summarize_chain
        mock_chain_instance # This is actually the mock for load_summarize_chain itself
        args, _ = mock_chain_instance.call_args # mock_chain_instance is load_summarize_chain
        assert args[0] == mock_llm_returned_by_init

    @patch(OS_PATH_EXISTS_PATH, return_value=False) # Model doesn't exist
    @patch(LLAMA_CPP_PATH) # Mock LlamaCpp to prevent actual instantiation error
    def test_summarize_text_langchain_model_not_found_in_initialize_llm(
        self, mock_llama_cpp_class, mock_exists, capsys, mock_chain_instance
    ):
        """Test that warning for model not found is propagated from initialize_llm."""
        summarize_text_langchain(self.SAMPLE_TEXT, model_path="/non/existent/model.gguf")
        
        captured = capsys.readouterr()
        assert "WARNING: Model file not found at '/non/existent/model.gguf'" in captured.out
        # Chain should still be called with the (mocked) LLM instance
        mock_chain_instance.assert_called_once()

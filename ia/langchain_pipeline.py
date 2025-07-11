# ia/langchain_pipeline.py

import os
from typing import Dict, Any, List

from langchain_community.llms import LlamaCpp # This is the Langchain specific LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
# RecursiveCharacterTextSplitter is now imported via core
from langchain.docstore.document import Document

# Import from ia.core
from .core import (
    DEFAULT_MODEL_PATH,
    DEFAULT_PROMPT_DIR,
    DEFAULT_MAP_PROMPT_FILENAME,
    DEFAULT_REDUCE_PROMPT_FILENAME,
    FALLBACK_MAP_PROMPT_TEMPLATE,
    FALLBACK_REDUCE_PROMPT_TEMPLATE,
    load_prompt_template,
    create_text_splitter,
    initialize_llm,  # This now comes from core
)


def summarize_text_langchain(
    text_content: str,
    model_path: str = DEFAULT_MODEL_PATH,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
    map_prompt_file: str = os.path.join(DEFAULT_PROMPT_DIR, DEFAULT_MAP_PROMPT_FILENAME),
    reduce_prompt_file: str = os.path.join(DEFAULT_PROMPT_DIR, DEFAULT_REDUCE_PROMPT_FILENAME),
    llm_kwargs: Dict[str, Any] = None, # For LangchainLlamaCpp constructor and other settings
    llm_instance: LlamaCpp = None  # Added parameter for pre-initialized LLM
) -> str:
    """
    Summarizes the given text using a LangChain map-reduce pipeline with LlamaCpp.

    Args:
        text_content: The text to summarize.
        model_path: Path to the GGUF model file.
        chunk_size: The character count for splitting the text.
                    (Note: Sprint requirement is ~1000 tokens; this is a char-based proxy).
        chunk_overlap: Character overlap between chunks.
        map_prompt_template_str: Prompt template for the map step.
        reduce_prompt_template_str: Prompt template for the reduce step.
        llm_kwargs: Additional keyword arguments for LlamaCpp initialization.

    Returns:
        The summarized text.
    """
    if llm_kwargs is None:
        llm_kwargs = {}

    # Load prompts using core utility
    map_prompt_template_str = load_prompt_template(map_prompt_file, FALLBACK_MAP_PROMPT_TEMPLATE)
    reduce_prompt_template_str = load_prompt_template(reduce_prompt_file, FALLBACK_REDUCE_PROMPT_TEMPLATE)

    # Initialize LLM using the core function, specifying 'langchain' type
    # llm_kwargs here are passed to core.initialize_llm, which will handle them appropriately
    # for the LangchainLlamaCpp constructor (e.g. temp, max_tokens, top_p, n_gpu_layers, verbose etc.)
    llm: LlamaCpp # Type hint for clarity
    if llm_instance is None:
        llm = initialize_llm(
            model_path=model_path,
            pipeline_type="langchain",
            **llm_kwargs 
        )
    else:
        llm = llm_instance

    map_prompt = PromptTemplate(template=map_prompt_template_str, input_variables=["text"])
    reduce_prompt = PromptTemplate(
        template=reduce_prompt_template_str, input_variables=["text"]
    )

    # Create text splitter using core utility
    text_splitter = create_text_splitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs: List[Document] = [
        Document(page_content=x) for x in text_splitter.split_text(text_content)
    ]

    if not docs:
        return "Input text was empty or too short to create document chunks."

    chain = load_summarize_chain(
        llm,
        chain_type="map_reduce",
        map_prompt=map_prompt,
        combine_prompt=reduce_prompt,
        verbose=llm_kwargs.get("verbose", False),
        # token_max can be useful for combine_prompt if it exceeds context
        # combine_document_variable_name="text", # Default is text
    )

    # Using invoke as it's the more modern LangChain method.
    result = chain.invoke({"input_documents": docs})
    summary = result.get("output_text", "Failed to generate summary.")

    return summary


def generate_summary(llm, prompt: str) -> str:
    """Generate a summary using a pre-initialized LLM.
    
    Args:
        llm: Pre-initialized LangChain LLM
        prompt: The prompt to generate a summary for
        
    Returns:
        Generated summary text
    """
    try:
        # Simple generation with the pre-initialized LLM
        result = llm(prompt)
        return result.strip() if result else "No summary generated"
    except Exception as e:
        print(f"Error in generate_summary: {e}")
        raise


if __name__ == "__main__":
    # This block is for basic, direct testing of the pipeline.
    # For formal unit tests, use tests/test_langchain_pipeline.py.

    current_dir = os.path.dirname(__file__)
    sample_file_path = os.path.join(current_dir, "sample_text.txt")
    # The DEFAULT_MODEL_PATH is already an absolute path if __file__ is resolved, or relative to ia/
    # Let's ensure it's explicitly joined from current_dir for clarity if it's not absolute
    # model_file_path = DEFAULT_MODEL_PATH # This is already well-defined

    if not os.path.exists(DEFAULT_MODEL_PATH):
        print(f"SKIPPING `if __name__ == \"__main__\"` block in `langchain_pipeline.py`:")
        print(f"Model file not found at '{DEFAULT_MODEL_PATH}'.")
        print(
            "Please ensure the model is downloaded and placed in `ia/models/` "
            "or update DEFAULT_MODEL_PATH."
        )
    elif not os.path.exists(sample_file_path):
        print(f"SKIPPING `if __name__ == \"__main__\"` block in `langchain_pipeline.py`:")
        print(f"Sample text file not found at '{sample_file_path}'.")
    else:
        print("Running basic summarization test using LangChain pipeline...")
        print(f"Model: {DEFAULT_MODEL_PATH}")
        print(f"Sample Text: {sample_file_path}")

        with open(sample_file_path, "r", encoding="utf-8") as f:
            sample_text_content = f.read()

        print(f"\nOriginal Text (first 300 chars):\n{sample_text_content[:300]}...")

        # Example of providing LlamaCpp specific arguments for the test run
        test_llm_kwargs = {
            "n_ctx": 2048,  # Ensure context window is appropriate
            "temperature": 0.2,
            "verbose": True,  # Enable LlamaCpp verbose logging for this test
            # "n_gpu_layers": 0 # To force CPU for testing if GPU is problematic
        }

        try:
            summary_output = summarize_text_langchain(
                sample_text_content,
                model_path=DEFAULT_MODEL_PATH,
                llm_kwargs=test_llm_kwargs, # This will initialize a new LLM for the __main__ test

                # Reduce chunk_size for the short sample_text.txt if needed for testing map-reduce
                # chunk_size=500, # Example: smaller chunk for testing multiple chunks
            )
            print("\n--- Summary ---")
            print(summary_output)
            print("----------------")
        except Exception as e:
            import traceback
            print(f"\nError during summarization test: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            print(
                "This might be due to an incorrect model path, issues with "
                "llama-cpp-python installation, or CUDA problems."
            )
            print(
                "Please check your setup and the model path in `langchain_pipeline.py`."
            )

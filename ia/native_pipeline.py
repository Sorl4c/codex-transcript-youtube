# ia/native_pipeline.py

import os
from typing import Dict, Any, List

from llama_cpp import Llama # LlamaGrammar might be useful later

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
    map_summarize_chunk,
    reduce_summaries,
)


def summarize_text(
    text_content: str,
    model_path: str = DEFAULT_MODEL_PATH,
    chunk_size: int = 1000,
    chunk_overlap: int = 100,
    map_prompt_file: str = os.path.join(DEFAULT_PROMPT_DIR, DEFAULT_MAP_PROMPT_FILENAME),
    reduce_prompt_file: str = os.path.join(DEFAULT_PROMPT_DIR, DEFAULT_REDUCE_PROMPT_FILENAME),
    llm_instance: Llama = None,
    verbose: bool = False,
    llm_constructor_kwargs: Dict[str, Any] = None,
    generation_params: Dict[str, Any] = None
) -> str:
    """
    Summarizes text using llama-cpp-python directly with map-reduce logic.

    Args:
        text_content: The text to summarize.
        model_path: Path to the GGUF model file.
        chunk_size: Character count for splitting text.
        chunk_overlap: Character overlap between chunks.
        map_prompt_template_str: Prompt template for map step.
        reduce_prompt_template_str: Prompt template for reduce step.
        llm_kwargs: Keyword arguments for Llama initialization.
        generation_params: Params for LLM generation (e.g., max_tokens, temperature).

    Returns:
        The summarized text.
    """
    if generation_params is None:
        generation_params = {}

    # Load prompts
    map_prompt_template = load_prompt_template(map_prompt_file, FALLBACK_MAP_PROMPT_TEMPLATE)
    reduce_prompt_template = load_prompt_template(reduce_prompt_file, FALLBACK_REDUCE_PROMPT_TEMPLATE)

    # Use provided LLM instance if available, otherwise initialize
    llm: Llama # Type hint for clarity
    if llm_instance is None:
        if llm_constructor_kwargs is None:
            llm_constructor_kwargs = {}
        # Quita 'verbose' si está en llm_constructor_kwargs para evitar conflicto
        if "verbose" in llm_constructor_kwargs:
            llm_constructor_kwargs = dict(llm_constructor_kwargs)  # Copia defensiva
            llm_constructor_kwargs.pop("verbose")
        llm = initialize_llm(
            model_path=model_path,
            pipeline_type="native",
            verbose=verbose,  # solo se pasa aquí
            **llm_constructor_kwargs
        )
    else:
        llm = llm_instance

    # Default generation parameters, can be overridden by user-supplied generation_params
    # These are for the llm.__call__() or llm.create_completion()
    default_gen_params = {
        "temperature": 0.1,
        "max_tokens": 512,
        "top_p": 0.9,
        # Add other relevant llama.cpp generation params: top_k, repeat_penalty etc.
    }
    final_gen_params = {**default_gen_params, **generation_params}

    # Create text splitter
    text_splitter = create_text_splitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks: List[str] = text_splitter.split_text(text_content)

    if not chunks:
        return "Input text was empty or too short to create document chunks."

    # Map step
    map_summaries: List[str] = []
    print(f"Native Pipeline: Processing {len(chunks)} chunks for map step...")
    for i, chunk_text in enumerate(chunks):
        if verbose: # Use the new verbose parameter
            print(f"  Processing map chunk {i+1}/{len(chunks)}")
        summary = map_summarize_chunk(llm, chunk_text, map_prompt_template, final_gen_params, verbose) # Use the new verbose parameter
        map_summaries.append(summary)

    # Reduce step
    print(f"Native Pipeline: Combining {len(map_summaries)} summaries for reduce step...")
    final_summary = reduce_summaries(llm, map_summaries, reduce_prompt_template, final_gen_params, verbose) # Use the new verbose parameter

    return final_summary


def generate_summary(llm, prompt: str) -> str:
    """Generate a summary using a pre-initialized native LLM.
    
    Args:
        llm: Pre-initialized native LLM (Llama instance)
        prompt: The prompt to generate a summary for
        
    Returns:
        Generated summary text
    """
    try:
        # Simple generation with the pre-initialized LLM
        response = llm(prompt, max_tokens=512, temperature=0.7, top_p=0.9, echo=False)
        if response and 'choices' in response and len(response['choices']) > 0:
            return response['choices'][0]['text'].strip()
        return "No summary generated"
    except Exception as e:
        print(f"Error in generate_summary: {e}")
        raise


if __name__ == "__main__":
    current_dir = os.path.dirname(__file__)
    sample_file_path = os.path.join(current_dir, "sample_text.txt")

    if not os.path.exists(DEFAULT_MODEL_PATH):
        print(f"SKIPPING `if __name__ == \"__main__\"` block in `native_pipeline.py`:")
        print(f"Model file not found at '{DEFAULT_MODEL_PATH}'.")
    elif not os.path.exists(sample_file_path):
        print(f"SKIPPING `if __name__ == \"__main__\"` block in `native_pipeline.py`:")
        print(f"Sample text file not found at '{sample_file_path}'.")
    else:
        print("Running basic summarization test using Native pipeline...")
        print(f"Model: {DEFAULT_MODEL_PATH}")
        print(f"Sample Text: {sample_file_path}")

        with open(sample_file_path, "r", encoding="utf-8") as f:
            sample_text_content = f.read()

        print(f"\nOriginal Text (first 300 chars):\n{sample_text_content[:300]}...")

        test_llm_constructor_kwargs = {
            "n_ctx": 2048,
            "verbose": True, # Enable Llama.cpp verbose logging
            "n_gpu_layers": 0 # Example: Force CPU for this test if needed
        }
        test_gen_params = {
            "temperature": 0.2,
            "max_tokens": 150 # For the short sample text
        }

        try:
            summary_output = summarize_text(
                sample_text_content,
                model_path=DEFAULT_MODEL_PATH,
                llm_constructor_kwargs=test_llm_constructor_kwargs,
                generation_params=test_gen_params,
                # chunk_size=500 # Example for testing multiple chunks
            )
            print("\n--- Native Summary ---")
            print(summary_output)
            print("----------------------")
        except Exception as e:
            import traceback
            print(f"\nError during native summarization test: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            print("This might be due to an incorrect model path or llama-cpp-python issues.")

# ia/core.py

import os
from typing import Dict, Any, List, Union

# RecursiveCharacterTextSplitter will be imported conditionally inside create_text_splitter

# --- Constants ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MODEL_DIR = os.path.join(PROJECT_ROOT, "ia", "models")
DEFAULT_MODEL_FILENAME = "tinyllama.gguf"
DEFAULT_MODEL_PATH = f"/mnt/c/local/modelos/{DEFAULT_MODEL_FILENAME}" # Using TinyLlama for testing

DEFAULT_PROMPT_DIR = os.path.join(PROJECT_ROOT, "ia", "prompts")
DEFAULT_MAP_PROMPT_FILENAME = "map_summary.txt"
DEFAULT_REDUCE_PROMPT_FILENAME = "reduce_summary.txt"

# Default prompt templates (can be loaded from files too)
# These are kept for reference or if file loading fails, but load_prompt_template is preferred.
FALLBACK_MAP_PROMPT_TEMPLATE = """Please summarize the following text concisely and accurately:

{text}

Summary:"""

FALLBACK_REDUCE_PROMPT_TEMPLATE = """The following is a set of summaries:

{text}

Please synthesize these into a single, coherent summary.
The summary should be concise and capture the main points from all the provided summaries.

Combined Summary:"""

# --- Utility Functions ---

def load_prompt_template(prompt_file_path: str, fallback_template: str = "") -> str:
    """Loads a prompt template from a file. Uses fallback if file not found."""
    try:
        with open(prompt_file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: Prompt file not found at '{prompt_file_path}'. Using fallback template.")
        return fallback_template
    except Exception as e:
        print(f"Error loading prompt from '{prompt_file_path}': {e}. Using fallback template.")
        return fallback_template

def create_text_splitter(
    chunk_size: int = 1000, 
    chunk_overlap: int = 100
) -> "RecursiveCharacterTextSplitter":
    """
    Creates a RecursiveCharacterTextSplitter instance.
    Default chunk_size is characters, not tokens.
    """
    from langchain.text_splitter import RecursiveCharacterTextSplitter # Import here
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )

def initialize_llm(
    model_path: str = DEFAULT_MODEL_PATH,
    pipeline_type: str = "native",  # 'native' or 'langchain'
    n_gpu_layers: int = -1,
    n_batch: int = 512,
    verbose: bool = False,
    n_ctx: int = 2048,
    # LangchainLlamaCpp specific constructor params often passed via llm_kwargs in summarize_text_langchain
    temperature: float = 0.1, 
    max_tokens: int = 512, # Note: For Llama, this is a generation param, not constructor
    top_p: float = 0.9,
    **additional_kwargs: Any,
) -> Union["Llama", "LangchainLlamaCpp"]:
    """
    Initializes and returns an LLM instance (either Llama or LangchainLlamaCpp).
    Handles common parameters and pipeline-specific instantiation.
    """
    if not os.path.exists(model_path):
        print(f"WARNING: Model file not found at '{model_path}'. LLM initialization will likely fail.")
        # Allow the respective library to raise the specific error upon instantiation attempt.

    if pipeline_type == "native":
        from llama_cpp import Llama # Import Llama here

        # Explicitly list known Llama constructor args from its signature (excluding self, model_path)
        # Consult llama-cpp-python documentation for the exact list for the version used.
        # Common ones include: n_gpu_layers, main_gpu, tensor_split, vocab_only, use_mmap, use_mlock,
        # seed, n_ctx, n_batch, n_threads, n_threads_batch, rope_scaling_type, rope_freq_base,
        # rope_freq_scale, yarn_ext_factor, yarn_attn_factor, yarn_beta_fast, yarn_beta_slow,
        # yarn_orig_ctx, mul_mat_q, logits_all, embedding, lora_base, lora_path, verbose etc.
        known_llama_constructor_args = {
            "n_gpu_layers", "n_batch", "verbose", "n_ctx", "seed", "main_gpu", 
            "tensor_split", "vocab_only", "use_mmap", "use_mlock", "n_threads", 
            "n_threads_batch", "rope_scaling_type", "rope_freq_base", "rope_freq_scale",
            "yarn_ext_factor", "yarn_attn_factor", "yarn_beta_fast", "yarn_beta_slow",
            "yarn_orig_ctx", "mul_mat_q", "logits_all", "embedding", "lora_base", "lora_path"
        }

        # Base parameters that are explicitly handled or always passed
        base_params = {
            "model_path": model_path,
            "n_gpu_layers": n_gpu_layers,
            "n_batch": n_batch,
            "verbose": verbose,
            "n_ctx": n_ctx,
        }

        # Filter additional_kwargs to only include known Llama constructor args
        filtered_additional_kwargs = {
            k: v for k, v in additional_kwargs.items() if k in known_llama_constructor_args
        }

        # Combine base params with filtered additional_kwargs
        # Filtered_additional_kwargs will override base_params if there are common keys, which is intended.
        final_constructor_params = {**base_params, **filtered_additional_kwargs}
        
        return Llama(**final_constructor_params)

    elif pipeline_type == "langchain":
        from langchain_community.llms import LlamaCpp as LangchainLlamaCpp # Import LangchainLlamaCpp here

        # Parameters for LangchainLlamaCpp constructor
        # It takes temperature, max_tokens, top_p directly in constructor unlike raw Llama
        constructor_params = {
            "model_path": model_path,
            "n_gpu_layers": n_gpu_layers,
            "n_batch": n_batch,
            "verbose": verbose,
            "n_ctx": n_ctx,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            **additional_kwargs
        }
        return LangchainLlamaCpp(**constructor_params)
    
    else:
        raise ValueError(f"Unsupported pipeline_type: '{pipeline_type}'. Must be 'native' or 'langchain'.")

# --- Core Summarization Logic (for native/custom pipelines) ---

def map_summarize_chunk(
    llm: "Llama", 
    text_chunk: str, 
    map_prompt_template: str, 
    generation_params: Dict[str, Any],
    verbose: bool = False
) -> str:
    """Summarizes a single chunk of text using the provided LLM and map prompt."""
    prompt = map_prompt_template.format(text=text_chunk)
    if verbose:
        print(f"  Map chunk prompt (first 100 chars): {prompt[:100]}...")
    
    response = llm(prompt, **generation_params)
    summary = response["choices"][0]["text"].strip()
    
    if verbose:
        print(f"  Map chunk summary (first 100 chars): {summary[:100]}...")
    return summary

def reduce_summaries(
    llm: "Llama",
    summaries: List[str],
    reduce_prompt_template: str,
    generation_params: Dict[str, Any],
    verbose: bool = False
) -> str:
    """Combines multiple summaries into a final summary using the LLM and reduce prompt."""
    combined_text = "\n\n".join(summaries)
    prompt = reduce_prompt_template.format(text=combined_text)
    
    if verbose:
        print(f"  Reduce prompt (first 100 chars): {prompt[:100]}...")

    # Adjust generation params for reduce step if necessary (e.g., potentially longer summary)
    # final_gen_params = generation_params.copy()
    # final_gen_params["max_tokens"] = generation_params.get("max_tokens", 512) * 2 # Example

    response = llm(prompt, **generation_params) # Using original generation_params for now
    final_summary = response["choices"][0]["text"].strip()
    
    if verbose:
        print(f"  Final summary (first 100 chars): {final_summary[:100]}...")
    return final_summary


if __name__ == "__main__":
    # Basic tests for core utilities
    print("--- Testing ia.core utilities ---")

    # Test model path constant
    print(f"Default model path: {DEFAULT_MODEL_PATH}")
    if not os.path.exists(os.path.dirname(DEFAULT_MODEL_PATH)):
        os.makedirs(os.path.dirname(DEFAULT_MODEL_PATH), exist_ok=True)
        print(f"Created directory for model: {os.path.dirname(DEFAULT_MODEL_PATH)}")
    # Create a dummy model file for testing if it doesn't exist
    if not os.path.exists(DEFAULT_MODEL_PATH):
        try:
            with open(DEFAULT_MODEL_PATH, "w") as f_dummy:
                f_dummy.write("dummy model content")
            print(f"Created dummy model file for testing at: {DEFAULT_MODEL_PATH}")
        except Exception as e:
            print(f"Could not create dummy model file: {e}")


    # Test prompt loading
    map_prompt_file = os.path.join(DEFAULT_PROMPT_DIR, DEFAULT_MAP_PROMPT_FILENAME)
    reduce_prompt_file = os.path.join(DEFAULT_PROMPT_DIR, DEFAULT_REDUCE_PROMPT_FILENAME)
    
    if not os.path.exists(DEFAULT_PROMPT_DIR):
        os.makedirs(DEFAULT_PROMPT_DIR, exist_ok=True)
        print(f"Created prompt directory: {DEFAULT_PROMPT_DIR}")

    if not os.path.exists(map_prompt_file):
        with open(map_prompt_file, "w", encoding="utf-8") as f:
            f.write(FALLBACK_MAP_PROMPT_TEMPLATE)
        print(f"Created dummy map prompt file: {map_prompt_file}")

    if not os.path.exists(reduce_prompt_file):
        with open(reduce_prompt_file, "w", encoding="utf-8") as f:
            f.write(FALLBACK_REDUCE_PROMPT_TEMPLATE)
        print(f"Created dummy reduce prompt file: {reduce_prompt_file}")

    loaded_map_prompt = load_prompt_template(map_prompt_file, FALLBACK_MAP_PROMPT_TEMPLATE)
    print(f"Loaded map prompt (first 50 chars): {loaded_map_prompt[:50]}...")
    assert "{text}" in loaded_map_prompt

    # Test text splitter
    splitter = create_text_splitter(chunk_size=50, chunk_overlap=5)
    test_text = "This is a test sentence. It is a bit longer to see splitting. Another sentence here."
    chunks = splitter.split_text(test_text)
    print(f"Split text into {len(chunks)} chunks: {chunks}")
    assert len(chunks) > 1

    # Test LLM initialization (will print warnings if dummy model is not a real GGUF)
    print("Testing LLM initialization (expect warnings if using dummy model file)...")
    try:
        native_llm = initialize_llm(DEFAULT_MODEL_PATH, pipeline_type="native", verbose=False, n_gpu_layers=0) # n_gpu_layers=0 for CPU on test
        print(f"Native LLM initialized: {type(native_llm)}")
    except Exception as e:
        print(f"Error initializing native LLM (expected with dummy model): {e}")

    try:
        lc_llm = initialize_llm(DEFAULT_MODEL_PATH, pipeline_type="langchain", verbose=False, n_gpu_layers=0)
        print(f"Langchain LLM initialized: {type(lc_llm)}")
    except Exception as e:
        print(f"Error initializing Langchain LLM (expected with dummy model): {e}")
    
    print("--- ia.core tests finished ---")

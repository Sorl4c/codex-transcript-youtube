#!/usr/bin/env python3
# bench.py - Benchmarking tool for LLM summarization pipelines

import argparse
import json
import os
import sys
import time
import glob
import datetime
from pathlib import Path
from typing import Dict, List, Any, Union, Optional

# Ensure the 'ia' module can be found
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from llama_cpp import Llama as NativeLlama
from langchain_community.llms import LlamaCpp as LangchainLlama

from ia.langchain_pipeline import summarize_text_langchain
from ia.native_pipeline import summarize_text as summarize_text_native
from ia.core import (
    initialize_llm as core_initialize_llm,
    DEFAULT_MODEL_PATH as CORE_DEFAULT_MODEL_PATH,
    DEFAULT_PROMPT_DIR
)
from ia.gemini_api import summarize_text_gemini, count_tokens_gemini, GEMINI_MODEL_NAME as DEFAULT_GEMINI_MODEL_NAME # Added


# Default paths
DEFAULT_INPUT_PATH = os.path.join(project_root, "ia", "sample_text.txt")
DEFAULT_OUTPUT_DIR = os.path.join(project_root, "bench_results")

def count_tokens(model_instance: Union[NativeLlama, LangchainLlama], text: str) -> int:
    """Count tokens in text using the model's tokenizer."""
    if not text:
        return 0
    try:
        if isinstance(model_instance, NativeLlama):
            return len(model_instance.tokenize(text.encode("utf-8", "ignore")))
        elif isinstance(model_instance, LangchainLlama):
            return model_instance.get_num_tokens(text)
        return 0
    except Exception as e:
        print(f"Warning: Error counting tokens: {e}")
        return 0

def get_model_context_size(model_path: str) -> int:
    """Determine context size based on model filename."""
    model_name = os.path.basename(model_path).lower()
    if "tinyllama" in model_name:
        return 2048
    elif "mistral" in model_name or "mixtral" in model_name:
        return 8192
    elif "llama" in model_name:
        return 4096
    return 2048  # Default safe value

def load_prompts(prompts_dir: str) -> Dict[str, str]:
    """Load all prompt templates from directory."""
    prompts = {}
    for prompt_file in glob.glob(os.path.join(prompts_dir, "*.txt")):
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_name = os.path.basename(prompt_file).replace('.txt', '')
                prompts[prompt_name] = f.read().strip()
        except Exception as e:
            print(f"Error loading prompt {prompt_file}: {e}")
    
    if not prompts:
        print(f"Warning: No prompts found in {prompts_dir}")
        return {"default": "Resume el siguiente texto de manera concisa:\n\n{text}"}
    return prompts

def run_benchmark(args, native_llm, model_load_time, langchain_llm=None):
    """Run benchmark with given arguments and pre-initialized LLM(s).
    
    Args:
        args: Command line arguments
        native_llm: Initialized native LLM instance (or None if not using native pipeline)
        model_load_time: Time taken to load the model(s)
        langchain_llm: Initialized LangChain LLM instance (or None if not using LangChain pipeline)
    """
    # Check which pipelines to run
    run_native = args.pipeline in ['native', 'both'] and native_llm is not None
    run_langchain = args.pipeline in ['langchain', 'both'] and langchain_llm is not None
    run_gemini = args.pipeline in ['gemini', 'both'] # Gemini doesn't need a pre-loaded LLM instance in the same way
    
    pipeline_desc_parts = []
    if run_native:
        pipeline_desc_parts.append("native")
    if run_langchain:
        pipeline_desc_parts.append("LangChain")
    if run_gemini:
        pipeline_desc_parts.append("Gemini")
    
    if not pipeline_desc_parts:
        pipeline_desc = "no pipelines selected or LLM not available for selected local pipelines"
    elif len(pipeline_desc_parts) == 1:
        pipeline_desc = f"{pipeline_desc_parts[0]} pipeline"
    else:
        pipeline_desc = f"{', '.join(pipeline_desc_parts[:-1])} & {pipeline_desc_parts[-1]} pipelines"
                   
    print(f"🚀 Starting benchmark with {pipeline_desc}")
    print(f"📄 Input: {args.input}")
    print(f"🤖 Model: {args.model_path}")

    # Check if at least one LLM instance is available for the requested pipelines
    if run_native and native_llm is None:
        print("⚠️  Native pipeline was requested, but the native LLM instance is not available.")
        run_native = False # Disable native run if instance is missing
    if run_langchain and langchain_llm is None:
        print("⚠️  LangChain pipeline was requested, but the LangChain LLM instance is not available.")
        run_langchain = False # Disable LangChain run if instance is missing
    
    if not run_native and not run_langchain and not run_gemini:
        print("❌ No valid pipelines to run. Exiting benchmark.")
        return None

    # Load input text
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            input_text = f.read()
    except FileNotFoundError:
        print(f"❌ Error: Input file not found at {args.input}")
        return None
    except Exception as e:
        print(f"❌ Error reading input file: {e}")
        return None

    # Load prompts
    prompts = load_prompts(args.prompts_dir)
    if not prompts:
        print("❌ Error: No prompts found. Check your prompt directory or provide default prompts.")
        return None
    print(f"📝 Loaded {len(prompts)} prompt(s)")

    # Display model configuration for clarity
    print("⚙️  Model configuration:")
    effective_n_ctx = args.n_ctx or get_model_context_size(args.model_path)
    print(f"   - Context size: {effective_n_ctx} tokens")
    max_new_tokens = args.max_tokens or (effective_n_ctx // 4) if effective_n_ctx else 512
    print(f"   - Max new tokens: {max_new_tokens}")

    # Shared LLM parameters
    llm_params = {
        "n_gpu_layers": args.n_gpu_layers,
        "n_batch": args.n_batch,
        "verbose": args.verbose_llm,
        "temperature": 0.7,
        "max_tokens": max_new_tokens,
        "top_p": 0.9,
        "n_ctx": effective_n_ctx,
        "repeat_penalty": 1.1
    }
    
    # model_load_time is now passed directly
    print("✅ Using pre-initialized LLM")
    
    # Para el modo 'both', vamos a crear un diccionario para almacenar resultados de ambos pipelines
    results_by_pipeline = {
        "native": [] if run_native else None,
        "langchain": [] if run_langchain else None
    }
    
    # Run each prompt
    combined_results = []
    
    for prompt_name, prompt_template in prompts.items():
        print(f"\n{'='*60}")
        print(f"🧪 Testing prompt: {prompt_name}")
        print(f"{'='*60}")
        
        # Prepare prompt with input text
        prompt = prompt_template.format(text=input_text) if "{text}" in prompt_template \
                else f"{prompt_template}\n\n{input_text}"
        
        # Create a record for this prompt that will contain results from both pipelines
        prompt_result = {
            "prompt_name": prompt_name,
            "prompt": prompt_template
        }
        
        generation_specific_params = {
            "max_tokens": llm_params.get("max_tokens"),
            "temperature": llm_params.get("temperature"),
            "top_p": llm_params.get("top_p"),
        }
        
        # Run native pipeline if enabled
        if run_native and native_llm is not None:
            print("🔄 Running native pipeline...")
            try:
                start_time = time.time()
                
                native_summary = summarize_text_native(
                    prompt,
                    model_path=args.model_path, 
                    llm_instance=native_llm,
                    generation_params=generation_specific_params,
                    verbose=args.verbose_llm
                )
                
                end_time = time.time()
                duration = end_time - start_time
                input_tokens = count_tokens(native_llm, prompt) if hasattr(native_llm, 'tokenize') else len(prompt.split())
                output_tokens = count_tokens(native_llm, native_summary) if hasattr(native_llm, 'tokenize') else len(native_summary.split())
                tokens_per_sec = output_tokens / duration if duration > 0 else 0
                compression_ratio = output_tokens / input_tokens if input_tokens > 0 else 0
                
                # Store native results
                native_data = {
                    "metrics": {
                        "model_load_time_seconds": model_load_time,
                        "processing_time_seconds": duration,
                        "input_tokens": input_tokens,
                        "total_tokens": output_tokens,
                        "tokens_per_second": round(tokens_per_sec, 2),
                        "compression_ratio": round(compression_ratio, 3)
                    },
                    "llm_parameters_used": {k: v for k, v in llm_params.items() if k in ["temperature", "max_tokens", "top_p", "n_ctx"]},
                    "summary": native_summary,
                    "input_sample": input_text[:500] + ("..." if len(input_text) > 500 else ""),
                    "model": os.path.basename(args.model_path),
                    "pipeline": "native",
                    "input_file": args.input,
                    "hardware": {
                        "cpu": os.environ.get("PROCESSOR_IDENTIFIER", "To be specified"),
                        "gpu": "To be specified"
                    }
                }
                
                if args.pipeline == "both":
                    prompt_result["native_result"] = native_data
                else:
                    prompt_result["result"] = native_data
                    
                print(f"✓ Native: Generated {output_tokens} tokens in {duration:.2f}s ({tokens_per_sec:.2f} tok/s)")
                
            except Exception as e:
                print(f"❌ Error in native pipeline: {e}")
                import traceback
                traceback.print_exc()
                
        # Run LangChain pipeline if enabled
        if run_langchain and langchain_llm is not None:
            print("🔄 Running LangChain pipeline...")
            try:
                start_time = time.time()
                
                langchain_summary = summarize_text_langchain(
                    prompt,
                    model_path=args.model_path,
                    llm_instance=langchain_llm,
                    llm_kwargs={"verbose": args.verbose_llm}
                )
                
                end_time = time.time()
                duration = end_time - start_time
                
                # Handle token counting for LangChain LLM
                if hasattr(langchain_llm, 'get_num_tokens'):
                    input_tokens = langchain_llm.get_num_tokens(prompt)
                    output_tokens = langchain_llm.get_num_tokens(langchain_summary)
                else:
                    # Fallback to simple word count if tokenizer not available
                    input_tokens = len(prompt.split())
                    output_tokens = len(langchain_summary.split())
                
                tokens_per_sec = output_tokens / duration if duration > 0 else 0
                compression_ratio = output_tokens / input_tokens if input_tokens > 0 else 0
                
                # Store LangChain results
                langchain_data = {
                    "metrics": {
                        "model_load_time_seconds": model_load_time,
                        "processing_time_seconds": duration,
                        "input_tokens": input_tokens,
                        "total_tokens": output_tokens,
                        "tokens_per_second": round(tokens_per_sec, 2),
                        "compression_ratio": round(compression_ratio, 3)
                    },
                    "llm_parameters_used": {k: v for k, v in llm_params.items() if k in ["temperature", "max_tokens", "top_p", "n_ctx"]},
                    "summary": langchain_summary,
                    "input_sample": input_text[:500] + ("..." if len(input_text) > 500 else ""),
                    "model": os.path.basename(args.model_path),
                    "pipeline": "langchain",
                    "input_file": args.input,
                    "hardware": {
                        "cpu": os.environ.get("PROCESSOR_IDENTIFIER", "To be specified"),
                        "gpu": "To be specified"
                    }
                }
                
                if args.pipeline == "both":
                    prompt_result["langchain_result"] = langchain_data
                else:
                    prompt_result["result"] = langchain_data
                    
                print(f"✓ LangChain: Generated {output_tokens} tokens in {duration:.2f}s ({tokens_per_sec:.2f} tok/s)")
                
            except Exception as e:
                print(f"❌ Error in LangChain pipeline: {e}")
                import traceback
                traceback.print_exc()
        
        # Run Gemini pipeline if enabled
        if run_gemini:
            print("🔄 Running Gemini pipeline...")
            try:
                start_time = time.time()
                
                gemini_result = ia.gemini_api.summarize_text_gemini(
                    text_content=input_text,
                    prompt_template=prompt_template,
                    model_name=args.gemini_model,
                    api_key=args.gemini_api_key
                )
                summary_text = gemini_result.get('summary_text', '')
                if gemini_result.get('error'):
                    print(f"[ERROR] Gemini API Error: {gemini_result['error']}", file=sys.stderr)
                
                end_time = time.time()
                duration = end_time - start_time
                
                if gemini_result.get("error"):
                    raise Exception(gemini_result["error"])

                summary_gemini = gemini_result.get("summary_text", "No summary generated")
                gemini_input_tokens = gemini_result.get("input_tokens", 0)
                gemini_output_tokens = gemini_result.get("output_tokens", 0)
                gemini_cost = gemini_result.get("cost", 0.0)
                
                # Store Gemini results
                gemini_data = {
                    "metrics": {
                        "processing_time_seconds": duration,
                        "input_tokens": gemini_input_tokens,
                        "output_tokens": gemini_output_tokens,
                        "cost_usd": gemini_cost,
                        "tokens_per_second": gemini_output_tokens / duration if duration > 0 else 0,
                        "compression_ratio": gemini_input_tokens / gemini_output_tokens if gemini_output_tokens > 0 else float('inf')
                    },
                    "llm_parameters_used": {"model_name": args.gemini_model},
                    "summary": summary_gemini,
                    "input_sample": input_text[:500] + ("..." if len(input_text) > 500 else ""),
                    "model": args.gemini_model,
                    "pipeline": "gemini",
                    "input_file": args.input,
                    "hardware": {
                        "cpu": os.environ.get("PROCESSOR_IDENTIFIER", "To be specified"),
                        "gpu": "To be specified"
                    }
                }
                
                # Always store under 'gemini_result' for consistency with native_result and langchain_result
                prompt_result["gemini_result"] = gemini_data
                    
                print(f"✓ Gemini: Generated {gemini_output_tokens} tokens in {duration:.2f}s ({gemini_output_tokens / duration:.2f} tok/s), Cost: ${gemini_cost:.6f}")
                
            except Exception as e:
                print(f"❌ Error in Gemini pipeline: {e}")
                # Store error information
                if 'gemini_result' not in prompt_result: prompt_result['gemini_result'] = {}
                prompt_result['gemini_result']['summary'] = ''
                prompt_result['gemini_result']['metrics'] = {}
                prompt_result['gemini_result']['error'] = str(e)
                prompt_result['gemini_result']['llm_params'] = {"model_name": args.gemini_model}
                # traceback.print_exc() # Uncomment for debugging if needed
        
        # Add this prompt's results to the combined results
        combined_results.append(prompt_result)
        
    # Preparar la estructura final de resultados según el modo de benchmark
    final_results = {}
    
    if args.pipeline == "both":
        final_results = {
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "pipeline": "combined",
                "model": os.path.basename(args.model_path),
                "total_prompts_tested": len(combined_results)
            },
            "results": combined_results
        }
    else:
        # Formato estándar para un solo pipeline
        final_results = {
            "metadata": {
                "timestamp": datetime.datetime.now().isoformat(),
                "pipeline": args.pipeline,
                "model": os.path.basename(args.model_path) if args.pipeline != "gemini" else args.gemini_model,
                "total_prompts_tested": len(combined_results)
            },
            "results": combined_results
        }
    
    return final_results

def save_results(results: Dict[str, Any], output_dir: str) -> str:
    """Save benchmark results to file."""
    os.makedirs(output_dir, exist_ok=True)
    
    pipeline = results.get("metadata", {}).get("pipeline", "unknown")
    model_name = results.get("metadata", {}).get("model", "model").split(".")[0]
    
    # Usar solo la fecha (sin timestamp) para mejor legibilidad
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    
    output_file = os.path.join(
        output_dir, 
        f"benchmark_{pipeline}_{model_name}_{date_str}.json"
    )
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\u2705 Results saved to {output_file}")
    return output_file

def main():
    parser = argparse.ArgumentParser(
        description="Benchmark tool for LLM summarization pipelines"
    )
    parser.add_argument(
        "--pipeline",
        type=str,
        choices=['native', 'langchain', 'gemini', 'both'],
        default="native",
        help="Pipeline to benchmark (default: native, 'both' runs native and langchain with the same model load)"
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default=CORE_DEFAULT_MODEL_PATH,
        help=f"Path to the GGUF model file for local pipelines (default: {CORE_DEFAULT_MODEL_PATH})"
    )
    parser.add_argument(
        "--input",
        type=str,
        default=DEFAULT_INPUT_PATH,
        help=f"Path to input text file (default: {DEFAULT_INPUT_PATH})"
    )
    parser.add_argument(
        "--prompts-dir",
        type=str,
        default=DEFAULT_PROMPT_DIR,
        help=f"Directory containing prompt templates (default: {DEFAULT_PROMPT_DIR})"
    )
    # Model configuration
    model_group = parser.add_argument_group('Model Configuration')
    model_group.add_argument(
        "--n-ctx",
        type=int,
        default=2048,
        help="Context window size in tokens (default: 2048, set to 0 to auto-detect from model)"
    )
    model_group.add_argument(
        "--n-batch",
        type=int,
        default=512,
        help="Batch size for prompt processing (default: 512)"
    )
    model_group.add_argument(
        "--n-gpu-layers",
        type=int,
        default=-1,
        help="Number of layers to offload to GPU (-1 for all, 0 for CPU only, default: -1)"
    )
    model_group.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Maximum tokens to generate (default: 1/4 of context size)"
    )
    
    # Output configuration
    # Gemini API specific arguments
    gemini_group = parser.add_argument_group('Gemini API Configuration')
    gemini_group.add_argument(
        "--gemini-api-key",
        type=str,
        default=None,
        help="Gemini API key. If not provided, uses GEMINI_API_KEY environment variable."
    )
    gemini_group.add_argument(
        "--gemini-model",
        type=str,
        default=DEFAULT_GEMINI_MODEL_NAME,
        help=f"Gemini model to use (default: {DEFAULT_GEMINI_MODEL_NAME})"
    )

    output_group = parser.add_argument_group('Output Configuration')
    output_group.add_argument(
        "--output-dir",
        type=str,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to save benchmark results (default: {DEFAULT_OUTPUT_DIR})"
    )
    output_group.add_argument(
        "--verbose-llm",
        action="store_true",
        help="Enable verbose output from LLM"
    )
    
    args = parser.parse_args()
    
    # Initialize LLM and measure load time
    print("\n🔄 Initializing LLM...")
    llm_init_start_time = time.time()
    model_load_time = 0
    native_llm = None
    langchain_llm = None

    # Initialize local LLMs if needed
    if args.pipeline in ['native', 'langchain', 'both']:
        print("\n🔄 Initializing Local LLM(s)...")
        if args.pipeline == 'native' or args.pipeline == 'both':
            print("🔄 Initializing native LLM...")
            native_llm = core_initialize_llm(
                model_path=args.model_path,
                pipeline_type='native',
                n_ctx=args.n_ctx or get_model_context_size(args.model_path),
                n_gpu_layers=args.n_gpu_layers,
                n_batch=args.n_batch,
                verbose=args.verbose_llm
            )
            if native_llm: print("✅ Native LLM initialized.")
            else: print("❌ Native LLM initialization failed.")

        if args.pipeline == 'langchain' or args.pipeline == 'both':
            print("🔄 Initializing LangChain LLM...")
            # Common LangChain LlamaCpp settings, can be overridden by additional_kwargs in core_initialize_llm
            lc_init_params = {
                "temperature": 0.1,
                "max_tokens": args.max_tokens or (args.n_ctx // 4) if args.n_ctx else 512,
                "top_p": 0.9
            }
            langchain_llm = core_initialize_llm(
                model_path=args.model_path,
                pipeline_type='langchain',
                n_ctx=args.n_ctx or get_model_context_size(args.model_path),
                n_gpu_layers=args.n_gpu_layers,
                n_batch=args.n_batch,
                verbose=args.verbose_llm,
                **lc_init_params
            )
            if langchain_llm: print("✅ LangChain LLM initialized.")
            else: print("❌ LangChain LLM initialization failed.")
        
        model_load_time = time.time() - llm_init_start_time
        if native_llm or langchain_llm:
            print(f"✅ Local LLM(s) loaded in {model_load_time:.2f} seconds")
        elif args.pipeline != 'gemini': # only print warning if a local pipeline was explicitly chosen and failed
             print(f"⚠️ Local LLM loading finished in {model_load_time:.2f} seconds, but no local LLM was successfully initialized for '{args.pipeline}'.")
    
    elif args.pipeline == 'gemini':
        print("✨ Running Gemini API pipeline. No local LLM initialization needed for this pipeline.")
        model_load_time = 0 # No local model loaded
    else:
        print(f"Unknown pipeline: {args.pipeline}. Cannot initialize LLMs.")
        return 1

    try:
        # Run benchmark, passing the appropriate LLM instance(s) and load time
        # run_benchmark now handles which pipelines to run based on args.pipeline and available llms
        results = run_benchmark(args, native_llm, model_load_time, langchain_llm)

        
        # Save results if successful
        if results:
            output_file = save_results(results, args.output_dir)
            print(f"\n✅ Benchmark completed! Results saved to: {output_file}")
            
    except Exception as e:
        print(f"\n❌ Error during benchmark: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n🏁 Benchmark completed")

if __name__ == "__main__":
    main()

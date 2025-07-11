import argparse
import json
import os
import glob
import re
import statistics
import datetime
from math import isnan, isinf

# Constants
DEFAULT_RESULTS_DIR = 'bench_results'
DEFAULT_OUTPUT_REPORT = os.path.join(DEFAULT_RESULTS_DIR, 'comparison_report.md')
BAR_LENGTH = 20  # Length of the visual bar in characters

# Emojis for winners
WINNER_NATIVE_EMOJI = "Native 🥇"
WINNER_LANGCHAIN_EMOJI = "LangChain 🥈"
WINNER_TIE_EMOJI = "Tie 🤝"

# --- Helper Functions ---

def load_results(file_path):
    """Loads benchmark results from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"❌ Error: Could not decode JSON from {file_path}")
        return None

def find_latest_benchmark_file(results_dir):
    """Finds the latest combined benchmark file."""
    pattern = os.path.join(results_dir, 'benchmark_combined_*.json')
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getctime)

def calculate_word_count(text):
    """Calculates the number of words in a text."""
    if not text or not isinstance(text, str):
        return 0
    words = re.findall(r'\b\w+\b', text.lower())
    return len(words)

def calculate_vocabulary_richness(text):
    """Calculates vocabulary richness (unique words / total words)."""
    if not text or not isinstance(text, str):
        return 0.0
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return 0.0
    total_words = len(words)
    unique_words = len(set(words))
    return unique_words / total_words if total_words > 0 else 0.0

def calculate_input_output_token_ratio(input_tokens, output_tokens):
    """Calculates compression ratio as Input Tokens / Output Tokens."""
    if output_tokens is None or input_tokens is None:
        return None
    if not isinstance(input_tokens, (int,float)) or not isinstance(output_tokens, (int,float)):
        return None
    if output_tokens == 0:
        return float('inf') if input_tokens > 0 else 0.0
    return input_tokens / output_tokens

def get_metric_from_json(data_dict, path_keys, default=None):
    """Safely retrieves a value from a nested dict using a list of keys."""
    current = data_dict
    for key in path_keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current if not (isinstance(current, float) and isnan(current)) else default

def format_value(value, specifier="", unit="", default_na="N/A"):
    """Formats a value for display, handling None or non-numeric types."""
    if value is None:
        return default_na
    if isinstance(value, float) and (isnan(value) or isinf(value)):
        return default_na
    if not isinstance(value, (int, float)):
        return str(value) # Or default_na if preferred for non-numerics
    
    try:
        return f"{value:{specifier}}{unit}"
    except (ValueError, TypeError):
        return str(value) + unit # Fallback if format spec fails

def determine_winner(native_val, lc_val, lower_is_better):
    """Determines the winner between native and LangChain for a metric."""
    if native_val is None or lc_val is None or \
       not isinstance(native_val, (int, float)) or \
       not isinstance(lc_val, (int, float)) or \
       isnan(native_val) or isnan(lc_val) or isinf(native_val) or isinf(lc_val):
        return WINNER_TIE_EMOJI

    if lower_is_better:
        if native_val < lc_val: return WINNER_NATIVE_EMOJI
        if lc_val < native_val: return WINNER_LANGCHAIN_EMOJI
    else:
        if native_val > lc_val: return WINNER_NATIVE_EMOJI
        if lc_val > native_val: return WINNER_LANGCHAIN_EMOJI
    return WINNER_TIE_EMOJI

def generate_comparison_bar(value, reference_value, bar_length, lower_is_better):
    """Generates a bar for 'value' relative to 'reference_value'."""
    if value is None or reference_value is None or \
       not isinstance(value, (int, float)) or not isinstance(reference_value, (int, float)) or \
       isnan(value) or isnan(reference_value) or isinf(value) or isinf(reference_value):
        return '[' + ' ' * bar_length + ']'

    # Normalize so that a "better" score is higher (closer to 1.0)
    # Max_val is the "anchor" for scaling, typically the worse of the two values.
    # Or, if lower is better, max_val is the higher (worse) value.
    # If higher is better, max_val is the higher (better) value.

    # Let's simplify: the bar represents the value's magnitude.
    # The "winner" emoji will tell which direction is good.
    # Scale against the maximum of the two values.
    
    scale_max = max(abs(value), abs(reference_value))
    if scale_max == 0:
        fill_length = 0 if value == 0 else bar_length # if both 0, empty, if one non-zero, full
    else:
        ratio = abs(value) / scale_max
        fill_length = int(ratio * bar_length)
    
    fill_length = max(0, min(bar_length, fill_length))
    bar_char = '█'
    return f"[{bar_char * fill_length}{' ' * (bar_length - fill_length)}]"

# --- Metrics Configuration ---
METRICS_CONFIG = [
    {
        'id': 'proc_time', 'display': "⏱️ Processing Time", 'unit': "s",
        'path': ['metrics', 'processing_time_seconds'], 'lower_is_better': True, 'format': ".2f"
    },
    {
        'id': 'tokens_per_sec', 'display': "⚡ Tokens/Second", 'unit': " tok/s",
        'path': ['metrics', 'tokens_per_second'], 'lower_is_better': False, 'format': ".2f"
    },
    {
        'id': 'tokens_generated', 'display': "📄 Tokens Generated", 'unit': " tokens",
        'path': ['metrics', 'total_tokens'], 'lower_is_better': False, 'format': ".0f" # Subjective
    },
    {
        'id': 'tokens_input', 'display': "📥 Input Tokens", 'unit': " tokens",
        'path': ['metrics', 'input_tokens'], 'lower_is_better': False, 'format': ".0f" # Informational
    },
    {
        'id': 'summary_len_chars', 'display': "📏 Summary Length (chars)", 'unit': " chars",
        'func': lambda res_data: len(res_data.get('summary', "")),
        'lower_is_better': False, 'format': ".0f" # Subjective
    },
    {
        'id': 'summary_len_words', 'display': "🗣️ Summary Length (words)", 'unit': " words",
        'func': lambda res_data: calculate_word_count(res_data.get('summary', "")),
        'lower_is_better': False, 'format': ".0f" # Subjective
    },
    {
        'id': 'vocab_richness', 'display': "🎨 Vocabulary Richness", 'unit': "", # Ratio
        'func': lambda res_data: calculate_vocabulary_richness(res_data.get('summary', "")),
        'lower_is_better': False, 'format': ".3f"
    },
    {
        'id': 'io_token_ratio', 'display': "⚖️ Compression (In/Out)", 'unit': ":1",
        'func': lambda res_data: calculate_input_output_token_ratio(
            get_metric_from_json(res_data, ['metrics', 'input_tokens']),
            get_metric_from_json(res_data, ['metrics', 'total_tokens'])
        ),
        'lower_is_better': False, 'format': ".2f" # Higher is more compression
    },
    {
        'id': 'compression_ratio_json', 'display': "📦 Compression (Out/In JSON)", 'unit': "",
        'path': ['metrics', 'compression_ratio'], 'lower_is_better': True, 'format': ".3f" # Lower is more compression
    }
]

# --- Main Application ---
def main():
    parser = argparse.ArgumentParser(description="Visually compare LLM benchmark results from a combined JSON file.")
    parser.add_argument(
        "--results-dir", type=str, default=DEFAULT_RESULTS_DIR,
        help=f"Directory containing benchmark JSON files. Default: {DEFAULT_RESULTS_DIR}"
    )
    parser.add_argument(
        "--output", type=str, default=DEFAULT_OUTPUT_REPORT,
        help=f"Path to the output markdown report. Default: {DEFAULT_OUTPUT_REPORT}"
    )
    args = parser.parse_args()

    combined_file_path = find_latest_benchmark_file(args.results_dir)
    if not combined_file_path:
        print(f"❌ No combined benchmark file found in '{args.results_dir}'. Searched for 'benchmark_combined_*.json'.")
        print("Ensure 'bench.py --pipeline both' has run successfully.")
        return 1

    print(f"ℹ️ Processing combined results file: {os.path.basename(combined_file_path)}")
    combined_data = load_results(combined_file_path)
    if not combined_data or 'results' not in combined_data:
        print("❌ Combined data is invalid or missing 'results' key. Exiting.")
        return 1

    report_content = ["# LLM Pipeline Benchmark Comparison Report"]
    metadata = combined_data.get('metadata', {})
    report_content.append(f"_Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")
    report_content.append(f"**Source File:** `{os.path.basename(combined_file_path)}`")
    report_content.append(f"**LLM Model:** `{metadata.get('model', 'N/A')}`")
    report_content.append(f"**Total Prompts in File:** {metadata.get('total_prompts_tested', 'N/A')}\n")

    # --- Prepare data for all prompts ---
    processed_prompts = []
    for item in combined_data.get('results', []):
        prompt_name = item.get('prompt_name')
        native_res = item.get('native_result')
        lc_res = item.get('langchain_result')

        if not prompt_name or not native_res or not lc_res:
            print(f"⚠️ Skipping item due to missing data: {prompt_name or 'Unknown Prompt'}")
            continue

        prompt_data = {
            'name': prompt_name,
            'original_text': native_res.get('input_sample', "Original text not found."), # Assuming same for both
            'native_summary': native_res.get('summary', "N/A"),
            'lc_summary': lc_res.get('summary', "N/A"),
            'native_params': native_res.get('llm_parameters_used', {}),
            'lc_params': lc_res.get('llm_parameters_used', {}),
            'metrics': {}
        }

        for m_conf in METRICS_CONFIG:
            val_n, val_l = None, None
            if 'func' in m_conf: # Calculated metric
                val_n = m_conf['func'](native_res)
                val_l = m_conf['func'](lc_res)
            elif 'path' in m_conf: # Metric from JSON path
                val_n = get_metric_from_json(native_res, m_conf['path'])
                val_l = get_metric_from_json(lc_res, m_conf['path'])
            prompt_data['metrics'][m_conf['id']] = {'native': val_n, 'lc': val_l}
        processed_prompts.append(prompt_data)

    if not processed_prompts:
        report_content.append("\n**No common prompts with full data found to compare.**")
        # ... (write report and exit)
        try:
            os.makedirs(args.results_dir, exist_ok=True)
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_content))
            print(f"\n⚠️ Report generated with no comparable prompts: {args.output}")
        except Exception as e:
            print(f"\n❌ Error writing report file: {e}")
        return 1
        
    report_content.append(f"**Prompts Compared:** {len(processed_prompts)}\n")

    # --- Executive Summary ---
    report_content.append("## 🏆 Executive Summary: Average Performance")
    summary_table = ["| Metric                       | Avg. Native Value | Avg. LangChain Value | Overall Winner   |",
                     "|------------------------------|-------------------|----------------------|------------------|"]
    
    avg_metrics_overall = {}

    for m_conf in METRICS_CONFIG:
        m_id = m_conf['id']
        native_values = [p['metrics'][m_id]['native'] for p in processed_prompts if p['metrics'][m_id]['native'] is not None and isinstance(p['metrics'][m_id]['native'], (int, float)) and not isnan(p['metrics'][m_id]['native']) and not isinf(p['metrics'][m_id]['native'])]
        lc_values = [p['metrics'][m_id]['lc'] for p in processed_prompts if p['metrics'][m_id]['lc'] is not None and isinstance(p['metrics'][m_id]['lc'], (int, float)) and not isnan(p['metrics'][m_id]['lc']) and not isinf(p['metrics'][m_id]['lc'])]

        avg_n = statistics.mean(native_values) if native_values else None
        avg_l = statistics.mean(lc_values) if lc_values else None
        avg_metrics_overall[m_id] = {'native': avg_n, 'lc': avg_l}

        winner = determine_winner(avg_n, avg_l, m_conf['lower_is_better'])
        
        summary_table.append(
            f"| {m_conf['display']:<28} | "
            f"{format_value(avg_n, m_conf['format'], m_conf['unit']):<17} | "
            f"{format_value(avg_l, m_conf['format'], m_conf['unit']):<20} | "
            f"{winner:<16} |"
        )
    report_content.extend(summary_table)
    report_content.append("\n_Note: Averages are calculated over prompts where both pipelines provided valid numeric data for the metric._\n")

    # --- Detailed Prompt Analysis ---
    report_content.append("\n## 📊 Detailed Prompt-by-Prompt Analysis")
    for p_data in processed_prompts:
        report_content.append(f"\n### Comparison for Prompt: `{p_data['name']}`")

        # Original Text
        report_content.append("\n<details><summary>📜 View Original Input Text</summary>\n\n```text")
        report_content.append(p_data['original_text'])
        report_content.append("```\n</details>\n")

        # LLM Parameters
        report_content.append("<details><summary>⚙️ View LLM Parameters Used</summary>\n")
        report_content.append("**Native LLM Parameters:**\n```json")
        report_content.append(json.dumps(p_data['native_params'], indent=2))
        report_content.append("```\n")
        report_content.append("**LangChain LLM Parameters:**\n```json")
        report_content.append(json.dumps(p_data['lc_params'], indent=2))
        report_content.append("```\n</details>\n")

        # Metrics Table for this prompt
        prompt_metrics_table = ["| Metric                       | Native Value      | Native Bar         | LangChain Value   | LangChain Bar      | Winner           |",
                                "|------------------------------|-------------------|--------------------|-------------------|--------------------|------------------|"]
        for m_conf in METRICS_CONFIG:
            m_id = m_conf['id']
            val_n = p_data['metrics'][m_id]['native']
            val_l = p_data['metrics'][m_id]['lc']
            
            bar_n = generate_comparison_bar(val_n, val_l, BAR_LENGTH, m_conf['lower_is_better'])
            bar_l = generate_comparison_bar(val_l, val_n, BAR_LENGTH, m_conf['lower_is_better'])
            winner = determine_winner(val_n, val_l, m_conf['lower_is_better'])

            prompt_metrics_table.append(
                f"| {m_conf['display']:<28} | "
                f"{format_value(val_n, m_conf['format'], m_conf['unit']):<17} | "
                f"{bar_n:<18} | "
                f"{format_value(val_l, m_conf['format'], m_conf['unit']):<17} | "
                f"{bar_l:<18} | "
                f"{winner:<16} |"
            )
        report_content.extend(prompt_metrics_table)

        # Summaries
        report_content.append("\n<details><summary>📝 View Native Summary</summary>\n\n```text")
        report_content.append(p_data['native_summary'])
        report_content.append("```\n</details>\n")
        report_content.append("<details><summary>📝 View LangChain Summary</summary>\n\n```text")
        report_content.append(p_data['lc_summary'])
        report_content.append("```\n</details>\n")
        report_content.append("\n---")

    # --- Finalize Report ---
    try:
        os.makedirs(args.results_dir, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_content))
        print(f"\n✅ Comparison report successfully generated: {args.output}")
    except Exception as e:
        print(f"\n❌ Error writing report file: {e}")

if __name__ == "__main__":
    main()
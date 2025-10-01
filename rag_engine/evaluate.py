#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Evaluation - Compare retrieval strategies with metrics.

This module evaluates different retrieval modes (vector, keyword, hybrid)
using standard IR metrics:
- Recall@K: Proportion of relevant documents in top-k results
- MRR (Mean Reciprocal Rank): Average of reciprocal ranks of first relevant result
"""

import sys
import os
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

# Añadir el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_engine.hybrid_retriever import HybridRetriever


@dataclass
class QueryEvaluation:
    """Evaluation results for a single query."""
    query_id: int
    query_text: str
    mode: str
    recall_at_5: float
    reciprocal_rank: float
    relevant_found: int
    total_relevant: int
    results_preview: List[str]  # First 100 chars of each result


@dataclass
class EvaluationReport:
    """Aggregate evaluation report for a retrieval mode."""
    mode: str
    total_queries: int
    mean_recall_at_5: float
    mean_reciprocal_rank: float
    queries: List[QueryEvaluation]


def load_test_queries(queries_file: str = "rag_engine/test_queries.json") -> List[Dict]:
    """
    Load test queries from JSON file.

    Args:
        queries_file: Path to queries JSON file

    Returns:
        List of query dictionaries
    """
    if not os.path.exists(queries_file):
        raise FileNotFoundError(f"Queries file not found: {queries_file}")

    with open(queries_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data.get('queries', [])


def calculate_recall_at_k(
    results: List[str],
    relevant_keywords: List[str],
    k: int = 5
) -> tuple[float, int]:
    """
    Calculate Recall@K: proportion of relevant documents in top-k results.

    Uses keyword matching as a proxy for relevance.
    A result is "relevant" if it contains at least one keyword.

    Args:
        results: List of retrieved document contents
        relevant_keywords: List of keywords that indicate relevance
        k: Number of top results to consider

    Returns:
        Tuple of (recall_at_k, relevant_found_count)
    """
    if not results or not relevant_keywords:
        return 0.0, 0

    top_k_results = results[:k]

    # Count how many results contain at least one keyword
    relevant_found = 0
    for result in top_k_results:
        result_lower = result.lower()
        if any(keyword.lower() in result_lower for keyword in relevant_keywords):
            relevant_found += 1

    # Recall = (relevant found in top-k) / (total possible relevant in top-k)
    # Since we don't know total relevant docs in corpus, we use k as denominator
    # This gives us a "coverage" metric
    recall = relevant_found / k if k > 0 else 0.0

    return recall, relevant_found


def calculate_reciprocal_rank(
    results: List[str],
    relevant_keywords: List[str]
) -> float:
    """
    Calculate Reciprocal Rank: 1 / rank of first relevant result.

    Args:
        results: List of retrieved document contents
        relevant_keywords: List of keywords that indicate relevance

    Returns:
        Reciprocal rank (0.0 if no relevant results)
    """
    if not results or not relevant_keywords:
        return 0.0

    for rank, result in enumerate(results, start=1):
        result_lower = result.lower()
        if any(keyword.lower() in result_lower for keyword in relevant_keywords):
            return 1.0 / rank

    return 0.0  # No relevant result found


def evaluate_query(
    retriever: HybridRetriever,
    query: Dict,
    mode: str,
    top_k: int = 5
) -> QueryEvaluation:
    """
    Evaluate a single query with a specific retrieval mode.

    Args:
        retriever: HybridRetriever instance
        query: Query dictionary with 'id', 'query', 'relevant_keywords'
        mode: Retrieval mode ('vector', 'keyword', 'hybrid')
        top_k: Number of results to retrieve

    Returns:
        QueryEvaluation object with metrics
    """
    query_text = query['query']
    relevant_keywords = query.get('relevant_keywords', [])

    # Execute query
    results = retriever.query(query_text, top_k=top_k, mode=mode)

    # Extract content from results
    result_contents = [r.content for r in results]

    # Calculate metrics
    recall, relevant_found = calculate_recall_at_k(result_contents, relevant_keywords, k=top_k)
    reciprocal_rank = calculate_reciprocal_rank(result_contents, relevant_keywords)

    # Create preview (first 100 chars of each result)
    results_preview = [content[:100] + "..." if len(content) > 100 else content
                      for content in result_contents]

    return QueryEvaluation(
        query_id=query['id'],
        query_text=query_text,
        mode=mode,
        recall_at_5=recall,
        reciprocal_rank=reciprocal_rank,
        relevant_found=relevant_found,
        total_relevant=len(relevant_keywords),
        results_preview=results_preview
    )


def evaluate_mode(
    retriever: HybridRetriever,
    queries: List[Dict],
    mode: str,
    top_k: int = 5
) -> EvaluationReport:
    """
    Evaluate all queries with a specific retrieval mode.

    Args:
        retriever: HybridRetriever instance
        queries: List of query dictionaries
        mode: Retrieval mode ('vector', 'keyword', 'hybrid')
        top_k: Number of results to retrieve

    Returns:
        EvaluationReport with aggregate metrics
    """
    query_evaluations = []

    for query in queries:
        try:
            eval_result = evaluate_query(retriever, query, mode, top_k)
            query_evaluations.append(eval_result)
        except Exception as e:
            print(f"[WARNING] Error evaluating query {query['id']}: {e}")
            continue

    # Calculate aggregate metrics
    if query_evaluations:
        mean_recall = sum(q.recall_at_5 for q in query_evaluations) / len(query_evaluations)
        mean_mrr = sum(q.reciprocal_rank for q in query_evaluations) / len(query_evaluations)
    else:
        mean_recall = 0.0
        mean_mrr = 0.0

    return EvaluationReport(
        mode=mode,
        total_queries=len(query_evaluations),
        mean_recall_at_5=mean_recall,
        mean_reciprocal_rank=mean_mrr,
        queries=query_evaluations
    )


def print_evaluation_report(report: EvaluationReport, verbose: bool = False):
    """
    Print evaluation report to console.

    Args:
        report: EvaluationReport object
        verbose: If True, show per-query details
    """
    print(f"\n{'=' * 70}")
    print(f"MODE: {report.mode.upper()}")
    print(f"{'=' * 70}")
    print(f"Total Queries: {report.total_queries}")
    print(f"Mean Recall@5: {report.mean_recall_at_5:.4f}")
    print(f"Mean Reciprocal Rank (MRR): {report.mean_reciprocal_rank:.4f}")

    if verbose:
        print(f"\n{'-' * 70}")
        print("Per-Query Results:")
        print(f"{'-' * 70}")

        for q in report.queries:
            print(f"\nQuery #{q.query_id}: \"{q.query_text}\"")
            print(f"  Recall@5: {q.recall_at_5:.4f} ({q.relevant_found}/5 relevant)")
            print(f"  Reciprocal Rank: {q.reciprocal_rank:.4f}")

            if q.results_preview:
                print(f"  Top result preview: {q.results_preview[0][:80]}...")


def save_evaluation_results(
    reports: List[EvaluationReport],
    output_file: str = "rag_engine/evaluation_results.json"
):
    """
    Save evaluation results to JSON file.

    Args:
        reports: List of EvaluationReport objects
        output_file: Path to output JSON file
    """
    # Convert to dict format (dataclasses to dict)
    results = {
        "evaluation_timestamp": "2025-10-01",
        "modes_evaluated": [r.mode for r in reports],
        "summary": {
            report.mode: {
                "mean_recall_at_5": report.mean_recall_at_5,
                "mean_reciprocal_rank": report.mean_reciprocal_rank,
                "total_queries": report.total_queries
            }
            for report in reports
        },
        "detailed_results": [
            {
                "mode": report.mode,
                "total_queries": report.total_queries,
                "mean_recall_at_5": report.mean_recall_at_5,
                "mean_reciprocal_rank": report.mean_reciprocal_rank,
                "queries": [asdict(q) for q in report.queries]
            }
            for report in reports
        ]
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n[SAVED] Evaluation results saved to: {output_file}")


def compare_modes(reports: List[EvaluationReport]):
    """
    Print comparison table between different modes.

    Args:
        reports: List of EvaluationReport objects
    """
    print(f"\n{'=' * 70}")
    print("COMPARATIVE SUMMARY")
    print(f"{'=' * 70}")
    print(f"{'Mode':<15} {'Recall@5':<15} {'MRR':<15} {'Winner'}")
    print(f"{'-' * 70}")

    # Find best for each metric
    best_recall = max(reports, key=lambda r: r.mean_recall_at_5)
    best_mrr = max(reports, key=lambda r: r.mean_reciprocal_rank)

    for report in reports:
        winner_marks = []
        if report.mode == best_recall.mode:
            winner_marks.append("Best Recall")
        if report.mode == best_mrr.mode:
            winner_marks.append("Best MRR")

        winner_str = ", ".join(winner_marks) if winner_marks else ""

        print(f"{report.mode:<15} {report.mean_recall_at_5:<15.4f} "
              f"{report.mean_reciprocal_rank:<15.4f} {winner_str}")

    print(f"{'=' * 70}")


def main():
    """Main evaluation entry point."""
    print("\n" + "=" * 70)
    print("RAG EVALUATION - Vector vs Keyword vs Hybrid")
    print("=" * 70)

    # Load test queries
    print("\n[1/4] Loading test queries...")
    try:
        queries = load_test_queries()
        print(f"   Loaded {len(queries)} test queries")
    except Exception as e:
        print(f"[ERROR] Failed to load queries: {e}")
        return 1

    # Initialize retriever
    print("\n[2/4] Initializing retriever...")
    retriever = HybridRetriever()
    stats = retriever.get_stats()
    print(f"   Database: {stats['total_documents']} documents")

    if stats['total_documents'] == 0:
        print("\n[ERROR] No documents in database!")
        print("Run ingestion first:")
        print("  python -m rag_engine.rag_cli ingest transcripts_for_rag/sample.txt --mock")
        return 1

    # Evaluate each mode
    print("\n[3/4] Evaluating retrieval modes...")
    modes = ['vector', 'keyword', 'hybrid']
    reports = []

    for mode in modes:
        print(f"\n   Evaluating mode: {mode}...")
        report = evaluate_mode(retriever, queries, mode, top_k=5)
        reports.append(report)

    # Print results
    print("\n[4/4] Results:")
    print("=" * 70)

    for report in reports:
        print_evaluation_report(report, verbose=False)

    # Print comparison
    compare_modes(reports)

    # Save to file
    save_evaluation_results(reports)

    print("\n" + "=" * 70)
    print("[SUCCESS] Evaluation completed!")
    print("=" * 70 + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())

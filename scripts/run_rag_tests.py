#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Test Runner

Comprehensive test runner for the RAG system with modular execution,
performance benchmarking, and detailed reporting.
"""

import sys
import os
import argparse
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class RAGTestRunner:
    """Test runner for RAG system with modular execution and reporting."""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.test_dir = self.project_root / "tests" / "test_rag"
        self.results = {}

    def run_module_tests(self, module: str, verbose: bool = False, coverage: bool = False) -> Dict[str, Any]:
        """
        Run tests for a specific module.

        Args:
            module: Module name (e.g., 'database', 'retriever', 'integration')
            verbose: Enable verbose output
            coverage: Enable coverage reporting

        Returns:
            Dictionary with test results
        """
        module_path = self.test_dir / f"test_{module}"
        if not module_path.exists():
            return {"error": f"Module {module} not found"}

        cmd = [sys.executable, "-m", "pytest", str(module_path)]

        if verbose:
            cmd.append("-v")

        if coverage:
            cmd.extend([
                f"--cov=rag_engine.{module}" if module != "performance" else "--cov=rag_engine",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov"
            ])

        # Add timeout for safety
        cmd.extend(["--timeout=300"])

        print(f"\n{'='*60}")
        print(f"Running {module} tests...")
        print(f"Command: {' '.join(cmd)}")
        print(f"{'='*60}")

        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )

            execution_time = time.time() - start_time

            return {
                "module": module,
                "exit_code": result.returncode,
                "execution_time": execution_time,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }

        except subprocess.TimeoutExpired:
            return {
                "module": module,
                "error": "timeout",
                "execution_time": time.time() - start_time,
                "success": False
            }
        except Exception as e:
            return {
                "module": module,
                "error": str(e),
                "execution_time": time.time() - start_time,
                "success": False
            }

    def run_performance_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run performance-specific tests with benchmarking."""
        performance_dir = self.test_dir / "test_performance"

        if not performance_dir.exists():
            return {"error": "Performance tests not found"}

        cmd = [sys.executable, "-m", "pytest", str(performance_dir), "--benchmark-only"]

        if verbose:
            cmd.append("-v")

        print(f"\n{'='*60}")
        print("Running Performance Benchmarks...")
        print(f"Command: {' '.join(cmd)}")
        print(f"{'='*60}")

        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600
            )

            execution_time = time.time() - start_time

            return {
                "type": "performance",
                "exit_code": result.returncode,
                "execution_time": execution_time,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }

        except subprocess.TimeoutExpired:
            return {
                "type": "performance",
                "error": "timeout",
                "execution_time": time.time() - start_time,
                "success": False
            }
        except Exception as e:
            return {
                "type": "performance",
                "error": str(e),
                "execution_time": time.time() - start_time,
                "success": False
            }

    def run_regression_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run regression tests to validate sqlite-vec optimization."""
        regression_dir = self.test_dir / "test_regression"

        if not regression_dir.exists():
            return {"error": "Regression tests not found"}

        cmd = [sys.executable, "-m", "pytest", str(regression_dir)]

        if verbose:
            cmd.append("-v")

        # Add markers for regression tests
        cmd.extend(["-m", "regression"])

        print(f"\n{'='*60}")
        print("Running Regression Tests...")
        print(f"Command: {' '.join(cmd)}")
        print(f"{'='*60}")

        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )

            execution_time = time.time() - start_time

            return {
                "type": "regression",
                "exit_code": result.returncode,
                "execution_time": execution_time,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }

        except subprocess.TimeoutExpired:
            return {
                "type": "regression",
                "error": "timeout",
                "execution_time": time.time() - start_time,
                "success": False
            }
        except Exception as e:
            return {
                "type": "regression",
                "error": str(e),
                "execution_time": time.time() - start_time,
                "success": False
            }

    def run_critical_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run only critical tests for quick validation."""
        critical_modules = ["database", "retriever"]

        results = {
            "type": "critical",
            "modules": {},
            "overall_success": True,
            "total_time": 0
        }

        start_time = time.time()
        for module in critical_modules:
            result = self.run_module_tests(module, verbose=verbose)
            results["modules"][module] = result
            results["overall_success"] &= result.get("success", False)

        results["total_time"] = time.time() - start_time
        return results

    def run_full_validation(self, verbose: bool = False, coverage: bool = False) -> Dict[str, Any]:
        """Run complete test suite with all modules."""
        all_modules = [
            "database", "embedder", "chunker", "ingestor",
            "retriever", "integration", "performance", "regression"
        ]

        results = {
            "type": "full_validation",
            "modules": {},
            "performance": {},
            "regression": {},
            "overall_success": True,
            "total_time": 0
        }

        start_time = time.time()

        # Run module tests
        for module in all_modules:
            if module in ["performance", "regression"]:
                continue  # Handle separately

            result = self.run_module_tests(module, verbose=verbose, coverage=coverage)
            results["modules"][module] = result
            results["overall_success"] &= result.get("success", False)

        # Run performance tests
        perf_result = self.run_performance_tests(verbose=verbose)
        results["performance"] = perf_result
        results["overall_success"] &= perf_result.get("success", False)

        # Run regression tests
        reg_result = self.run_regression_tests(verbose=verbose)
        results["regression"] = reg_result
        results["overall_success"] &= reg_result.get("success", False)

        results["total_time"] = time.time() - start_time
        return results

    def print_results(self, results: Dict[str, Any]):
        """Print formatted test results."""
        print(f"\n{'='*80}")
        print("RAG TEST RESULTS")
        print(f"{'='*80}")

        if results.get("type") == "full_validation":
            print(f"\nOverall Success: {'✅ PASS' if results['overall_success'] else '❌ FAIL'}")
            print(f"Total Execution Time: {results['total_time']:.2f}s")

            print(f"\n{'-'*60}")
            print("MODULE TESTS:")
            for module, result in results["modules"].items():
                status = "✅ PASS" if result.get("success") else "❌ FAIL"
                time_taken = result.get("execution_time", 0)
                print(f"  {module:15} {status:8} ({time_taken:.2f}s)")

                if not result.get("success") and "error" in result:
                    print(f"    Error: {result['error']}")

            print(f"\n{'-'*60}")
            print("PERFORMANCE TESTS:")
            perf_result = results["performance"]
            status = "✅ PASS" if perf_result.get("success") else "❌ FAIL"
            time_taken = perf_result.get("execution_time", 0)
            print(f"  Performance    {status:8} ({time_taken:.2f}s)")

            print(f"\n{'-'*60}")
            print("REGRESSION TESTS:")
            reg_result = results["regression"]
            status = "✅ PASS" if reg_result.get("success") else "❌ FAIL"
            time_taken = reg_result.get("execution_time", 0)
            print(f"  Regression     {status:8} ({time_taken:.2f}s)")

        elif results.get("type") == "critical":
            print(f"\nCritical Tests: {'✅ PASS' if results['overall_success'] else '❌ FAIL'}")
            print(f"Total Time: {results['total_time']:.2f}s")

            print(f"\n{'-'*60}")
            for module, result in results["modules"].items():
                status = "✅ PASS" if result.get("success") else "❌ FAIL"
                time_taken = result.get("execution_time", 0)
                print(f"  {module:15} {status:8} ({time_taken:.2f}s)")

        else:
            # Single module or performance result
            if "module" in results:
                module = results["module"]
                status = "✅ PASS" if results.get("success") else "❌ FAIL"
                time_taken = results.get("execution_time", 0)
                print(f"{module:15} {status:8} ({time_taken:.2f}s)")
            else:
                test_type = results.get("type", "unknown")
                status = "✅ PASS" if results.get("success") else "❌ FAIL"
                time_taken = results.get("execution_time", 0)
                print(f"{test_type:15} {status:8} ({time_taken:.2f}s)")

        print(f"\n{'='*80}")

    def save_results(self, results: Dict[str, Any], output_file: Optional[str] = None):
        """Save test results to JSON file."""
        if output_file is None:
            timestamp = int(time.time())
            output_file = f"rag_test_results_{timestamp}.json"

        output_path = self.project_root / output_file

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\nResults saved to: {output_path}")
        except Exception as e:
            print(f"\nError saving results: {e}")


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(
        description="RAG Test Runner - Comprehensive testing for RAG system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full validation with coverage
  python run_rag_tests.py --full-validation --coverage

  # Run specific module tests
  python run_rag_tests.py --module database
  python run_rag_tests.py --module retriever

  # Run critical tests only
  python run_rag_tests.py --critical-only

  # Run performance benchmarks
  python run_rag_tests.py --performance-only

  # Run regression tests
  python run_rag_tests.py --regression-only

  # Run with verbose output
  python run_rag_tests.py --full-validation --verbose
        """
    )

    parser.add_argument(
        "--full-validation",
        action="store_true",
        help="Run complete test suite (all modules + performance + regression)"
    )

    parser.add_argument(
        "--module",
        choices=["database", "embedder", "chunker", "ingestor", "retriever", "integration", "performance", "regression"],
        help="Run tests for specific module"
    )

    parser.add_argument(
        "--critical-only",
        action="store_true",
        help="Run only critical tests (database, retriever)"
    )

    parser.add_argument(
        "--performance-only",
        action="store_true",
        help="Run only performance benchmarks"
    )

    parser.add_argument(
        "--regression-only",
        action="store_true",
        help="Run only regression tests"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage reports"
    )

    parser.add_argument(
        "--output", "-o",
        help="Save results to specified JSON file"
    )

    args = parser.parse_args()

    # Validate arguments
    if sum([args.full_validation, args.module is not None, args.critical_only, args.performance_only, args.regression_only]) > 1:
        parser.error("Only one test mode can be specified")

    if not any([args.full_validation, args.module, args.critical_only, args.performance_only, args.regression_only]):
        parser.error("Must specify a test mode (e.g., --full-validation, --module database, --critical-only)")

    runner = RAGTestRunner()

    # Run appropriate tests
    if args.full_validation:
        results = runner.run_full_validation(verbose=args.verbose, coverage=args.coverage)
    elif args.module:
        results = runner.run_module_tests(args.module, verbose=args.verbose, coverage=args.coverage)
    elif args.critical_only:
        results = runner.run_critical_tests(verbose=args.verbose)
    elif args.performance_only:
        results = runner.run_performance_tests(verbose=args.verbose)
    elif args.regression_only:
        results = runner.run_regression_tests(verbose=args.verbose)
    else:
        parser.error("No valid test mode specified")

    # Print results
    runner.print_results(results)

    # Save results if requested
    if args.output:
        runner.save_results(results, args.output)

    # Exit with appropriate code
    exit_code = 0 if results.get("overall_success", results.get("success", False)) else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
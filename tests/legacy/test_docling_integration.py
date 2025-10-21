#!/usr/bin/env python3
"""
Comprehensive tests comparing DocLing vs traditional parsing.

This test suite compares the performance and output quality between
DocLing preprocessing and traditional parsing methods.
"""

import unittest
import time
import os
import tempfile
from typing import Dict, Any, Tuple

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import vtt_to_plain_text_enhanced, is_docling_available
from rag_engine.docling_parser import DocLingParser, create_docling_parser


class TestDocLingIntegration(unittest.TestCase):
    """Test suite for DocLing integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_markdown_content = """# Test Document

This is a test document with multiple sections.

## Section 1

Some content here with **bold text** and *italic text*.

## Section 2

More content with a list:
- Item 1
- Item 2
- Item 3

Final paragraph with some special characters: áéíóú ñ."""

        self.test_vtt_content = """WEBVTT

00:00:00.000 --> 00:00:05.000
Hello world, this is a test subtitle.

00:00:05.000 --> 00:00:10.000
This is the second subtitle with some formatting.

00:00:10.000 --> 00:00:15.000
Final subtitle with special characters: áéíóú."""

        self.test_plain_content = """Simple plain text content.
Multiple lines of text for testing purposes.
This should work with both parsing methods.
Special characters: áéíóú ñ ¿ ¡."""

    def test_docling_availability(self):
        """Test if DocLing is available."""
        available = is_docling_available()
        print(f"\nDocLing availability: {available}")
        # This test passes regardless of DocLing availability
        self.assertIsInstance(available, bool)

    def test_traditional_vs_docling_parsing(self):
        """Compare traditional parsing vs DocLing processing."""
        if not is_docling_available():
            self.skipTest("DocLing not available")

        print("\n=== Testing Traditional vs DocLing Parsing ===")

        # Create temporary files for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(self.test_markdown_content)
            md_file = f.name

        try:
            # Test traditional parsing
            print("\n1. Testing traditional parsing...")
            start_time = time.time()
            traditional_result = self._test_traditional_parse(md_file)
            traditional_time = time.time() - start_time

            # Test DocLing parsing
            print("\n2. Testing DocLing parsing...")
            start_time = time.time()
            docling_result = self._test_docling_parse(md_file)
            docling_time = time.time() - start_time

            # Compare results
            print(f"\n=== Performance Comparison ===")
            print(f"Traditional parsing time: {traditional_time:.3f}s")
            print(f"DocLing parsing time: {docling_time:.3f}s")
            print(f"Performance ratio: {docling_time/traditional_time:.2f}x")

            print(f"\n=== Quality Comparison ===")
            print(f"Traditional content length: {len(traditional_result['content'])} chars")
            print(f"DocLing content length: {len(docling_result['content'])} chars")

            # Verify both methods produced valid content
            self.assertGreater(len(traditional_result['content']), 0)
            self.assertGreater(len(docling_result['content']), 0)
            self.assertTrue(traditional_result['success'])
            self.assertTrue(docling_result['success'])

            # Show sample outputs
            print(f"\n=== Sample Outputs ===")
            print(f"Traditional (first 100 chars): {traditional_result['content'][:100]}...")
            print(f"DocLing (first 100 chars): {docling_result['content'][:100]}...")

        finally:
            # Clean up
            os.unlink(md_file)

    def _test_traditional_parse(self, file_path: str) -> Dict[str, Any]:
        """Test traditional parsing method."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                'content': content,
                'success': True,
                'processor': 'traditional',
                'time': 0
            }
        except Exception as e:
            return {
                'content': None,
                'success': False,
                'error': str(e),
                'processor': 'traditional'
            }

    def _test_docling_parse(self, file_path: str) -> Dict[str, Any]:
        """Test DocLing parsing method."""
        try:
            parser = create_docling_parser()
            result = parser.parse_file(file_path)

            return {
                'content': result['content'],
                'success': result['success'],
                'processor': result['metadata']['processor'],
                'error': result['error'],
                'metadata': result['metadata']
            }
        except Exception as e:
            return {
                'content': None,
                'success': False,
                'error': str(e),
                'processor': 'docling_failed'
            }

    def test_vtt_processing_comparison(self):
        """Test VTT file processing with both methods."""
        if not is_docling_available():
            self.skipTest("DocLing not available")

        print("\n=== Testing VTT Processing ===")

        # Create temporary VTT file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.vtt', delete=False, encoding='utf-8') as f:
            f.write(self.test_vtt_content)
            vtt_file = f.name

        try:
            # Test enhanced VTT parsing (with DocLing fallback)
            with open(vtt_file, 'r', encoding='utf-8') as f:
                vtt_content = f.read()

            # Test with DocLing enabled
            docling_content, docling_meta = vtt_to_plain_text_enhanced(
                vtt_content, vtt_file, use_docling=True
            )

            # Test with DocLing disabled
            traditional_content, traditional_meta = vtt_to_plain_text_enhanced(
                vtt_content, vtt_file, use_docling=False
            )

            print(f"\nVTT Processing Results:")
            print(f"DocLing processor: {docling_meta['processor']}")
            print(f"Traditional processor: {traditional_meta['processor']}")
            print(f"DocLing content length: {len(docling_content)} chars")
            print(f"Traditional content length: {len(traditional_content)} chars")

            # Both should produce content
            self.assertGreater(len(docling_content), 0)
            self.assertGreater(len(traditional_content), 0)

            # Show samples
            print(f"\nDocLing output: {docling_content[:100]}...")
            print(f"Traditional output: {traditional_content[:100]}...")

        finally:
            os.unlink(vtt_file)

    def test_error_handling_and_fallback(self):
        """Test error handling and fallback mechanisms."""
        print("\n=== Testing Error Handling ===")

        # Test with non-existent file
        if is_docling_available():
            result = vtt_to_plain_text_enhanced("nonexistent.txt", "nonexistent.txt", use_docling=True)
            self.assertIsNotNone(result[0])  # Should fallback to traditional
            self.assertEqual(result[1]['processor'], 'traditional_fallback')

        # Test with empty content
        empty_result = vtt_to_plain_text_enhanced("", "", use_docling=True)
        self.assertIsInstance(empty_result[0], str)

    def test_parser_factory_methods(self):
        """Test parser factory and utility methods."""
        print("\n=== Testing Factory Methods ===")

        # Test DocLing parser creation
        if is_docling_available():
            parser = create_docling_parser()
            self.assertIsNotNone(parser)
            self.assertIsInstance(parser, DocLingParser)

            # Test supported formats
            formats = parser.get_supported_formats()
            self.assertIsInstance(formats, set)
            self.assertIn('.md', formats)
            self.assertIn('.vtt', formats)
            print(f"Supported formats: {formats}")

    def test_metadata_preservation(self):
        """Test that metadata is properly preserved."""
        if not is_docling_available():
            self.skipTest("DocLing not available")

        print("\n=== Testing Metadata Preservation ===")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(self.test_markdown_content)
            md_file = f.name

        try:
            parser = create_docling_parser()
            result = parser.parse_file(md_file)

            if result['success']:
                metadata = result['metadata']
                print(f"Metadata keys: {list(metadata.keys())}")
                self.assertIn('processor', metadata)
                self.assertIn('format', metadata)
                self.assertEqual(metadata['processor'], 'docling')

        finally:
            os.unlink(md_file)

    @classmethod
    def run_performance_benchmark(cls):
        """Run performance benchmark tests."""
        print("\n" + "="*60)
        print("DOCILING INTEGRATION PERFORMANCE BENCHMARK")
        print("="*60)

        # Create larger test content
        large_content = cls.test_markdown_content * 50  # Repeat 50 times

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(large_content)
            test_file = f.name

        try:
            if is_docling_available():
                parser = create_docling_parser()

                # Benchmark DocLing
                times = []
                for i in range(5):
                    start = time.time()
                    result = parser.parse_file(test_file)
                    times.append(time.time() - start)

                avg_docling_time = sum(times) / len(times)
                print(f"DocLing average time: {avg_docling_time:.3f}s (5 runs)")

                # Benchmark traditional
                times = []
                for i in range(5):
                    start = time.time()
                    with open(test_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    times.append(time.time() - start)

                avg_traditional_time = sum(times) / len(times)
                print(f"Traditional average time: {avg_traditional_time:.3f}s (5 runs)")

                print(f"Overhead ratio: {avg_docling_time/avg_traditional_time:.2f}x")
            else:
                print("DocLing not available for benchmarking")

        finally:
            os.unlink(test_file)


def run_comparison_tests():
    """Run comprehensive comparison tests."""
    print("Starting DocLing Integration Comparison Tests...")
    print("="*60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDocLingIntegration)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Run performance benchmark
    TestDocLingIntegration.run_performance_benchmark()

    print(f"\nTest Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")

    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\nSuccess rate: {success_rate:.1f}%")

    return success_rate == 100


if __name__ == '__main__':
    success = run_comparison_tests()
    exit(0 if success else 1)
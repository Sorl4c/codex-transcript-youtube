#!/usr/bin/env python3
"""
DocLing parser wrapper for enhanced document processing.

This module provides a wrapper around DocLing for intelligent document
preprocessing, particularly for YouTube transcripts and VTT files.
"""

import os
import tempfile
from typing import Optional, Dict, Any, Union, List
from pathlib import Path

try:
    from docling.document_converter import DocumentConverter
    from docling.datamodel.base_models import InputFormat
    from docling.exceptions import ConversionError
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    # Create dummy classes for type hints when DocLing is not available
    class InputFormat:
        pass


class DocLingParser:
    """Parser wrapper for DocLing document processing."""

    def __init__(self, allowed_formats: Optional[List[InputFormat]] = None):
        """
        Initialize the DocLing parser.

        Args:
            allowed_formats: Optional list of allowed input formats
        """
        if not DOCLING_AVAILABLE:
            raise ImportError(
                "DocLing is not available. Install it with: pip install docling"
            )

        self.converter = DocumentConverter(allowed_formats=allowed_formats)
        self._supported_formats = {
            '.vtt', '.md', '.html', '.pdf', '.docx', '.pptx',
            '.xlsx', '.csv', '.asciidoc', '.json'
        }

    def is_supported_format(self, file_path: str) -> bool:
        """
        Check if file format is supported by DocLing.

        Args:
            file_path: Path to the file to check

        Returns:
            True if format is supported, False otherwise
        """
        ext = Path(file_path).suffix.lower()
        return ext in self._supported_formats

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a file using DocLing.

        Args:
            file_path: Path to the file to parse

        Returns:
            Dictionary containing parsed content and metadata

        Raises:
            ConversionError: If DocLing cannot process the file
            FileNotFoundError: If the file doesn't exist
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not self.is_supported_format(file_path):
            # For unsupported formats, try to convert to markdown temporarily
            return self._parse_unsupported_format(file_path)

        try:
            result = self.converter.convert(file_path)
            document = result.document

            return {
                'content': document.export_to_markdown(),
                'metadata': {
                    'source': file_path,
                    'processor': 'docling',
                    'format': 'markdown',
                    'docling_metadata': getattr(document, 'metadata', {}),
                    'pipeline_info': getattr(result, 'pipeline_info', {}),
                },
                'success': True,
                'error': None
            }
        except ConversionError as e:
            return {
                'content': None,
                'metadata': {
                    'source': file_path,
                    'processor': 'docling',
                    'format': 'error',
                },
                'success': False,
                'error': str(e)
            }

    def _parse_unsupported_format(self, file_path: str) -> Dict[str, Any]:
        """
        Handle unsupported file formats by converting to temporary markdown.

        Args:
            file_path: Path to the unsupported file

        Returns:
            Dictionary with parsed content or fallback data
        """
        try:
            # For plain text files, read directly and wrap in basic markdown
            if file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                return {
                    'content': content,
                    'metadata': {
                        'source': file_path,
                        'processor': 'docling_fallback',
                        'format': 'plain_text',
                        'note': 'Processed as plain text (DocLing fallback)'
                    },
                    'success': True,
                    'error': None
                }

            # For VTT files, we can process them directly since DocLing supports VTT
            elif file_path.endswith('.vtt'):
                result = self.converter.convert(file_path)
                document = result.document

                return {
                    'content': document.export_to_markdown(),
                    'metadata': {
                        'source': file_path,
                        'processor': 'docling',
                        'format': 'vtt',
                        'docling_metadata': getattr(document, 'metadata', {}),
                    },
                    'success': True,
                    'error': None
                }

            else:
                return {
                    'content': None,
                    'metadata': {
                        'source': file_path,
                        'processor': 'docling',
                        'format': 'unsupported',
                    },
                    'success': False,
                    'error': f"Unsupported file format: {Path(file_path).suffix}"
                }

        except Exception as e:
            return {
                'content': None,
                'metadata': {
                    'source': file_path,
                    'processor': 'docling_fallback',
                    'format': 'error',
                },
                'success': False,
                'error': f"Error processing {file_path}: {str(e)}"
            }

    def parse_text(self, text: str, source_name: str = "text_input") -> Dict[str, Any]:
        """
        Parse text content directly by creating a temporary markdown file.

        Args:
            text: Text content to parse
            source_name: Name to use as source in metadata

        Returns:
            Dictionary containing parsed content and metadata
        """
        try:
            # Create temporary markdown file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
                f.write(text)
                temp_path = f.name

            try:
                result = self.converter.convert(temp_path)
                document = result.document

                return {
                    'content': document.export_to_markdown(),
                    'metadata': {
                        'source': source_name,
                        'processor': 'docling',
                        'format': 'markdown',
                        'docling_metadata': getattr(document, 'metadata', {}),
                    },
                    'success': True,
                    'error': None
                }
            finally:
                # Clean up temporary file
                os.unlink(temp_path)

        except Exception as e:
            return {
                'content': text,  # Return original text as fallback
                'metadata': {
                    'source': source_name,
                    'processor': 'docling_fallback',
                    'format': 'plain_text',
                    'note': 'DocLing failed, returned original text'
                },
                'success': False,
                'error': str(e)
            }

    def get_supported_formats(self) -> set:
        """
        Get the set of supported file formats.

        Returns:
            Set of supported file extensions
        """
        return self._supported_formats.copy()

    @staticmethod
    def is_available() -> bool:
        """
        Check if DocLing is available.

        Returns:
            True if DocLing is installed and available, False otherwise
        """
        return DOCLING_AVAILABLE


def create_docling_parser() -> Optional[DocLingParser]:
    """
    Factory function to create a DocLing parser instance.

    Returns:
        DocLingParser instance if DocLing is available, None otherwise
    """
    if DocLingParser.is_available():
        return DocLingParser()
    return None


# Example usage and testing
if __name__ == "__main__":
    # Test if DocLing is available
    if not DocLingParser.is_available():
        print("DocLing is not available. Install with: pip install docling")
        exit(1)

    # Create parser instance
    parser = DocLingParser()

    # Test with existing transcript file
    test_file = "transcripts_for_rag/test_agentic.md"
    if os.path.exists(test_file):
        print(f"Testing with file: {test_file}")
        result = parser.parse_file(test_file)

        if result['success']:
            print("[SUCCESS] Parsing successful!")
            print(f"Content length: {len(result['content'])} chars")
            print(f"Processor: {result['metadata']['processor']}")
            print(f"Format: {result['metadata']['format']}")
            print("\nFirst 200 characters:")
            print(result['content'][:200])
        else:
            print("[FAILED] Parsing failed!")
            print(f"Error: {result['error']}")
    else:
        print(f"Test file not found: {test_file}")

    # Test supported formats
    print(f"\nSupported formats: {parser.get_supported_formats()}")
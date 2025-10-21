"""
Parser module for processing VTT subtitle files into plain text.

Supports both traditional parsing and enhanced DocLing preprocessing.
"""
import re
from typing import Iterator, Optional, Dict, Any

def vtt_to_plain_text_stream(vtt_lines_iterator: Iterator[str], remove_timestamps: bool = True) -> Iterator[str]:
    """
    Cleans VTT content from an iterator and yields plain text lines.
    This is memory-efficient as it processes the file line by line.

    TODO: Consider separating filtering responsibilities into distinct classes for better
    maintainability and extensibility (e.g., TimestampFilter, MetadataFilter, StyleFilter).

    Args:
        vtt_lines_iterator: Iterator over VTT lines
        remove_timestamps: If True, removes timestamp lines (default: True for backward compatibility)
    """
    last_line = None
    for line in vtt_lines_iterator:
        line = line.strip()
        
        # Skip metadata, timestamps, style blocks, empty lines, and VTT headers
        timestamp_condition = '-->' in line if remove_timestamps else False
        if (
            line.startswith('WEBVTT') or
            timestamp_condition or
            line.startswith('::cue') or
            line.startswith('STYLE') or
            not line or
            line.isdigit() or
            line.startswith('Kind:') or
            line.startswith('Language:')
        ):
            continue
            
        # Clean the line from any remaining HTML-like tags
        clean_line = re.sub(r'<[^>]+>', '', line).strip()
        
        # Avoid duplicate consecutive lines
        if clean_line and clean_line != last_line:
            last_line = clean_line
            yield clean_line

def vtt_to_plain_text(vtt_content: str, remove_timestamps: bool = True) -> str:
    """
    Cleans VTT content from a string and returns a single plain text string.
    Uses the streaming parser internally for consistent logic.

    TODO: Consider creating a VTTProcessor class that encapsulates different parsing
    strategies and maintains state for better extensibility.

    Args:
        vtt_content: VTT content as string
        remove_timestamps: If True, removes timestamp lines (default: True for backward compatibility)

    Returns:
        Plain text content with or without timestamps depending on the parameter
    """
    lines_iterator = iter(vtt_content.strip().split('\n'))
    return "\n".join(vtt_to_plain_text_stream(lines_iterator, remove_timestamps))

def format_transcription(text: str, title: str = None, url: str = None) -> str:
    """
    Añade un encabezado al texto y formatea el cuerpo de la transcripción.
    Une todas las líneas de subtítulos en un único párrafo separado por espacios.
    """
    encabezado = ""
    if title:
        encabezado += f"Título: {title}\n"
    if url:
        encabezado += f"URL: {url}\n"
    if encabezado:
        encabezado += "\n"

    # Une todas las líneas en un solo bloque de texto separado por espacios.
    cuerpo = " ".join(linea.strip() for linea in text.splitlines() if linea.strip())

    # Eliminar espacios múltiples que puedan haber quedado
    cuerpo = re.sub(r'\s+', ' ', cuerpo).strip()

    return encabezado + cuerpo


# DocLing integration
try:
    from rag_engine.docling_parser import DocLingParser, create_docling_parser
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False


def parse_with_docling(file_path: str, use_docling: bool = True) -> Dict[str, Any]:
    """
    Parse file using DocLing if available and enabled.

    Args:
        file_path: Path to the file to parse
        use_docling: Whether to use DocLing if available

    Returns:
        Dictionary with parsing results and metadata
    """
    if not use_docling or not DOCLING_AVAILABLE:
        return {
            'content': None,
            'metadata': {
                'processor': 'traditional',
                'reason': 'DocLing disabled or unavailable'
            },
            'success': False
        }

    try:
        parser = create_docling_parser()
        if parser is None:
            return {
                'content': None,
                'metadata': {
                    'processor': 'traditional',
                    'reason': 'DocLing parser creation failed'
                },
                'success': False
            }

        result = parser.parse_file(file_path)
        return result

    except Exception as e:
        return {
            'content': None,
            'metadata': {
                'processor': 'traditional',
                'reason': f'DocLing error: {str(e)}'
            },
            'success': False
        }


def vtt_to_plain_text_enhanced(vtt_content: str, file_path: str = None, use_docling: bool = True) -> tuple[str, Dict[str, Any]]:
    """
    Enhanced VTT parsing with DocLing support.

    Args:
        vtt_content: VTT content as string
        file_path: Optional file path for DocLing processing
        use_docling: Whether to use DocLing if available

    Returns:
        Tuple of (plain_text, metadata_dict)
    """
    metadata = {'processor': 'traditional', 'use_docling': use_docling}

    # Try DocLing first if enabled and file_path is provided
    if use_docling and DOCLING_AVAILABLE and file_path:
        docling_result = parse_with_docling(file_path, use_docling)
        if docling_result['success']:
            # DocLing succeeded, return its results
            metadata.update(docling_result['metadata'])
            return docling_result['content'], metadata
        else:
            # DocLing failed, note the reason and fall back
            metadata['docling_error'] = docling_result['metadata'].get('reason', 'Unknown error')
            metadata['processor'] = 'traditional_fallback'

    # Fall back to traditional parsing
    plain_text = vtt_to_plain_text(vtt_content)
    return plain_text, metadata


def is_docling_available() -> bool:
    """
    Check if DocLing is available.

    Returns:
        True if DocLing is installed and available, False otherwise
    """
    return DOCLING_AVAILABLE

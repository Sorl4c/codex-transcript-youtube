"""
Parser module for processing VTT subtitle files into plain text.
"""
import re
from typing import Iterator, Optional

def vtt_to_plain_text_stream(vtt_lines_iterator: Iterator[str]) -> Iterator[str]:
    """
    Cleans VTT content from an iterator and yields plain text lines.
    This is memory-efficient as it processes the file line by line.
    """
    last_line = None
    for line in vtt_lines_iterator:
        line = line.strip()
        
        # Skip metadata, timestamps, style blocks, empty lines, and VTT headers
        if (
            line.startswith('WEBVTT') or
            '-->' in line or
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

def vtt_to_plain_text(vtt_content: str) -> str:
    """
    Cleans VTT content from a string and returns a single plain text string.
    Uses the streaming parser internally for consistent logic.
    """
    lines_iterator = iter(vtt_content.strip().split('\n'))
    return "\n".join(vtt_to_plain_text_stream(lines_iterator))

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

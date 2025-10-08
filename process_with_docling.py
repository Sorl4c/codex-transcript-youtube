#!/usr/bin/env python3
"""
Script para procesar archivos con DocLing sin almacenar en la base de datos.
Solo para ver el resultado del preprocesamiento de DocLing.
"""

import os
import sys
import json
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from rag_engine.docling_parser import DocLingParser, create_docling_parser
    from parser import is_docling_available, parse_with_docling
    DOCLING_AVAILABLE = is_docling_available()
except ImportError as e:
    print(f"Error importing modules: {e}")
    DOCLING_AVAILABLE = False

def process_file_with_docling(input_file_path: str, output_file_path: str) -> Dict[str, Any]:
    """
    Procesa un archivo con DocLing y guarda el resultado completo.

    Args:
        input_file_path: Ruta al archivo de entrada
        output_file_path: Ruta donde guardar el resultado

    Returns:
        Diccionario con información del procesamiento
    """

    print("=== PROCESAMIENTO CON DOCLING ===")
    print(f"Archivo de entrada: {input_file_path}")
    print(f"Archivo de salida: {output_file_path}")
    print(f"DocLing disponible: {DOCLING_AVAILABLE}")

    if not DOCLING_AVAILABLE:
        print("ERROR: DocLing no está disponible")
        return {"success": False, "error": "DocLing no disponible"}

    # Verificar que el archivo de entrada existe
    if not os.path.exists(input_file_path):
        print(f"ERROR: El archivo {input_file_path} no existe")
        return {"success": False, "error": "Archivo no encontrado"}

    try:
        print("\n1. Creando parser DocLing...")
        parser = create_docling_parser()

        print("2. Procesando archivo con DocLing...")
        result = parser.parse_file(input_file_path)

        if result['success']:
            print("SUCCESS: Procesamiento exitoso!")

            # Extraer información
            content = result['content']
            metadata = result['metadata']

            print(f"3. Estadísticas del procesamiento:")
            print(f"   - Longitud del contenido: {len(content)} caracteres")
            print(f"   - Processor: {metadata.get('processor', 'unknown')}")
            print(f"   - Formato detectado: {metadata.get('format', 'unknown')}")

            # Mostrar metadata disponible
            if 'docling_metadata' in metadata:
                docling_meta = metadata['docling_metadata']
                print(f"   - Pipeline info: {docling_meta.get('pipeline_info', {}).get('pipeline_name', 'N/A')}")
                print(f"   - Tiempo de procesamiento: {docling_meta.get('processing_stats', {}).get('total_time', 'N/A')}s")

            # Preparar resultado completo para guardar
            output_data = {
                "processing_info": {
                    "input_file": input_file_path,
                    "output_file": output_file_path,
                    "processor": "docling",
                    "timestamp": os.path.getmtime(input_file_path)
                },
                "metadata": metadata,
                "content": content,
                "statistics": {
                    "char_count": len(content),
                    "word_count": len(content.split()),
                    "line_count": len(content.split('\n'))
                }
            }

            # Guardar resultado en formato JSON
            print(f"4. Guardando resultado en: {output_file_path}")
            with open(output_file_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            # También guardar versión solo texto para fácil lectura
            txt_output_path = output_file_path.replace('.json', '_texto.txt')
            with open(txt_output_path, 'w', encoding='utf-8') as f:
                f.write("=== CONTENIDO PROCESADO CON DOCLING ===\n\n")
                f.write(f"Archivo original: {input_file_path}\n")
                f.write(f"Processor: {metadata.get('processor', 'unknown')}\n")
                f.write(f"Formato: {metadata.get('format', 'unknown')}\n")
                f.write(f"Longitud: {len(content)} caracteres\n\n")
                f.write("=== CONTENIDO ===\n\n")
                f.write(content)

            print(f"SUCCESS: Resultado guardado en:")
            print(f"   - JSON: {output_file_path}")
            print(f"   - Texto: {txt_output_path}")

            return {
                "success": True,
                "content": content,
                "metadata": metadata,
                "output_files": [output_file_path, txt_output_path]
            }

        else:
            print(f"ERROR: Error en procesamiento: {result.get('error', 'Error desconocido')}")
            return {"success": False, "error": result.get('error', 'Error desconocido')}

    except Exception as e:
        print(f"ERROR: Error durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

def compare_with_original(input_file_path: str, docling_content: str):
    """
    Compara el contenido procesado con el archivo original.
    """
    print("\n=== COMPARACIÓN CON ORIGINAL ===")

    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        original_stats = {
            "char_count": len(original_content),
            "word_count": len(original_content.split()),
            "line_count": len(original_content.split('\n'))
        }

        docling_stats = {
            "char_count": len(docling_content),
            "word_count": len(docling_content.split()),
            "line_count": len(docling_content.split('\n'))
        }

        print(f"Estadísticas archivo original:")
        print(f"  - Caracteres: {original_stats['char_count']}")
        print(f"  - Palabras: {original_stats['word_count']}")
        print(f"  - Líneas: {original_stats['line_count']}")

        print(f"\nEstadísticas procesado DocLing:")
        print(f"  - Caracteres: {docling_stats['char_count']}")
        print(f"  - Palabras: {docling_stats['word_count']}")
        print(f"  - Líneas: {docling_stats['line_count']}")

        # Calcular diferencias
        char_diff = docling_stats['char_count'] - original_stats['char_count']
        word_diff = docling_stats['word_count'] - original_stats['word_count']

        print(f"\nDiferencias:")
        print(f"  - Caracteres: {char_diff:+d}")
        print(f"  - Palabras: {word_diff:+d}")

        return {
            "original": original_stats,
            "docling": docling_stats,
            "differences": {"chars": char_diff, "words": word_diff}
        }

    except Exception as e:
        print(f"Error en comparación: {e}")
        return None

if __name__ == "__main__":
    # Archivo a procesar - CAMBIAR AQUÍ para probar diferentes archivos
    input_file = "transcripts_for_rag/texto_mal_formateado_test.txt"

    # Directorio de salida
    output_dir = "transcripts_for_rag/docling"
    os.makedirs(output_dir, exist_ok=True)

    # Nombre del archivo de salida
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_dir, f"{base_name}_docling.json")

    print(f"Procesando archivo: {input_file}")
    print(f"Directorio de salida: {output_dir}")

    # Procesar con DocLing
    result = process_file_with_docling(input_file, output_file)

    if result['success']:
        print("\n" + "="*60)
        print("SUCCESS: PROCESAMIENTO COMPLETADO CON ÉXITO")
        print("="*60)

        # Mostrar preview del contenido
        content = result['content']
        print(f"\nPreview del contenido procesado (primeros 500 caracteres):")
        print("-" * 50)
        print(content[:500])
        print("-" * 50)

        # Comparar con original
        comparison = compare_with_original(input_file, content)

        print(f"\nArchivos generados:")
        for file_path in result['output_files']:
            print(f"  - {file_path}")

        # Mostrar información específica para markdown
        if 'markdown' in input_file.lower():
            print(f"\n=== ANÁLISIS DE FORMATEO MARKDOWN ===")
            print(f"Formato detectado: {result['metadata'].get('format', 'unknown')}")
            print(f"Processor: {result['metadata'].get('processor', 'unknown')}")

            # Buscar elementos de markdown en el contenido
            has_headers = '#' in content
            has_lists = '*' in content or '-' in content or '1.' in content
            has_code = '`' in content
            has_links = '[' in content and '](' in content
            has_tables = '|' in content

            print(f"Elementos detectados en el resultado:")
            print(f"  - Headers (títulos): {'Sí' if has_headers else 'No'}")
            print(f"  - Listas: {'Sí' if has_lists else 'No'}")
            print(f"  - Código: {'Sí' if has_code else 'No'}")
            print(f"  - Enlaces: {'Sí' if has_links else 'No'}")
            print(f"  - Tablas: {'Sí' if has_tables else 'No'}")

    else:
        print("\n" + "="*60)
        print("ERROR: ERROR EN EL PROCESAMIENTO")
        print("="*60)
        print(f"Error: {result.get('error', 'Error desconocido')}")
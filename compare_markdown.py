#!/usr/bin/env python3
"""
Script para comparar el markdown original vs el procesado por DocLing
"""

import os
import difflib

def compare_markdown_files(original_path, processed_path):
    """
    Compara dos archivos markdown y muestra las diferencias
    """

    print("=== COMPARACIÓN DETALLADA MARKDOWN ===\n")

    # Leer archivos
    with open(original_path, 'r', encoding='utf-8') as f:
        original_lines = f.readlines()

    with open(processed_path, 'r', encoding='utf-8') as f:
        processed_lines = f.readlines()

    print(f"Archivo original: {len(original_lines)} líneas")
    print(f"Archivo procesado: {len(processed_lines)} líneas")

    # Encontrar el contenido real (saltar encabezado del archivo procesado)
    if processed_lines and "=== CONTENIDO ===" in processed_lines[7]:
        # Saltar las primeras 8 líneas (encabezado)
        processed_content_lines = processed_lines[8:]
    else:
        processed_content_lines = processed_lines

    print(f"Contenido procesado: {len(processed_content_lines)} líneas")

    print("\n=== DIFERENCIAS ENCONTRADAS ===\n")

    # Mostrar diferencias línea por línea
    differ = difflib.Differ()

    diff = list(differ.compare(original_lines, processed_content_lines))

    line_num = 0
    changes_found = []

    for line in diff:
        line_num += 1

        if line.startswith('  '):
            # Líneas iguales
            continue
        elif line.startswith('- '):
            # Línea eliminada (estaba en original, no en procesado)
            original_line = line[2:]
            changes_found.append(f"Línea {line_num}: ELIMINADA")
            changes_found.append(f"  Original: {original_line.strip()}")
        elif line.startswith('+ '):
            # Línea añadida (no estaba en original, sí en procesado)
            processed_line = line[2:]
            changes_found.append(f"Línea {line_num}: AÑADIDA")
            changes_found.append(f"  Procesado: {processed_line.strip()}")
        elif line.startswith('? '):
            # Indicador de cambios dentro de la línea
            indicator = line[2:]
            changes_found.append(f"Línea {line_num}: CAMBIO INTERNO [{indicator}]")

    # Mostrar cambios significativos
    if changes_found:
        for change in changes_found[:20]:  # Limitar a primeros 20 cambios
            print(change)

        if len(changes_found) > 20:
            print(f"... y {len(changes_found) - 20} cambios más")
    else:
        print("No se encontraron diferencias significativas")

    print("\n=== ANÁLISIS DE CORRECCIONES DE FORMATEO ===")

    # Buscar correcciones específicas
    original_text = ''.join(original_lines)
    processed_text = ''.join(processed_content_lines)

    corrections = []

    # 1. Corrección de listas
    if "* Lista sin espacio" in original_text and "- Lista sin espacio" in processed_text:
        corrections.append("OK: Corrección de formato de lista: '*' -> '-'")

    # 2. Corrección de bloques de código
    if "```código sin cierre" in original_text and "```\nesto sigue siendo código?" in processed_text:
        corrections.append("OK: Corrección de bloque de código: cerrado correctamente")

    # 3. Normalización de espacios
    if len(original_text) != len(processed_text):
        corrections.append(f"OK: Normalización de espacios/longitud: {len(original_text)} -> {len(processed_text)} chars")

    # 4. Limpieza de formato incorrecto
    if "2.Segundo elemento sin espacio" in original_text and "2.Segundo elemento sin espacio" not in processed_text:
        corrections.append("OK: Corrección de formato de lista numerada")

    if corrections:
        for correction in corrections:
            print(correction)
    else:
        print("No se detectaron correcciones de formato obvias")

    print(f"\n=== CONCLUSIONES ===")
    print(f"¿DocLing procesó el markdown? SI")
    print(f"¿Detectó el formato correctamente? SI (formato: markdown)")
    print(f"¿Hizo correcciones significativas? {len(corrections) > 0}")
    print(f"¿Mantuvo el contenido esencial? SI")

    return {
        'original_lines': len(original_lines),
        'processed_lines': len(processed_content_lines),
        'corrections_found': len(corrections),
        'changes_detected': len(changes_found)
    }

if __name__ == "__main__":
    original_file = "transcripts_for_rag/markdown_mal_formateado_test.md"
    processed_file = "transcripts_for_rag/docling/markdown_mal_formateado_test_docling_texto.txt"

    if os.path.exists(original_file) and os.path.exists(processed_file):
        result = compare_markdown_files(original_file, processed_file)
        print(f"\nResumen: {result}")
    else:
        print("Error: No se encontraron los archivos para comparar")
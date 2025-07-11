#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script para demostrar las diferentes estrategias de chunking
Ejecutar: python rag_engine/test_chunking_strategies.py
"""

import sys
import os

# Configurar encoding para Windows
if sys.platform.startswith('win'):
    os.system('chcp 65001 >nul 2>&1')  # UTF-8

# Añadir el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag_engine.chunker import TextChunker, chunk_text
from rag_engine.logger import logger, set_debug_mode

# Activar modo debug para las pruebas
set_debug_mode(True)

def test_chunking_strategies():
    """Prueba todas las estrategias de chunking con texto de ejemplo"""
    
    # Texto de ejemplo con estructura clara
    sample_text = """
Capítulo 1: Introducción a la Inteligencia Artificial

La inteligencia artificial (IA) es una rama de la informática que se ocupa de la creación de sistemas capaces de realizar tareas que normalmente requieren inteligencia humana. Estos sistemas pueden aprender, razonar, percibir y tomar decisiones.

Historia de la IA

Los primeros conceptos de inteligencia artificial se remontan a la antigüedad, pero el campo moderno comenzó en la década de 1950. Alan Turing propuso el famoso "Test de Turing" como una forma de evaluar si una máquina puede exhibir comportamiento inteligente.

En 1956, John McCarthy acuñó el término "inteligencia artificial" durante la Conferencia de Dartmouth. Este evento se considera el nacimiento oficial del campo de la IA.

Tipos de Inteligencia Artificial

Existen diferentes tipos de IA según su capacidad y funcionalidad:

1. IA Débil (Narrow AI): Sistemas diseñados para realizar tareas específicas, como reconocimiento de voz o juegos.

2. IA General (AGI): Sistemas con capacidades cognitivas similares a las humanas, capaces de entender y aprender cualquier tarea intelectual.

3. Superinteligencia: IA que supera la inteligencia humana en todos los aspectos.

Aplicaciones Actuales

La IA se utiliza en numerosos campos:
- Medicina: Diagnóstico por imágenes, descubrimiento de fármacos
- Transporte: Vehículos autónomos, optimización de rutas
- Finanzas: Detección de fraudes, trading algorítmico
- Entretenimiento: Recomendaciones personalizadas, generación de contenido

Desafíos y Consideraciones Éticas

El desarrollo de la IA plantea importantes desafíos éticos y sociales. Es crucial considerar temas como la privacidad, el sesgo algorítmico, el impacto en el empleo y la responsabilidad de las decisiones automatizadas.
"""

    print("[TEST] PRUEBA DE ESTRATEGIAS DE CHUNKING")
    print("=" * 50)
    
    strategies = ['caracteres', 'palabras', 'semantico', 'agentic']
    chunk_size = 500
    chunk_overlap = 100
    
    for strategy in strategies:
        print(f"\n[ESTRATEGIA] {strategy.upper()}")
        print("-" * 30)
        
        try:
            # Usar función de conveniencia
            chunks = chunk_text(sample_text, strategy=strategy, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            
            print(f"[OK] Chunks generados: {len(chunks)}")
            print(f"[INFO] Tamaño promedio: {sum(len(c.content) for c in chunks) / len(chunks):.1f} caracteres")
            
            # Mostrar información de metadatos si está disponible
            if chunks and hasattr(chunks[0], 'metadata'):
                print(f"[INFO] Primer chunk: chars {chunks[0].metadata.char_start_index}-{chunks[0].metadata.char_end_index}")
                if len(chunks) > 1:
                    print(f"[INFO] Último chunk: chars {chunks[-1].metadata.char_start_index}-{chunks[-1].metadata.char_end_index}")
            
            # Mostrar primeros 2 chunks como ejemplo
            for i, chunk in enumerate(chunks[:2]):
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                print(f"\n[CHUNK] {i+1} ({len(content)} chars):")
                if hasattr(chunk, 'metadata'):
                    print(f"   Rango: {chunk.metadata.char_start_index}-{chunk.metadata.char_end_index}")
                preview = content.strip()[:150] + "..." if len(content) > 150 else content.strip()
                print(f"   {preview}")
                
            if len(chunks) > 2:
                print(f"   ... y {len(chunks) - 2} chunks más")
                
        except Exception as e:
            print(f"[ERROR] Error con estrategia {strategy}: {str(e)}")
    
    print("\n" + "=" * 50)
    print("[COMPARACION] ESTRATEGIAS")
    print("=" * 50)
    
    # Comparar todas las estrategias
    results = {}
    for strategy in strategies:
        try:
            chunks = chunk_text(sample_text, strategy=strategy, chunk_size=chunk_size)
            results[strategy] = {
                'count': len(chunks),
                'avg_size': sum(len(c.content if hasattr(c, 'content') else str(c)) for c in chunks) / len(chunks),
                'total_chars': sum(len(c.content if hasattr(c, 'content') else str(c)) for c in chunks)
            }
        except Exception as e:
            results[strategy] = {'error': str(e)}
    
    # Mostrar tabla comparativa
    print(f"{'Estrategia':<12} {'Chunks':<8} {'Promedio':<10} {'Total':<8}")
    print("-" * 40)
    
    for strategy, data in results.items():
        if 'error' in data:
            print(f"{strategy:<12} {'ERROR':<8} {'-':<10} {'-':<8}")
        else:
            print(f"{strategy:<12} {data['count']:<8} {data['avg_size']:<10.1f} {data['total_chars']:<8}")

def test_dynamic_strategy_change():
    """Prueba el cambio dinámico de estrategias"""
    print("\n[DINAMICO] PRUEBA DE CAMBIO DE ESTRATEGIA")
    print("=" * 50)
    
    text = "Este es un texto de prueba. Tiene varias frases. Cada frase tiene un propósito específico para probar el chunking."
    
    # Crear chunker con estrategia inicial
    chunker = TextChunker(chunk_size=50, chunk_overlap=10, strategy='caracteres')
    
    strategies = ['caracteres', 'palabras', 'semantico']
    
    for strategy in strategies:
        chunker.set_strategy(strategy)
        chunks = chunker.chunk(text)
        print(f"\n[{strategy.upper()}] {len(chunks)} chunks")
        for i, chunk in enumerate(chunks):
            content = chunk.content if hasattr(chunk, 'content') else str(chunk)
            range_info = f" ({chunk.metadata.char_start_index}-{chunk.metadata.char_end_index})" if hasattr(chunk, 'metadata') else ""
            print(f"   {i+1}{range_info}: '{content.strip()}'")

if __name__ == "__main__":
    print("[INICIO] Ejecutando pruebas de chunking con logging activado")
    logger.info("Iniciando pruebas de estrategias de chunking")
    
    test_chunking_strategies()
    test_dynamic_strategy_change()
    
    print("\n[COMPLETADO] Pruebas terminadas! Ahora puedes probar la GUI:")
    print("   python rag_engine/chunking_playground.py")
    logger.info("Pruebas completadas exitosamente")

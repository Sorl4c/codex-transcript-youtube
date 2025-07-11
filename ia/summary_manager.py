"""
Módulo para gestionar la generación y actualización de resúmenes.

Este módulo proporciona funciones para generar resúmenes de transcripciones
y actualizarlos en la base de datos.
"""

import os
import sys
from typing import Optional, Dict, Any

# Asegurarse de que el directorio padre esté en el path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_video_by_id, update_video_summary
from ia.ia_processor import cargar_modelo_llm, resumir_texto

# Variable para almacenar la instancia del modelo
_llm_instance = None

def get_or_load_model():
    """
    Obtiene la instancia del modelo, cargándola si es necesario.
    
    Returns:
        Instancia del modelo o None si hay un error.
    """
    global _llm_instance
    if _llm_instance is None:
        try:
            _llm_instance = cargar_modelo_llm()
        except Exception as e:
            print(f"Error al cargar el modelo: {e}")
            return None
    return _llm_instance

def generate_and_save_summary(video_id: int) -> Dict[str, Any]:
    """
    Genera un resumen para un video y lo guarda en la base de datos.
    
    Args:
        video_id: ID del video para el que generar el resumen.
        
    Returns:
        Dict con el estado de la operación y el resumen generado (si hubo éxito).
    """
    # Obtener los datos del video
    video_data = get_video_by_id(video_id)
    if not video_data:
        return {"success": False, "error": f"No se encontró el video con ID {video_id}"}
    
    # Verificar que el video tenga transcripción
    transcript = video_data.get('transcript')
    if not transcript or not transcript.strip():
        return {"success": False, "error": "El video no tiene transcripción disponible"}
    
    # Cargar el modelo
    llm = get_or_load_model()
    if not llm:
        return {"success": False, "error": "No se pudo cargar el modelo de lenguaje"}
    
    try:
        # Generar el resumen
        summary = resumir_texto(llm, transcript)
        
        # Verificar que se generó un resumen válido
        if not summary or "Error" in summary:
            return {"success": False, "error": f"Error al generar el resumen: {summary}"}
        
        # Guardar en la base de datos
        success = update_video_summary(video_id, summary)
        if not success:
            return {"success": False, "error": "No se pudo guardar el resumen en la base de datos"}
        
        return {
            "success": True,
            "video_id": video_id,
            "summary": summary,
            "title": video_data.get('title', 'Sin título')
        }
        
    except Exception as e:
        return {"success": False, "error": f"Error inesperado: {str(e)}"}

def batch_update_summaries(video_ids=None):
    """
    Actualiza los resúmenes para múltiples videos.
    
    Args:
        video_ids: Lista de IDs de video. Si es None, se procesan todos los videos.
        
    Returns:
        Lista de resultados para cada video procesado.
    """
    results = []
    
    # Si no se proporcionan IDs, obtener todos los videos
    if video_ids is None:
        # Importación local para evitar dependencia circular
        from db import get_all_videos
        videos = get_all_videos()
        video_ids = [v['id'] for v in videos]
    
    # Procesar cada video
    for vid in video_ids:
        print(f"\nProcesando video ID: {vid}")
        result = generate_and_save_summary(vid)
        results.append({"video_id": vid, "result": result})
    
    return results


if __name__ == "__main__":
    # Ejemplo de uso
    import argparse
    
    parser = argparse.ArgumentParser(description='Generar resúmenes para videos.')
    parser.add_argument('--video-id', type=int, help='ID del video a procesar')
    parser.add_argument('--all', action='store_true', help='Procesar todos los videos')
    
    args = parser.parse_args()
    
    if args.video_id:
        # Procesar un video específico
        result = generate_and_save_summary(args.video_id)
        print("\nResultado:", result)
    elif args.all:
        # Procesar todos los videos
        print("Iniciando actualización de resúmenes para todos los videos...")
        results = batch_update_summaries()
        print("\nResumen de resultados:")
        for r in results:
            status = "✓" if r["result"].get("success") else "✗"
            print(f"{status} Video {r['video_id']}: {r['result'].get('error', 'Éxito')}")
    else:
        print("Debe especificar --video-id o --all")

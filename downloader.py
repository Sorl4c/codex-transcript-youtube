"""
Module for downloading VTT subtitles from YouTube videos using yt-dlp.
"""
import os
import sys
import yt_dlp
from typing import Optional, Tuple, Dict, Any

def get_available_languages(info: Dict[str, Any]) -> list:
    """Extrae y unifica la lista de idiomas de subtítulos disponibles.

    Combina los subtítulos subidos manualmente y los generados automáticamente,
    eliminando duplicados y entradas no deseadas como 'live_chat'.

    Args:
        info (Dict[str, Any]): El diccionario de información del vídeo extraído por yt-dlp.

    Returns:
        list: Una lista ordenada de los códigos de idioma disponibles (ej. ['en', 'es']).
    """
    available_langs = []
    if 'subtitles' in info:
        available_langs.extend(info['subtitles'].keys())
    if 'automatic_captions' in info:
        available_langs.extend(info['automatic_captions'].keys())
    # Remove duplicates and 'live_chat'
    return sorted(list(set(lang for lang in available_langs if lang != 'live_chat')))

def download_vtt(url: str, lang: str = 'es') -> Tuple[Optional[str], Optional[str], Optional[Dict[str, Any]]]:
    """Descarga los subtítulos de un vídeo de YouTube en formato VTT.

    El proceso se divide en tres fases:
    1. Obtiene la información del vídeo para listar los idiomas disponibles.
    2. Selecciona el mejor idioma para descargar, con una lógica de fallback:
       - Intenta descargar el idioma solicitado (`lang`).
       - Si no está disponible, intenta con inglés ('en').
       - Si tampoco está, usa el primer idioma de la lista.
    3. Descarga el archivo VTT, lo lee en memoria y lo elimina del disco.

    Args:
        url (str): La URL del vídeo de YouTube.
        lang (str): El código de idioma preferido para los subtítulos (ej. 'es', 'en').

    Returns:
        Tuple[Optional[str], Optional[str], Optional[Dict[str, Any]]]: Una tupla con:
        - El contenido de los subtítulos en formato VTT.
        - El código del idioma que finalmente se descargó.
        - Un diccionario con metadatos básicos del vídeo (título, canal, etc.).
        O (None, None, None) si ocurre un error.
    """
    # 1. Get video info to check for available subtitles
    try:
        with yt_dlp.YoutubeDL({'skip_download': True, 'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        print(f"[ERROR] No se pudo obtener la información del video: {e}")
        return None, None, None

    if not info:
        print("[ERROR] No se encontró información del video.")
        return None, None, None

    video_title = info.get('title', 'Título no disponible')
    try:
        print(f"\n[VIDEO] {video_title}")
        available_langs = get_available_languages(info)
        print(f"[IDIOMAS DISPONIBLES] {', '.join(available_langs) if available_langs else 'Ninguno'}")
    except Exception:
        # Fallback for weird characters in title
        print("\n[INFO] Video encontrado.")
        available_langs = get_available_languages(info)

    # 2. Decide which language to download
    lang_to_download = None
    if lang in available_langs:
        lang_to_download = lang
        print(f"[INFO] Subtítulos encontrados para el idioma solicitado: '{lang}'")
    else:
        print(f"[WARN] No se encontraron subtítulos para '{lang}'.")
        # Fallback to English if available, otherwise the first one
        if 'en' in available_langs:
            lang_to_download = 'en'
            print(f"[INFO] Usando idioma de respaldo: 'en'")
        elif available_langs:
            lang_to_download = available_langs[0]
            print(f"[INFO] Usando primer idioma disponible como respaldo: '{lang_to_download}'")
        else:
            print("[ERROR] No hay subtítulos disponibles para descargar.")
            return None, None, None

    # 3. Download only the selected subtitle language
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    video_id = info.get('id', 'video')
    temp_file_base = os.path.join(temp_dir, f'{video_id}')
    expected_file_path = f'{temp_file_base}.{lang_to_download}.vtt'

    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': [lang_to_download],
        'subtitlesformat': 'vtt',
        'outtmpl': temp_file_base,
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if os.path.exists(expected_file_path):
            with open(expected_file_path, 'r', encoding='utf-8') as f:
                vtt_content = f.read()
            
            try:
                os.remove(expected_file_path)
            except OSError as e:
                print(f"[WARN] No se pudo eliminar el archivo temporal: {e}")
                
            video_metadata = {
                'title': info.get('title', 'N/A'),
                'channel': info.get('uploader', 'N/A'),
                'upload_date': info.get('upload_date', 'N/A'), # Format YYYYMMDD
                'url': url
            }
            return vtt_content, lang_to_download, video_metadata
        else:
            print(f"[ERROR] El archivo de subtítulos no fue creado en '{expected_file_path}'.")
            return None, None, None

    except Exception as e:
        print(f"[ERROR] Error inesperado durante la descarga de subtítulos: {e}")
        return None, None, None
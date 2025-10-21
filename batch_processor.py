from downloader import download_vtt
from parser import vtt_to_plain_text, format_transcription
from db import insert_video

def process_urls_to_single_file(url_list, output_path, lang='es', keep_timestamps=False):
    """
    Procesa una lista de URLs de YouTube, descarga sus subtítulos,
    y los guarda todos en un solo archivo de texto con encabezados.

    Args:
        url_list: Lista de URLs de YouTube a procesar
        output_path: Ruta del archivo de salida
        lang: Idioma de los subtítulos (default: 'es')
        keep_timestamps: Si True, mantiene las marcas de tiempo (default: False)
    """
    print(f"[INFO] Iniciando procesamiento por lotes de {len(url_list)} URLs.")
    all_texts = []
    success_count = 0
    fail_count = 0

    for i, url in enumerate(url_list, 1):
        try:
            print(f"\n[{i}/{len(url_list)}] Procesando URL: {url.strip()}")
            vtt_content, detected_lang, video_metadata = download_vtt(url, lang)
            
            if vtt_content:
                remove_timestamps = not keep_timestamps
                plain_text = vtt_to_plain_text(vtt_content, remove_timestamps)

                # Formatear el texto ANTES de guardarlo
                formatted_text = format_transcription(plain_text, title=video_metadata['title'], url=url)

                # Guardar en la base de datos el texto ya formateado
                db_data = {
                    'url': video_metadata['url'],
                    'channel': video_metadata['channel'],
                    'title': video_metadata['title'],
                    'upload_date': video_metadata['upload_date'],
                    'transcript': formatted_text,  # Usar el texto formateado
                    'summary': None,
                    'key_ideas': None,
                    'ai_categorization': None
                }
                insert_video(db_data)
                all_texts.append(f"{formatted_text}\n\n---\n\n")
                print(f"[OK] Transcripción de '{video_metadata['title']}' procesada.")
                success_count += 1
            else:
                print(f"[ERROR] No se pudo obtener la transcripción para la URL.")
                fail_count += 1
        except Exception as e:
            print(f"[ERROR] Fallo inesperado procesando {url.strip()}: {e}")
            fail_count += 1

    # Guardar todo en un solo archivo
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.writelines(all_texts)
        print(f"\n[HECHO] Proceso por lotes completado.")
        print(f"    Total de transcripciones guardadas: {success_count}")
        print(f"    Total de fallos: {fail_count}")
        print(f"    Archivo de salida: {output_path}")
    except IOError as e:
        print(f"\n[ERROR] No se pudo escribir en el archivo de salida '{output_path}': {e}")

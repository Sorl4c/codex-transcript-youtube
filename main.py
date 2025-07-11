"""
Main script to download and parse YouTube subtitles into plain text.
"""
import argparse
import sys
import os
import re
from urllib.parse import urlparse

# Set console encoding for Windows to prevent Unicode errors
if sys.platform == 'win32' and sys.stdout.isatty():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except TypeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# --- Dependency Check --- #
try:
    import yt_dlp
except ImportError:
    print("La dependencia 'yt-dlp' no está instalada. Por favor, ejecuta: pip install yt-dlp")
    sys.exit(1)
# --- End Dependency Check --- #

from downloader import download_vtt
from parser import vtt_to_plain_text, format_transcription, vtt_to_plain_text_stream
from batch_processor import process_urls_to_single_file
from utils import is_url
from db import init_db, insert_video

stats = {"processed": 0, "failed": 0}

def is_url(path):
    """Check if the given path is a URL."""
    return urlparse(path).scheme in ('http', 'https')

def process_vtt_content(vtt_content, title=None, url=None):
    """Converts VTT content to formatted plain text."""
    plain_text = vtt_to_plain_text(vtt_content)
    if not plain_text.strip():
        return None
    return format_transcription(plain_text, title=title, url=url)

def save_output(text, output_path):
    """Saves the given text to the output path."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"[INFO] Transcripción guardada en: {output_path}")
        stats["processed"] += 1
    except IOError as e:
        print(f"[ERROR] No se pudo escribir en el archivo '{output_path}'. {e}")
        stats["failed"] += 1

def handle_url(url, lang, output_file):
    """Handles processing a single YouTube URL."""
    vtt_content, detected_lang, video_metadata = download_vtt(url, lang)
    if not vtt_content:
        stats["failed"] += 1
        return

    print(f"[INFO] Subtítulos en '{detected_lang}' descargados. Convirtiendo a texto plano...")
    
    plain_text = vtt_to_plain_text(vtt_content)
    if not plain_text.strip():
        print("[WARN] El contenido de los subtítulos estaba vacío después de la limpieza.")
        stats["failed"] += 1
        return

    # Formatear el texto con título y URL
    formatted_text = format_transcription(plain_text, title=video_metadata['title'], url=url)
    
    # Guardar en la base de datos el texto formateado
    db_data = {
        'url': video_metadata['url'],
        'channel': video_metadata['channel'],
        'title': video_metadata['title'],
        'upload_date': video_metadata['upload_date'],
        'transcript': formatted_text,  # Usamos el texto formateado
        'summary': None,
        'key_ideas': None,
        'ai_categorization': None
    }
    insert_video(db_data)

    # Guardar en archivo o mostrar por consola
    if output_file:
        save_output(formatted_text, output_file)
    else:
        print("\n--- INICIO DE LA TRANSCRIPCIÓN ---")
        print(formatted_text)
        print("--- FIN DE LA TRANSCRIPCIÓN ---")
    
    stats["processed"] += 1

def handle_local_file(file_path, output_path):
    """Handles processing a single local VTT file using streaming for memory efficiency."""
    print(f"[INFO] Procesando archivo local: {file_path}")
    
    if not output_path:
        output_path = os.path.splitext(file_path)[0] + '.txt'

    try:
        with open(file_path, 'r', encoding='utf-8') as in_file, \
             open(output_path, 'w', encoding='utf-8') as out_file:
            
            # 1. Write header to the output file
            title = os.path.basename(file_path)
            header = f"Título: {title}\nURL: N/A\n\n"
            out_file.write(header)
            
            # 2. Stream-process VTT and write the body
            clean_lines_iterator = vtt_to_plain_text_stream(in_file)
            
            # Write the first line without a leading space
            first_line = next(clean_lines_iterator, None)
            if first_line:
                out_file.write(first_line)
                # Write subsequent lines with a leading space to form a single paragraph
                for line in clean_lines_iterator:
                    out_file.write(" " + line)
                
                print(f"[INFO] Transcripción guardada en: {output_path}")
                stats["processed"] += 1
            else:
                # This case means the file was empty after cleaning
                print(f"[WARN] El contenido de '{file_path}' estaba vacío después de la limpieza.")
                stats["processed"] += 1 # Still counts as processed

    except FileNotFoundError:
        print(f"[ERROR] Archivo no encontrado: {file_path}")
        stats["failed"] += 1
    except Exception as e:
        print(f"[ERROR] No se pudo procesar el archivo '{file_path}': {e}")
        stats["failed"] += 1

def handle_directory(dir_path, output_dir):
    """Handles processing all VTT files in a directory."""
    print(f"[INFO] Procesando directorio: {dir_path}")
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files_to_process = [f for f in os.listdir(dir_path) if f.lower().endswith('.vtt')]
    if not files_to_process:
        print("[WARN] No se encontraron archivos .vtt en el directorio.")
        return

    for filename in files_to_process:
        file_path = os.path.join(dir_path, filename)
        output_filename = os.path.splitext(filename)[0] + '.txt'
        output_path = os.path.join(output_dir or dir_path, output_filename)
        handle_local_file(file_path, output_path)

def main():
    """Main function to orchestrate the download and parsing process."""
    init_db() # Ensure the database is ready
    parser = argparse.ArgumentParser(
        description='Descarga subtítulos de YouTube o procesa archivos locales.',
        epilog='Ejemplos:\n' \
               '  python main.py "URL_DEL_VIDEO" -o transcripcion.txt\n' \
               '  python main.py "./lista_urls.txt" -o transcripciones.txt\n' \
               '  python main.py "./mi_video.vtt"\n' \
               '  python main.py "./mi_carpeta/" -o "./salida/"',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('source', nargs='?', default=None, help='Fuente de datos: URL de YouTube, ruta a archivo .vtt, a carpeta, o a .txt con URLs.')
    parser.add_argument('-o', '--output', help='Ruta de salida (archivo o carpeta). Opcional.')
    parser.add_argument('-l', '--lang', default='es', help='Idioma para subtítulos de YouTube (por defecto: \'es\').')
    parser.add_argument('--gui', action='store_true', help='Lanza la interfaz gráfica para gestionar la base de datos.')
    parser.add_argument('--streamlit-ui', action='store_true', help='Lanza la nueva interfaz web con Streamlit.')
    parser.add_argument('--view-db', action='store_true', help='Abre el visor de la base de datos de vídeos.')
    parser.add_argument('--unified-ui', action='store_true', help='Lanza la nueva interfaz gráfica unificada.')

    args = parser.parse_args()

    if args.streamlit_ui:
        print("Lanzando interfaz Streamlit...")
        try:
            from gui_streamlit import run as run_streamlit
            # Para lanzar streamlit, es mejor hacerlo desde la línea de comandos
            # con 'streamlit run gui_streamlit.py'. Este es un placeholder.
            print("Por favor, ejecuta el siguiente comando en tu terminal:")
            print("streamlit run gui_streamlit.py")
            # run_streamlit() # Esto no funcionará como se espera directamente
        except ImportError as e:
            print(f"Error: No se pudo importar la UI de Streamlit. ¿Instalaste Streamlit?", file=sys.stderr)
            print(f"Detalle: {e}", file=sys.stderr)
            sys.exit(1)

    if args.gui or args.unified_ui:  # Ambas opciones lanzan la interfaz unificada
        try:
            from gui_unified import UnifiedApp
            import sys
            # Usar localhost si se especifica --gui, de lo contrario usar la IP de WSL
            api_url = "http://localhost:8000/v1/chat/completions" if '--gui' in sys.argv else "http://172.31.126.236:8000/v1/chat/completions"
            unified_app = UnifiedApp(api_url=api_url)
            unified_app.mainloop()
        except ImportError as e:
            print(f"[ERROR] No se pudo cargar la interfaz unificada: {e}")
            print("Asegúrate de que el archivo gui_unified.py existe en el directorio.")
        except Exception as e:
            print(f"[ERROR] Error al iniciar la interfaz: {e}")
        return

    if args.view_db:
        try:
            from gui_db import DBViewer
            db_app = DBViewer()
            db_app.mainloop()
        except ImportError as e:
            print(f"[ERROR] No se pudo cargar el visor de la base de datos: {e}")
        return

    if not args.source:
        parser.print_help()
        print("\n[ERROR] Debes proporcionar una fuente de datos o usar la opción --gui.")
        return
    source = args.source
    is_batch_mode = False

    if is_url(source):
        handle_url(source, args.lang, args.output)
    elif os.path.isdir(source):
        handle_directory(source, args.output)
    elif os.path.isfile(source):
        if source.lower().endswith('.vtt'):
            handle_local_file(source, args.output)
        elif source.lower().endswith('.txt'):
            is_batch_mode = True
            print(f"[INFO] Detectado archivo de URLs: {source}")
            try:
                with open(source, 'r', encoding='utf-8') as f:
                    urls = [line.strip() for line in f if line.strip() and is_url(line.strip())]
                if not urls:
                    print("[WARN] El archivo de URLs está vacío o no contiene URLs válidas.")
                else:
                    output_file = args.output or "transcripciones_completas.txt"
                    process_urls_to_single_file(urls, output_file, args.lang)
            except Exception as e:
                print(f"[ERROR] No se pudo leer el archivo de URLs: {e}")
        else:
            print(f"[ERROR] Tipo de archivo no soportado: {source}. Use .vtt o .txt.")
            stats["failed"] += 1
    else:
        print(f"[ERROR] La ruta especificada no es una URL, archivo o directorio válido: {source}")
        stats["failed"] += 1

    if not is_batch_mode:
        print("\n--- RESUMEN DEL PROCESO ---")
        print(f"Archivos procesados con éxito: {stats['processed']}")
        print(f"Archivos fallidos: {stats['failed']}")
        print("-----------------------------")

if __name__ == "__main__":
    main()
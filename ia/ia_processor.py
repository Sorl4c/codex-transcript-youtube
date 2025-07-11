import os
from typing import TYPE_CHECKING

from llama_cpp import Llama  # Importación directa para uso en runtime

# --- Configuración del Modelo ---
# ¡¡¡IMPORTANTE!!! ACTUALIZA ESTA RUTA A TU MODELO GGUF
# Asegúrate de que la ruta sea accesible desde el entorno donde ejecutas este script (WSL o Windows).
# Ejemplo para WSL: MODEL_PATH = "/mnt/c/AI_Models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
# Ejemplo para Windows: MODEL_PATH = "C:/AI_Models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
MODEL_PATH = "/mnt/c/local/modelos/tinyllama.gguf" 

# Variable global para almacenar la instancia del modelo y evitar recargas múltiples.
_llm_instance: Llama | None = None

# Ruta al directorio de prompts, relativa a este script
# Asume que ia_processor.py está en el directorio 'ia' y los prompts en 'ia/prompts/'
PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "prompts")
SUMMARY_PROMPT_FILE = os.path.join(PROMPTS_DIR, "summary.txt")

# --- Funciones del Modelo ---
def cargar_modelo_llm(model_path: str = MODEL_PATH, n_gpu_layers: int = -1, verbose: bool = True) -> Llama:
    """
    Carga el modelo Llama GGUF si aún no está cargado.
    Utiliza una variable global para almacenar la instancia del modelo y evitar recargas.

    Args:
        model_path (str): Ruta al archivo del modelo .gguf.
        n_gpu_layers (int): Número de capas a descargar en la GPU. -1 para todas las posibles.
                            Si es 0, se usará solo CPU.
        verbose (bool): Si se deben imprimir mensajes de log del modelo desde llama_cpp.

    Returns:
        Llama: Instancia del modelo Llama cargado.

    Raises:
        FileNotFoundError: Si el archivo del modelo no se encuentra en la ruta especificada.
        RuntimeError: Si ocurre un error durante la carga o inicialización del modelo.
    """
    global _llm_instance
    if _llm_instance is None:
        if not model_path or model_path == "PON_AQUI_LA_RUTA_A_TU_MODELO_TINYLAMA.gguf" or not os.path.exists(model_path):
            abs_path = os.path.abspath(model_path) if model_path and model_path != "PON_AQUI_LA_RUTA_A_TU_MODELO_TINYLAMA.gguf" else "No especificada o placeholder sin cambiar"
            error_msg = (
                f"[IA_Processor] Error: Ruta del modelo no válida o archivo no encontrado: '{abs_path}'.\n"
                f"Por favor, actualiza la variable 'MODEL_PATH' en 'ia_processor.py' con la ruta correcta a tu archivo .gguf."
            )
            print(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            print(f"[IA_Processor] Cargando modelo Llama desde: {model_path}...")
            _llm_instance = Llama(
                model_path=model_path,
                n_gpu_layers=n_gpu_layers,  # -1 para intentar cargar todas las capas en GPU
                n_ctx=2048,                 # Tamaño del contexto, ajustar según sea necesario
                verbose=verbose,            # Muestra logs de llama-cpp
                # chat_format="llama-2",    # Descomentar y ajustar si tu modelo usa un formato de chat específico
                                            # Formatos comunes: "llama-2", "chatml", "vicuna", etc.
            )
            if verbose and _llm_instance:
                print(f"[IA_Processor] Modelo Llama cargado exitosamente. (GPU Layers: {n_gpu_layers if n_gpu_layers != -1 else 'todas las posibles'})")
            elif not _llm_instance:
                raise RuntimeError("[IA_Processor] La inicialización de Llama() no produjo una instancia válida.")

        except Exception as e:
            detailed_error_msg = (
                f"[IA_Processor] Error crítico al cargar el modelo Llama desde '{model_path}': {e}\n"
                "Posibles causas:\n"
                "- Ruta incorrecta o archivo de modelo dañado.\n"
                "- Versión incompatible de llama-cpp-python o dependencias (CUDA, cuBLAS).\n"
                "- Problemas de memoria (RAM o VRAM insuficiente).\n"
                "- Modelo no compatible con la versión de llama.cpp.\n"
                "Revisa la salida de la consola para más detalles de llama.cpp."
            )
            print(detailed_error_msg)
            # import traceback # Descomentar para depuración más profunda
            # print(traceback.format_exc())
            _llm_instance = None 
            raise RuntimeError(detailed_error_msg) from e
            
    return _llm_instance

def leer_plantilla_prompt(ruta_archivo: str) -> str:
    """
    Lee una plantilla de prompt desde la ruta especificada.
    
    Args:
        ruta_archivo: Ruta al archivo de plantilla.
        
    Returns:
        str: Contenido del archivo de plantilla.
        
    Raises:
        FileNotFoundError: Si el archivo de plantilla no existe.
    """
    if not os.path.exists(ruta_archivo):
        ruta_absoluta = os.path.abspath(ruta_archivo)
        raise FileNotFoundError(f"Archivo de plantilla no encontrado: {ruta_absoluta}")
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        return f.read()

def resumir_texto(instancia_llm: 'Llama', texto: str, max_tokens: int = 250) -> str:
    """
    Genera un resumen del texto proporcionado usando una instancia del modelo Llama.

    Args:
        instancia_llm: Instancia del modelo Llama ya inicializado.
        texto: Texto que se desea resumir.
        max_tokens: Número máximo de tokens para el resumen generado.

    Returns:
        str: El resumen generado, o un mensaje de error si falla.
    """
    if instancia_llm is None:
        return "Error: No se proporcionó una instancia válida del modelo Llama."
    if not texto or not texto.strip():
        return "Error: El texto de entrada está vacío o solo contiene espacios en blanco."

    try:
        plantilla_prompt = leer_plantilla_prompt(SUMMARY_PROMPT_FILE)
    except FileNotFoundError as e:
        return str(e)

    # Reemplaza el marcador {text} en la plantilla con el texto real
    contenido_mensaje = plantilla_prompt.replace("{text}", texto)

    try:
        respuesta = instancia_llm.create_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "Eres un asistente que se especializa en resumir texto de manera concisa y precisa."
                },
                {
                    "role": "user",
                    "content": contenido_mensaje
                }
            ],
            max_tokens=max_tokens,
            temperature=0.3,  # Temperatura baja para respuestas más deterministas
        )
        
        resumen = respuesta['choices'][0]['message']['content'].strip()
        return resumen
    except Exception as e:
        # Para depuración: import traceback; print(traceback.format_exc())
        return f"Error al generar el resumen: {e}"

if __name__ == '__main__':
    print("--- Testing IA Processor with Actual Llama Model ---")

    sample_text_to_summarize = (
        "This is a rather long and elaborate piece of text that has been specifically designed "
        "for the purpose of testing the summarization capabilities of our newly implemented AI module. "
        "The module is expected to take this text, process it through a language model, "
        "and return a concise and accurate summary. We are hopeful that this test will demonstrate "
        "the effectiveness of the prompt engineering and model interaction. "
        "YouTube subtitles can often be lengthy, and users would benefit greatly from a quick "
        "overview of the content. This feature aims to provide just that, using local AI "
        "to ensure privacy and speed. The model chosen is TinyLlama, which should be "
        "efficient enough for this task on compatible hardware."
    )

    llm_instance = None
    try:
        if MODEL_PATH == "PON_AQUI_LA_RUTA_A_TU_MODELO_TINYLAMA.gguf":
             print("\nERROR: MODEL_PATH no está configurado en ia_processor.py.")
             print("Por favor, edita el archivo y establece la ruta correcta a tu modelo .gguf.")
             print("Saliendo del script de prueba.")
             exit(1)
        
        print(f"Intentando cargar el modelo desde: {MODEL_PATH}")
        # Cargar el modelo. Si ya está cargado, reutilizará la instancia global.
        llm_instance = cargar_modelo_llm(verbose=True) 
        print("Modelo cargado (o reutilizado si ya estaba cargado).")

    except FileNotFoundError as e_fnf:
        print(f"{e_fnf}") # El mensaje de error ya es detallado desde cargar_modelo_llm
    except RuntimeError as e_rt:
        print(f"{e_rt}") # El mensaje de error ya es detallado
    except Exception as e_generic:
        print(f"\nOcurrió un error inesperado durante la carga del modelo: {e_generic}")
        import traceback
        print(traceback.format_exc())

    if llm_instance:
        print(f"\nSummarizing sample text (first 80 chars): '{sample_text_to_summarize[:80]}...'\n")
        summary_result = resumir_texto(llm_instance, sample_text_to_summarize, max_tokens=150)
        print(f"--- Generated Summary ---")
        print(summary_result)
        print("-------------------------")

        print("\nTesting with empty text:")
        summary_empty_text_result = resumir_texto(llm_instance, "   ")
        print(f"Result: {summary_empty_text_result}")
        
        # Opcional: Prueba de manejo de error de plantilla de prompt faltante
        # Para probar, renombra temporalmente 'ia/prompts/summary.txt'
        # print("\nTesting with missing prompt file (simulated by renaming summary.txt):")
        # original_prompt_path = SUMMARY_PROMPT_FILE
        # temp_prompt_path = original_prompt_path + '.bak'
        # if os.path.exists(original_prompt_path):
        #     try:
        #         os.rename(original_prompt_path, temp_prompt_path)
        #         print(f"Renamed '{original_prompt_path}' to '{temp_prompt_path}' for test.")
        #         missing_prompt_summary = resumir_texto(llm_instance, sample_text_to_summarize)
        #         print(f"Result for missing prompt: {missing_prompt_summary}")
        #     except Exception as e_rename:
        #         print(f"Error during missing prompt test: {e_rename}")
        #     finally:
        #         if os.path.exists(temp_prompt_path):
        #             os.rename(temp_prompt_path, original_prompt_path)
        #             print(f"Restored '{original_prompt_path}'.")
        # else:
        #     print(f"Cannot simulate missing prompt: '{original_prompt_path}' not found.")

    else:
        print("\nNo se pudo cargar el modelo LLM. Pruebas de resumen omitidas.")

    print("\n--- IA Processor Test Complete ---")

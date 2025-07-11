import os
import sys

# Adjust path to import from parent directory if 'ia' is a module
# This assumes test_ia.py is run from within the 'ia' directory or the parent of 'ia' is in PYTHONPATH
# For simplicity, if 'ia_models' and 'ia_processor' are in the same directory ('ia'), direct relative imports work.

try:
    from .ia_models import get_model, MODELS_BASE_DIR
    from .ia_processor import resumir_texto
except ImportError:
    # Fallback for running the script directly from the 'ia' directory for testing
    # when 'ia' itself is not (yet) a package recognized by a higher-level entry point.
    # This means Python might not see 'ia' as a package for relative imports like '.ia_models'.
    # In such a case, if the CWD is 'yt-dlp/ia/', then 'ia_models.py' is directly importable.
    # If CWD is 'yt-dlp/', then 'from ia.ia_models ...' would be needed.
    # This is a common point of confusion with Python imports.
    # For robustness, let's try to adjust sys.path if needed, assuming script is in 'ia'
    # and 'yt-dlp' (parent of 'ia') is the project root.
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    PARENT_DIR = os.path.dirname(CURRENT_DIR)
    if PARENT_DIR not in sys.path:
        sys.path.insert(0, PARENT_DIR) # Add project root to path
    
    # Now try importing as if 'ia' is a package known to the project root
    from ia.ia_models import get_model, MODELS_BASE_DIR
    from ia.ia_processor import resumir_texto


# --- Configuration ---
# The user needs to download this model and place it in the 'ia/models/' directory.
# Example: tinyllama-1.1b-chat.Q4_K_M.gguf
# You can find models like this on Hugging Face (e.g., TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF)
MODEL_NAME = "tinyllama-1.1b-chat.Q4_K_M.gguf" 
SAMPLE_TEXT_FILE = os.path.join(os.path.dirname(__file__), "sample_text.txt")
# --- End Configuration ---

import os
import sys
from pathlib import Path

# Ajustar el path para importar módulos desde el directorio raíz
sys.path.insert(0, str(Path(__file__).parent.parent))

from ia.ia_models import cargar_modelo, obtener_ruta_modelo
from ia.ia_processor import resumir_texto

MODELO_DEFECTO = "tinyllama-1.1b-chat.Q4_K_M.gguf"
ARCHIVO_EJEMPLO = Path(__file__).parent / "sample_text.txt"

def cargar_ejemplo(ruta_archivo: str = None) -> str:
    """
    Carga un texto de ejemplo desde un archivo. Si no existe, devuelve un texto por defecto.
    """
    if ruta_archivo is None:
        ruta_archivo = ARCHIVO_EJEMPLO
    else:
        ruta_archivo = Path(ruta_archivo)
    if not ruta_archivo.exists():
        return "Este es un texto de ejemplo para probar el resumen. El módulo de IA analizará este contenido y generará un resumen conciso."
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    print("="*60)
    print("  PRUEBA DEL MÓDULO DE IA - RESUMEN AUTOMÁTICO")
    print("="*60)
    
    print("\n⚙️  CONFIGURACIÓN:")
    print(f"Directorio de modelos: {obtener_ruta_modelo()}")
    print(f"Ubicación del script: {Path(__file__).resolve()}")
    
    print("\n🔄 Cargando modelo...")
    try:
        try:
            llm = cargar_modelo(dispositivo='gpu')
        except Exception as e:
            print(f"⚠️  No se pudo cargar con GPU, intentando con CPU... ({str(e).split('.')[0]})")
            llm = cargar_modelo(dispositivo='cpu')
        print("\n📄 Cargando texto de ejemplo...")
        texto = cargar_ejemplo()
        print(f"Texto de entrada ({len(texto)} caracteres):")
        print("-"*50)
        print(texto[:500] + ("..." if len(texto) > 500 else ""))
        print("-"*50)
        print("\n🧠 Generando resumen...")
        resumen = resumir_texto(llm, texto)
        print("\n📝 RESUMEN GENERADO:")
        print("="*50)
        print(resumen)
        print("="*50)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nℹ️  Posibles soluciones:")
        print("1. ¿Tienes instalado llama-cpp-python con soporte GPU?")
        print("   Instálalo con: CMAKE_ARGS='-DLLAMA_CUBLAS=on' FORCE_CMAKE=1 pip install llama-cpp-python")
        print(f"2. ¿El archivo del modelo está en {obtener_ruta_modelo()}?")
        print("   Descarga un modelo GGUF y colócalo en ese directorio.")
        return 1
    print("\n✅ ¡Prueba completada exitosamente!")
    return 0

if __name__ == '__main__':
    sys.exit(main())

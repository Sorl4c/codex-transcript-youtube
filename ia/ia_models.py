import os
import sys
from pathlib import Path
from llama_cpp import Llama

# =====================
# SOPORTE DE RUTA GLOBAL PARA MODELOS GGUF
# =====================
def obtener_ruta_base_modelos() -> Path:
    """
    Devuelve la ruta base donde buscar los modelos GGUF.
    Prioridad:
    1. Variable de entorno GGUF_MODELS_PATH
    2. Ruta por defecto global según sistema operativo
    """
    ruta_env = os.environ.get('GGUF_MODELS_PATH')
    if ruta_env:
        return Path(ruta_env)
    if sys.platform.startswith('win'):
        ruta_defecto = Path('C:/local/modelos')
    else:
        ruta_defecto = Path('/mnt/c/local/modelos')
    ruta_defecto.mkdir(parents=True, exist_ok=True)
    return ruta_defecto

def obtener_ruta_modelo(nombre_modelo: str = None) -> Path:
    """
    Devuelve la ruta completa a un modelo concreto o al directorio de modelos si no se pasa nombre.
    """
    base = obtener_ruta_base_modelos()
    if nombre_modelo is None:
        return base
    return base / nombre_modelo

def cargar_modelo(
    nombre_modelo: str = 'tinyllama-1.1b-chat.Q4_K_M.gguf',
    dispositivo: str = 'gpu',
    modo: str = 'local'
) -> Llama:
    """
    Carga un modelo GGUF usando llama-cpp-python.
    - Busca primero la ruta en variable de entorno GGUF_MODELS_PATH
    - Si no existe, usa la ruta global por defecto
    - Permite elegir entre GPU y CPU
    - Solo soporta modo local por ahora
    """
    if modo != 'local':
        raise NotImplementedError("Solo se soporta el modo 'local' actualmente.")
    ruta_modelo = obtener_ruta_modelo(nombre_modelo)
    if not ruta_modelo.exists():
        raise FileNotFoundError(
            f"No se encontró el modelo en: {ruta_modelo}\n"
            f"Descarga el modelo GGUF y colócalo ahí."
        )
    n_gpu_layers = -1 if dispositivo == 'gpu' else 0
    print(f" Buscando modelo en: {ruta_modelo}")
    print(f"  Dispositivo: {dispositivo.upper()} | Capas GPU: {n_gpu_layers if dispositivo == 'gpu' else 'N/A'}")
    try:
        llm = Llama(
            model_path=str(ruta_modelo),
            n_gpu_layers=n_gpu_layers,
            n_ctx=4096,
            verbose=False
        )
        print(" Modelo cargado correctamente.")
        return llm
    except Exception as e:
        print(f" Error al cargar el modelo: {e}")
        if dispositivo == 'gpu':
            print("\n ¿Tienes instalado el soporte para GPU? Instala llama-cpp-python con cuBLAS:")
            print("CMAKE_ARGS='-DLLAMA_CUBLAS=on' FORCE_CMAKE=1 pip install llama-cpp-python")
        raise

if __name__ == '__main__':
    print("Prueba de rutas de modelos:")
    print(f"Directorio base: {obtener_ruta_base_modelos()}")
    print(f"Ruta modelo por defecto: {obtener_ruta_modelo()}")
    try:
        print("\nProbando carga de modelo...")
        modelo = cargar_modelo(dispositivo='cpu')
        print("¡Módulo de modelos funcionando!")
    except FileNotFoundError as e:
        print(f"\n  {e}")
        print("\nPasos para continuar:")
        print(f"1. Crea el directorio: {obtener_ruta_base_modelos()}")
        print("2. Descarga un modelo GGUF (ej: TinyLlama) en ese directorio")
        print("3. Vuelve a ejecutar esta prueba")
        print("\nEjemplo de descarga:")
        print(f"  mkdir -p {obtener_ruta_base_modelos()}")
        print("  cd", obtener_ruta_base_modelos())
        print("  wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
    # Intentar cargar un modelo de prueba (el usuario debe proporcionar el modelo real)
    nombre_modelo_prueba = "tinyllama-1.1b-chat.Q4_K_M.gguf"  # Modelo de ejemplo
    
    # Crear un archivo de modelo simulado para probar la lógica de rutas
    # En un escenario real, el usuario debe descargar y colocar un modelo real
    ruta_modelo_simulado = obtener_ruta_modelo(nombre_modelo_prueba)
    
    # Crear directorio si no existe
    ruta_modelo_simulado.parent.mkdir(parents=True, exist_ok=True)
    
    if not ruta_modelo_simulado.exists():
        try:
            with open(ruta_modelo_simulado, 'w') as f:
                f.write("Este es un archivo GGUF simulado solo para pruebas.\n")
            print(f"\n⚠️  Se creó un archivo de modelo simulado para pruebas en: {ruta_modelo_simulado}")
            print("¡IMPORTANTE! Este NO es un modelo real. Reemplázalo con un archivo .gguf real.")
        except Exception as e:
            print(f"\n❌ No se pudo crear el archivo de modelo simulado: {e}")

    # Intentar cargar el modelo en CPU
    print(f"\n🔍 Intentando cargar '{nombre_modelo_prueba}' en CPU...")
    try:
        modelo_cpu = cargar_modelo(dispositivo='cpu')
        print(f"✅ Modelo cargado correctamente en CPU: {type(modelo_cpu)}")
    except Exception as e:
        print(f"❌ No se pudo cargar el modelo en CPU: {e}")

    # Intentar cargar el modelo en GPU
    print(f"\n🔍 Intentando cargar '{nombre_modelo_prueba}' en GPU...")
    print("(Esto probablemente falle si no se ejecuta en WSL con soporte GPU y un modelo real)")
    try:
        modelo_gpu = cargar_modelo(dispositivo='gpu')
        print(f"✅ Modelo cargado correctamente en GPU: {type(modelo_gpu)}")
    except Exception as e:
        print(f"❌ No se pudo cargar el modelo en GPU: {e}")
        
    print("\n--- PRUEBA DE CARGA DE MODELO COMPLETADA ---")
    print(f"\nℹ️  Para usar el módulo, coloca tu modelo .gguf en esta carpeta:")
    print(f"   {obtener_ruta_base_modelos()}")
    print("\nPuedes descargar modelos de Hugging Face, por ejemplo:")
    print(f"  cd {obtener_ruta_base_modelos()}")
    print("  wget https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")

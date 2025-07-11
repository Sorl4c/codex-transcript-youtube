from llama_cpp import Llama
import time
from pathlib import Path

def probar_modelo():
    print("=== PRUEBA DE MODELO TINYLLAMA ===")
    print("Iniciando prueba con el modelo...")
    
    # Ruta al modelo (ajustada para WSL)
    ruta_modelo = "/mnt/c/local/modelos/tinyllama.gguf"
    
    if not Path(ruta_modelo).exists():
        print(f"Error: No se encontró el modelo en {ruta_modelo}")
        print("Asegúrate de que el archivo existe y tienes permisos de lectura.")
        return
    
    try:
        # 1. Cargar el modelo
        print("\n1. Cargando modelo (esto puede tardar un momento)...")
        inicio_carga = time.time()
        
        llm = Llama(
            model_path=ruta_modelo,
            n_ctx=2048,      # Tamaño del contexto
            n_threads=4,     # Número de hilos a usar
            verbose=False    # Menos salida en consola
        )
        
        tiempo_carga = time.time() - inicio_carga
        print(f"✓ Modelo cargado en {tiempo_carga:.1f} segundos")
        
        # 2. Prueba de generación
        print("\n2. Probando generación de texto...")
        prompt = "Ponme un título creativo para un video sobre programación en Python"
        print(f"Prompt: '{prompt}'")
        
        inicio_gen = time.time()
        resultado = llm(
            prompt,
            max_tokens=50,    # Máximo de tokens a generar
            stop=["\n", "###"],  # Detenerse en saltos de línea
            echo=False         # No incluir el prompt en la salida
        )
        
        # 3. Mostrar resultados
        tiempo_gen = time.time() - inicio_gen
        texto_generado = resultado['choices'][0]['text'].strip()
        
        print("\n✓ Resultado generado:")
        print("-" * 50)
        print(texto_generado)
        print("-" * 50)
        print(f"\nTiempo de generación: {tiempo_gen:.2f} segundos")
        print(f"Tokens generados: {len(texto_generado.split())} palabras aprox.")
        
    except Exception as e:
        print(f"\n✗ Error durante la ejecución: {str(e)}")
        print("\nPosibles soluciones:")
        print("1. Verifica que el archivo del modelo no esté corrupto")
        print("2. Intenta con un modelo más pequeño si hay problemas de memoria")
        print("3. Revisa que tengas todos los permisos necesarios")

if __name__ == "__main__":
    probar_modelo()

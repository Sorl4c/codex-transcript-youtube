"""
Implementación de chunking agentic usando LLMs (Gemini API y LLM local).
Este módulo proporciona funciones para dividir texto de manera inteligente
usando modelos de lenguaje, generando chunks con metadatos enriquecidos.
"""

import os
import json
import time
import requests
from typing import List, Dict, Any, Optional, Tuple, Callable
import logging

# Importar las clases de chunk del módulo principal
try:
    from .chunker import Chunk, ChunkMetadata
except ImportError:
    from chunker import Chunk, ChunkMetadata

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Función para debug detallado
def debug_log(message: str, data: Any = None):
    """Log de debug con datos opcionales"""
    if data is not None:
        logger.debug(f"[AGENTIC_DEBUG] {message}: {data}")
    else:
        logger.debug(f"[AGENTIC_DEBUG] {message}")

# ============================================================================
# CONFIGURACIÓN Y CONSTANTES
# ============================================================================

# Prompt template para chunking agentic
AGENTIC_CHUNKING_PROMPT = """
Eres un experto en análisis de texto y división inteligente de contenido. Tu tarea es dividir el siguiente texto en chunks semánticamente coherentes y generar metadatos enriquecidos para cada chunk.

INSTRUCCIONES:
1. Divide el texto en chunks de aproximadamente {chunk_size} caracteres, pero prioriza la coherencia semántica sobre el tamaño exacto.
2. Cada chunk debe ser una unidad de significado completa (párrafo, sección, idea completa).
3. Genera un título semántico descriptivo para cada chunk.
4. Crea un resumen breve (1-2 frases) del contenido de cada chunk.
5. Identifica overlaps semánticos entre chunks adyacentes cuando sea relevante.

FORMATO DE RESPUESTA (JSON):
Responde ÚNICAMENTE con un JSON válido en el siguiente formato:
```json
{{
  "chunks": [
    {{
      "content": "texto del chunk",
      "semantic_title": "Título descriptivo del chunk",
      "summary": "Resumen breve del contenido",
      "semantic_overlap": "Descripción de la conexión con el chunk anterior (opcional)"
    }}
  ]
}}
```

TEXTO A PROCESAR:
{text}

RESPUESTA JSON:
"""

# Configuración para diferentes proveedores de LLM
LLM_PROVIDERS = {
    "gemini": {
        "api_key_env": "GEMINI_API_KEY",
        "default_model": "gemini-2.5-pro"
    },
    "local": {
        "default_url": "http://localhost:8000/v1/chat/completions",
        "fallback_url": "http://172.31.126.236:8000/v1/chat/completions"
    }
}

# ============================================================================
# FUNCIONES DE CHUNKING AGENTIC
# ============================================================================

def chunk_text_with_gemini(
    text: str, 
    chunk_size: int = 1000, 
    chunk_overlap: int = 200,
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.0-flash-exp"
) -> List[Chunk]:
    """
    Realiza chunking agentic usando la API de Google Gemini.
    
    Args:
        text: Texto a dividir en chunks
        chunk_size: Tamaño aproximado de cada chunk
        chunk_overlap: Overlap entre chunks (no usado directamente por el LLM)
        api_key: Clave API de Gemini (opcional, se toma del env)
        model_name: Modelo de Gemini a usar
        
    Returns:
        Lista de objetos Chunk con metadatos enriquecidos
    """
    try:
        debug_log("=== INICIANDO CHUNKING CON GEMINI ===")
        debug_log("Parámetros recibidos", {
            "text_length": len(text),
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "model_name": model_name
        })
        
        # Importar la API de Gemini
        debug_log("Importando módulos de Gemini...")
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from ia.gemini_api import configure_gemini, make_api_call_with_retry
        import google.generativeai as genai
        debug_log("Módulos de Gemini importados correctamente")
        
        # Configurar API
        debug_log("Configurando API de Gemini...")
        if not configure_gemini(api_key):
            debug_log("ERROR: No se pudo configurar la API de Gemini")
            raise Exception("No se pudo configurar la API de Gemini")
        debug_log("API de Gemini configurada correctamente")
        
        # Preparar prompt
        debug_log("Preparando prompt para Gemini...")
        prompt = AGENTIC_CHUNKING_PROMPT.format(
            chunk_size=chunk_size,
            text=text
        )
        debug_log("Prompt preparado", {"prompt_length": len(prompt)})
        
        # Crear modelo y realizar llamada
        debug_log(f"Creando modelo Gemini: {model_name}")
        model = genai.GenerativeModel(model_name)
        logger.info(f"Iniciando chunking agentic con Gemini ({model_name})")
        debug_log("Enviando request a Gemini...")
        
        start_time = time.time()
        response = make_api_call_with_retry(model, prompt, max_retries=3)
        api_time = time.time() - start_time
        debug_log("Respuesta recibida de Gemini", {
            "response_length": len(response.text) if hasattr(response, 'text') and response.text else 0,
            "api_time_seconds": round(api_time, 2)
        })
        
        # Extraer respuesta
        if not response or not response.text:
            raise Exception("Respuesta vacía de la API de Gemini")
        
        response_text = response.text.strip()
        logger.info(f"Respuesta de Gemini recibida en {api_time:.2f}s")
        
        # Parsear JSON
        chunks_data = _parse_llm_response(response_text)
        
        # Convertir a objetos Chunk
        chunks = _convert_to_chunks(chunks_data, text)
        
        logger.info(f"Chunking agentic completado: {len(chunks)} chunks generados")
        return chunks
        
    except Exception as e:
        debug_log("ERROR EN CHUNKING CON GEMINI", str(e))
        logger.error(f"Error en chunking con Gemini: {e}")
        raise

def chunk_text_with_local_llm(
    text: str, 
    chunk_size: int = 1000, 
    chunk_overlap: int = 200,
    api_url: Optional[str] = None,
    model_name: str = "local-model"
) -> List[Chunk]:
    """
    Realiza chunking agentic usando un LLM local compatible con OpenAI API.
    
    Args:
        text: Texto a dividir en chunks
        chunk_size: Tamaño aproximado de cada chunk
        chunk_overlap: Overlap entre chunks (no usado directamente por el LLM)
        api_url: URL del servicio LLM local
        model_name: Nombre del modelo (para logging)
        
    Returns:
        Lista de objetos Chunk con metadatos enriquecidos
    """
    try:
        debug_log("=== INICIANDO CHUNKING CON LLM LOCAL ===")
        debug_log("Parámetros recibidos", {
            "text_length": len(text),
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "model_name": model_name,
            "api_url": api_url
        })
        
        # Configurar URL del LLM local
        if api_url is None:
            api_url = LLM_PROVIDERS["local"]["default_url"]
        debug_log("URL del LLM local configurada", api_url)
        
        # Preparar prompt
        debug_log("Preparando prompt para LLM local...")
        prompt = AGENTIC_CHUNKING_PROMPT.format(
            chunk_size=chunk_size,
            text=text
        )
        debug_log("Prompt preparado", {"prompt_length": len(prompt)})
        
        # Preparar payload para la API
        payload = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 4000
        }
        debug_log("Payload preparado para LLM local", {"model": model_name, "temperature": 0.1})
        
        logger.info(f"Iniciando chunking agentic con LLM local ({model_name})")
        debug_log("Enviando request a LLM local...")
        
        start_time = time.time()
        response = requests.post(
            api_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        api_time = time.time() - start_time
        debug_log("Respuesta recibida de LLM local", {
            "status_code": response.status_code,
            "api_time_seconds": round(api_time, 2)
        })
        
        if response.status_code != 200:
            debug_log("ERROR: Respuesta no exitosa del LLM local", {
                "status_code": response.status_code,
                "response_text": response.text[:500]
            })
            raise Exception(f"Error en API local: {response.status_code} - {response.text}")
        
        # Extraer contenido de la respuesta
        debug_log("Extrayendo contenido de la respuesta...")
        response_data = response.json()
        llm_response = response_data["choices"][0]["message"]["content"]
        debug_log("Contenido extraído", {"response_length": len(llm_response)})
        
        # Parsear respuesta
        debug_log("Parseando respuesta de LLM local...")
        chunks_data = _parse_llm_response(llm_response)
        debug_log("Respuesta parseada", {"chunks_count": len(chunks_data.get('chunks', []))})
        
        debug_log("Convirtiendo a objetos Chunk...")
        chunks = _convert_to_chunks(chunks_data, text)
        debug_log("Chunks convertidos", {"final_chunks_count": len(chunks)})
        
        # Validar chunks
        debug_log("Validando chunks...")
        if not _validate_chunks(chunks):
            debug_log("ERROR: Los chunks generados no son válidos")
            raise Exception("Los chunks generados no son válidos")
        debug_log("Chunks validados correctamente")
        
        logger.info(f"Chunking con LLM local completado: {len(chunks)} chunks en {api_time:.2f}s")
        debug_log("=== CHUNKING CON LLM LOCAL COMPLETADO ===")
        return chunks
        
    except Exception as e:
        debug_log("ERROR EN CHUNKING CON LLM LOCAL", str(e))
        logger.error(f"Error en chunking con LLM local: {e}")
        raise

def chunk_text_agentic_auto(
    text: str, 
    chunk_size: int = 1000, 
    chunk_overlap: int = 200,
    prefer_local: bool = True
) -> List[Chunk]:
    """
    Realiza chunking agentic automático, intentando primero el método preferido
    y haciendo fallback al alternativo si falla.
    
    Args:
        text: Texto a dividir en chunks
        chunk_size: Tamaño aproximado de cada chunk
        chunk_overlap: Overlap entre chunks
        prefer_local: Si True, intenta primero LLM local, luego Gemini
        
    Returns:
        Lista de objetos Chunk con metadatos enriquecidos
    """
    methods = [
        ("local", chunk_text_with_local_llm),
        ("gemini", chunk_text_with_gemini)
    ]
    
    if not prefer_local:
        methods.reverse()
    
    last_error = None
    
    for method_name, method_func in methods:
        try:
            logger.info(f"Intentando chunking agentic con {method_name}")
            return method_func(text, chunk_size, chunk_overlap)
        except Exception as e:
            logger.warning(f"Chunking con {method_name} falló: {e}")
            last_error = e
            continue
    
    # Si ambos métodos fallan, lanzar la última excepción
    raise Exception(f"Todos los métodos de chunking agentic fallaron. Último error: {last_error}")

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def _parse_llm_response(response_text: str) -> Dict[str, Any]:
    """
    Parsea la respuesta JSON del LLM, manejando posibles errores de formato.
    
    Args:
        response_text: Texto de respuesta del LLM
        
    Returns:
        Diccionario con los datos parseados
    """
    try:
        # Intentar parsear directamente
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Intentar extraer JSON de markdown code blocks
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Intentar encontrar JSON sin code blocks
        json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        raise Exception(f"No se pudo parsear la respuesta JSON: {response_text[:200]}...")

def _convert_to_chunks(chunks_data: Dict[str, Any], original_text: str) -> List[Chunk]:
    """
    Convierte los datos parseados del LLM en objetos Chunk con metadatos.
    
    Args:
        chunks_data: Datos parseados del LLM
        original_text: Texto original para calcular posiciones
        
    Returns:
        Lista de objetos Chunk
    """
    if "chunks" not in chunks_data:
        raise Exception("Formato de respuesta inválido: falta campo 'chunks'")
    
    chunks = []
    current_pos = 0
    
    for i, chunk_data in enumerate(chunks_data["chunks"]):
        content = chunk_data.get("content", "").strip()
        if not content:
            continue
        
        # Buscar la posición del contenido en el texto original
        start_pos = original_text.find(content, current_pos)
        if start_pos == -1:
            # Si no se encuentra exactamente, usar posición aproximada
            start_pos = current_pos
        
        end_pos = start_pos + len(content)
        current_pos = end_pos
        
        # Crear metadatos
        metadata = ChunkMetadata(
            index=i,
            char_start_index=start_pos,
            char_end_index=end_pos,
            semantic_title=chunk_data.get("semantic_title"),
            summary=chunk_data.get("summary"),
            semantic_overlap=chunk_data.get("semantic_overlap"),
            additional_metadata={
                "generated_by": "agentic_chunking",
                "timestamp": time.time()
            }
        )
        
        # Crear chunk
        chunk = Chunk(content=content, metadata=metadata)
        chunks.append(chunk)
    
    # Establecer enlaces entre chunks adyacentes
    for i in range(len(chunks)):
        if i > 0:
            chunks[i].metadata.prev_chunk_id = chunks[i-1].metadata.index
        if i < len(chunks) - 1:
            chunks[i].metadata.next_chunk_id = chunks[i+1].metadata.index
    
    return chunks

def _validate_chunks(chunks: List[Chunk]) -> bool:
    """
    Valida que los chunks generados sean coherentes.
    
    Args:
        chunks: Lista de chunks a validar
        
    Returns:
        True si los chunks son válidos
    """
    if not chunks:
        return False
    
    for chunk in chunks:
        if not chunk.content.strip():
            return False
        if chunk.metadata.char_start_index < 0:
            return False
        if chunk.metadata.char_end_index <= chunk.metadata.char_start_index:
            return False
    
    return True

# ============================================================================
# FUNCIÓN PRINCIPAL PARA INTEGRACIÓN
# ============================================================================

def create_agentic_chunking_function(
    provider: str = "auto",
    prefer_local: bool = True,
    **kwargs
) -> Callable[[str, int, int], List[Chunk]]:
    """
    Crea una función de chunking agentic configurada para usar con TextChunker.
    
    Args:
        provider: "gemini", "local", o "auto"
        prefer_local: Si usar LLM local como primera opción (solo para "auto")
        **kwargs: Argumentos adicionales para el proveedor específico
        
    Returns:
        Función compatible con AgenticChunkingStrategy
    """
    def chunking_function(text: str, chunk_size: int, chunk_overlap: int) -> List[Chunk]:
        if provider == "gemini":
            return chunk_text_with_gemini(text, chunk_size, chunk_overlap, **kwargs)
        elif provider == "local":
            return chunk_text_with_local_llm(text, chunk_size, chunk_overlap, **kwargs)
        elif provider == "auto":
            return chunk_text_agentic_auto(text, chunk_size, chunk_overlap, prefer_local)
        else:
            raise ValueError(f"Proveedor no soportado: {provider}")
    
    return chunking_function

# ============================================================================
# TESTING Y EJEMPLOS
# ============================================================================

if __name__ == "__main__":
    # Texto de ejemplo para testing
    sample_text = """
    La inteligencia artificial (IA) es una tecnología revolucionaria que está transformando múltiples sectores de la sociedad. 
    Desde sus inicios en la década de 1950, la IA ha evolucionado desde simples programas de ajedrez hasta sistemas complejos 
    capaces de procesar lenguaje natural, reconocer imágenes y tomar decisiones autónomas.
    
    En el ámbito de la medicina, la IA está siendo utilizada para diagnosticar enfermedades con mayor precisión que los médicos humanos. 
    Los algoritmos de aprendizaje automático pueden analizar miles de imágenes médicas en segundos, identificando patrones que podrían 
    pasar desapercibidos para el ojo humano. Esto no solo mejora la precisión del diagnóstico, sino que también reduce significativamente 
    el tiempo necesario para obtener resultados.
    
    El sector financiero también ha adoptado ampliamente la IA para la detección de fraudes, el análisis de riesgos y el trading algorítmico. 
    Los sistemas de IA pueden procesar enormes volúmenes de datos de transacciones en tiempo real, identificando patrones sospechosos 
    y tomando decisiones de inversión basadas en análisis complejos del mercado.
    
    Sin embargo, el desarrollo de la IA también plantea importantes desafíos éticos y sociales. La automatización podría desplazar 
    a millones de trabajadores, mientras que los algoritmos sesgados podrían perpetuar discriminaciones existentes. Es crucial que 
    el desarrollo de la IA se realice de manera responsable, con consideraciones éticas en el centro del proceso de diseño.
    """
    
    print("=== TESTING CHUNKING AGENTIC ===")
    
    # Test con función automática
    try:
        chunking_func = create_agentic_chunking_function("auto", prefer_local=True)
        chunks = chunking_func(sample_text, 500, 100)
        
        print(f"\n✅ Chunking exitoso: {len(chunks)} chunks generados")
        
        for i, chunk in enumerate(chunks):
            print(f"\n--- Chunk {i+1} ---")
            print(f"Título: {chunk.metadata.semantic_title}")
            print(f"Resumen: {chunk.metadata.summary}")
            print(f"Posición: {chunk.metadata.char_start_index}-{chunk.metadata.char_end_index}")
            print(f"Contenido: {chunk.content[:100]}...")
            if chunk.metadata.semantic_overlap:
                print(f"Overlap: {chunk.metadata.semantic_overlap}")
    
    except Exception as e:
        print(f"❌ Error en testing: {e}")
        print("Nota: Asegúrate de tener configurado al menos un proveedor de LLM")

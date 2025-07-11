# Documentación del Sistema de Chunking: `agentic_chunking` y GUIs

Este documento describe la arquitectura y el funcionamiento de los componentes clave del sistema de chunking, diseñado para ser presentado en una reunión técnica.

## 1. `rag_engine/agentic_chunking.py` - El Cerebro del Chunking

Este módulo es el núcleo de la funcionalidad de chunking inteligente. Su responsabilidad principal es comunicarse con los Modelos de Lenguaje (LLMs) para dividir texto de una manera semánticamente rica.

### Funcionalidades Clave:

-   **Doble Proveedor de LLM:** Soporta tanto la API de **Google Gemini** como un **LLM local** (compatible con la API de OpenAI).
-   **Chunking Basado en Prompt:** Utiliza un prompt detallado para guiar al LLM en la tarea de división.
-   **Metadatos Enriquecidos:** El LLM no solo divide el texto, sino que también genera un `título semántico`, un `resumen` y `overlaps semánticos` para cada chunk.
-   **Manejo de Errores:** Incluye lógica para reintentos y manejo de fallos en las llamadas a las APIs.
-   **Estructura Modular:** Las funciones están diseñadas para ser integradas fácilmente en otras partes del sistema, como el `TextChunker` a través de la `AgenticChunkingStrategy`.

### Funciones Principales:

-   `chunk_text_with_gemini(...)`: Orquesta el proceso de chunking usando un modelo de Gemini.
-   `chunk_text_with_local_llm(...)`: Hace lo mismo pero apuntando a un servidor LLM local.
-   `_parse_llm_response(...)`: Una función auxiliar crítica que toma la respuesta del LLM (que puede ser un string JSON o un bloque de código markdown) y la convierte en un diccionario Python.
-   `_convert_to_chunks(...)`: Transforma los datos del diccionario en los objetos `Chunk` estandarizados que usa el resto del sistema.

### Prompt para Chunking Agéntico (`AGENTIC_CHUNKING_PROMPT`)

Este es el prompt exacto que se envía al LLM para instruirlo sobre cómo realizar el chunking.

```
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
```

---

## 2. `rag_engine/agentic_testing_gui.py` - El Laboratorio de Pruebas

Esta es una **herramienta de depuración especializada**. Su único propósito es probar y comparar el rendimiento del chunking agéntico entre Gemini y el LLM local, sin ningún tipo de fallback o lógica de producción.

### Propósito:

-   **Aislar y Depurar:** Permite ejecutar cada proveedor de LLM de forma aislada para identificar problemas específicos de cada uno (ej. errores de API, formato de respuesta, etc.).
-   **Comparación Directa:** Muestra los resultados de ambos modelos lado a lado, facilitando la comparación de la calidad de los chunks, los metadatos generados y los tiempos de respuesta.
-   **Visualización de Logs:** Presenta logs de debug detallados en tiempo real para trazar cada paso del proceso de chunking.

### Flujo de Trabajo Típico:

1.  Cargar un archivo de texto.
2.  Configurar los parámetros (tamaño de chunk, modelos, URL del LLM local).
3.  Ejecutar el test para Gemini, el LLM local, o ambos.
4.  Analizar los logs en busca de errores y los resultados en las tablas comparativas.

**En resumen, esta GUI no es para el usuario final, sino una herramienta de desarrollo para asegurar que el `agentic_chunking.py` funcione correctamente.**

---

## 3. `rag_engine/chunking_playground.py` - El Campo de Juego del RAG

Esta es la **herramienta principal y más completa** para interactuar con todo el sistema de chunking y la base de datos vectorial. Es una aplicación mucho más compleja que la GUI de testing.

### Propósito:

-   **Probar Todas las Estrategias:** A diferencia de la GUI de testing, esta permite experimentar con **todas** las estrategias de chunking: `caracteres`, `palabras`, `semántico` y `agéntico`.
-   **Simulación del Flujo RAG Completo:** Permite no solo crear chunks, sino también generar sus embeddings y guardarlos en la base de datos vectorial SQLite.
-   **Búsqueda Vectorial:** Incluye una interfaz para realizar búsquedas de similitud sobre la base de datos, completando así el ciclo de un sistema RAG (Indexing y Retrieval).
-   **Visualización Integral:** Ofrece una vista completa del estado de la base de datos, estadísticas y resultados de búsqueda.

### Flujo de Trabajo Típico:

1.  Cargar un archivo de texto.
2.  Seleccionar una estrategia de chunking y ajustar sus parámetros.
3.  Visualizar los chunks generados.
4.  Guardar los chunks en la base de datos (esto genera los embeddings).
5.  Realizar búsquedas semánticas para probar la eficacia de los chunks generados.

**En resumen, esta es la herramienta para entender y optimizar el rendimiento del sistema RAG de principio a fin.**

---

## Comparativa de GUIs: `Testing GUI` vs. `Playground`

| Característica         | `agentic_testing_gui.py` (Laboratorio)                               | `chunking_playground.py` (Campo de Juego)                                |
| ---------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **Propósito**          | Depurar y comparar Gemini vs. Local de forma aislada.                | Probar y visualizar todo el flujo RAG.                                   |
| **Estrategias**        | Solo `agéntico`.                                                     | `caracteres`, `palabras`, `semántico`, `agéntico`.                       |
| **Base de Datos**      | No interactúa con la base de datos.                                  | Sí, guarda y busca en la base de datos vectorial.                        |
| **Complejidad**        | Simple, enfocada en una tarea.                                       | Alta, cubre múltiples funcionalidades (chunking, embedding, búsqueda).   |
| **Usuario Objetivo**   | Desarrollador que trabaja en `agentic_chunking.py`.                  | Desarrollador o analista que optimiza el sistema RAG completo.           |

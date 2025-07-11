# 🧠 Guía de Estudio del Módulo RAG Engine

Este documento explica la arquitectura y el funcionamiento interno del `rag_engine`, un sistema modular para implementar pipelines de Retrieval-Augmented Generation (RAG). Está diseñado para ser una guía de estudio que te permita entender cada componente y cómo interactúan entre sí.

## 🗺️ Arquitectura General

El módulo sigue un diseño desacoplado, donde cada componente tiene una responsabilidad única. Esto facilita la experimentación y la sustitución de piezas (por ejemplo, cambiar el modelo de embedding o la base de datos) sin afectar al resto del sistema.

El flujo de datos principal es el siguiente:

1.  **Texto de entrada**: Se parte de un documento o texto largo.
2.  **Chunking**: El texto se divide en fragmentos más pequeños y manejables (`chunks`) usando el `chunker`.
3.  **Embedding**: Cada `chunk` se convierte en un vector numérico (`embedding`) que captura su significado semántico. Esto lo hace el `embedder`.
4.  **Almacenamiento**: Los `chunks` y sus `embeddings` correspondientes se guardan en una base de datos vectorial (`database`).
5.  **Búsqueda**: Cuando se hace una pregunta, se convierte en un `embedding` y se usa para buscar los `chunks` más similares en la base de datos.

--- 

## 📁 Desglose de Ficheros y Clases

A continuación se detalla el propósito de cada fichero y las clases que contiene.

### 1. `config.py`

-   **Propósito**: Centraliza toda la configuración del módulo. Es el primer sitio que debes mirar si quieres cambiar el comportamiento del sistema.
-   **Variables Clave**:
    -   `DB_PATH`: Ruta al fichero de la base de datos SQLite.
    -   `DB_TABLE_NAME`: Nombre de la tabla para los vectores.
    -   `CHUNK_SIZE`, `CHUNK_OVERLAP`: Parámetros por defecto para el chunking.
    -   `EMBEDDER_TYPE`: Define qué motor de embeddings usar (`'local'` o `'api'`).
    -   `LOCAL_EMBEDDER_MODEL`: Nombre del modelo de `sentence-transformers` a usar localmente.

### 2. `chunker.py` ⭐ **ACTUALIZADO CON CHUNKING SEMÁNTICO**

-   **Propósito**: Dividir texto en fragmentos (`chunks`) usando diferentes estrategias.
-   **Arquitectura**: Implementa el **Patrón Strategy** para permitir diferentes algoritmos de chunking.
-   **Estrategias Disponibles**:
    -   🔤 **Caracteres**: División por tamaño fijo.
    -   📝 **Palabras**: División respetando límites de palabras.
    -   🧠 **Semántico**: División por estructura natural (párrafos, frases, puntuación).
    -   🤖 **Agentic**: Utiliza LLMs para una división inteligente (orquestado desde la GUI y `agentic_chunking.py`).

-   **Clases Principales**:
    -   `ChunkingStrategy` (ABC): Interfaz base para todas las estrategias.
    -   `SemanticChunkingStrategy`: Divide por párrafos y frases, agrupa hasta tamaño óptimo.
    -   `TextChunker`: Clase principal que orquesta las estrategias.
        -   `set_strategy(strategy)`: Cambia la estrategia de chunking dinámicamente.

-   **Función de Conveniencia**: `chunk_text(text, strategy='caracteres')` para uso rápido

### 3. `embedder.py`

-   **Propósito**: Convertir texto en vectores (`embeddings`). Utiliza el **Patrón de Diseño Strategy** para permitir diferentes "estrategias" de embedding (local vs. API).
-   **Clases**:
    -   `Embedder` (Clase Base Abstracta): Define la interfaz que todos los embedders deben seguir. Su único método es `embed(self, chunks)`.
    -   `LocalEmbedder(Embedder)`: Implementación que usa la librería `sentence-transformers` para generar embeddings en tu propia máquina (usará la GPU si está disponible).
    -   `APIEmbedder(Embedder)`: Implementación que llama a una API externa (compatible con OpenAI) para generar los embeddings.
    -   `EmbedderFactory`:
        -   `create_embedder(embedder_type)`: Un método estático que lee la configuración (`EMBEDDER_TYPE`) y te devuelve la instancia correcta (`LocalEmbedder` o `APIEmbedder`) sin que tengas que preocuparte por cuál usar. Esto desacopla el resto del código de la implementación concreta del embedder.

### 4. `database.py`

-   **Propósito**: Gestionar el almacenamiento y la búsqueda de vectores en una base de datos.
-   **Tecnología Clave**: **`sqlite-vec`**. Es una extensión de SQLite que le añade capacidades de base de datos vectorial. Permite hacer búsquedas de similitud de forma muy eficiente sin necesidad de un sistema externo como FAISS o ChromaDB.
-   **Clase Principal**: `SQLiteVecDatabase`
    -   `__init__(self, db_path, table_name)`: Se conecta a la base de datos SQLite y carga la extensión `sqlite-vec`.
    -   `_create_table_if_not_exists(self, vector_dim)`: Crea la tabla necesaria para guardar los `chunks` y sus `embeddings`.
    -   `add_documents(self, documents)`: Recibe una lista de tuplas `(chunk, embedding)` y las guarda en la base de datos. Es un método optimizado para inserciones masivas.
    -   `search_similar(self, query_embedding, top_k)`: **El corazón de la búsqueda RAG**. Recibe el embedding de una pregunta y devuelve los `k` chunks más similares de la base de datos, usando las funciones de `sqlite-vec` para el cálculo de similitud.

### 5. `agentic_chunking.py`

-   **Propósito**: Contiene toda la lógica para realizar el chunking utilizando LLMs. Este módulo se llama directamente desde las GUIs.
-   **Funciones Clave**:
    -   `chunk_text_with_gemini(text, chunk_size, ...)`: Envía el texto y un prompt específico a la API de Google Gemini para obtener los chunks.
    -   `chunk_text_with_local_llm(text, chunk_size, ...)`: Se comunica con un endpoint de API local (como el `llm_service`) para realizar el chunking con un modelo GGUF.
    -   Manejo de errores explícito para fallos de API, timeouts, etc.

### 6. `agentic_testing_gui.py`

-   **Propósito**: Una GUI de testing dedicada exclusivamente al chunking agéntico. Permite probar los proveedores (Gemini y LLM local) de forma aislada, sin fallbacks, para una depuración rápida y efectiva.
-   **Características**:
    -   Selección directa del proveedor a probar.
    -   Visor de logs en tiempo real para ver las peticiones y respuestas de la API.
    -   Muestra de errores de forma clara y directa en la interfaz.

### 7. `chunking_playground.py`

-   **Propósito**: Es una herramienta de desarrollo con interfaz gráfica (GUI) construida con Tkinter. **Orquesta todos los módulos anteriores** para que puedas experimentar visualmente con un sistema RAG completo.
-   **Clase Principal**: `ChunkingPlayground` - **Interfaz de 3 paneles (v2.6.1)**
    -   **Panel Izquierdo (Configuración)**: 
        - Carga texto desde archivos .txt
        - Selección de estrategia de chunking (caracteres, palabras, semántico, agentic)
        - Configuración visual de parámetros (chunk_size, overlap)
        - Vista de chunks resultantes con índices y previews
        - **Botón "Guardar en BD"**: Flujo completo RAG:
            1. Toma los `chunks` de la tabla izquierda
            2. Llama a `EmbedderFactory.create_embedder()` para obtener el motor de embeddings
            3. Usa el `embedder` para convertir los `chunks` en `embeddings`
            4. Crea una instancia de `SQLiteVecDatabase`
            5. Llama a `db.add_documents()` para guardar todo en la base de datos
    -   **Panel Central (Base de Datos)**: 
        - Estadísticas en tiempo real de la BD vectorial
        - Ejemplo de chunk con información de embedding
        - Tabla con los primeros 20 chunks almacenados
        - Botón de actualización manual
    -   **Panel Derecho (Búsquedas Vectoriales)**: 
        - **Campo de consulta** para búsquedas semánticas
        - **Configuración Top K** (1-20 resultados)
        - **Tabla de chunks generados** con metadatos: ID, Título, Resumen, Contenido (preview) y Chars.
        - **Ventana emergente con detalles completos** al hacer doble clic en un chunk.
    -   **Panel Derecho (Búsquedas Vectoriales)**: 
        - **Campo de consulta** para búsquedas semánticas
        - **Configuración Top K** (1-20 resultados)
        - **Tabla de resultados** con ranking, similitud y preview
        - **Ventanas emergentes** para ver contenido completo
        - **Información detallada** de cada búsqueda realizada
        - **Funciones de limpieza** para resetear consultas

--- 

## 🚀 Cómo se Relaciona Todo (Diagrama Conceptual)

```
+----------------------------------+
| chunking_playground.py v2.7.1   | (Interfaz Gráfica de 3 Paneles)
| Panel Izq | Panel Central | Panel Der |
| Chunking  | Base Datos   | Búsquedas  |
+----------------------------------+
           |           
           | (Orquesta todos los módulos RAG)
           v
.------------------------------------------------.
| Carga Texto -> [ chunker.py ] -> Chunks        |
|                  (TextChunker)                 |
|                      |                         |
|                      v                         |
|                  [ embedder.py ] -> Embeddings |
|                  (EmbedderFactory)             |
|                      |                         |
|                      v                         |
|                  [ database.py ] -> Guardado   |
|                  (SQLiteVecDatabase)           |
'------------------------------------------------'
```

## 📚 Ejemplos de Uso

### Uso Básico con Diferentes Estrategias

```python
from chunker import TextChunker, chunk_text

# Método 1: Función de conveniencia
text = "Tu texto aquí..."
chunks_semanticos = chunk_text(text, strategy='semantico')
chunks_por_palabras = chunk_text(text, strategy='palabras')

# Método 2: Usando la clase directamente
chunker = TextChunker(chunk_size=1000, chunk_overlap=200, strategy='semantico')
chunks = chunker.chunk(text)

# Cambiar estrategia dinámicamente
chunker.set_strategy('agentic')
chunks_agentic = chunker.chunk(text)
```

### Chunking Semántico Avanzado

```python
# El chunking semántico respeta la estructura natural del texto:
# - Divide por párrafos primero
# - Luego por frases si es necesario
# - Agrupa hasta alcanzar el tamaño óptimo
# - Mantiene coherencia semántica

chunker = TextChunker(strategy='semantico')
text = """
Capítulo 1: Introducción

Este es el primer párrafo que explica conceptos básicos.
Contiene varias frases relacionadas.

Este es el segundo párrafo con información adicional.
También tiene múltiples frases coherentes.
"""

chunks = chunker.chunk(text)
# Resultado: chunks que respetan párrafos y mantienen coherencia
```

### Chunking Agentic en Acción

```python
# El chunking agéntico ya no usa un "hook".
# Se llama directamente a las funciones específicas desde la GUI.

from agentic_chunking import chunk_text_with_gemini, chunk_text_with_local_llm

text = "Tu texto largo y complejo aquí..."

# Ejemplo con Google Gemini
try:
    chunks_gemini = chunk_text_with_gemini(text, chunk_size=1024)
    print("Chunks generados con Gemini:", chunks_gemini)
except Exception as e:
    print(f"Error con Gemini: {e}")

# Ejemplo con un LLM local (a través de su API)
try:
    chunks_local = chunk_text_with_local_llm(text, chunk_size=1024)
    print("Chunks generados con LLM Local:", chunks_local)
except Exception as e:
    print(f"Error con el LLM local: {e}")
```

### Uso en la GUI

1. **Ejecutar la aplicación**:
   ```bash
   python rag_engine/chunking_playground.py
   ```

2. **Seleccionar estrategia**: Usar los radiobuttons para elegir entre:
   - 🔤 **Caracteres**: División tradicional por tamaño fijo
   - 📝 **Palabras**: Respeta límites de palabras
   - 🧠 **Semántico**: División inteligente por estructura
   - 🤖 **Agentic**: Usa LLMs (Gemini/Local) para chunking inteligente (¡totalmente funcional!)

3. **Ajustar parámetros**: Tamaño de chunk y solapamiento

4. **Procesar**: Los chunks se generan automáticamente al cambiar parámetros

5. **Visualizar**: Ver chunks generados, embeddings y estadísticas

---

Este `README` te da una base sólida para entender cómo funciona cada pieza del sistema RAG con chunking semántico y agentic. ¡El sistema ahora es mucho más flexible y potente!

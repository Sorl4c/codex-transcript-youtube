# Módulo de IA - YouTube Subtitle Downloader

Este documento proporciona instrucciones para configurar y utilizar el módulo de IA para resumen de texto dentro del proyecto YouTube Subtitle Downloader.

**Estado Actual (v2.7.1):**
- ✅ Módulo RAG (Retrieval-Augmented Generation) con soporte para búsqueda semántica
- ✅ Almacenamiento vectorial eficiente con SQLite + sqlite-vec
- ✅ Generación de embeddings con modelos locales (sentence-transformers)
- ✅ Soporte para CPU/GPU con CUDA (RTX 5070 Ti verificada)
- ✅ Procesamiento por lotes de documentos
- ✅ Sistema avanzado de chunking con múltiples estrategias:
  - ✅ Chunking por caracteres (tradicional) con solapamiento configurable
  - ✅ Chunking por palabras respetando límites léxicos
  - ✅ Chunking semántico basado en estructura natural (párrafos/frases)
  - ✅ **Chunking Agentic con LLMs (Gemini/Local) totalmente funcional y depurado**

- ✅ Soporte para múltiples modelos GGUF (TinyLlama, Mistral, Mixtral, LLaMA 2)
- ✅ Integración con Gemini API para resúmenes en la nube
- ✅ Cálculo automático de costos por token para Gemini
- ✅ Pipeline nativo optimizado con soporte para chunking configurable
- ✅ Integración completa con LangChain
- ✅ Sistema de benchmarking comparativo entre modelos locales y en la nube
- ✅ Generación de informes detallados en Markdown con métricas de costo-efectividad
- ✅ Sistema de pruebas unitarias completo
- ✅ Manejo de errores y validación robustos
- ✅ Soporte multilingüe mejorado
- ✅ Gestión avanzada de vídeos con interfaz intuitiva

> **Nota sobre GPU**: Se ha verificado el funcionamiento con CUDA 12.9. Para más detalles, consulta la [Guía de configuración CUDA/WSL2](./GUIA_CUDA_WSL.md).

## Modos de Uso: CLI y GUI

Actualmente existen dos formas principales de interacción:

### CLI (Command Line Interface)
- **Estado:** Experimental. El script `summarize_transcript.py` sirve para pruebas de prompt y ajuste de parámetros.
- **Limitación:** No soporta procesamiento por lotes (solo un archivo/transcripción por ejecución).
- **Ejemplo:**
  ```bash
  python ia/summarize_transcript.py -i entrada.txt -o salida.txt --max-tokens 2048
  ```
- **Uso típico:** Ajuste de prompts, pruebas rápidas desde terminal.

### Interfaz Web con Streamlit
- **Estado:** Implementación principal y recomendada para uso interactivo
- **Características principales:**
  - Interfaz web moderna y responsiva accesible desde cualquier navegador
  - Gestión avanzada de vídeos con vista previa en tiempo real
  - Soporte para procesamiento por lotes con modelos de IA (Gemini, modelos locales)
  - Panel de depuración integrado para diagnóstico
  - Filtros por canal y búsqueda de vídeos
  - Visualización y edición de metadatos y resúmenes
  - Exportación de datos en formato JSON o CSV

> **Nota:** La interfaz Streamlit está orientada a la gestión y análisis de vídeos. El benchmarking de modelos solo está disponible por CLI, no desde la interfaz web.

### GUI Legacy (tkinter)
- **Estado:** Mantenimiento, se recomienda migrar a la interfaz Streamlit
- **Características:**
  - Aplicación de escritorio independiente
  - Soporte básico para gestión de vídeos
  - Ordenación por columnas
  - Procesamiento por lotes

---

> **NOTA:** El próximo objetivo es unificar la UX: al procesar un vídeo, guardar el transcript completo (como ya se hace) y, además, guardar el resumen generado en un nuevo campo de la base de datos. 
> 
> **PRÓXIMO OBJETIVO: Implementación de RAG**
> 
> El siguiente gran hito del proyecto es la implementación de un sistema **Retrieval-Augmented Generation (RAG)**. El objetivo es crear un motor de búsqueda semántica que permita a los usuarios hacer preguntas en lenguaje natural sobre el contenido de los vídeos almacenados y obtener respuestas precisas y contextualizadas, citando las fuentes originales.
> 
> **Nota:** Con la estabilización de la interfaz de Streamlit, el trabajo en la UI se considera pausado para centrar todos los esfuerzos en esta nueva funcionalidad.

## Arquitectura Modular y Flujo Típico

1. Descarga de vídeo/audio (yt-dlp)
2. Transcripción automática (whisper/whisper.cpp)
3. Procesamiento/resumen (CLI o GUI, ambos usan microservicio LLM local)
4. Exportación y visualización de resultados

---

## Microservicio LLM Local (OpenAI Compatible)

Servicio de alto rendimiento para servir modelos GGUF locales a través de una API HTTP compatible con OpenAI. Optimizado para procesamiento de contexto largo y uso eficiente de GPU.

**🚀 Características Principales**
- **API 100% compatible con OpenAI** - Usa los mismos endpoints y formatos de petición/respuesta
- **Soporte para modelos avanzados** - Qwen2-7B, Mistral, TinyLlama y más
- **Contexto extenso** - Hasta 10,000 tokens probados sin pérdida de calidad
- **Alto rendimiento** - 300-400 tokens/segundo en RTX 5070 Ti
- **Streaming eficiente** - Respuestas token por token con baja latencia
- **Configuración flexible** - Ajustes vía variables de entorno

**📊 Rendimiento Verificado**
- **Respuestas cortas**: < 2 segundos
- **Textos largos (8000+ tokens)**: ~6 segundos
- **Uso de GPU**: Optimizado para carga completa en VRAM
- **Concurrencia**: Múltiples peticiones simultáneas con gestión de recursos

**🔧 Casos de Uso Verificados**
- Resúmenes de texto (50-300 palabras)
- Clasificación temática
- Procesamiento de documentos largos
- Generación de contenido estructurado

**📚 Documentación Detallada**
Para configuración avanzada, ejemplos de uso y solución de problemas, consulta:
➡️ **[Documentación Completa del Microservicio](../llm_service/README.md)**

## 1.1 Requisitos para Modelos Locales

Antes de comenzar, asegúrate de tener lo siguiente:

- **Python**: Versión 3.8 o superior.
- **WSL (Windows Subsystem for Linux)**: **Recomendado para aceleración GPU**.
    - Para verificar si WSL está instalado y tu distribución, ejecuta en PowerShell o CMD: `wsl --list --verbose`
    - Asegúrate de usar WSL 2.
- **GPU NVIDIA (opcional)**: Para aceleración GPU, necesitarás una GPU compatible con CUDA (ej: GeForce RTX 5070 Ti).
- **Controladores NVIDIA**: Últimos controladores instalados en Windows.
- **Toolkit CUDA (solo si usas GPU)**: Debe instalarse dentro de WSL.
    - Verifica con: `nvidia-smi` y `nvcc --version`
    - Sigue las guías oficiales de NVIDIA para instalar CUDA Toolkit en WSL si es necesario.

### 1.2 Requisitos para Gemini API

Para utilizar la integración con Gemini API:

1. **Cuenta de Google Cloud**: Necesitarás una cuenta de Google Cloud con facturación habilitada.
2. **Clave de API de Gemini**: 
   - Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Crea una nueva clave de API
   - Configura la variable de entorno:
     ```bash
     export GEMINI_API_KEY='tu-clave-api-aquí'
     ```
   O proporciónala como argumento al ejecutar el script.

3. **Límites de cuota**: Revisa y ajusta los límites de cuota según sea necesario en Google Cloud Console.

## 2. Configuración e Instalación

### 2.1 Configuración Básica (CPU/GPU)

Antes de comenzar, asegúrate de tener lo siguiente:

- **Python**: Versión 3.8 o superior.
- **WSL (Windows Subsystem for Linux)**: **Recomendado para aceleración GPU**.
    - Para verificar si WSL está instalado y tu distribución, ejecuta en PowerShell o CMD: `wsl --list --verbose`
    - Asegúrate de usar WSL 2.
- **GPU NVIDIA (opcional)**: Para aceleración GPU, necesitarás una GPU compatible con CUDA (ej: GeForce RTX 5070 Ti).
- **Controladores NVIDIA**: Últimos controladores instalados en Windows.
- **Toolkit CUDA (solo si usas GPU)**: Debe instalarse dentro de WSL.
    - Verifica con: `nvidia-smi` y `nvcc --version`
    - Sigue las guías oficiales de NVIDIA para instalar CUDA Toolkit en WSL si es necesario.

## 2. Configuración e Instalación

### Configuración Básica (CPU)

1. **Navegar al directorio del proyecto**:
   ```bash
   cd /mnt/c/local/tools/tools/yt-dlp
   ```

2. **Crear y activar entorno virtual**:
   ```bash
   python3 -m venv venv-yt-ia
   source venv-yt-ia/bin/activate
   ```

3. **Instalar dependencias básicas**:
   ```bash
   pip install llama-cpp-python numpy
   ```

### Configuración Avanzada (GPU - Pendiente)

Para habilitar la aceleración por GPU con una RTX 5070 Ti:

1. **Instalar compiladores y CMake**:
   ```bash
   sudo apt update && sudo apt install -y build-essential cmake
   ```

2. **Reinstalar llama-cpp-python con soporte CUDA**:
   ```bash
   CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install --upgrade --force-reinstall llama-cpp-python --no-cache-dir
   ```

3. **Verificar instalación CUDA**:
   ```bash
   nvidia-smi
   nvcc --version
   ```

## 3. Configuración de Modelos

El módulo de IA requiere modelos en formato GGUF. Hasta ahora hemos probado con éxito TinyLlama en CPU.

### Modelos Probados

1. **TinyLlama (1.1B parámetros)**
   - **Estado**: ✅ Funciona correctamente en CPU/GPU
   - **Tamaño**: ~700MB (versión cuantizada)
   - **Rendimiento**: Aceptable para pruebas, recomendado usar GPU para producción
   - **Ubicación recomendada**: `C:\local\modelos\tinyllama.gguf`
   - **Uso con CUDA**: Configura `n_gpu_layers=-1` para máxima aceleración

2. **Configuración de modelos**
   - Los modelos se cargan bajo demanda
   - Se soportan tanto el pipeline nativo como LangChain
   - Los parámetros de generación son configurables en tiempo de ejecución

### Estructura de Directorios

```
yt-dlp/
├── ia/
│   ├── __init__.py
│   ├── ia_models.py    # Carga de modelos
│   ├── ia_processor.py # Procesamiento de texto
│   ├── test_ia.py      # Pruebas del módulo
│   └── prompts/        # Plantillas de prompts
│       └── summary.txt
└── modelos/            # Directorio para modelos GGUF
    └── tinyllama.gguf  # Modelo actual
```

### Uso del Módulo de IA

#### Inicialización básica
```python
from ia.core import initialize_llm, map_summarize_chunk, reduce_summaries

# Inicializar el modelo (CPU/GPU automático)
llm = initialize_llm(
    model_path="/ruta/al/modelo.gguf",
    pipeline_type="native",  # o "langchain"
    n_ctx=2048,             # contexto máximo
    n_gpu_layers=-1         # -1 para usar todas las capas en GPU
)

# Configuración de generación
generation_params = {
    "temperature": 0.1,
    "max_tokens": 512,
    "top_p": 0.9
}

# Resumir un fragmento de texto
summary = map_summarize_chunk(
    llm,
    "Texto a resumir...",
    "Resume el siguiente texto: {text}",
    generation_params
)

# Combinar múltiples resúmenes
combined = reduce_summaries(
    llm,
    ["Resumen 1", "Resumen 2"],
    "Combina estos resúmenes: {text}",
    generation_params
)
```

### Añadir Nuevos Modelos

1. Descarga el modelo GGUF (recomendado desde [TheBloke en Hugging Face](https://huggingface.co/TheBloke))
2. Colócalo en `C:\local\modelos\`
3. El sistema detectará automáticamente modelos en esta ubicación

## 4. Pruebas del Módulo

El módulo incluye un conjunto completo de pruebas unitarias que verifican:

- Carga de modelos (nativo y LangChain)
- Procesamiento de texto con diferentes configuraciones
- Manejo de errores y casos límite
- Compatibilidad con diferentes tamaños de contexto

### Ejecutar pruebas

```bash
# Navegar al directorio del proyecto
cd /mnt/c/local/tools/tools/yt-dlp

# Activar entorno virtual (si no está activo)
source venv-yt-ia/bin/activate

# Ejecutar pruebas unitarias
python -m unittest ia.tests.test_core

# Ejecutar pruebas con cobertura (opcional)
pip install coverage
coverage run -m unittest ia.tests.test_core
coverage report -m
```

### Estructura de pruebas

- `test_core.py`: Pruebas unitarias para las funciones principales
  - Carga de plantillas de prompts
  - Inicialización de modelos
  - Funciones de mapeo y reducción
  - Manejo de errores

**Salida esperada**:
```
=== PRUEBA DE MODELO TINYLLAMA ===
Iniciando prueba con el modelo...

1. Cargando modelo (esto puede tardar un momento)...
✓ Modelo cargado en 18.0 segundos

2. Probando generación de texto...
Prompt: 'Ponme un título creativo para un video sobre programación en Python'

✓ Resultado generado:
--------------------------------------------------
y Python.
--------------------------------------------------

Tiempo de generación: 0.21 segundos
```

### test_ia.py

Prueba más completa que utiliza el módulo de IA para procesar texto de ejemplo.

```bash
python test_ia.py
```

## 5. Sistema Avanzado de Chunking

El sistema ahora incluye un avanzado módulo de chunking con múltiples estrategias implementadas mediante el patrón Strategy.

### 5.1 Estrategias Disponibles

- **Chunking por Caracteres**: Estrategia tradicional que divide el texto en fragmentos de tamaño fijo.
  ```python
  from rag_engine.chunker import chunk_text
  chunks = chunk_text(texto, strategy='caracteres', chunk_size=1000, chunk_overlap=200)
  ```

- **Chunking por Palabras**: Divide respetando límites de palabras para evitar cortes abruptos.
  ```python
  chunks = chunk_text(texto, strategy='palabras', chunk_size=1000, chunk_overlap=200)
  ```

- **Chunking Semántico**: Divide respetando la estructura natural del texto (párrafos y frases).
  ```python
  # Mantiene párrafos juntos cuando es posible y preserva la coherencia semántica
  chunks = chunk_text(texto, strategy='semantico', chunk_size=1000, chunk_overlap=200)
  ```

- **Chunking Agentic (con LLMs)**: Sistema de división de texto **totalmente funcional y robusto** que utiliza LLMs (Google Gemini o un modelo local) para realizar un chunking inteligente basado en el contenido semántico.
  - **Selección Directa de Proveedor**: Elige explícitamente entre "Google Gemini" y "LLM Local" en la GUI.
  - **Sin Fallbacks**: El sistema ya no recurre a otras estrategias si un LLM falla. Los errores de API se muestran directamente para un diagnóstico claro.
  - **Alta Coherencia Semántica**: Los LLMs analizan el texto para identificar los puntos de división más lógicos, creando chunks con un alto grado de coherencia interna.

  ```python
  # En la GUI, simplemente selecciona la estrategia "Agentic"
  # y el proveedor deseado (Gemini o Local).
  
  # Ejemplo de uso directo (como en la GUI):
  from rag_engine.agentic_chunking import chunk_text_with_gemini, chunk_text_with_local_llm

  # Usar Gemini
  chunks_gemini = chunk_text_with_gemini(texto, chunk_size=1024, chunk_overlap=200)

  # Usar LLM Local
  chunks_local = chunk_text_with_local_llm(texto, chunk_size=1024, chunk_overlap=200)
  ```

### 5.2 Chunking Playground

El sistema incluye una interfaz gráfica para experimentar con diferentes estrategias de chunking:

```bash
python rag_engine/chunking_playground.py
```

Funcionalidades:
- Carga de texto desde archivos o entrada manual
- Selección de estrategia de chunking (caracteres, palabras, semántico, agentic)
- Configuración de tamaño y solapamiento
- Visualización de chunks generados con metadatos (ID, Título, Resumen, Contenido, Chars)
- Ventana emergente con detalles completos del chunk (doble clic)
- Almacenamiento en base de datos vectorial
- Visualización de embeddings

### 5.3 Prueba de Estrategias

Para comparar el rendimiento de las diferentes estrategias:

```bash
python rag_engine/test_chunking_strategies.py
```

Este script demuestra las diferencias entre cada estrategia utilizando textos de ejemplo con estructura clara.

## 6. Uso de Gemini API

### 6.1 Configuración Básica

Para utilizar Gemini API, sigue estos pasos:

1. **Configura tu clave de API** (puedes usar variable de entorno o parámetro):
   ```bash
   # Usando variable de entorno
   export GEMINI_API_KEY='tu-clave-api-aquí'
   
   # O como parámetro
   python bench.py --pipeline gemini --gemini-api-key 'tu-clave-api-aquí'
   ```

2. **Ejecuta el benchmark con Gemini**:
   ```bash
   python bench.py \
     --input-file ia/sample_text.txt \
     --prompt-dir ia/prompts \
     --pipeline gemini \
     --gemini-model gemini-1.5-flash-latest  # Modelo por defecto
   ```

### 5.2 Modelos Disponibles

- `gemini-1.5-flash`: Equilibrio entre velocidad y costo (recomendado)
- `gemini-1.5-pro`: Mayor capacidad, mayor costo
- `gemini-1.0-pro`: Versión anterior

### 5.3 Control de Costos

El costo se calcula automáticamente basado en:
- Tokens de entrada: $0.35 por millón de tokens
- Tokens de salida: $1.05 por millón de tokens

Ejemplo de salida de costos:
```
Tokens de entrada: 1,234 (Costo: $0.00043)
Tokens de salida: 456 (Costo: $0.00048)
Costo total: $0.00091
```

## 6. Solución de Problemas

### Problemas Comunes con Modelos Locales

#### Modelo no encontrado
```
Error: No se encontró el modelo en /mnt/c/local/modelos/tinyllama.gguf
```
**Solución**:
- Verifica que el archivo del modelo existe en la ruta especificada
- Asegúrate de tener permisos de lectura

#### Errores de GPU / CUDA
```
Could not load library cublas
CUDA error: no kernel image is available for execution
```
**Solución**:
1. Verifica los controladores de NVIDIA en Windows
2. Instala CUDA Toolkit en WSL
3. Reinstala llama-cpp-python con soporte CUDA:
   ```bash
   CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install --upgrade --force-reinstall llama-cpp-python --no-cache-dir
   ```

#### Errores de importación
```
ModuleNotFoundError: No module named 'ia.ia_models'
```
**Solución**:
- Asegúrate de ejecutar los scripts desde el directorio raíz del proyecto
- Verifica que el directorio `ia` tenga un archivo `__init__.py`

### Problemas con Gemini API

**Problema:** Errores de cuota (`429 Too Many Requests`).

**Solución (Implementada):**
- **Modelo por defecto cambiado**: El sistema ahora usa `gemini-1.5-flash-latest` por defecto, que tiene un nivel gratuito más generoso.
- **Configuración centralizada**: Todas las partes de la aplicación (GUI, CLI, benchmarks) ahora usan la configuración del modelo definida en `ia/gemini_api.py`, asegurando consistencia.

#### Error de autenticación
```
google.api_core.exceptions.PermissionDenied: 403 Permission denied on resource project _
```
**Solución**:
- Verifica que la clave de API sea correcta y tenga permisos suficientes
- Asegúrate de que la facturación esté habilitada en tu proyecto de Google Cloud

#### Límite de cuota excedido
```
429 Resource has been exhausted
```
**Solución**:
- Espera unos minutos antes de realizar más solicitudes
- Verifica y ajusta los límites de cuota en Google Cloud Console
- Considera implementar un sistema de reintentos con backoff exponencial

## 7. Módulo RAG (Retrieval-Augmented Generation)

El módulo RAG permite realizar búsquedas semánticas sobre las transcripciones de los vídeos, encontrando fragmentos relevantes basados en el significado en lugar de solo palabras clave.

### Características Principales

- **Chunking Inteligente**: Divide el texto en fragmentos con solapamiento para mantener el contexto
- **Embeddings Locales**: Usa modelos sentence-transformers (all-MiniLM-L6-v2 por defecto)
- **Almacenamiento Eficiente**: Vectores almacenados en SQLite con extensión sqlite-vec
- **Búsqueda Semántica**: Encuentra contenido relevante basado en similitud de significado
- **Soporte GPU**: Aceleración con CUDA para generación de embeddings

### Uso Básico

```python
from rag_engine.ingestor import RAGIngestor

# Inicializar el ingestor (crea la base de datos si no existe)
ingestor = RAGIngestor()

# Ingresar texto (puede ser una transcripción de vídeo)
texto = """
[Contenido de la transcripción...]
"""

# Procesar y almacenar el texto
ingestor.ingest_text(texto)

# Buscar contenido similar
resultados = ingestor.search("tema de búsqueda", top_k=3)
for contenido, similitud in resultados:
    print(f"Similitud: {similitud:.2f}")
    print(contenido)
    print("-" * 80)
```

### Configuración Avanzada

Puedes personalizar el comportamiento del módulo RAG modificando `rag_engine/config.py`:

- `CHUNK_SIZE`: Tamaño de los fragmentos de texto (en tokens)
- `CHUNK_OVERLAP`: Solapamiento entre fragmentos
- `EMBEDDING_MODEL`: Modelo de embeddings a utilizar
- `DB_PATH`: Ubicación del archivo de base de datos
- `DB_TABLE_NAME`: Nombre de la tabla para almacenar los vectores

### RAG Chunking Playground

Herramienta de desarrollo con interfaz gráfica Tkinter para experimentar y ajustar parámetros de chunking:

```bash
# Ejecutar desde el directorio del proyecto
python rag_engine/chunking_playground.py
```

**Características:**
- **Panel de Configuración**: Sliders para ajustar `chunk_size` y `chunk_overlap` en tiempo real
- **Selector de Modo**: Chunking por caracteres o por palabras
- **Vista de Resultados**: Tabla con índice, preview y longitud de cada chunk
- **Base de Datos en Tiempo Real**: Estadísticas y contenido de `rag_database.db`
- **Exportación**: Guardar resultados en formato CSV
- **Manejo de Errores**: La aplicación nunca se cierra por errores, muestra feedback

**Casos de Uso:**
- Ajustar parámetros de chunking antes de procesar documentos grandes
- Visualizar cómo diferentes configuraciones afectan la división del texto
- Inspeccionar el contenido actual de la base de datos vectorial
- Exportar configuraciones de chunking para documentación

### Chunking Agentic Avanzado con Metadatos Enriquecidos (En Desarrollo)

La próxima gran mejora del sistema RAG se centrará en la implementación de una estrategia de **chunking agentic avanzada**. A diferencia del placeholder actual, esta nueva versión no solo dividirá el texto, sino que lo enriquecerá con una capa de metadatos estructurados generados por un LLM. El objetivo es crear chunks "inteligentes" que tengan un conocimiento profundo de su contenido y su relación con los chunks vecinos.

#### Características Clave:

- **Modelo de Datos de Chunk Enriquecido**: Cada chunk será un objeto con:
  - `content`: El texto del chunk.
  - `metadata`:
    - `index`: Índice secuencial.
    - `char_start_index` / `char_end_index`: Posición exacta en el texto original.
    - `semantic_title`: Un título corto generado por el LLM que resume la idea principal.
    - `summary`: Un resumen breve del contenido.
    - `prev_chunk_id` / `next_chunk_id`: Enlaces para reconstruir el contexto completo.
    - `semantic_overlap`: Descripción de la relación semántica con los chunks adyacentes (ej. "continúa la explicación de...", "introduce un nuevo concepto sobre...").

- **Integración con LLMs**: La lógica de chunking y generación de metadatos será manejada por una función LLM inyectable, permitiendo el uso de modelos locales (vía microservicio) o APIs externas (Gemini, OpenAI).

- **Fallback Inteligente**: Si el LLM falla, el sistema recurrirá al chunking semántico y generará una estructura de metadatos básica para mantener la consistencia.

- **Actualización de la Base de Datos**: El esquema de la base de datos vectorial se ampliará para almacenar y consultar estos metadatos enriquecidos, permitiendo búsquedas más contextuales.

- **Visualización en la GUI**: El `Chunking Playground` será actualizado para mostrar los metadatos de cada chunk, facilitando el análisis y la depuración.

Esta funcionalidad transformará el sistema de chunking de una simple herramienta de división de texto a un motor de procesamiento de conocimiento, sentando las bases para un sistema RAG mucho más potente y preciso.

### Próximos Pasos y Mejoras Futuras

- [ ] Integración con la interfaz de Streamlit existente
- [ ] Soporte para múltiples colecciones/namespaces
- [ ] Búsqueda híbrida (semántica + keywords)
- [ ] Indexado incremental de nuevos documentos

## 8. Próximos Pasos

1. **Optimización de rendimiento**
   - Sintonización fina de parámetros de generación
   - Soporte para batch processing
   - Mejora del manejo de memoria para modelos grandes

2. **Nuevas funcionalidades**
   - Integración con el sistema de subtítulos
   - Resumen automático de transcripciones
   - Extracción de palabras clave
   - Generación de títulos y descripciones
   - Soporte para más modelos y formatos

3. **Mejoras en la API**
   - Interfaz más intuitiva
   - Soporte para streaming de respuestas
   - Callbacks para monitoreo de progreso

4. **Documentación ampliada**
   - Guías de inicio rápido
   - Ejemplos de casos de uso
   - Referencia de API completa

## 8. Contribuciones

Este módulo es experimental y se encuentra en desarrollo activo. Las contribuciones son bienvenidas. Algunas áreas de mejora incluyen:

- Mejora en la evaluación de calidad de resúmenes
- Soporte para más proveedores de modelos en la nube
- Optimización de costos para uso en producción
- Mejora en la documentación y ejemplos

## 9. Limitaciones y Futuro Desarrollo

### Limitaciones Actuales
- Los modelos locales tienen limitaciones de contexto (ej: 4096 tokens para Mistral 7B)
- La calidad de los resúmenes puede variar significativamente entre modelos
- El rendimiento en GPU depende fuertemente de la configuración del sistema

### Próximas Características
- [ ] Integración con más proveedores de modelos en la nube
- [ ] Soporte para procesamiento por lotes
- [ ] Interfaz web para configuración y monitoreo
- [ ] Sistema de caché para reducir costos
- [ ] Soporte para más tareas de procesamiento de lenguaje natural

### Notas de Versión
Para ver el historial completo de cambios, consulta el archivo [CHANGELOG.md](./CHANGELOG.md).

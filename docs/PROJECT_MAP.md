# Mapa Mental del Proyecto

```mermaid
mindmap
  root((YouTube Subtitle\nDownloader v2.8.0))
    ├── 🔄 Control de Versiones
    │   ├── 🌐 Repositorio en GitHub
    │   │   └── 🔗 https://github.com/Sorl4c/codex-transcript-youtube
    │   ├── 📋 .gitignore optimizado
    │   │   ├── 🔹 Exclusión de archivos temporales
    │   │   ├── 🔹 Exclusión de entornos virtuales
    │   │   └── 🔹 Exclusión de archivos sensibles
    │   └── 🔄 Flujo de trabajo Git
    │       ├── 🔹 Rama principal (main)
    │       └── 🔹 Ramas de características
    │
    ├── 📦 Módulos Principales
    │   ├── 📄 main.py
    │   │   ├── 🔹 Procesamiento CLI
    │   │   ├── 🔹 Manejo de argumentos
    │   │   └── 🔹 Orquestación
    │   │
    │   ├── 🖥️ Interfaz Gráfica
    │   │   ├── 📄 gui_streamlit.py
    │   │   │   ├── 🔹 Interfaz web principal (Streamlit)
    │   │   │   ├── 🔹 Gestión y análisis de vídeos
    │   │   │   ├── 🔹 Procesamiento por lotes con IA (Gemini, modelos locales)
    │   │   │   ├── 🔹 Panel de depuración y feedback
    │   │   │   ├── 🔹 Filtros por canal y búsqueda
    │   │   │   ├── 🔹 Exportación de datos (JSON, CSV)
    │   │   │   ├── 🔹 Selección de vídeo mejorada (clic en fila)
    │   │   │   └── 🔹 UI recomendada
    │   │   ├── 📄 gui_unified.py
    │   │   │   ├── 🔹 Interfaz de escritorio legacy (tkinter)
    │   │   │   └── 🔹 Mantenimiento mínimo
    │   │   ├── 📄 gui.py
    │   │   │   └── 🔹 Interfaz gráfica original (deprecada)
    │   │
    │   ├── 🧠 Módulo RAG (v1.1.0)
    │   │   ├── 📄 database.py
    │   │   │   ├── 🔹 Gestión de base de datos vectorial
    │   │   │   ├── 🔹 Almacenamiento eficiente de embeddings
    │   │   │   └── 🔹 Búsqueda semántica
    │   │   ├── 📄 embedder.py
    │   │   │   ├── 🔹 Generación de embeddings locales
    │   │   │   └── 🔹 Soporte para CPU/GPU
    │   │   ├── 📄 chunker.py
    │   │   │   ├── 🔹 Sistema modular de chunking (Strategy Pattern)
    │   │   │   ├── 🔹 Múltiples estrategias: caracteres, palabras, semántico, agentic
    │   │   │   ├── 🔹 Chunking semántico por párrafos/frases
    │   │   │   ├── 🔹 Integración con chunking agéntico
    │   │   │   └── 🔹 Función de conveniencia chunk_text()
    │   │   ├── 📄 agentic_chunking.py
    │   │   │   ├── 🔹 Lógica para chunking con Gemini y LLM local
    │   │   │   ├── 🔹 Manejo de errores de API
    │   │   │   └── 🔹 Prompts específicos para chunking
    │   │   ├── 📄 agentic_testing_gui.py
    │   │   │   ├── 🔹 GUI dedicada para probar proveedores agénticos
    │   │   │   ├── 🔹 Selección directa de Gemini/LLM local
    │   │   │   └── 🔹 Logging de errores en tiempo real
    │   │   ├── 📄 ingestor.py
    │   │   │   ├── 🔹 Procesamiento de documentos
    │   │   │   └── 🔹 Gestión del ciclo de vida RAG
    │   │   ├── 📄 chunking_playground.py
    │   │   │   ├── 🔹 Interfaz Tkinter con 3 paneles para testing completo
    │   │   │   ├── 🔹 Panel izquierdo: Configuración de chunking y estrategias
    │   │   │   ├── 🔹 Panel central: Vista en tiempo real de base de datos
    │   │   │   ├── 🔹 Panel derecho: Búsquedas vectoriales interactivas
    │   │   │   ├── 🔹 Visualización de metadatos de chunks (Título, Resumen)
    │   │   │   ├── 🔹 Búsqueda semántica con Top K configurable
    │   │   │   ├── 🔹 Resultados con ranking y similitud
    │   │   │   └── 🔹 Exportación de resultados y ventanas emergentes
    │   │   ├── 📄 test_chunking_strategies.py
    │   │   │   ├── 🔹 Demostración de estrategias de chunking
    │   │   │   └── 🔹 Pruebas comparativas
    │   │   ├── 📄 config.py
    │   │       └── 🔹 Configuración del sistema RAG
    │   │
    │   ├── ⬇️ downloader.py
    │   │   └── 🔹 Descarga de subtítulos
    │   │
    │   ├── 🔍 parser.py
    │   │   └── 🔹 Conversión VTT a texto
    │   │
    │   ├── 🔄 batch_processor.py
    │   │   └── 🔹 Procesamiento por lotes
    │   │
    │   ├── 🛠️ utils.py
    │   │   └── 🔹 Funciones auxiliares
    │   │
    │   ├── 💾 db.py
    │   │   └── 🔹 Gestión de base de datos SQLite
    │   │
    │   ├── 📊 benchmark/
    │   │   ├── 📄 bench.py
    │   │   │   ├── 🔹 Ejecución de benchmarks
    │   │   │   ├── 🔹 Comparación de pipelines
    │   │   │   ├── 🔹 Generación de métricas
    │   │   │   └── 🔹 Soporte para Gemini API
    │   │   │
    │   │   ├── 📄 compare.py
    │   │   │   ├── 🔹 Análisis comparativo
    │   │   │   ├── 🔹 Generación de informes
    │   │   │   └── 🔹 Visualización de resultados
    │   │   │
    │   │   └── 📂 results/
    │   │       └── 📄 comparison_report.md
    │   │           ├── 🔹 Resumen ejecutivo
    │   │           ├── 🔹 Análisis por prompt
    │   │           └── 🔹 Métricas detalladas
    │   │
    │   ├── 🚀 llm_service/ (Nuevo Microservicio LLM)
    │   │   ├── 📄 main.py             # Aplicación FastAPI
    │   │   ├── 📄 model_loader.py     # Carga y gestión del modelo LLM
    │   │   ├── 📄 config.py           # Configuración del servicio
    │   │   ├── 📄 schemas.py          # Modelos Pydantic (OpenAI compatible)
    │   │   ├── 📄 logger.py           # Logger centralizado
    │   │   ├── 📄 README.md           # Documentación específica del servicio
    │   │   └── 📄 requirements_service.txt # Dependencias del servicio
    │   │
    │   ├── 🧠 Módulo IA (v1.9.0)
    │   │   ├── 📄 core.py
    │   │   │   ├── 🔹 Inicialización de modelos
    │   │   │   └── 🔹 Gestión de recursos
    │   │   │
    │   │   ├── 📄 gemini_api.py
    │   │   │   ├── 🔹 Integración con Google Gemini
    │   │   │   ├── 🔹 Manejo de respuestas estructuradas
    │   │   │   └── 🔹 Gestión de errores de API
    │   │   │   ├── 🔹 Cálculo de costos
    │   │   │   └── 🔹 Manejo de autenticación
    │   │   │
    │   │   ├── 📄 native_pipeline.py
    │   │   │   ├── 🔹 Pipeline nativo optimizado
    │   │   │   └── 🔹 Soporte para múltiples modelos GGUF
    │   │   │
    │   │   └── 📄 langchain_pipeline.py
    │   │       ├── 🔹 Integración con LangChain
    │   │       └── 🔹 Soporte para procesamiento estructurado
    │   │   │   └── 🔹 Configuración por defecto
    │   │   │
    │   │   ├── 📄 native_pipeline.py
    │   │   │   └── 🔹 Pipeline de inferencia directa
    │   │   │
    │   │   ├── 📄 langchain_pipeline.py
    │   │   │   └── 🔹 Integración con LangChain
    │   │   │
    │   │   └── 📂 prompts/
    │   │       ├── 📄 summary.txt
    │   │       ├── 📄 map_summary.txt
    │   │       └── 📄 reduce_summary.txt
    │   │
    │   └── 📊 benchmark/
    │       ├── 📄 bench.py
    │       └── 📂 results/
    │           └── 📄 comparison_report.md
    │
    │   # Módulo de IA (v1.8.0)
    │   - Soporte para múltiples modelos (TinyLlama, Mistral, etc.)
    │   - Integración con RAG para búsqueda semántica
    │   - Optimización para GPU con CUDA
    │   - Detección automática de configuración
    │   - Benchmarking comparativo
    │   - Documentación actualizada
    │
    ├── 📚 Documentación
    │   ├── 📄 README_IA.md
    │   ├── 📄 BENCHMARKING.md
    │   ├── 📄 GUIA_CUDA_WSL.md
    │   └── 📄 CHANGELOG.md
    │   └── 📊 gui_db.py
    │       └── 🔹 Visor de base de datos
    │
    │   └── 🧠 Módulo IA (v1.8.0)
    │   │   ├── 📄 __init__.py
    │   │   ├── 📄 core.py             # Funcionalidad principal de IA
    │   │   ├── 📄 ia_models.py        # Carga de modelos GGUF (CPU/GPU)
    │   │   ├── 📄 ia_processor.py     # Procesamiento de texto y generación
    │   │   ├── 📄 native_pipeline.py  # Pipeline nativo optimizado
    │   │   ├── 📄 langchain_pipeline.py # Integración con LangChain
    │   │   ├── 📂 tests/              # Pruebas unitarias
    │   │   │   ├── 📄 test_core.py    # Pruebas del núcleo
    │   │   │   └── test_ia.py        # Pruebas del módulo
    │   │   └── 📂 prompts/            # Plantillas de prompts
    │   │       ├── 📄 summary.txt     # Para resúmenes
    │   │       ├── 📄 map_summary.txt # Para la fase de mapeo
    │   │       ├── 📄 reduce_summary.txt # Para la fase de reducción
    │   │       ├── 📄 qa.txt          # Preguntas y respuestas
    │   │       ├── 📄 tldr.txt        # Resúmenes cortos
    │   │       └── 📄 chapters.txt    # Generación de capítulos
    │   │
    │   ├── 📊 benchmarking/ (v1.8.0)
    │   │   ├── 📄 bench.py           # Script principal de benchmarking
    │   │   ├── 📄 compare.py         # Generador de informes mejorado
    │   │   └── 📂 results/           # Resultados de las pruebas
    │   │       └── 📄 comparison_report.md  # Informe detallado en Markdown
    │   │
    │   └── 📂 modelos/               # Enlace simbólico a C:\\local\\modelos
    │       ├── 📄 tinyllama.gguf     # Modelo pequeño para pruebas rápidas
    │       ├── 📄 qwen2-7b-instruct-q6_k.gguf  # Modelo de 7B parámetros
    │       └── 📄 mistral-7b-instruct-v0.1.Q5_K_M.gguf  # Modelo de 7B parámetros
    │
    ├── 📂 ia/
    │   ├── 📄 summarize_transcript.py   # Script CLI experimental para resumen de transcripciones (SOLO uno a la vez)
    │   └── ...                         # Otros scripts auxiliares
    │
    ├── 📂 llm_service/            # Microservicio LLM Local (v2.0.0+)
    │   ├── 📄 __init__.py         # Inicialización del paquete
    │   ├── 📄 main.py             # Punto de entrada de FastAPI
    │   ├── 📄 config.py           # Configuración y variables de entorno
    │   ├── 📄 model_loader.py     # Carga y gestión de modelos GGUF
    │   ├── 📄 schemas.py          # Esquemas Pydantic para la API
    │   ├── 📄 logger.py           # Configuración de logging centralizado
    │   ├── 📄 README.md           # Documentación del servicio
    │   └── 📂 tests/              # Pruebas unitarias
    │       ├── 📄 test_llm_service_api.py      # Pruebas de la API
    │       └── 📄 test_llm_service_inference.py # Pruebas de inferencia
    │
    ├── 📂 GUI/
    │   ├── 📄 gui_db.py           # Interfaz gráfica para gestión y procesamiento por lotes
    │   └── ...                   # Otros módulos GUI
    │
    ├── 📂 Tests
    │   ├── test_parser.py
    │   ├── test_db.py
    │   └── 📂 ia/

    │
    ├── 🔮 Sistema RAG (En Desarrollo)
    │   ├── 📄 rag_core.py
    │   │   ├── 🔹 Lógica de búsqueda semántica
    │   │   └── 🔹 Generación de respuestas aumentadas
    │   ├── 📄 vector_db.py
    │   │   ├── 🔹 Gestión de base de datos de vectores (FAISS/ChromaDB)
    │   │   └── 🔹 Creación y actualización de embeddings
    │   └── 📄 rag_interface.py
    │       └── 🔹 Nueva interfaz para consultas RAG

# TODO: Añadir integración web (FastAPI/Streamlit) y RAG en futuras versiones.

    │       ├── test_core.py
    │       └── test_ia.py
    │
    ├── 📝 Documentación
    │   ├── CHANGELOG.md
    │   ├── project_meta.json
    │   ├── requirements.txt
    │   └── README_IA.md (Docs. del Módulo IA)
    │
    └── 🧩 Dependencias
        ├── yt-dlp (≥2023.3.4)
        ├── tkinter
        ├── sqlite3 (incluido en Python)
        └── 🎯 Dependencias IA:
            ├── llama-cpp-python (con soporte CUDA)
            ├── langchain (parcial)
            └── langchain-community

    %% Nueva rama de flujo de ejecución
    ├── ▶️ Flujo de Ejecución
    │   ├── Entrada (URL o archivo)
    │   ├── Procesamiento (main.py + downloader.py + parser.py)
    │   ├── GUI opcional (gui.py)
    │   └── Salida (archivo .txt limpio)

    %% Enlaces a docstrings/README
    click main.py "# Descripción: Orquestación CLI y lógica principal"
    click gui.py "# Descripción: Interfaz gráfica de usuario"
    click downloader.py "# Descripción: Descarga de subtítulos YouTube"
    click parser.py "# Descripción: Procesamiento y limpieza de VTT"
    click batch_processor.py "# Descripción: Procesamiento por lotes"
    click utils.py "# Descripción: Utilidades y helpers"
    click test_parser.py "# Pruebas unitarias de parser"
    click CHANGELOG.md "CHANGELOG.md"
    click project_meta.json "project_meta.json"
    click requirements.txt "requirements.txt"
    click README_IA.md "README_IA.md"

    %% Estilos
    classDef module fill:#e1f5fe,stroke:#01579b,color:#01579b
    classDef test fill:#e8f5e9,stroke:#2e7d32,color:#2e7d32
    classDef doc fill:#fff3e0,stroke:#e65100,color:#e65100
    classDef dep fill:#f3e5f5,stroke:#4a148c,color:#4a148c
    
    class main.py,gui.py,downloader.py,parser.py,batch_processor.py,utils.py,ia_models.py,ia_processor.py,ia/core.py module
    class test_parser.py,test_ia.py,ia/tests/test_core.py test
    class CHANGELOG.md,project_meta.json,requirements.txt,README_IA.md doc
    class yt-dlp,tkinter,llama-cpp-python,langchain,langchain-community dep
```

## Arquitectura del Sistema

### Pipelines de Procesamiento

1. **Nativo**
   - Uso directo de `llama-cpp-python`
   - Máximo rendimiento
   - Soporte para modelos GGUF
   - Ideal para inferencia local

2. **LangChain**
   - Abstracción de alto nivel
   - Facilita el procesamiento estructurado
   - Soporte para múltiples backends

3. **Gemini API**
   - Modelos en la nube de Google
   - Mayor capacidad de contexto
   - Pago por uso
   - Requiere conexión a Internet

### Flujo de Trabajo

1. **Entrada**: Texto a resumir + Prompt
2. **Procesamiento**:
   - Tokenización
   - División en chunks (si es necesario)
   - Generación de resúmenes
   - Combinación de resultados
3. **Salida**:
   - Resumen estructurado
   - Métricas de rendimiento
   - Costos (para Gemini API)

## Cómo visualizar

1. **Visual Studio Code**:
   - Instala la extensión "Markdown Preview Mermaid Support"
   - Abre la vista previa del archivo Markdown

2. **GitHub**:
   - Simplemente visualiza el archivo en el repositorio

3. **Editores en línea**:
   - Copia el contenido del diagrama a [Mermaid Live Editor](https://mermaid.live/)

## Características Clave

- **Interfaz Triple**: CLI, GUI de descarga y GUI de base de datos
- **Almacenamiento Local**: Base de datos SQLite para historial de transcripciones
- **Búsqueda y Filtrado**: Fácil acceso a transcripciones anteriores
- **Procesamiento Eficiente**: Soporte para lotes y archivos grandes
- **Metadatos**: Almacenamiento de título, canal, URL y fecha
- **Cross-Platform**: Funciona en Windows, macOS y Linux

## Generación automática de documentación

- Puedes generar documentación HTML enlazable con:
    - `pdoc` ([ver ejemplo](https://pdoc.dev/docs/pdoc.html))
    - `mkdocs` ([ver ejemplo](https://www.mkdocs.org/))
    - O con un script propio que recorra los docstrings y genere enlaces
- Los enlaces del mapa mental pueden apuntar a secciones específicas generadas por estas herramientas.


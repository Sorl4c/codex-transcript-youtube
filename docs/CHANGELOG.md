# Historial de Cambios

Este documento registra todos los cambios notables en el proyecto de descarga y procesamiento de subtítulos de YouTube.

## [v2.7.1] - 2025-07-10
### Mejorado
- **Visualización de Chunks en `chunking_playground.py`**:
  - Añadidas columnas "Título" y "Resumen" a la tabla de chunks para mostrar metadatos semánticos cuando estén disponibles (estrategias `agentic` y `semantic`).
  - La ventana emergente de detalles de chunk (doble clic) ahora muestra una vista completa de todos los metadatos: Título, Resumen, Caracteres y Posición.

### Corregido
- **Pérdida de Vista Previa de Contenido**: Se ha restaurado la columna "Contenido (preview)" en la tabla de chunks, asegurando que todas las estrategias de chunking (incluidas `caracteres` y `palabras`) muestren un fragmento del contenido para una fácil identificación.

## [v2.7.0] - 2025-07-09
### Añadido
- **Herramienta de Testing para Chunking Agéntico (`agentic_testing_gui.py`)**:
  - GUI dedicada para aislar y depurar los proveedores de LLM (Local y Gemini).
  - Permite la ejecución sin fallbacks para un diagnóstico de errores preciso.
  - Visor de logs en tiempo real y comparativa de resultados.

### Corregido
- **Error Crítico `KeyError` en Prompt Agéntico**: Solucionado un error de formato en el prompt JSON que impedía el funcionamiento de ambos LLMs. Las llaves del JSON fueron escapadas (`{{...}}`).
- **Error `TypeError` con la API de Gemini**: Corregido el manejo de la respuesta de la API de Gemini, que devuelve un objeto `GenerateContentResponse` en lugar de texto plano. Ahora se accede a `response.text`.

### Mejorado
- **Sistema de Chunking Agéntico Robusto y Transparente**:
  - Eliminado por completo el sistema de fallback a chunking semántico. Los errores de los LLMs ahora se reportan directamente.
  - La GUI principal (`chunking_playground.py`) fue refactorizada para usar llamadas directas a los proveedores de LLM.
- **Interfaz de Usuario Simplificada**:
  - Eliminado el modo "Automático" y la preferencia de proveedor en la GUI principal.
  - Reemplazado por un selector directo y explícito: "LLM Local" o "Google Gemini".

### Técnico
- Refactorización de `run_agentic_chunking` para orquestar llamadas directas a `chunk_text_with_local_llm` y `chunk_text_with_gemini`.
- Limpieza de código obsoleto relacionado con el sistema de fallback en `chunking_playground.py`.

## [v2.6.2] - 2025-07-09
### Corregido
- **Búsqueda Vectorial**: Corregido error en `SQLiteVecDatabase.search_similar()` que causaba fallo al procesar embeddings almacenados como JSON strings
- **Compatibilidad**: Mejorado manejo de formatos de embeddings (JSON string y bytes) para mayor robustez
- **Estabilidad**: Eliminados crashes durante búsquedas vectoriales en el tercer panel

### Técnico
- Actualizado método `search_similar()` para detectar automáticamente el formato de embeddings almacenados
- Añadido soporte para embeddings en formato JSON string (actual) y bytes (legacy)
- Mejorado manejo de excepciones en búsquedas vectoriales

## [v2.6.1] - 2025-07-09
### Añadido
- **Tercer panel de búsquedas vectoriales** en RAG Chunking Playground
- **Interfaz interactiva de búsqueda semántica** con campo de consulta y configuración Top K
- **Tabla de resultados** con ranking, similitud y preview de contenido
- **Ventanas emergentes** para visualizar resultados completos
- **Información detallada de búsqueda** con estadísticas y tips
- **Funciones de limpieza** para resetear búsquedas

### Mejorado
- **Layout de 3 paneles** optimizado para mejor distribución del espacio
- **Tamaño de ventana** aumentado a 1600x900 para acomodar el nuevo panel
- **Experiencia de usuario** con feedback visual y manejo de errores

### Técnico
- Integración completa con `SQLiteVecDatabase.search_similar()`
- Uso del sistema de embeddings existente (`EmbedderFactory`)
- Threading para búsquedas no bloqueantes
- Comentarios `@docs` para enlace con documentación

## [v2.6.0] - 2025-07-09
### Añadido
- **Sistema Avanzado de Chunking**:
  - Implementación del patrón Strategy para múltiples estrategias de chunking
  - Chunking semántico basado en estructura natural del texto (párrafos y frases)
  - Chunking por palabras que respeta límites léxicos
  - Preparación para chunking agentic con hooks para LLMs externos
  - Función de conveniencia `chunk_text()` para uso rápido

- **Mejoras en RAG Chunking Playground**:
  - Selección de estrategia de chunking mediante radiobuttons
  - Actualización dinámica al cambiar estrategia
  - Visualización mejorada de embeddings en la tabla
  - Información de estrategia en estadísticas de chunks

- **Herramientas de Prueba**:
  - Nuevo script `test_chunking_strategies.py` para comparar estrategias
  - Documentación extendida con ejemplos de uso

### Mejorado
- **Modularidad del Código**: Refactorización completa de `chunker.py` para soportar nuevas estrategias sin modificar el código existente
- **Coherencia Semántica**: Los chunks generados mantienen mejor la coherencia y estructura original del texto
- **Documentación**: Actualización del README con ejemplos detallados de cada estrategia

## [v2.5.1] - 2025-07-08
### Corregido
- **Error de Cuota en API de Gemini**: Se solucionaron los errores de cuota (429 Too Many Requests) cambiando el modelo por defecto de `gemini-1.5-pro` a `gemini-1.5-flash-latest`, que tiene un nivel gratuito más permisivo. Aunque el problema de la cuota no me ha quedado del todo claro lo hemos solucionado así y tenemos ahora una lista de muchos modelos gratuitos. 
- **Consistencia en el Modelo de IA**: Se refactorizó el script de benchmarking (`bench.py`) para que utilice la función centralizada `summarize_text_gemini` de `ia/gemini_api.py`, asegurando que toda la aplicación utilice el mismo modelo de IA por defecto y eliminando código duplicado.

### Mejorado
- **Documentación del Código**: Se ha añadido una lista de los modelos de Gemini disponibles y una nota de implementación futura (`TODO`) directamente en `ia/gemini_api.py` para facilitar el mantenimiento y futuras actualizaciones.

## [v2.5.0] - 2025-07-08
### Añadido
- **Módulo RAG (Retrieval-Augmented Generation)**:
  - Implementación inicial del módulo de recuperación de información basado en embeddings
  - Soporte para embeddings locales con modelos sentence-transformers
  - Almacenamiento vectorial usando SQLite con extensión sqlite-vec
  - Sistema de chunking de texto con solapamiento configurable
  - Búsqueda semántica con soporte para GPU (CUDA)
  - Integración con la infraestructura existente de procesamiento de texto

- **RAG Chunking Playground (Tkinter)**:
  - Interfaz gráfica para experimentar con parámetros de chunking
  - Panel de configuración con sliders para chunk_size y chunk_overlap
  - Selector de modo: caracteres vs palabras
  - Vista en tiempo real de la base de datos vectorial
  - Estadísticas detalladas de chunks almacenados
  - Exportación de resultados a CSV
  - Manejo robusto de errores sin cierre de aplicación
  - Visualización de embeddings y contenido de la base de datos

### Mejorado
- **Rendimiento**:
  - Optimización para uso eficiente de GPU con CUDA
  - Soporte para procesamiento por lotes de embeddings
  - Almacenamiento binario de vectores para mejor rendimiento

### Corregido
- **Compatibilidad**:
  - Solucionados problemas de carga de extensiones SQLite en entornos WSL
  - Mejor manejo de versiones de dependencias
  - Corregido problema con la inicialización de la base de datos vectorial

### Notas Técnicas
- **Requisitos**:
  - Se requiere pysqlite3-binary para mejor compatibilidad
  - Se recomienda CUDA 12.8+ para aceleración por GPU
  - Dependencias principales: sentence-transformers, sqlite-vec, numpy

## [v2.4.0] - 2025-07-08

## [v2.4.0] - 2025-07-08
### Corregido
- **Pipeline de Streamlit Unificado**: Se ha corregido la lógica de procesamiento de vídeos en la interfaz de Streamlit (`gui_oop.py`) para que sea idéntica a la de la GUI de Tkinter. Ahora se guardan correctamente todos los metadatos, incluyendo el nombre del canal, título y fecha.
- **Errores de UI en Streamlit**: Solucionados múltiples errores de indentación y lógica que causaban el fallo de la aplicación al procesar vídeos.
- **Uso de LLM Local**: Se ha forzado el uso del pipeline `native` (LLM local) en todas las operaciones de la interfaz de Streamlit para evitar los errores de cuota de la API de Gemini y asegurar un funcionamiento consistente.

### Nota Estratégica
- **Cambio de Enfoque a RAG**: Aunque la interfaz de Streamlit es ahora funcional, se ha decidido no invertir más tiempo en pulir detalles menores de la UI. El enfoque del proyecto se desplaza hacia el desarrollo e integración de un sistema de **Retrieval-Augmented Generation (RAG)** para permitir búsquedas semánticas y consultas complejas sobre las transcripciones almacenadas.

## [v2.3.2] - 2025-07-01
### Mejorado
- **Selección de Vídeo en Videoteca (Streamlit)**
  - Se ha rediseñado la selección de vídeos en la página "Videoteca".
  - Ahora se puede seleccionar un vídeo haciendo clic directamente en cualquier parte de su fila en la tabla.
  - La vista de detalles del vídeo se actualiza automáticamente al seleccionar una fila, mejorando la fluidez y la experiencia de usuario (`on_select="rerun"`).
  - Se eliminó el `selectbox` y los botones de selección, simplificando la interfaz.

### Corregido
- **Error de Tipo en ID de Vídeo**
  - Solucionado un error crítico que ocurría al seleccionar un vídeo en la tabla de la Videoteca.
  - El ID del vídeo, que era de tipo `numpy.int64`, ahora se convierte explícitamente a `int` nativo de Python antes de consultar la base de datos, evitando el fallo "Vídeo no encontrado".

## [v2.3.1] - 2025-06-30
### Añadido
- **Nueva Interfaz Web con Streamlit**
  - Interfaz web moderna y responsiva accesible desde cualquier navegador
  - Gestión avanzada de vídeos con vista previa en tiempo real
  - Panel de depuración integrado para diagnóstico
  - Filtros por canal y búsqueda de vídeos
  - Visualización y edición de metadatos y resúmenes
  - Exportación de datos en formato JSON o CSV

> **Nota:** La interfaz Streamlit está orientada a la gestión y análisis de vídeos. El benchmarking de modelos solo está disponible por CLI, no desde la interfaz web.

### Corregido
- **Integración con Gemini API**
  - Solucionado `AttributeError` en el manejo de respuestas de la API
  - Mejorado el manejo de errores y validación de datos
  - Corregida la serialización JSON para el almacenamiento en base de datos

### Mejorado
- **Documentación**
  - Añadidos docstrings completos a los módulos principales
  - Mejorada la documentación de funciones críticas
  - Actualizado el mapa del proyecto para reflejar la nueva arquitectura
  - Guías de migración desde la interfaz tkinter

- **Interfaz de Usuario**
  - Añadido panel de depuración en la barra lateral
  - Mejorados los mensajes de error y retroalimentación al usuario
  - Optimizada la experiencia de selección de vídeos
  - Mejor rendimiento en la carga y visualización de datos

## [v2.3.0] - 2025-06-24
### Añadido
- **Nuevo Panel Lateral**
  - Vista previa completa del resumen del vídeo seleccionado
  - Soporte para scroll vertical en el panel de vista previa
  - Formato mejorado para títulos y texto en la vista previa
  - Actualización automática al seleccionar un vídeo

### Mejorado
- **Interfaz de Usuario**
  - Rediseño responsivo con panel lateral deslizable
  - Mejor distribución del espacio en pantalla
  - Tamaño mínimo de ventana establecido para mejor usabilidad
  - Manejo mejorado del redimensionamiento de la ventana

### Corregido
- **Errores de Interfaz**
  - Ajuste automático del ancho del texto en el panel de vista previa
  - Mejor manejo de textos largos en la vista previa
  - Corregido problema de actualización al cambiar entre vídeos

## [v2.2.0] - 2025-06-23
### Añadido
- **Gestión de Vídeos**
  - Función para eliminar vídeos desde la interfaz gráfica con confirmación
  - Ordenación dinámica por columnas (ID, Título, Canal, Fecha)
  - Actualización automática de la vista tras eliminar un vídeo

### Mejorado
- **Interfaz de Usuario**
  - Mejora en la experiencia de usuario al gestionar múltiples vídeos
  - Indicadores visuales para el orden de clasificación
  - Mejora en el rendimiento al cargar listas grandes de vídeos
  - Manejo robusto de errores en la interfaz gráfica

### Corregido
- **Errores de Interfaz**
  - Corregido error al seleccionar filas en la tabla
  - Solucionado problema de visualización de resúmenes en la tabla principal
  - Mejorado el manejo de IDs de vídeo para evitar errores de tipo
  - Corregida la carga de resúmenes en vistas filtradas

## [v2.1.0] - 2025-06-22
### Añadido
- **Interfaz Gráfica Unificada (`gui_unified.py`)**
  - Nueva interfaz con vista previa de resúmenes en la tabla principal
  - Soporte para ordenar por columnas
  - Panel de detalles con resumen editable
  - Integración con el servicio LLM local
  - Manejo asíncrono de tareas con cola de actualización

### Mejorado
- **Integración LLM**
  - Configuración automática de URL de API según entorno (WSL2/Windows)
  - Mejor manejo de errores en la generación de resúmenes
  - Feedback visual durante el procesamiento

## [v2.0.0] - 2025-06-20
### Añadido
- **Microservicio LLM Local (`llm_service/`)**
  - Implementado servidor FastAPI para modelos GGUF con API compatible con OpenAI
  - Carga única del modelo al inicio con soporte para múltiples modelos (Qwen2-7B, Mistral, TinyLlama)
  - Endpoint `/v1/chat/completions` con soporte para streaming
  - Configuración mediante variables de entorno (`.env`)
  - Validación de peticiones con Pydantic
  - Logging centralizado y estructurado
  - Control de concurrencia con `asyncio.Lock`
  - Documentación detallada en `llm_service/README.md`
  - Tests unitarios iniciales
  - Optimización para GPU con CUDA

### Mejorado
- **Rendimiento**
  - Soporte para carga completa en GPU (RTX 5070 Ti verificada)
  - Streaming de respuestas token por token con baja latencia
  - Manejo eficiente de memoria y VRAM
  - Tiempos de respuesta optimizados:
    - Respuestas cortas: < 2 segundos
    - Textos largos (8000+ tokens): ~6 segundos
  - Velocidad de generación: 300-400 tokens/segundo
  - Soporte para contexto extenso (hasta 10,000 tokens probados)

### Documentación
- Guía completa de configuración para modelos locales
- Documentación detallada de la API con ejemplos
- Instrucciones para desarrollo y pruebas
- Sección de solución de problemas
- Recomendaciones de hardware y rendimiento

### Verificado
- **Casos de Uso**
  - Resúmenes de texto (50-300 palabras)
  - Clasificación temática
  - Procesamiento de documentos largos
  - Generación de contenido estructurado
  - **Procesamiento por lotes**: Disponible en GUI (no en CLI por ahora)
- **Modelos Probados**
  - Qwen2-7B-Instruct (q6_k) - Excelente rendimiento
  - Mistral 7B - Buen rendimiento
  - TinyLlama - Rápido para pruebas iniciales

### Integración Modular
- CLI y GUI pueden trabajar de forma independiente o combinada
- Microservicio LLM local como backend común

### Futuro
- Planificada integración web y RAG (Retrieval-Augmented Generation)

## [v1.9.0] - 2025-06-20
### Añadido
- **Integración con Gemini API**:
  - Soporte para resúmenes mediante la API de Google Gemini
  - Cálculo automático de costos basado en tokens de entrada/salida
  - Gestión de claves de API mediante variables de entorno o parámetros
  - Soporte para múltiples modelos de Gemini (configurable)
- **Mejoras en el sistema de benchmarking**:
  - Comparación de calidad entre modelos locales y en la nube
  - Métricas de costo-efectividad para evaluar relación calidad/precio
  - Soporte para evaluación cualitativa de resúmenes

### Mejoras
- Optimización del manejo de memoria para textos largos
- Mejora en la precisión del conteo de tokens
- Documentación ampliada con ejemplos de uso de Gemini API
- Sistema de reintentos automáticos para fallos de API

## [v1.8.0] - 2025-06-18
### Añadido
- **Sistema de Comparación Mejorado**:
  - Nuevas métricas de calidad: longitud del resumen y riqueza de vocabulario
  - Barras visuales para comparación de métricas
  - Indicadores de ganador por métrica (🥇 Native, 🥈 LangChain, 🤝 Empate)
  - Secciones plegables para mejor organización
  - Resumen ejecutivo con promedios globales
  - Análisis detallado por prompt
- **Documentación Actualizada**:
  - Explicación detallada de las métricas en BENCHMARKING.md
  - Guía de interpretación de resultados
  - Ejemplos de uso mejorados

### Mejoras
- Refactorización completa del sistema de generación de informes
- Mejora en la precisión de las métricas de rendimiento
- Optimización del cálculo de estadísticas
- Documentación ampliada y actualizada

## [v1.7.0] - 2025-06-17
### Añadido
- **Soporte mejorado para múltiples modelos**:
  - Detección automática del tamaño de contexto según el modelo (TinyLlama, Mistral, etc.)
  - Parámetros de línea de comandos para personalizar la generación
  - Soporte para `--n-ctx` y `--max-tokens` en el script de benchmark

## [v1.6.0] - 2025-06-17
### Añadido
- **Sistema de Benchmarking**:
  - Scripts para comparar rendimiento entre pipelines nativo y LangChain
  - Métricas detalladas: tiempo de carga, latencia, tokens/segundo
  - Generación de informes comparativos en Markdown
  - Soporte para múltiples modelos GGUF
  - Documentación completa en [BENCHMARKING.md](./BENCHMARKING.md)

### Mejoras
- **Módulo de IA**: Refactorización completa del sistema de pruebas unitarias
- **Módulo de IA**: Mejora en el manejo de dependencias pesadas (importación diferida)
- **Módulo de IA**: Soporte mejorado para LangChain y pipeline nativo
- **Documentación**: Actualización completa de la documentación del módulo de IA

### Corregido
- **Módulo de IA**: Corrección de errores de importación en entornos sin GPU
- **Módulo de IA**: Mejora en el manejo de rutas de modelos
- **Tests**: Corrección de pruebas unitarias y mejor cobertura

## [v1.5.0] - 2025-06-16
### Añadido
- **Soporte para aceleración GPU con CUDA**:
  - Integración con `llama-cpp-python` para aceleración en GPU NVIDIA
  - Guía detallada de configuración para WSL2 y CUDA 12.9
  - Verificado el funcionamiento con RTX 5070 Ti
  - Documentación completa en [GUIA_CUDA_WSL.md](./GUIA_CUDA_WSL.md)
  - Soporte para cargar modelos GGUF en GPU con `n_gpu_layers=-1`

## [v1.4.0] - 2025-06-16
### Añadido
- **Base de Datos Local (SQLite)**:
  - Creado el módulo `db.py` para gestionar una base de datos SQLite (`subtitles.db`).
  - Se guardan automáticamente los metadatos y transcripciones de cada vídeo procesado (URL, canal, título, fecha, texto).
  - La base de datos evita duplicados basados en la URL del vídeo.
  - Soporte para pruebas unitarias con base de datos temporal.
- **Visor de Base de Datos (GUI)**:
  - Nueva interfaz gráfica `gui_db.py` para consultar los vídeos almacenados.
  - Permite listar, filtrar por título o canal, y ver la transcripción completa.
  - Se accede con el nuevo argumento `main.py --view-db`.
- **Integración en Flujo de Trabajo**:
  - El guardado en la base de datos se integra de forma transparente en el procesamiento de URLs individuales y por lotes.
  - Mejor manejo del formato de transcripción antes de guardar en la base de datos.
- **Pruebas de Base de Datos**:
  - Añadido `tests/test_db.py` con pruebas unitarias completas.
  - Mejor cobertura de pruebas para operaciones CRUD.

### Cambios
- **Refactorización del Módulo de Base de Datos**:
  - Mejorada la gestión de conexiones a la base de datos.
  - Añadido soporte para especificar el nombre de la base de datos en todas las funciones.
  - Optimizado el manejo de errores y mensajes de depuración.
- **Mejoras en el Procesamiento por Lotes**:
  - Corregido el formato de transcripción al guardar en la base de datos.
  - Mejorado el manejo de errores durante el procesamiento de múltiples URLs.
- **Documentación**:
  - Actualizada la documentación en `/docs` para reflejar los cambios recientes.
  - Mejorada la organización de la documentación del proyecto.

### Cambios
- El módulo `downloader.py` ahora extrae también el nombre del canal y la fecha de subida del vídeo.
- El `main.py` ha sido actualizado para orquestar la inicialización de la base de datos y lanzar el nuevo visor.

## [v1.3.0] - 2025-06-16
### Añadido
- **Documentación mejorada**:
  - Mapa mental interactivo del proyecto (`PROJECT_MAP.md`)
  - Archivo `project_meta.json` con metadatos estructurados
  - Documentación de módulos y funciones principales
- **Mejoras en la organización del proyecto**

## [v1.2.0] - 2025-06-16
### Añadido
- **Interfaz Gráfica (GUI)** con `tkinter` para una experiencia de usuario más amigable
- **Procesamiento por lotes mejorado**:
  - Soporte para archivos de texto con múltiples URLs
  - Salida unificada en un solo archivo con formato consistente
  - Mejor manejo de metadatos (título, URL)
- **Optimizaciones de rendimiento**:
  - Procesamiento en segundo plano sin bloquear la interfaz
  - Mejor gestión de memoria

## [v1.1.0] - 2025-06-16
### Añadido
- Soporte para procesar múltiples URLs de YouTube en un solo comando
- Procesamiento por lotes de archivos VTT locales
- Optimización de memoria para manejar archivos grandes
- Sistema de logging mejorado
- Manejo de errores más robusto

### Corregido
- Eliminada dependencia innecesaria de NLTK
- Mejorado el formateo de texto en las transcripciones
- Corregido el manejo de caracteres especiales en Windows
- Solucionado el problema de saltos de línea en el procesamiento por lotes

### Cambios
- Reestructuración del código para mejor mantenibilidad
- Actualización de dependencias
- Mejora en la documentación del código
- Refactorización del sistema de procesamiento de texto

## [v1.0.1] - 2025-06-16
### Corregido
- Se eliminó la dependencia `nltk` de `requirements.txt` ya que no era utilizada.
- Se actualizó el `CHANGELOG.md` para reflejar con precisión las características actuales del proyecto.

### Cambios
- **Estructura modular**: El código está separado en `downloader.py` para descargas y `parser.py` para el procesamiento de texto, con `main.py` como punto de entrada.
- **Soporte multi-idioma**: El script intenta descargar el idioma solicitado y tiene mecanismos de respaldo (`fallback`).
- **Manejo de errores**: Se mejoró la captura de errores durante la descarga y el procesamiento.
- **Limpieza de VTT**: Se eliminan correctamente las cabeceras, metadatos, timestamps y etiquetas de formato de los archivos VTT.

## [v1.0.0] - 2025-06-15
### Agregado
- Script inicial `vtt_to_text.py` con funcionalidad básica
- Soporte para descargar subtítulos usando `yt-dlp`
- Procesamiento básico de archivos VTT
- Formateo de texto con marcas de tiempo

### Comportamiento Original (v1.0.0)
El script original funcionaba de la siguiente manera:

1. **Descarga de subtítulos**:
   - Usaba `subprocess` para ejecutar `yt-dlp`
   - Guardaba temporalmente el archivo VTT en disco
   - Leía el contenido del archivo

2. **Procesamiento**:
   - Eliminaba etiquetas HTML y de tiempo
   - Agrupaba el texto en bloques basados en saltos de línea
   - Aplicaba un formato simple de timestamp (MM:SS)

3. **Uso**:
   ```bash
   python vtt_to_text.py "URL" [archivo_salida]
   ```
   o modo interactivo si no se proporcionaban argumentos

### Diferencias Clave con la Versión Actual

| Característica | Versión Original (v1.0.0) | Versión Actual |
|----------------|---------------------------|----------------|
| Estructura | Script único | Módulos separados |
| Procesamiento | Simple (regex) | Lógica de parseo mejorada |
| Dependencias | yt-dlp (binario) | yt-dlp (paquete Python) |
| Manejo de errores | Básico | Mejorado |
| Internacionalización | Solo español | Múltiples idiomas |
| Rendimiento | Carga todo en memoria | Carga todo en memoria (optimización pendiente) |

## Notas de Migración

### Para volver al comportamiento original:
1. Usa el archivo `vtt_to_text.py` original
2. Asegúrate de tener `yt-dlp` instalado en el sistema
3. Ejecuta directamente el script sin dependencias adicionales

### Para usar la nueva versión:
1. Instala las dependencias: `pip install -r requirements.txt`
2. Usa `main.py` como punto de entrada
3. Disfruta de las mejoras y nuevas características

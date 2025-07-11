# Sistema de Benchmarking para Pipelines de IA

## Visión General

Este módulo permite comparar el rendimiento y la calidad de diferentes pipelines de generación de resúmenes de texto, incluyendo:

- **Pipeline nativo** (usando directamente `llama-cpp-python`)
- **Pipeline LangChain** (para procesamiento estructurado)
- **Gemini API** (modelos en la nube de Google)

El sistema genera informes detallados en formato Markdown con comparativas visuales fáciles de interpretar.

## Características

- **Comparación de rendimiento** entre múltiples pipelines
- **Métricas detalladas**:
  - Tiempo de carga del modelo (local)
  - Latencia de generación
  - Tokens por segundo
  - Tokens generados y de entrada
  - Costo estimado (para Gemini API)
  - Ratio de compresión (tokens entrada/salida)
  - Longitud del resumen (caracteres y palabras)
  - Riqueza de vocabulario (palabras únicas / total palabras)
- **Visualizaciones integradas** con barras comparativas
- **Informe ejecutivo** con resumen de resultados
- **Análisis detallado** por prompt
- Soporte para múltiples modelos (locales y en la nube)


### 1. Pipeline Nativo (Local)

```bash
# Configuración básica
export MODEL_PATH="/ruta/al/modelo.gguf"
python bench.py --pipeline native --model_path $MODEL_PATH

# Personalización avanzada
python bench.py --pipeline native \
  --model_path "$MODEL_PATH" \
  --n-ctx 4096 \
  --max-tokens 1024 \
  --chunk-size 0  # Desactivar chunking para modelos con contexto amplio
```

### 2. Pipeline LangChain (Local)

```bash
# Configuración básica
python bench.py --pipeline langchain --model_path "$MODEL_PATH"

# Con parámetros personalizados
python bench.py --pipeline langchain \
  --model_path "$MODEL_PATH" \
  --n-ctx 4096 \
  --max-tokens 1024
```

### 3. Gemini API (Nube)

```bash
# Usando variable de entorno
export GEMINI_API_KEY='tu-clave-api'
python bench.py --pipeline gemini

# O especificando la clave directamente
python bench.py --pipeline gemini \
  --gemini-api-key 'tu-clave-api' \
  --gemini-model gemini-1.5-flash-latest  # Modelo por defecto (configurable en ia/gemini_api.py)
```

### 4. Comparación Múltiple

```bash
# Ejecutar múltiples pipelines y comparar
python bench.py --pipeline all \
  --model_path "$MODEL_PATH" \
  --gemini-api-key 'tu-clave-api'
```

### 3. Modelos Soportados
El sistema detecta automáticamente los siguientes modelos:

- **TinyLlama**: 2048 tokens de contexto
- **Mistral/Mixtral**: 8192 tokens de contexto
- **LLaMA 2**: 4096 tokens de contexto
- **Otros**: 2048 tokens por defecto

### 3. Generar Informe Comparativo

El script `compare.py` analiza los resultados de los benchmarks y genera un informe detallado en Markdown:

```bash
# Generar informe comparativo
python compare.py

# Especificar archivo de resultados específico
python compare.py --input bench_results/benchmark_combined_20240618.json
```

### Características del Informe

1. **Resumen Ejecutivo**
   - Promedios de todas las métricas
   - Ganadores globales por categoría
   - Estadísticas generales

2. **Análisis Detallado por Prompt**
   - Tablas comparativas con métricas
   - Barras visuales para comparación
   - Texto completo de prompts y respuestas
   - Secciones plegables para mejor legibilidad

3. **Métricas Incluidas**
   - Tiempos de procesamiento
   - Rendimiento en tokens/segundo
   - Estadísticas de tokens
   - Calidad del resumen (longitud, vocabulario)
   - Ratios de compresión

4. **Visualizaciones**
   - Barras comparativas
   - Indicadores de ganador
   - Formato de tabla para fácil lectura

El informe se guarda en `bench_results/comparison_report.md` por defecto.

## Estructura del Proyecto

- `bench.py`: Script principal para ejecutar benchmarks
- `compare.py`: Genera informes comparativos
- `ia/native_pipeline.py`: Implementación del pipeline nativo
- `ia/langchain_pipeline.py`: Implementación del pipeline LangChain
- `ia/core.py`: Funcionalidad compartida
- `bench_results/`: Directorio con resultados e informes

## Requisitos

- Python 3.8+
- Dependencias listadas en `requirements.txt`
- Modelos GGUF compatibles

## Personalización

### Parámetros Ajustables

- `--temperature`: Controla la aleatoriedad (0.0 a 1.0)
- `--max_tokens`: Máximo de tokens por generación
- `--top_p`: Muestreo de núcleo (nucleus sampling)
- `--chunk_size`: Tamaño de fragmentos para procesamiento

### Prompts Personalizados

Crea archivos en `ia/prompts/`:
- `map_summary.txt`: Para la fase de mapeo
- `reduce_summary.txt`: Para la fase de reducción

## Interpretación de Resultados

### Métricas Clave

1. **Tiempo de Carga**: Tiempo que tarda en cargar el modelo en memoria (solo local).
2. **Latencia**: Tiempo total de generación del resumen.
3. **Tokens/seg**: Velocidad de generación del modelo.
4. **Costo (Gemini)**: Costo estimado en USD basado en tokens E/S.
5. **Tokens (E/S)**: Relación entre tokens de entrada y salida.
6. **Compresión**: Porcentaje de reducción de tamaño.
7. **Longitud**: Tamaño del resumen generado.
8. **Vocabulario**: Riqueza léxica del resumen.

### Ejemplo de Salida

#### Modelo Local
```
=== RESULTADOS DEL BENCHMARK ===

Modelo: mistral-7b-instruct-v0.1.Q5_K_M.gguf
Pipeline: native

Métricas:
- Tiempo de carga: 5.23s
- Latencia: 18.76s
- Tokens/s: 38.4
- Tokens (E/S): 1,245/312 (4.0x compresión)
- Longitud: 2,145 caracteres (415 palabras)
- Vocabulario: 0.62 (palabras únicas/total)
```

#### Gemini API
```
=== RESULTADOS DEL BENCHMARK ===

Modelo: gemini-1.5-flash-latest
Pipeline: gemini

Métricas:
- Latencia: 3.21s
- Tokens (E/S): 1,856/429 (4.3x compresión)
- Costo: $0.00091 USD
  - Entrada (1,856 tokens): $0.00065
  - Salida (429 tokens): $0.00026
- Longitud: 2,845 caracteres (512 palabras)
- Vocabulario: 0.68 (palabras únicas/total)
```

### Símbolos en los Informes

- **Native**: Pipeline nativo obtuvo mejor resultado
- **LangChain**: Pipeline de LangChain obtuvo mejor resultado
- **Gemini**: Pipeline de Gemini obtuvo mejor resultado
- **Empate**: Ambos pipelines obtuvieron resultados equivalentes
- 🥈 **LangChain**: Pipeline de LangChain obtuvo mejor resultado
- 🤝 **Empate**: Ambos pipelines obtuvieron resultados equivalentes

## Solución de Problemas

### Problemas Comunes con Modelos Locales
- **Modelo no encontrado**: Verifica la ruta al archivo GGUF
- **Falta de memoria**: Reduce el tamaño de los fragmentos o usa un modelo más pequeño
- **Errores de CUDA**: Verifica la instalación de los controladores NVIDIA

### Problemas con Gemini API
- **Error 403 (Permiso denegado)**: Verifica que la clave de API sea correcta y tenga permisos
- **Error 429 (Límite de cuota)**: Espera o aumenta los límites en Google Cloud Console
- **Tiempos de espera**: Verifica tu conexión a Internet o aumenta el timeout

## Mejores Prácticas

1. **Para desarrollo local**:
   - Usa modelos más pequeños (TinyLlama, 7B cuantizados)
   - Limita el tamaño del contexto con `--n-ctx`
   - Usa `--chunk-size 0` para modelos con contexto amplio

2. **Para producción con Gemini**:
   - Monitorea el uso de la API y costos
   - Implementa caché para reducir llamadas repetitivas
   - Usa `gemini-1.5-flash-latest` para mejor relación costo-rendimiento

3. **Optimización de costos**:
   - Procesa lotes de texto juntos cuando sea posible
   - Usa el modelo más pequeño que cumpla con tus requisitos
   - Considera procesamiento híbrido (local + nube)

## Próximas Mejoras

- Soporte para métricas de calidad automáticas (ROUGE, BLEU)
- Integración con TensorBoard para visualización
- Pruebas de estrés y carga
- Soporte para más modelos y frameworks

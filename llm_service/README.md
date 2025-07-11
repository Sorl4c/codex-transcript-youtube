# LLM Microservice

Servicio local que proporciona una API compatible con OpenAI para interactuar con modelos de lenguaje GGUF en hardware local. Optimizado para procesamiento de contexto largo y alto rendimiento en GPU.

## Características Principales

- **API compatible con OpenAI** (endpoint `/v1/chat/completions`)
- **Soporte para modelos GGUF** (Qwen2, Mistral, TinyLlama, etc.)
- **Procesamiento de contexto largo** (hasta 10,000 tokens probados)
- **Optimizado para GPU** con aceleración CUDA
- **Streaming de respuestas** para una mejor experiencia de usuario
- **Configuración flexible** mediante variables de entorno

## Configuración Recomendada

### Hardware Verificado
- **GPU**: NVIDIA RTX 5070 Ti (16GB VRAM)
- **RAM**: 32GB+
- **Sistema Operativo**: Linux con WSL2

### Variables de Entorno Recomendadas

```ini
# Configuración del Modelo
MODEL_PATH=/ruta/al/modelo.gguf
MODEL_N_CTX=10000          # Contexto máximo (tokens)
MODEL_N_GPU_LAYERS=-1      # Usar todas las capas en GPU

# Configuración de la API
API_HOST=0.0.0.0           # Escuchar en todas las interfaces
API_PORT=8000              # Puerto del servidor

# Parámetros de Generación
DEFAULT_TEMPERATURE=0.4    # Para respuestas más deterministas
DEFAULT_TOP_P=0.9
DEFAULT_MAX_TOKENS=1024    # Aumentar para respuestas más largas

# Configuración Avanzada
BATCH_SIZE=512
THREADS=0                  # 0 para usar todos los núcleos
```

## Uso Básico

### Iniciar el Servicio

```bash
uvicorn llm_service.main:app --host 0.0.0.0 --port 8000 --reload
```

### Ejemplo de Uso con cURL

**Petición Básica:**
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
  "model": "local-model",
  "messages": [
    {"role": "user", "content": "Resume el siguiente texto en una frase: [texto]"}
  ],
  "temperature": 0.4,
  "max_tokens": 1024
}'
```

**Petición con Streaming:**
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
  "model": "local-model",
  "messages": [
    {"role": "user", "content": "Genera un resumen detallado de..."}
  ],
  "temperature": 0.4,
  "max_tokens": 1024,
  "stream": true
}'
```

## Rendimiento

### Con Qwen2-7B-Instruct (q6_k)
- **Contexto**: Hasta 10,000 tokens sin pérdida de coherencia
- **Velocidad**: 300-400 tokens/segundo en RTX 5070 Ti
- **Tiempo de respuesta**: 
  - Respuestas cortas: < 2 segundos
  - Textos largos (8000+ tokens): ~6 segundos

### Casos de Uso Verificados

1. **Resúmenes de Texto**
   - Entrada: 50-300 palabras
   - Tiempo: < 2 segundos
   - Calidad: Alta coherencia y relevancia

2. **Clasificación Temática**
   - Identificación precisa de categorías
   - Buen manejo de textos técnicos

3. **Procesamiento de Textos Largos**
   - Hasta 8000+ tokens en un solo prompt
   - Mantiene coherencia en todo el contexto

## Configuración Avanzada

### Ajuste de Parámetros

- **Para respuestas más creativas**:
  ```
  "temperature": 0.7,
  "top_p": 0.9
  ```

- **Para respuestas más concisas**:
  ```
  "temperature": 0.3,
  "max_tokens": 256
  ```

### Monitoreo

Verifica el uso de GPU:
```bash
watch -n 0.5 nvidia-smi
```

## Solución de Problemas

### Error: Falta de Memoria
- Reduce `MODEL_N_CTX`
- Disminuye `BATCH_SIZE`
- Cierra otras aplicaciones que usen GPU

### Rendimiento Lento
- Verifica que `MODEL_N_GPU_LAYERS=-1`
- Asegúrate de usar la versión con soporte CUDA de `llama-cpp-python`

## Próximos Pasos

- [ ] Pruebas con modelos más grandes
- [ ] Optimización de memoria
- [ ] Documentación avanzada de la API
- [ ] Ejemplos de integración con aplicaciones

---

*Última actualización: 2025-06-20*

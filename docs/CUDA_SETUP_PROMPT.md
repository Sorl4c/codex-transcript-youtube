# Prompt para Claude Code: Configurar CUDA + llama-cpp-python

## 📋 Cómo Usar Este Prompt

**Escenario:** Estás en un proyecto Python nuevo y necesitas configurar soporte GPU (CUDA) para ejecutar modelos `.gguf` con `llama-cpp-python`.

**Instrucciones:**
1. Abre Claude Code en tu nuevo proyecto
2. Copia y pega el prompt completo de la sección siguiente
3. Claude ejecutará todos los pasos de verificación e instalación
4. Al final tendrás `llama-cpp-python` compilado con CUDA listo para usar

---

## 🤖 PROMPT COMPLETO (Copiar desde aquí)

```
Necesito configurar llama-cpp-python con soporte CUDA en este proyecto para ejecutar modelos GGUF locales con aceleración GPU.

CONTEXTO DEL SISTEMA:
- Sistema operativo: WSL2 en Windows 10/11
- GPU: NVIDIA RTX 5070 Ti (o indicar tu GPU)
- Distribución WSL: Ubuntu 22.04
- Python: 3.12+ (verificar con `python3 --version`)

OBJETIVO:
Instalar y compilar llama-cpp-python con soporte CUDA 12.9 para poder cargar modelos .gguf y ejecutar inferencia acelerada por GPU.

PASOS A EJECUTAR:

1. VERIFICACIONES PREVIAS:
   - Confirmar que WSL2 está activo: `wsl.exe --list --verbose` (desde PowerShell)
   - Verificar que GPU es visible desde WSL: `nvidia-smi`
   - Confirmar herramientas de compilación: `gcc --version` y `cmake --version`

2. INSTALACIÓN CUDA TOOLKIT 12.9:
   - Descargar e instalar keyring de CUDA
   - Añadir repositorio oficial de NVIDIA
   - Instalar cuda-toolkit-12-9
   - Resolver dependencias con `apt --fix-broken install` si es necesario

3. CONFIGURAR VARIABLES DE ENTORNO:
   - Editar ~/.bashrc para añadir:
     * export CUDA_HOME=/usr/local/cuda-12.9
     * export PATH="$CUDA_HOME/bin:$PATH"
     * export LD_LIBRARY_PATH="$CUDA_HOME/lib64:$LD_LIBRARY_PATH"
   - Recargar entorno con `source ~/.bashrc`
   - Verificar nvcc: `nvcc --version` (debe mostrar CUDA 12.9)

4. CREAR ENTORNO VIRTUAL:
   - Crear venv en el proyecto: `python3 -m venv venv`
   - Activar venv: `source venv/bin/activate`
   - Actualizar pip: `pip install --upgrade pip`

5. COMPILAR llama-cpp-python CON CUDA:
   - Ejecutar: `CMAKE_ARGS="-DLLAMA_CUDA=on" FORCE_CMAKE=1 pip install --upgrade --force-reinstall llama-cpp-python --no-cache-dir`
   - IMPORTANTE: Usar LLAMA_CUDA (NO LLAMA_CUBLAS, está deprecated)
   - Esperar ~5-10 minutos para compilación

6. VERIFICACIÓN FINAL:
   - Importar en Python: `python -c "from llama_cpp import Llama; print('✅ CUDA OK')"`
   - Crear test_cuda.py con inferencia simple usando un modelo .gguf
   - Confirmar que logs muestran "CUDA" y offloading de capas

7. CONFIGURACIÓN DEL PROYECTO:
   - Crear archivo .env con:
     * MODEL_PATH=/mnt/c/local/modelos/[tu-modelo].gguf
     * MODEL_N_CTX=2048
     * MODEL_N_GPU_LAYERS=-1
   - Crear config.py con clase Settings para cargar estos valores
   - Añadir requirements.txt con llama-cpp-python y python-dotenv

RESULTADO ESPERADO:
Al finalizar, debo poder ejecutar:
```python
from llama_cpp import Llama
llm = Llama(model_path="/mnt/c/local/modelos/modelo.gguf", n_gpu_layers=-1)
response = llm("Test", max_tokens=50)
print(response["choices"][0]["text"])
```

Y ver respuesta generada en < 1 segundo con aceleración GPU.

DOCUMENTACIÓN DE REFERENCIA:
Si necesitas consultar detalles adicionales, existe una guía completa en:
docs/CUDA_SETUP_GENERIC.md (si estás trabajando desde el proyecto yt-dlp)

Por favor, procede con los pasos de verificación e instalación. Detente si encuentras errores y propón soluciones antes de continuar.
```

---

## 🎯 Variantes del Prompt

### Variante A: Si CUDA ya está instalado

```
Tengo CUDA 12.9 ya instalado en WSL2 (verificado con `nvcc --version`).

Solo necesito:
1. Crear entorno virtual Python en este proyecto
2. Compilar llama-cpp-python con soporte CUDA usando CMAKE_ARGS="-DLLAMA_CUDA=on"
3. Crear configuración básica (.env y config.py) para usar modelos .gguf
4. Verificar con test de inferencia simple

Procede por favor.
```

---

### Variante B: Solo verificación (si ya todo está instalado)

```
Tengo llama-cpp-python instalado. Necesito verificar que el soporte CUDA esté funcionando correctamente.

Por favor:
1. Confirmar que llama-cpp-python se puede importar
2. Crear test_cuda.py que cargue un modelo .gguf con n_gpu_layers=-1
3. Ejecutar test y confirmar que logs muestran "CUDA" y offloading
4. Medir tiempo de inferencia para confirmar aceleración GPU

Modelo disponible: /mnt/c/local/modelos/qwen2-7b-instruct-q6_k.gguf
```

---

### Variante C: Troubleshooting (si algo falla)

```
Tengo problemas con llama-cpp-python y CUDA. Los síntomas son:
[DESCRIBIR ERROR: ej. "ImportError al importar Llama", "CUDA out of memory", "nvcc not found", etc.]

INFORMACIÓN DEL SISTEMA:
- GPU: [tu GPU]
- CUDA instalado: [sí/no, versión si la sabes]
- Python: [versión]
- WSL2: [sí/no]

Por favor:
1. Diagnosticar la causa raíz del problema
2. Proponer soluciones paso a paso
3. Ejecutar verificaciones necesarias
4. Confirmar que el problema se resolvió

Referencia: docs/CUDA_SETUP_GENERIC.md (sección Troubleshooting)
```

---

## 🧪 Testing del Prompt

### Checklist de Validación

Antes de usar el prompt en producción, verifica:

- [ ] El prompt incluye verificación de `nvidia-smi`
- [ ] Especifica versión exacta de CUDA (12.9)
- [ ] Usa flag correcto: `LLAMA_CUDA=on` (NO `LLAMA_CUBLAS`)
- [ ] Incluye configuración de variables de entorno en `~/.bashrc`
- [ ] Pide crear test de inferencia para validación
- [ ] Menciona tiempo aproximado de compilación (5-10 min)
- [ ] Incluye troubleshooting para errores comunes

---

## 📦 Archivos de Configuración Template

### `.env` (copiar al nuevo proyecto)
```env
# Model Configuration
MODEL_PATH=/mnt/c/local/modelos/qwen2-7b-instruct-q6_k.gguf
MODEL_N_CTX=10000
MODEL_N_GPU_LAYERS=-1

# Generation Parameters
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=2048
DEFAULT_TOP_P=0.95

# API Settings (si usas FastAPI)
API_HOST=0.0.0.0
API_PORT=8000
```

### `config.py` (copiar al nuevo proyecto)
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Model settings
    MODEL_PATH: str = os.getenv("MODEL_PATH", "/path/to/model.gguf")
    MODEL_N_CTX: int = int(os.getenv("MODEL_N_CTX", 2048))
    MODEL_N_GPU_LAYERS: int = int(os.getenv("MODEL_N_GPU_LAYERS", -1))

    # Generation parameters
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", 0.7))
    DEFAULT_MAX_TOKENS: int = int(os.getenv("DEFAULT_MAX_TOKENS", 512))
    DEFAULT_TOP_P: float = float(os.getenv("DEFAULT_TOP_P", 0.95))

    # API settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", 8000))

settings = Settings()
```

### `test_cuda.py` (copiar al nuevo proyecto)
```python
#!/usr/bin/env python3
"""
Test script para verificar llama-cpp-python con CUDA
"""
import time
from llama_cpp import Llama

def test_cuda_inference():
    print("🔧 Cargando modelo con CUDA...")

    # Ajustar MODEL_PATH a tu modelo
    MODEL_PATH = "/mnt/c/local/modelos/qwen2-7b-instruct-q6_k.gguf"

    start_load = time.time()
    llm = Llama(
        model_path=MODEL_PATH,
        n_gpu_layers=-1,  # Todas las capas en GPU
        n_ctx=2048,
        verbose=True      # Ver logs de CUDA
    )
    load_time = time.time() - start_load
    print(f"✅ Modelo cargado en {load_time:.2f}s")

    print("\n🚀 Ejecutando inferencia...")
    start_infer = time.time()
    response = llm(
        "¿Qué es la inteligencia artificial?",
        max_tokens=100,
        temperature=0.7
    )
    infer_time = time.time() - start_infer

    print(f"✅ Inferencia completada en {infer_time:.2f}s")
    print(f"\n📄 Respuesta:\n{response['choices'][0]['text']}")
    print(f"\n📊 Stats:")
    print(f"   - Tokens generados: {response['usage']['completion_tokens']}")
    print(f"   - Tokens/segundo: {response['usage']['completion_tokens'] / infer_time:.2f}")

if __name__ == "__main__":
    test_cuda_inference()
```

### `requirements.txt` (copiar al nuevo proyecto)
```txt
# LLM Core
llama-cpp-python>=0.2.0  # IMPORTANTE: compilar con CUDA, no usar wheels

# Configuration
python-dotenv>=0.21.0

# API (opcional, si usas FastAPI)
fastapi>=0.100.0
uvicorn[standard]>=0.20.0
pydantic>=2.0.0
```

---

## 🎓 Ejemplo de Uso Real

### Escenario: Nuevo Proyecto RAG

```
[Usuario en nuevo proyecto "rag-chatbot"]

Usuario: "Necesito configurar llama-cpp-python con CUDA para este proyecto RAG. Tengo RTX 5070 Ti."

[Usuario copia el PROMPT COMPLETO de arriba]

Claude Code:
1. ✅ Verifica nvidia-smi → GPU detectada
2. ✅ Instala CUDA Toolkit 12.9
3. ✅ Configura ~/.bashrc con variables CUDA
4. ✅ Crea venv y compila llama-cpp-python
5. ✅ Crea .env, config.py, test_cuda.py
6. ✅ Ejecuta test → Inferencia OK en 0.8s

Usuario: "Perfecto, ahora integra esto con mi pipeline RAG"
[Continúa con el desarrollo del proyecto]
```

---

## 🔗 Referencias Rápidas

| Recurso | Ubicación |
|---------|-----------|
| Guía completa | `docs/CUDA_SETUP_GENERIC.md` |
| Troubleshooting | `docs/CUDA_SETUP_GENERIC.md#troubleshooting` |
| llama-cpp-python | https://github.com/abetlen/llama-cpp-python |
| CUDA Toolkit | https://developer.nvidia.com/cuda-downloads |

---

## 📝 Notas Importantes

1. **Compilación tarda 5-10 minutos:** No es un error, es normal.
2. **Usar LLAMA_CUDA, NO LLAMA_CUBLAS:** El flag antiguo está deprecated.
3. **Driver NVIDIA en Windows, Toolkit en WSL:** No confundir.
4. **n_gpu_layers=-1:** Significa "todas las capas en GPU".
5. **Path WSL:** Windows `C:\` se mapea a `/mnt/c/` en WSL.

---

**Última actualización:** Octubre 2025
**Proyecto origen:** yt-dlp (RAG engine)
**Autor:** Configuración validada en RTX 5070 Ti + CUDA 12.9

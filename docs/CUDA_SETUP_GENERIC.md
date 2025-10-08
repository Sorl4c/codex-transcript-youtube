# Guía Genérica: Configurar CUDA + llama-cpp-python en WSL2

## 📌 Descripción
Esta guía te permite configurar **llama-cpp-python con soporte GPU (CUDA)** en cualquier proyecto Python que ejecute modelos `.gguf` locales en WSL2 con GPUs NVIDIA.

**Hardware validado:**
- NVIDIA RTX 5070 Ti
- CUDA Toolkit 12.9
- WSL2 en Windows 10/11

---

## ✅ Requisitos Previos

### 1. Sistema Operativo
- Windows 10/11 con WSL2 activado
- Distribución Ubuntu 22.04 LTS (recomendado)

**Verificar versión WSL:**
```powershell
# Desde PowerShell (Windows)
wsl.exe --list --verbose
```
**Resultado esperado:** Tu distribución debe mostrar `VERSION 2`

### 2. Driver NVIDIA
- Driver NVIDIA actualizado en **Windows** (no en WSL)
- Versión mínima: 525.x o superior

**Verificar desde WSL:**
```bash
nvidia-smi
```
**Resultado esperado:** Debes ver tu GPU listada con información de temperatura, uso, etc.

### 3. Python y herramientas de compilación
```bash
sudo apt update
sudo apt install -y build-essential cmake python3-dev python3-pip python3-venv
```

---

## 🔧 Instalación Paso a Paso

### **PASO 1: Instalar CUDA Toolkit 12.9 en WSL2**

#### 1.1 Añadir repositorio oficial de NVIDIA
```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt update
```

#### 1.2 Instalar CUDA Toolkit
```bash
sudo apt install -y cuda-toolkit-12-9
```

**Nota:** La descarga puede tardar ~10-15 minutos y ocupa ~4 GB.

#### 1.3 Resolver dependencias (si aparecen errores)
```bash
sudo apt --fix-broken install
```

---

### **PASO 2: Configurar Variables de Entorno**

Edita tu archivo `~/.bashrc`:
```bash
nano ~/.bashrc
```

Añade al final:
```bash
# CUDA Configuration
export CUDA_HOME=/usr/local/cuda-12.9
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:$LD_LIBRARY_PATH"
```

Recarga el entorno:
```bash
source ~/.bashrc
```

---

### **PASO 3: Verificar Instalación de CUDA**

```bash
nvcc --version
```

**Resultado esperado:**
```
Cuda compilation tools, release 12.9, V12.9.86
```

---

### **PASO 4: Crear Entorno Virtual Python**

```bash
# Navegar a tu proyecto
cd /path/to/your/project

# Crear venv
python3 -m venv venv

# Activar venv
source venv/bin/activate
```

---

### **PASO 5: Compilar llama-cpp-python con Soporte CUDA**

**IMPORTANTE:** Debes compilar desde el código fuente con flags de CMake.

```bash
CMAKE_ARGS="-DLLAMA_CUDA=on" FORCE_CMAKE=1 pip install --upgrade --force-reinstall llama-cpp-python --no-cache-dir
```

**Notas:**
- `LLAMA_CUDA=on`: Habilita soporte CUDA (NO usar `LLAMA_CUBLAS`, está deprecated)
- `FORCE_CMAKE=1`: Fuerza recompilación
- `--no-cache-dir`: Evita usar builds previos cacheados
- Tiempo estimado: **5-10 minutos**

---

### **PASO 6: Verificar Instalación de llama-cpp-python**

#### 6.1 Test de importación
```bash
python -c "from llama_cpp import Llama; print('✅ llama-cpp-python con CUDA instalado correctamente')"
```

#### 6.2 Test con modelo real
Crea un archivo `test_cuda.py`:

```python
from llama_cpp import Llama

# Ruta a tu modelo .gguf (ajustar según tu sistema)
MODEL_PATH = "/mnt/c/local/modelos/tu-modelo.gguf"

# Cargar modelo con todas las capas en GPU
llm = Llama(
    model_path=MODEL_PATH,
    n_gpu_layers=-1,  # -1 = todas las capas en GPU
    n_ctx=2048,       # Contexto
    verbose=True      # Ver logs de carga
)

# Inferencia simple
response = llm(
    "¿Qué es una estrella?",
    max_tokens=100,
    temperature=0.7
)

print(response["choices"][0]["text"])
```

Ejecutar:
```bash
python test_cuda.py
```

**Resultado esperado:**
- Logs mostrando `CUDA` durante la carga
- Respuesta generada en < 1 segundo (dependiendo del modelo)
- No errores de memoria o compilación

---

## 🎯 Configuración Típica en Proyectos

### Opción A: Variables de Entorno (`.env`)
```env
MODEL_PATH=/mnt/c/local/modelos/qwen2-7b-instruct-q6_k.gguf
MODEL_N_CTX=10000
MODEL_N_GPU_LAYERS=-1
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=2048
```

### Opción B: Archivo de Config Python
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MODEL_PATH: str = os.getenv("MODEL_PATH", "/path/to/model.gguf")
    MODEL_N_CTX: int = int(os.getenv("MODEL_N_CTX", 2048))
    MODEL_N_GPU_LAYERS: int = int(os.getenv("MODEL_N_GPU_LAYERS", -1))
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", 0.7))
    DEFAULT_MAX_TOKENS: int = int(os.getenv("DEFAULT_MAX_TOKENS", 512))

settings = Settings()
```

---

## 🐛 Troubleshooting Común

### Error: `nvcc: command not found`
**Causa:** CUDA Toolkit no instalado o PATH no configurado.

**Solución:**
1. Verificar instalación: `ls /usr/local/cuda-12.9/bin/nvcc`
2. Si existe, revisar `~/.bashrc` y recargar: `source ~/.bashrc`
3. Si no existe, reinstalar: `sudo apt install cuda-toolkit-12-9`

---

### Error: `Could not load dynamic library 'libcuda.so.1'`
**Causa:** Driver NVIDIA no accesible desde WSL.

**Solución:**
1. Verificar driver en Windows (Panel de Control > NVIDIA)
2. Ejecutar `nvidia-smi` en WSL para confirmar visibilidad
3. Reiniciar WSL: `wsl.exe --shutdown` (desde PowerShell)

---

### Error: `CUDA out of memory`
**Causa:** Modelo muy grande para VRAM disponible.

**Solución:**
1. Reducir `n_gpu_layers`:
   ```python
   llm = Llama(model_path=path, n_gpu_layers=20)  # Ejemplo: solo 20 capas
   ```
2. Reducir `n_ctx` (contexto):
   ```python
   llm = Llama(model_path=path, n_ctx=1024)
   ```
3. Usar modelo cuantizado más agresivo (Q4_K_M en lugar de Q6_K)

---

### Compilación falla con errores de CMake
**Causa:** Versión incompatible de CMake o flags incorrectos.

**Solución:**
1. Actualizar CMake:
   ```bash
   pip install --upgrade cmake
   ```
2. Limpiar instalaciones previas:
   ```bash
   pip uninstall llama-cpp-python -y
   pip cache purge
   ```
3. Reintentar compilación con flags correctos

---

## 📦 Dependencias Mínimas (`requirements.txt`)

```txt
llama-cpp-python>=0.2.0  # Compilado con CUDA
python-dotenv>=0.21.0
```

**Nota:** `llama-cpp-python` DEBE compilarse localmente con CUDA, no usar wheels precompilados.

---

## 🧪 Verificación Final - Checklist

- [ ] `nvidia-smi` muestra tu GPU desde WSL
- [ ] `nvcc --version` muestra CUDA 12.9
- [ ] `python -c "from llama_cpp import Llama"` no genera errores
- [ ] Test con modelo `.gguf` completa exitosamente
- [ ] Logs de carga muestran `CUDA` y `offloading layers`
- [ ] Inferencia toma < 1 segundo para respuestas cortas

---

## 📚 Referencias

- [llama-cpp-python Docs](https://github.com/abetlen/llama-cpp-python)
- [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
- [WSL2 GPU Support](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gpu-compute)

---

## 🎯 Próximos Pasos

Una vez configurado CUDA, puedes:
1. Descargar modelos GGUF de [HuggingFace](https://huggingface.co/models?library=gguf)
2. Crear servicios FastAPI con endpoints OpenAI-compatible
3. Integrar en pipelines RAG, agentes, o chatbots
4. Optimizar rendimiento con profiling (`verbose=True`)

---

**Última actualización:** Octubre 2025
**Hardware validado:** NVIDIA RTX 5070 Ti + CUDA 12.9 + WSL2 Ubuntu 22.04

# Guía completa para configurar llama-cpp-python con soporte CUDA en WSL2 (NVIDIA RTX 5070 Ti)

## 📌 Objetivo
Instalar y compilar llama-cpp-python con soporte GPU para poder ejecutar modelos .gguf de forma local y acelerada por CUDA, dentro de WSL2 en Windows, usando una GPU NVIDIA RTX 5070 Ti.

---

## 🧾 Resumen de pasos realizados

### 1. ✅ Requisitos previos
- Windows 10/11 con WSL2 activado
- Distribución Ubuntu instalada y funcionando bajo WSL2
- Driver NVIDIA actualizado en Windows
- GPU RTX 5070 Ti
- Python 3.12+
- pip, venv, build-essential, cmake, etc.

### 2. 🧪 Verificaciones iniciales
**2.1 Confirmar que Ubuntu usa WSL2:**
- Ejecutar `wsl.exe --list --verbose` en Windows
- ✅ Debe indicar que Ubuntu está en versión 2 (Running Version 2)

**2.2 Verificar acceso a GPU desde WSL:**
- Ejecutar `nvidia-smi` en WSL
- ✅ Muestra la GPU desde WSL

### 3. ⚙️ Crear entorno virtual Python
- Navegar al directorio del proyecto
- Crear y activar entorno virtual con `python3 -m venv venv-yt-ia` y `source venv-yt-ia/bin/activate`

### 4. ❌ Primer intento fallido de instalación
- Se intentó compilar con:
  - `CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 pip install --upgrade --force-reinstall llama-cpp-python`
- ❌ Error: LLAMA_CUBLAS está deprecated. El mensaje sugería usar LLAMA_CUDA=on.

### 5. 🚨 Fallo por falta de nvcc
- Ejecutar `nvcc --version`
- ❌ Error: Command 'nvcc' not found
- Esto significaba que el compilador CUDA no estaba instalado en WSL.

### 6. ✅ Instalación del CUDA Toolkit 12.9 en Ubuntu WSL2
**6.1 Añadir repositorio de CUDA:**
- Descargar e instalar el keyring de CUDA
- Actualizar repositorios

**6.2 Instalar toolkit:**
- Instalar `cuda-toolkit-12-9`
- ⚠️ Aparecieron errores de dependencias

**6.3 Solucionar dependencias:**
- Ejecutar `sudo apt --fix-broken install`
- ✅ Esto descargó e instaló +90 paquetes (~4 GB)

### 7. ✅ Añadir CUDA al entorno (.bashrc)
- Comprobar que `nvcc` está instalado en `/usr/local/cuda-12.9/bin/nvcc`
- Añadir variables de entorno en `~/.bashrc`:
  - `export CUDA_HOME=/usr/local/cuda-12.9`
  - `export PATH="$CUDA_HOME/bin:$PATH"`
  - `export LD_LIBRARY_PATH="$CUDA_HOME/lib64:$LD_LIBRARY_PATH"`
- Recargar entorno con `source ~/.bashrc`

### 8. ✅ Verificación de nvcc
- Ejecutar `nvcc --version`
- ✅ Cuda compilation tools, release 12.9, V12.9.86

### 9. 🧩 Compilar llama-cpp-python con soporte CUDA
- Ejecutar:
  - `CMAKE_ARGS="-DLLAMA_CUDA=on" FORCE_CMAKE=1 pip install --upgrade --force-reinstall llama-cpp-python --no-cache-dir`
- ✅ Esta vez no hubo errores, y la compilación se realizó correctamente.

### 10. 🧪 Verificación desde Python
- Importar en Python:
  - `from llama_cpp import Llama`
  - `print("Llama importado correctamente ✅")`
- ✅ Importación exitosa

### 11. 🚀 Prueba con modelo real (tinyllama.gguf)
**11.1 Descargar modelo:**
- Ubicado en: `C:\local\modelos\tinyllama.gguf`
- Acceso desde WSL2: `/mnt/c/local/modelos/tinyllama.gguf`

**11.2 Inferencia simple:**
```python
from llama_cpp import Llama
llm = Llama(
    model_path="/mnt/c/local/modelos/tinyllama.gguf",
    n_gpu_layers=-1
)
respuesta = llm("¿Qué es una estrella?", max_tokens=50)
print(respuesta["choices"][0]["text"])
```
- ✅ Salida exitosa, acelerada por GPU
- 🕒 Tiempo: ~398 ms
- 💬 Respuesta generada correctamente

### 📦 Recomendación: guardar como ia/test_modelo.py
```python
from llama_cpp import Llama
llm = Llama(
    model_path="/mnt/c/local/modelos/tinyllama.gguf",
    n_gpu_layers=-1
)
respuesta = llm("¿Qué es una estrella?", max_tokens=50)
print(respuesta["choices"][0]["text"])
```

## 📁 Estructura recomendada del proyecto
```
/yt-dlp/
├── main.py
├── gui.py
├── ia/
│   ├── test_modelo.py
│   ├── ia_processor.py
│   └── prompts/
└── venv-yt-ia/
```

---

## 🧠 Conclusión
El entorno local con llama-cpp-python + CUDA está correctamente configurado.
Puedes usar cualquier modelo .gguf y aprovechar tu GPU para acelerar inferencias.

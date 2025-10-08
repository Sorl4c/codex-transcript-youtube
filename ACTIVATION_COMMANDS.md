# Comandos de Activación del Entorno Virtual

Este fichero contiene los comandos directos para activar el entorno virtual del proyecto en diferentes sistemas operativos.

## 🚀 Activación por Sistema Operativo

### Windows (CMD)
```cmd
.venv\Scripts\activate.bat
```

### Windows (PowerShell)
```powershell
.venv\Scripts\Activate.ps1
```

### WSL/Git Bash
```bash
source .venv/Scripts/activate
```

### Linux/Mac (si aplica)
```bash
source .venv/bin/activate
```

## ✅ Verificación de Activación

Para verificar que el entorno está activo:
```bash
# Verificar si VIRTUAL_ENV está definido
echo $VIRTUAL_ENV

# O simplemente revisar el prompt (debería mostrar (.venv))
```

## 🔧 Comandos Útiles Post-Activación

Una vez activado el entorno, puedes usar estos comandos:

### GUI Principal
```bash
streamlit run gui_streamlit.py
```

### RAG CLI
```bash
# Ver estadísticas
python -m rag_engine.rag_cli stats

# Hacer una consulta
python -m rag_engine.rag_cli query "tu pregunta aquí" --top-k 5

# Ingerir documento
python -m rag_engine.rag_cli ingest transcripts_for_rag/archivo.txt
```

### CLI para Procesar Videos
```bash
# Procesar un video de YouTube
python main.py <youtube_url>

# Con idioma específico
python main.py <youtube_url> -l es

# Guardar en archivo
python main.py <youtube_url> -o salida.txt
```

## 📋 Notas Importantes

- **Directorio del entorno**: `.venv/` (raíz del proyecto)
- **Python requerido**: Python 3.8+
- **Requisitos**: Instalar con `pip install -r requirements.txt` si es necesario
- **Desactivar**: Escribe `deactivate` para salir del entorno virtual

## 🐛 Solución de Problemas

### Si el entorno no existe:
```bash
# Crear entorno virtual
python -m venv .venv

# Luego instalar dependencias
source .venv/Scripts/activate  # o el comando para tu sistema
pip install -r requirements.txt
```

### Si hay problemas de permisos en Windows:
```cmd
# Ejecutar como administrador o usar PowerShell con permisos elevados
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Si los comandos no funcionan:
1. Verifica que estás en la raíz del proyecto
2. Confirma que el directorio `.venv/` existe
3. Asegúrate de haber activado el entorno correcto para tu sistema

---
*Fichero de referencia rápida. Mantener actualizado si cambian las rutas o comandos.*
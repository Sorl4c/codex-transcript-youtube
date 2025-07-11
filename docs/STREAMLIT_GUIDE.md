# Guía de la Interfaz Web con Streamlit

## Tabla de Contenidos
- [Introducción](#introducción)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso Básico](#uso-básico)
- [Características Principales](#características-principales)
- [Preguntas Frecuentes](#preguntas-frecuentes)

## Introducción

La interfaz web con Streamlit proporciona una forma moderna y accesible de gestionar tus vídeos y transcripciones de YouTube. Esta guía te ayudará a comenzar a utilizar todas sus funcionalidades.

## Requisitos

- Python 3.8 o superior
- Conexión a Internet
- Navegador web moderno (Chrome, Firefox, Safari, Edge)

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/youtube-subtitle-downloader.git
   cd youtube-subtitle-downloader
   ```

2. Crea y activa un entorno virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Inicia la aplicación:
   ```bash
   streamlit run gui_streamlit.py
   ```

5. Abre tu navegador en la dirección que se muestra en la terminal (normalmente http://localhost:8501)

## Uso Básico

### Añadir Nuevos Vídeos
1. Navega a la pestaña "Añadir Vídeos"
2. Introduce una o más URLs de YouTube (una por línea)
3. Selecciona el modelo de IA para el resumen
4. Haz clic en "Procesar"

### Explorar la Videoteca
1. Ve a la página "Videoteca".
2. Utiliza los filtros de búsqueda y las opciones de ordenación para encontrar vídeos.
3. **Para ver los detalles de un vídeo, simplemente haz clic en cualquier parte de su fila en la tabla.**
4. Los detalles del vídeo (título, resumen, transcripción, etc.) aparecerán automáticamente debajo de la tabla.

### Exportar Datos
1. Filtra los vídeos que deseas exportar
2. Haz clic en el botón "Exportar"
3. Selecciona el formato de salida (JSON, CSV o Markdown)
4. Guarda el archivo en tu dispositivo

## Características Principales

### Panel de Control
- Resumen de estadísticas de uso
- Uso de recursos del sistema
- Estado de la base de datos

### Gestión de Vídeos
- Búsqueda y filtrado avanzado.
- **Selección de vídeo intuitiva**: Haz clic en cualquier fila para ver los detalles al instante.
- Vista previa de resúmenes y transcripciones completas.
- Edición de metadatos.
- Eliminación segura con confirmación.

### Personalización
- Tema claro/oscuro
- Ajustes de visualización
- Configuración de modelos predeterminados

## Preguntas Frecuentes

### ¿Cómo actualizo la aplicación?
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

### ¿Dónde se almacenan los datos?
Los datos se almacenan en una base de datos SQLite llamada `videos.db` en el directorio del proyecto.

### ¿Cómo puedo realizar copias de seguridad?
Simplemente haz una copia del archivo `videos.db`. Puedes restaurar los datos copiando el archivo de vuelta a su ubicación original.

## Solución de Problemas

### La aplicación no se inicia
- Verifica que todas las dependencias estén instaladas
- Asegúrate de que el puerto 8501 no esté en uso
- Revisa los mensajes de error en la terminal

### No se pueden descargar subtítulos
- Verifica tu conexión a Internet
- Asegúrate de que las URLs de YouTube sean válidas
- Comprueba que los vídeos tengan subtítulos disponibles

## Soporte

Si necesitas ayuda, por favor:
1. Revisa la documentación
2. Busca en los issues de GitHub
3. Si el problema persiste, crea un nuevo issue con los detalles del error

---

Última actualización: 1 de julio de 2025

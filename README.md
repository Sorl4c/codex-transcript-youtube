# Gestor de Vídeos de YouTube con IA ✨

Esta es una aplicación web construida con Streamlit que permite a los usuarios gestionar una colección de vídeos de YouTube. La herramienta puede descargar subtítulos, procesarlos y generar resúmenes, ideas clave y títulos sugeridos utilizando la API de Google Gemini.

## 🚀 Características Principales

-   **Agregar Vídeos desde URL:** Pega una o más URLs de YouTube para añadirlas a tu colección.
-   **Dos Modos de Procesamiento:**
    1.  **Local:** Descarga la transcripción del vídeo y la guarda en la base de datos.
    2.  **API (Gemini):** Envía la transcripción a la API de Google Gemini para generar un resumen detallado, una lista de ideas clave y un título optimizado.
-   **Videoteca Interactiva:** Visualiza todos los vídeos procesados en una tabla. Aunque la selección directa en la tabla está en desarrollo, puedes gestionar tus vídeos.
-   **Análisis Detallado:** Una vista avanzada que permite filtrar vídeos por canal y luego seleccionarlos de una lista para ver sus detalles, incluyendo:
    -   Resumen generado por la IA.
    -   Transcripción completa.
    -   Botones para copiar el contenido al portapapeles.
-   **Gestión de Vídeos:** Elimina vídeos de tu colección directamente desde la interfaz.
-   **Base de Datos Local:** Toda la información se almacena de forma persistente en una base de datos SQLite (`subtitles.db`).

## 🛠️ Instalación

Sigue estos pasos para poner en marcha la aplicación en tu entorno local.

### 1. Prerrequisitos

-   Python 3.9 o superior.
-   `pip` y `venv` para la gestión de paquetes y entornos virtuales.

### 2. Clona el Repositorio

Si estás trabajando con git, clona el repositorio. Si no, asegúrate de tener todos los archivos del proyecto en una carpeta.

### 3. Configura el Entorno Virtual

Es altamente recomendable crear un entorno virtual para aislar las dependencias del proyecto.

```bash
# Navega a la carpeta del proyecto
cd /ruta/a/tu/proyecto

# Crea el entorno virtual
python -m venv venv

# Activa el entorno
# En Windows:
venv\\Scripts\\activate
# En macOS/Linux:
source venv/bin/activate
```

### 4. Instala las Dependencias

Instala todas las librerías necesarias con el siguiente comando:

```bash
pip install -r requirements.txt
```

### 5. Configura las Variables de Entorno

Para utilizar el modo de procesamiento con IA, necesitas una clave de API de Google Gemini.

1.  Crea un archivo llamado `.env` en la raíz del proyecto.
2.  Añade tu clave de API al archivo de la siguiente manera:

    ```
    GEMINI_API_KEY="TU_API_KEY_AQUI"
    ```

    La aplicación cargará esta clave automáticamente.

## ▶️ Cómo Ejecutar la Aplicación

Una vez que hayas completado la instalación, ejecuta el siguiente comando en tu terminal (con el entorno virtual activado):

```bash
streamlit run gui_streamlit.py
```

Se abrirá una nueva pestaña en tu navegador con la aplicación en funcionamiento.

---
*Desarrollado con la ayuda de Cascade, tu asistente de programación AI.*

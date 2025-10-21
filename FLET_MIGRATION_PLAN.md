# Plan de Migración a Flet 0.70.0.dev6333

## 📋 **Filosofía: MVP Primero, Arquitectura Después**

### **Objetivo de la Fase 1**:
Tener una UI funcional con videoteca completa que demuestre el potencial de Flet y permita evaluación objetiva vs Streamlit.

---

## 🏗️ **Estructura de Carpetas (Completa desde Fase 1)**

```
flet_ui/
├── main.py                    # Entry point - MVP funcional
├── requirements-flet.txt      # Dependencias Flet
├── config/
│   ├── __init__.py
│   ├── settings.py           # Configuración básica
│   └── theme.py              # Tema visual
├── core/
│   ├── __init__.py
│   ├── app.py                # App principal (simple)
│   └── session.py            # Estado global básico
├── services/
│   ├── __init__.py
│   ├── database_service.py   # Wrapper a db.py
│   └── youtube_service.py    # Wrapper a downloader/parser
├── models/
│   ├── __init__.py
│   └── video.py              # Modelo Video existente
├── components/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── video_table.py    # Tabla de videos (MVP)
│   │   └── search_bar.py     # Barra de búsqueda (MVP)
│   ├── video/
│   │   ├── __init__.py
│   │   └── video_details.py  # Detalles básicos (MVP)
│   └── layout/
│       ├── __init__.py
│       ├── sidebar.py        # Navegación básica
│       └── header.py         # Header simple
├── pages/
│   ├── __init__.py
│   ├── base_page.py          # Clase base simple
│   └── video_library/
│       ├── __init__.py
│       └── library_page.py   # Página principal (MVP)
└── utils/
    ├── __init__.py
    └── helpers.py            # Utilidades básicas
```

---

## 🚀 **Fase 1: MVP Funcional (Issues 1-8) - YA FUNCIONAL**

### **Entregable**: UI completa de videoteca con búsqueda, filtrado y detalles

- [ ] **Issue 1: Crear estructura de carpetas completa**
  - [ ] Crear directorio `flet_ui/` en la raíz del proyecto
  - [ ] Crear toda la estructura de subdirectorios
  - [ ] Agregar todos los archivos `__init__.py` necesarios
  - [ ] Crear archivos vacíos para cada módulo planificado

- [ ] **Issue 2: Instalar Flet 0.70.0.dev6333 y configurar requirements**
  - [ ] Instalar versión específica: `pip install flet==0.70.0.dev6333`
  - [ ] Crear `requirements-flet.txt` con todas las dependencias
  - [ ] Incluir dependencias existentes del proyecto
  - [ ] Probar instalación en entorno virtual limpio

- [ ] **Issue 3: Implementar servicios básicos**
  - [ ] Crear `services/database_service.py` como wrapper de `db.py`
  - [ ] Implementar `DatabaseService.get_all_videos()`
  - [ ] Implementar `DatabaseService.get_video_by_id()`
  - [ ] Implementar `DatabaseService.delete_video()`
  - [ ] Implementar `DatabaseService.update_summary()`
  - [ ] Crear `services/youtube_service.py` como wrapper de `downloader.py` y `parser.py`
  - [ ] Implementar métodos básicos de extracción de video info

- [ ] **Issue 4: Crear VideoTable component**
  - [ ] Implementar clase `VideoTable` en `components/data/video_table.py`
  - [ ] Integrar con `DatabaseService` para obtener datos
  - [ ] Implementar sorting por columnas (fecha, título, canal)
  - [ ] Agregar paginación básica
  - [ ] Implementar selección de filas
  - [ ] Agregar eventos de click para ver detalles
  - [ ] Manejar datasets grandes (>1000 videos)

- [ ] **Issue 5: Implementar SearchBar**
  - [ ] Crear clase `SearchBar` en `components/data/search_bar.py`
  - [ ] Implementar campo de texto con búsqueda en tiempo real
  - [ ] Conectar con `VideoTable` para filtrado instantáneo
  - [ ] Agregar placeholder descriptivo
  - [ ] Implementar debounce para evitar búsquedas excesivas
  - [ ] Agregar botón de limpiar búsqueda

- [ ] **Issue 6: Desarrollar VideoDetails**
  - [ ] Crear clase `VideoDetails` en `components/video/video_details.py`
  - [ ] Implementar tabs para resumen y transcripción
  - [ ] Agregar botones de copiar al portapapeles
  - [ ] Implementar botón de eliminar video
  - [ ] Mostrar metadata (título, canal, fecha)
  - [ ] Manejar videos sin resumen
  - [ ] Agregar indicador de carga para operaciones largas

- [ ] **Issue 7: Crear LibraryPage**
  - [ ] Implementar clase `LibraryPage` en `pages/video_library/library_page.py`
  - [ ] Integrar `VideoTable`, `SearchBar` y `VideoDetails`
  - [ ] Implementar layout responsivo
  - [ ] Agregar manejo de estado entre componentes
  - [ ] Implementar actualización automática de datos
  - [ ] Agregar manejo de errores básico

- [ ] **Issue 8: Implementar navegación básica**
  - [ ] Crear clase `Sidebar` en `components/layout/sidebar.py`
  - [ ] Implementar navegación entre secciones básicas
  - [ ] Crear clase `Header` en `components/layout/header.py`
  - [ ] Implementar `BasePage` en `pages/base_page.py`
  - [ ] Crear clase `App` en `core/app.py` como orquestador principal
  - [ ] Implementar sistema de routing simple
  - [ ] Crear `main.py` como entry point

### **Funcionalidades del MVP Fase 1:**
- ✅ **Listado completo de vídeos** con paginación
- ✅ **Búsqueda en tiempo real** por título/canal
- ✅ **Ordenación** por fecha, título, canal
- ✅ **Detalles de vídeo** con resumen/transcripción
- ✅ **Copiar al portapapeles** funcional
- ✅ **Eliminación de vídeos**
- ✅ **Estadísticas básicas** (total vídeos, etc.)
- ✅ **Diseño responsivo** simple

---

## 📈 **Fase 2: Mejoras y Nuevas Funcionalidades (Issues 9-18)**

### **Objetivo**: Agregar Agregar Vídeos y Búsqueda RAG**

- [ ] **Issue 9: Crear AddVideosPage**
  - [ ] Implementar formulario para múltiples URLs
  - [ ] Agregar textarea para entrada de URLs
  - [ ] Implementar validación de URLs YouTube
  - [ ] Agregar botones de procesamiento
  - [ ] Crear vista previa de URLs detectadas

- [ ] **Issue 10: Implementar procesamiento batch**
  - [ ] Integrar con `YouTubeService` para descarga
  - [ ] Implementar barras de progreso reales
  - [ ] Agregar cancelación de procesos
  - [ ] Mostrar estado de cada URL (procesando, error, completado)
  - [ ] Implementar modo Local vs API
  - [ ] Agregar opción de mantener timestamps

- [ ] **Issue 11: Integrar RAG básico**
  - [ ] Crear `services/rag_service.py` como wrapper de `rag_interface.py`
  - [ ] Implementar búsqueda RAG simple
  - [ ] Crear vista de resultados básica
  - [ ] Agregar input de consultas
  - [ ] Mostrar metadata de resultados

- [ ] **Issue 12: Agregar configuración de procesamiento**
  - [ ] Implementar selector modo Local/API
  - [ ] Agregar checkbox para mantener timestamps
  - [ ] Crear configuración de ingestión RAG
  - [ ] Implementar persistencia de preferencias

- [ ] **Issue 13: Implementar ingestión RAG opcional**
  - [ ] Agregar checkbox "Ingestar en RAG" en AddVideosPage
  - [ ] Mostrar estadísticas RAG disponibles
  - [ ] Implementar ingestión automática durante procesamiento
  - [ ] Agregar feedback de éxito/error en ingestión

- [ ] **Issue 14: Crear notificaciones Toast**
  - [ ] Implementar sistema de notificaciones no intrusivo
  - [ ] Agregar notificaciones para operaciones exitosas
  - [ ] Implementar notificaciones de error
  - [ ] Agregar animaciones y auto-dismiss
  - [ ] Crear diferentes tipos (success, error, warning, info)

- [ ] **Issue 15: Agregar indicadores de carga**
  - [ ] Implementar spinners para operaciones largas
  - [ ] Agregar progressBar para descargas
  - [ ] Crear overlay de carga para toda la app
  - [ ] Implementar skeletons para carga de datos
  - [ ] Agregar texto descriptivo durante operaciones

- [ ] **Issue 16: Implementar filtros avanzados**
  - [ ] Agregar filtro por canal
  - [ ] Implementar filtro por rango de fechas
  - [ ] Crear filtro por videos con/sin resumen
  - [ ] Agregar combinación de múltiples filtros
  - [ ] Implementar persistencia de filtros

- [ ] **Issue 17: Crear diálogo de confirmación**
  - [ ] Implementar diálogo modal para eliminación
  - [ ] Agregar confirmación para operaciones destructivas
  - [ ] Crear diálogos personalizables
  - [ ] Implementar manejo de cancelación
  - [ ] Agregar animaciones de entrada/salida

- [ ] **Issue 18: Optimizar rendimiento con caché básico**
  - [ ] Implementar caché para consultas de base de datos
  - [ ] Agregar caché para búsquedas recientes
  - [ ] Crear invalidación de caché inteligente
  - [ ] Implementar lazy loading para datasets grandes
  - [ ] Agregar indicadores de datos cacheados

---

## 🎨 **Fase 3: Componentes Avanzados (Issues 19-28)**

### **Objetivo**: Completar funcionalidades faltantes y mejoras UX

- [ ] **Issue 19: Crear AnalysisPage**
  - [ ] Implementar vista por canal
  - [ ] Agregar lista de canales disponibles
  - [ ] Crear filtrado por canal
  - [ ] Implementar estadísticas por canal
  - [ ] Agregar gráficos básicos de distribución

- [ ] **Issue 20: Implementar gráficos básicos**
  - [ ] Integrar librería de gráficos para Flet
  - [ ] Crear gráfico circular para categorías
  - [ ] Implementar gráfico de barras para estadísticas
  - [ ] Agregar gráfico de línea para evolución temporal
  - [ ] Implementar tooltips interactivos

- [ ] **Issue 21: Agregar exportación de datos**
  - [ ] Crear diálogo de exportación
  - [ ] Implementar exportación a CSV
  - [ ] Agregar exportación a JSON
  - [ ] Implementar exportación de transcripciones individuales
  - [ ] Agregar opciones de filtrado para exportación

- [ ] **Issue 22: Crear configuración de preferencias**
  - [ ] Implementar página de configuración
  - [ ] Agregar configuración de tema (claro/oscuro)
  - [ ] Crear configuración de idioma
  - [ ] Implementar configuración de procesamiento por defecto
  - [ ] Agregar configuración de RAG preferida

- [ ] **Issue 23: Implementar atajos de teclado**
  - [ ] Agregar atajos para navegación (Ctrl+1, Ctrl+2, etc.)
  - [ ] Implementar atajo para búsqueda (Ctrl+F)
  - [ ] Crear atajo para agregar videos (Ctrl+N)
  - [ ] Agregar atajo para cerrar diálogos (Escape)
  - [ ] Implementar atajo para refrescar datos (F5)

- [ ] **Issue 24: Agregar modo oscuro/claro**
  - [ ] Crear definición de temas en `config/theme.py`
  - [ ] Implementar cambio dinámico de tema
  - [ ] Agregar persistencia de preferencia de tema
  - [ ] Asegurar contraste y legibilidad en ambos modos
  - [ ] Implementar transiciones suaves entre temas

- [ ] **Issue 25: Crear componente de batch operations**
  - [ ] Implementar selección múltiple de videos
  - [ ] Agregar operaciones batch (eliminar, exportar, ingestar RAG)
  - [ ] Crear diálogo de confirmación para operaciones batch
  - [ ] Implementar progress indicator para operaciones batch
  - [ ] Agregar manejo de errores por lote

- [ ] **Issue 26: Implementar validación de forms**
  - [ ] Crear validador de URLs YouTube
  - [ ] Implementar validación de entradas de texto
  - [ ] Agregar mensajes de error descriptivos
  - [ ] Crear validación en tiempo real
  - [ ] Implementar deshabilitado de botones hasta validación

- [ ] **Issue 27: Agregar sistema de logging**
  - [ ] Implementar logging de operaciones del usuario
  - [ ] Crear logs de errores y excepciones
  - [ ] Agregar logs de rendimiento
  - [ ] Implementar rotación de logs
  - [ ] Crear visor de logs básico para debugging

- [ ] **Issue 28: Crear tests básicos**
  - [ ] Implementar tests unitarios para servicios
  - [ ] Crear tests para componentes UI básicos
  - [ ] Agregar tests de integración para flujos principales
  - [ ] Implementar tests de rendimiento para datasets grandes
  - [ ] Crear tests automatizados de regresión visual

---

## 🔧 **Fase 4: Optimización y Polish (Issues 29-35)**

### **Objetivo**: Optimización, testing y preparación para producción

- [ ] **Issue 29: Optimizar tiempos de arranque**
  - [ ] Medir tiempos de arranque actuales en WSL
  - [ ] Implementar carga lazy de componentes pesados
  - [ ] Optimizar importación de módulos
  - [ ] Agregar preload de datos críticos
  - [ ] Implementar caching de componentes UI

- [ ] **Issue 30: Implementar lazy loading para datasets grandes**
  - [ ] Implementar paginación virtual para tablas grandes
  - [ ] Agargar carga incremental de datos
  - [ ] Crear indicadores de carga durante scroll
  - [ ] Implementar cache de páginas visitadas
  - [ ] Optimizar consultas a base de datos

- [ ] **Issue 31: Agregar manejo de errores robusto**
  - [ ] Implementar captura global de excepciones
  - [ ] Crear diálogos de error amigables
  - [ ] Agregar reporte automático de errores
  - [ ] Implementar modo offline básico
  - [ ] Crear sistema de recuperación de estado

- [ ] **Issue 32: Crear tests de integración completos**
  - [ ] Implementar tests E2E para flujos completos
  - [ ] Crear tests de rendimiento automatizados
  - [ ] Agregar tests de compatibilidad entre navegadores
  - [ ] Implementar tests de carga estrés
  - [ ] Crear suite de tests de regresión

- [ ] **Issue 33: Implementar persistencia de estado**
  - [ ] Guardar última búsqueda realizada
  - [ ] Persistir filtros seleccionados
  - [ ] Recordar última página visitada
  - [ ] Guardar configuración de ordenación
  - [ ] Implementar sesión persistente

- [ ] **Issue 34: Crear documentación de componentes**
  - [ ] Documentar API de cada componente
  - [ ] Crear ejemplos de uso para componentes
  - [ ] Implementar documentación interactiva
  - [ ] Agregar guía de desarrollo
  - [ ] Crear diagramas de arquitectura

- [ ] **Issue 35: Configurar build y packaging**
  - [ ] Crear script de build para producción
  - [ ] Implementar minificación de assets
  - [ ] Configurar packaging multiplataforma
  - [ ] Agregar script de despliegue automatizado
  - [ ] Crear instaladores para Windows/Linux

---

## 🎯 **Criterios de Éxito de la Fase 1**

### **Métricas Objetivas:**
- **Tiempo de arranque**: < 3 segundos en WSL
- **Rendimiento**: 1000 vídeos en tabla con filtering instantáneo
- **Memory usage**: < 200MB en reposo
- **UX**: No bloqueos durante operaciones largas

### **Funcionalidades Críticas:**
- Todas las operaciones CRUD de vídeos funcionando
- Búsqueda y filtrado responsivo
- Copiar/eliminar vídeos funcionando
- Visualización de detalles completa

---

## 💡 **Ventajas de Este Enfoque Incremental**

1. **Valor inmediato**: Ya en Fase 1 tienes una UI completa y funcional
2. **Riesgo mitigado**: Solo inviertis tiempo en Flet si el MVP convence
3. **Comparación objetiva**: Podés medir rendimiento vs Streamlit directamente
4. **Estructura preparada**: La carpeta está lista para escalar
5. **Learning curve**: Aprendés Flet progresivamente
6. **Feedback rápido**: Tenés algo tangible para probar en días, no semanas

---

## 📋 **Entregable Fase 1: MVP Completo**

```
✅ Videoteca funcional con 100+ vídeos de prueba
✅ Búsqueda en tiempo real (< 100ms response)
✅ Ordenación por múltiples campos
✅ Detalles completos de cada vídeo
✅ Copiar transcripción/resumen al portapapeles
✅ Eliminar vídeos con confirmación
✅ Estadísticas básicas en tiempo real
✅ Diseño limpio y responsivo
✅ Navegación básica entre secciones
```

**Resultado**: Una aplicación Flet completa que reemplaza funcionalmente a la videoteca de Streamlit, lista para evaluación objetiva y base sólida para expansiones futuras.

---

## 🚀 **Cómo Comenzar**

### **Comandos Iniciales:**
```bash
# 1. Crear estructura base
mkdir flet_ui
cd flet_ui

# 2. Instalar Flet versión específica
pip install flet==0.70.0.dev6333

# 3. Crear requirements
echo "flet==0.70.0.dev6333" > requirements-flet.txt
echo "pandas>=1.3.0" >> requirements-flet.txt
echo "pyperclip>=1.8.2" >> requirements-flet.txt

# 4. Probar instalación
python -c "import flet; print(f'Flet version: {flet.__version__}')"
```

### **Primer Archivo a Crear: `main.py`**
```python
import flet as ft
from core.app import App

def main(page: ft.Page):
    app = App(page)
    app.run()

if __name__ == "__main__":
    ft.app(target=main)
```

**¡Listo para empezar con el Issue 1!** 🎉
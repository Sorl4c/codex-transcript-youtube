# Calm Tech Design System (Draft)

Este documento define los principios visuales y de interacción para la evolución del gestor de subtítulos de YouTube. Se basa en tendencias actuales (2024) de diseño calm tech y dashboards de análisis, con el objetivo de ofrecer una experiencia clara, elegante y con bajo ruido cognitivo.

## 1. Principios de Diseño

- **Calma sobre impacto**: priorizar espacio en blanco, jerarquías claras y feedback sutil en lugar de saturar la interfaz.
- **Estados visibles**: cada acción del pipeline (descarga, parsing, resumen) debe mostrar estado, progreso y resultado.
- **Progresión asistida**: guiar al usuario con microcopy, tooltips y asistentes paso a paso para reducir errores.
- **Consistencia cross-framework**: los mismos tokens visuales y patrones deben funcionar en Tkinter, PySide6 y Streamlit.
- **Accesibilidad integrada**: contraste AA mínimo, navegación por teclado, tamaños de fuente ajustables y modo oscuro/claro.

## 2. Tokens de Diseño

| Categoría     | Token                     | Claro          | Oscuro         |
|---------------|---------------------------|----------------|----------------|
| **Color**     | `color.surface`           | `#F8FAFC`      | `#1E293B`      |
|               | `color.surface.alt`       | `#EEF2FF`      | `#27364D`      |
|               | `color.primary`           | `#2563EB`      | `#60A5FA`      |
|               | `color.accent`            | `#10B981`      | `#34D399`      |
|               | `color.warning`           | `#F59E0B`      | `#FBBF24`      |
|               | `color.error`             | `#EF4444`      | `#F87171`      |
|               | `color.success`           | `#0EA5E9`      | `#38BDF8`      |
|               | `color.text.primary`      | `#0F172A`      | `#E2E8F0`      |
|               | `color.text.secondary`    | `#475569`      | `#94A3B8`      |
| **Tipografía**| `font.family`             | `Inter, Roboto, system` | Igual |
|               | `font.display` (32 px)    | `Inter SemiBold` | `Inter SemiBold` |
|               | `font.h1` (24 px)         | `Inter SemiBold` | `Inter SemiBold` |
|               | `font.h2` (18 px)         | `Inter Medium` | `Inter Medium` |
|               | `font.body` (14 px)       | `Inter Regular` | `Inter Regular` |
|               | `font.caption` (12 px)    | `Inter Medium` | `Inter Medium` |
| **Espaciado** | `space.xs`                | `4 px`         | `4 px`         |
|               | `space.sm`                | `8 px`         | `8 px`         |
|               | `space.md`                | `16 px`        | `16 px`        |
|               | `space.lg`                | `24 px`        | `24 px`        |
|               | `space.xl`                | `32 px`        | `32 px`        |
| **Bordes**    | `radius.sm`               | `8 px`         | `8 px`         |
|               | `radius.lg`               | `16 px`        | `16 px`        |
| **Sombras**   | `shadow.soft`             | `0 12px 32px rgba(15,23,42,0.08)` | `0 12px 32px rgba(15,23,42,0.35)` |
|               | `shadow.inner`            | `inset 0 1px 2px rgba(148,163,184,0.25)` | `inset 0 1px 2px rgba(148,163,184,0.35)` |

> **Nota**: Las paletas están optimizadas para displays SDR. Para HDR o monitores de alto brillo, incrementar contrastes un 10 %.

## 3. Layout Maestro

```
┌─────────────────────────────────────────────────────────────┐
│ Header (logo, toggle tema, accesos rápidos) — altura 72 px  │
├───────────┬─────────────────────────────────────────────────┤
│ Sidebar   │ Tabs principales:                               │
│ 20 %      │ • Videoteca                                      │
│           │ • Tareas                                         │
│           │ • Insights (futuro)                              │
│           │ • Configuración                                  │
├───────────┴─────────────────────────────────────────────────┤
│ Panel de logs plegable (estado del sistema, collapsible)    │
└─────────────────────────────────────────────────────────────┘
```

- **Sidebar**: iconografía minimal (Lucide/Tabler), indicador de sección activa; permite contraerse.
- **Contenido principal**: rejilla 12 columnas. Secciones claves:
  - `Videoteca`: lista en vista tabla + tarjeta de detalle lateral.
  - `Tareas`: tarjetas de progreso con barras animadas y botones “Ver log”.
  - `Agregar videos`: wizard modal (3 pasos).
- **Panel inferior**: logs estructurados con filtros por severidad (`INFO`, `WARN`, `ERROR`).

## 4. Componentes Clave

### 4.1 Tarjetas de Video
- Cabecera con título + favicon del canal.
- Badges: idioma, estado (`Listo`, `Procesando`, `Error`).
- Metadata: duración, fecha de descarga, resumen corto.
- Acciones rápidas: ver subtítulos, exportar Markdown, marcar favorito.

### 4.2 Panel de Tareas
- Cards horizontales con: nombre del video, paso actual, barra de progreso, CTA “Ver detalles”.
- Microinteracción: barra que cambia de color según estado.
- Posibilidad de pausar/reanudar (futuro).

### 4.3 Wizard de Ingesta
- Paso 1: URL + validación en vivo.
- Paso 2: idioma preferido (auto-detect + lista).
- Paso 3: confirmación y opciones (procesar en lote, generar resumen).
- Subheader con tiempos estimados y prerequisitos (`GEMINI_API_KEY`, base de datos).

### 4.4 Panel de Logs
- Tabla o lista con columnas: hora, nivel, mensaje, origen.
- Filtro por nivel + buscador.
- Botón “Exportar log” y toggle “Mostrar/ocultar”.

## 5. Interacciones y Feedback

- **Estados de botón**: normal, hover, pressed, loading (spinner inline), disabled.
- **Toasts**: aparecen en esquina inferior derecha, desaparecen tras 4 s; variantes `success`, `warning`, `error`.
- **Barras de progreso**: lineales con animación suave; mostrar porcentaje y texto del paso (`Descargando`, `Resumiendo`).
- **Transiciones**: usar `200–250 ms` con easing `cubic-bezier(0.2, 0.8, 0.2, 1)`.
- **Validaciones**: inline con mensajes específicos y links a guías cuando aplique.

## 6. Accesibilidad

- Contraste mínimo 4.5:1 en texto y elementos interactivos.
- Todas las acciones deben tener atajos (`Ctrl+L` URL, `Ctrl+Shift+A` abrir wizard, `Ctrl+Tab` cambiar pestañas).
- Focus visible con outline de alto contraste (`color.accent`).
- Text scaling global (niveles 90 %, 100 %, 115 %, 130 %).
- Tooltips con descripciones clave para iconos.

## 7. Próximos Entregables

1. **Tokens reutilizables** en Python (`ui/theme.py`) para Tkinter y PySide6.
2. **Mockups de alta fidelidad** (Figma o equivalente) para pantalla principal y wizard.
3. **Actualización de `gui.py` y `qt_ui`** para usar el layout maestro y componentes descritos.
4. **Guía de microcopy**: mensajes de éxito/error, vacíos y onboarding.
5. **Pruebas de accesibilidad** con checklist WCAG 2.1 AA.

## 8. Referencias de Tendencia (2024)

- Material Design 3 y Material You — Google.
- Fluent 2 Design System — Microsoft.
- Linear App + Arc Browser para calm tech y dashboards de foco.
- Nielsen Norman Group — heurísticas de visibilidad y feedback.

> Documento en iteración continua. Actualizar conforme se implementen componentes y se validen decisiones con uso real.


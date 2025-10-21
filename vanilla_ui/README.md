# Vanilla UI Videoteca

Este prototipo implementa la fase inicial del plan de migración a Flet utilizando HTML5, CSS moderno y JavaScript vanilla. La estructura replica el enfoque por capas y componentes descrito en `FLET_MIGRATION_PLAN.md`, manteniendo servicios, modelos, páginas y utilidades desacoplados.

## Estructura

```
vanilla_ui/
├── index.html
├── assets/
│   ├── css/
│   │   ├── main.css
│   │   ├── layout/
│   │   │   └── layout.css
│   │   ├── components/
│   │   │   ├── search-bar.css
│   │   │   ├── video-details.css
│   │   │   └── video-table.css
│   │   └── utils/
│   │       └── variables.css
│   └── js/
│       ├── app.js
│       ├── components/
│       │   ├── Header.js
│       │   ├── SearchBar.js
│       │   ├── Sidebar.js
│       │   ├── StatsPanel.js
│       │   ├── VideoDetails.js
│       │   └── VideoTable.js
│       ├── core/
│       │   ├── app.js
│       │   ├── router.js
│       │   └── state.js
│       ├── models/
│       │   └── video.js
│       ├── pages/
│       │   ├── BasePage.js
│       │   └── LibraryPage.js
│       ├── services/
│       │   ├── databaseService.js
│       │   └── youtubeService.js
│       └── utils/
│           ├── dom.js
│           └── formatters.js
└── data/
    └── sample_videos.json
```

## Características

- Tabla responsiva con ordenamiento, paginación y compatibilidad con datasets medianos.
- Búsqueda incremental con `debounce` y filtros aplicados desde el estado global.
- Panel de detalles con pestañas para resumen y transcripción, más acciones principales.
- Arquitectura basada en módulos ES6 (`type="module"`) y publicación de eventos en el estado centralizado.
- CSS moderno con `@layer`, variables personalizadas, glassmorphism y Grid/Flex para la shell principal.

## Ejecución local

1. Posicionarse en la raíz del repositorio y levantar un servidor estático:

   ```bash
   cd vanilla_ui
   python -m http.server 8000
   ```

2. Abrir `http://localhost:8000` en el navegador.

> Nota: Para evitar limitaciones de CORS al cargar `sample_videos.json`, abrir la aplicación mediante servidor HTTP y no directo desde el sistema de archivos.

## Próximos pasos sugeridos

- Sustituir el `DatabaseService` con llamadas reales a `db.py` vía API interna.
- Conectar las acciones de eliminación y actualización de resumen con endpoints persistentes.
- Añadir pruebas unitarias (por ejemplo, con Vitest o Jest) para los servicios y utilidades.
- Incorporar Dark Mode leyendo las preferencias del usuario desde `localStorage`.

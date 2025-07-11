#!/usr/bin/env python3
"""
RAG Chunking Playground - Tkinter GUI

@docs: Herramienta de desarrollo para probar y ajustar parámetros de chunking
       del sistema RAG. Permite visualizar chunks en tiempo real y consultar
       la base de datos vectorial. Documentado en docs/README_IA.md

Funcionalidades:
- Panel izquierdo: Configuración de chunking y visualización de resultados
- Panel derecho: Consulta en tiempo real de la base de datos RAG
- Exportación a CSV de resultados
- Manejo robusto de errores sin cierre de aplicación

Autor: Sistema RAG v2.5.0
Fecha: 2025-07-08
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import sqlite3
import csv
import json
import struct
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import threading
import traceback
# Añadir el directorio padre al path para importar módulos del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from rag_engine.chunker import TextChunker, Chunk
    from rag_engine.config import DB_PATH, DB_TABLE_NAME, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDER_TYPE
    from rag_engine.embedder import EmbedderFactory
    from rag_engine.database import SQLiteVecDatabase
    from rag_engine.logger import logger, set_debug_mode
    from rag_engine.agentic_chunking import chunk_text_with_gemini, chunk_text_with_local_llm
except ImportError as e:
    print(f"Error importing RAG modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


class ChunkingPlayground:
    """
    Interfaz gráfica para experimentar con parámetros de chunking y 
    visualizar la base de datos RAG en tiempo real.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("RAG Chunking Playground v2.6.1 - Con Búsquedas Vectoriales")
        self.root.geometry("1600x900")
        
        # Variables de estado
        self.current_text = ""
        self.current_chunks = []
        self.chunker = None
        
        # Configurar el layout principal
        self.setup_ui()
        
        # Inicializar con valores por defecto
        self.chunk_size_var.set(CHUNK_SIZE)
        self.chunk_overlap_var.set(CHUNK_OVERLAP)
        self.strategy_var.set("caracteres")
        
        # Actualizar la vista de la base de datos al inicio
        self.refresh_database_view()
        
        print("RAG Chunking Playground iniciado correctamente")
    
    def setup_ui(self):
        """Configura toda la interfaz de usuario"""
        
        # Frame principal con tres paneles
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel izquierdo (Chunking) - 40% del ancho
        left_frame = ttk.LabelFrame(main_frame, text="🔧 Configuración de Chunking", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 3))
        
        # Panel central (Base de datos) - 30% del ancho
        center_frame = ttk.LabelFrame(main_frame, text="💾 Base de Datos RAG", padding=10)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(3, 3))
        
        # Panel derecho (Búsquedas vectoriales) - 30% del ancho
        right_frame = ttk.LabelFrame(main_frame, text="🔍 Búsquedas Vectoriales", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(3, 0))
        
        self.setup_left_panel(left_frame)
        self.setup_center_panel(center_frame)
        self.setup_right_panel(right_frame)
        self.setup_status_bar()
    
    def setup_left_panel(self, parent):
        """Configura el panel izquierdo con controles de chunking"""
        
        # Sección 1: Carga de archivo
        file_frame = ttk.LabelFrame(parent, text="📁 Archivo de Texto", padding=5)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        file_control_frame = ttk.Frame(file_frame)
        file_control_frame.pack(fill=tk.X)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_control_frame, textvariable=self.file_path_var, state="readonly")
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(file_control_frame, text="Seleccionar", command=self.select_file).pack(side=tk.RIGHT)
        
        # Sección 2: Parámetros de chunking
        params_frame = ttk.LabelFrame(parent, text="⚙️ Parámetros", padding=5)
        params_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Chunk Size
        ttk.Label(params_frame, text="Tamaño del chunk:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.chunk_size_var = tk.IntVar()
        size_frame = ttk.Frame(params_frame)
        size_frame.grid(row=0, column=1, sticky=tk.EW, padx=(10, 0), pady=2)
        ttk.Scale(size_frame, from_=100, to=5000, variable=self.chunk_size_var, 
                 orient=tk.HORIZONTAL, command=self.on_parameter_change).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.size_label = ttk.Label(size_frame, text="1000")
        self.size_label.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Chunk Overlap
        ttk.Label(params_frame, text="Solapamiento:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.chunk_overlap_var = tk.IntVar()
        overlap_frame = ttk.Frame(params_frame)
        overlap_frame.grid(row=1, column=1, sticky=tk.EW, padx=(10, 0), pady=2)
        ttk.Scale(overlap_frame, from_=0, to=1000, variable=self.chunk_overlap_var,
                 orient=tk.HORIZONTAL, command=self.on_parameter_change).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.overlap_label = ttk.Label(overlap_frame, text="200")
        self.overlap_label.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Estrategia de Chunking
        ttk.Label(params_frame, text="Estrategia:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.strategy_var = tk.StringVar()
        strategy_frame = ttk.Frame(params_frame)
        strategy_frame.grid(row=2, column=1, sticky=tk.EW, padx=(10, 0), pady=2)
        
        # Crear radiobuttons para cada estrategia
        strategies = [
            ("Caracteres", "caracteres"),
            ("Palabras", "palabras"),
            ("Semantico", "semantico"),
            ("Agentic", "agentic")
        ]
        
        for i, (text, value) in enumerate(strategies):
            ttk.Radiobutton(strategy_frame, text=text, variable=self.strategy_var, 
                           value=value, command=self.on_parameter_change).grid(row=i//2, column=i%2, sticky=tk.W, padx=(0, 10))
        
        params_frame.columnconfigure(1, weight=1)
        
        # Sección 3: Configuración Agentic (inicialmente oculta)
        self.agentic_frame = ttk.LabelFrame(params_frame, text="🤖 Configuración Agentic", padding=5)
        self.agentic_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(10, 0), padx=5)

        # Proveedor LLM
        provider_frame = ttk.Frame(self.agentic_frame)
        provider_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        ttk.Label(provider_frame, text="Proveedor:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        self.agentic_provider_var = tk.StringVar(value="gemini")
        providers = {"Gemini": "gemini", "Local": "local"}
        for i, (text, value) in enumerate(providers.items()):
            ttk.Radiobutton(provider_frame, text=text, variable=self.agentic_provider_var, 
                            value=value).grid(row=0, column=i + 1, sticky=tk.W, padx=2)

        # --- Sub-frames para configuración de cada proveedor ---
        self.gemini_config_frame = ttk.LabelFrame(self.agentic_frame, text="Configuración Gemini", padding=5)
        self.gemini_config_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(5, 0))

        self.local_config_frame = ttk.LabelFrame(self.agentic_frame, text="Configuración Local", padding=5)
        self.local_config_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(5, 0))

        # Configuración Gemini
        ttk.Label(self.gemini_config_frame, text="Modelo:").grid(row=0, column=0, sticky=tk.W)
        self.gemini_model_var = tk.StringVar(value="gemini-2.5-pro")
        gemini_models = ["gemini-2.5-pro", "gemini-1.5-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite"]
        gemini_combo = ttk.Combobox(self.gemini_config_frame, textvariable=self.gemini_model_var, values=gemini_models, state="readonly")
        gemini_combo.grid(row=0, column=1, sticky=tk.EW, padx=(5, 0))
        self.gemini_config_frame.columnconfigure(1, weight=1)

        # Configuración Local
        ttk.Label(self.local_config_frame, text="URL API:").grid(row=0, column=0, sticky=tk.W)
        self.local_api_url_var = tk.StringVar(value="http://localhost:8000/v1/chat/completions")
        local_url_entry = ttk.Entry(self.local_config_frame, textvariable=self.local_api_url_var)
        local_url_entry.grid(row=0, column=1, sticky=tk.EW, padx=(5, 0))

        ttk.Label(self.local_config_frame, text="Modelo:").grid(row=1, column=0, sticky=tk.W, pady=(5,0))
        self.local_model_name_var = tk.StringVar(value="local-model")
        local_model_entry = ttk.Entry(self.local_config_frame, textvariable=self.local_model_name_var)
        local_model_entry.grid(row=1, column=1, sticky=tk.EW, padx=(5, 0), pady=(5,0))
        self.local_config_frame.columnconfigure(1, weight=1)

        # Botón para procesar con configuración agentic
        self.agentic_process_button = ttk.Button(self.agentic_frame, text="🚀 Procesar con LLM", command=self.run_agentic_chunking)
        self.agentic_process_button.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky='ew')

        # Bind para cambiar la visibilidad de los frames de config
        self.agentic_provider_var.trace_add("write", self.toggle_agentic_provider_config)
        
        self.agentic_frame.columnconfigure(1, weight=1)
        
        # Inicialmente ocultar la configuración agentic y mostrar la correcta
        self.toggle_agentic_provider_config()
        self.agentic_frame.grid_remove() # Usar grid_remove en lugar de pack_forget
        
        # Sección 3.5: Configuración de Debug
        debug_frame = ttk.Frame(parent)
        debug_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.debug_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(debug_frame, text="🔍 Modo Debug (logs detallados)", 
                       variable=self.debug_var, command=self.on_debug_change).pack(side=tk.LEFT)
        
        # Sección 4: Botones de acción
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(action_frame, text="🔄 Procesar", command=self.process_chunks).pack(side=tk.LEFT)
        ttk.Button(action_frame, text="💾 Exportar CSV", command=self.export_csv).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(action_frame, text="🧠 Guardar en BD", command=self.save_to_database).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(action_frame, text="🔄 Actualizar BD", command=self.refresh_database_view).pack(side=tk.RIGHT)
        
        # Sección 5: Resultados de chunking
        results_frame = ttk.LabelFrame(parent, text="📊 Chunks Generados", padding=5)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear Treeview para mostrar chunks
        columns = ("ID", "Título", "Resumen", "Contenido (preview)", "Chars")
        self.chunks_tree = ttk.Treeview(results_frame, columns=columns, show="headings")
        
        # Configurar columnas
        self.chunks_tree.heading("ID", text="ID")
        self.chunks_tree.heading("Título", text="Título")
        self.chunks_tree.heading("Resumen", text="Resumen")
        self.chunks_tree.heading("Contenido (preview)", text="Contenido (preview)")
        self.chunks_tree.heading("Chars", text="Chars")

        self.chunks_tree.column("ID", width=30, anchor=tk.CENTER)
        self.chunks_tree.column("Título", width=120)
        self.chunks_tree.column("Resumen", width=180)
        self.chunks_tree.column("Contenido (preview)", width=200)
        self.chunks_tree.column("Chars", width=100, anchor=tk.CENTER)
        
        # Scrollbars para el Treeview
        chunks_scrollbar_v = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.chunks_tree.yview)
        chunks_scrollbar_h = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.chunks_tree.xview)
        self.chunks_tree.configure(yscrollcommand=chunks_scrollbar_v.set, xscrollcommand=chunks_scrollbar_h.set)
        
        # Pack del Treeview y scrollbars
        self.chunks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chunks_scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        chunks_scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind para mostrar chunk completo al hacer doble clic
        self.chunks_tree.bind("<Double-1>", self.show_full_chunk)
    
    def setup_center_panel(self, parent):
        """Configura el panel central con información de la base de datos"""
        
        # Estadísticas de la base de datos
        stats_frame = ttk.LabelFrame(parent, text="📊 Estadísticas", padding=5)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=6, state=tk.DISABLED, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Ejemplo de chunk con embedding
        example_frame = ttk.LabelFrame(parent, text="📝 Ejemplo de Datos", padding=5)
        example_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.example_text = scrolledtext.ScrolledText(example_frame, height=4, state=tk.DISABLED, wrap=tk.WORD)
        self.example_text.pack(fill=tk.BOTH, expand=True)
        
        # Tabla de chunks en la base de datos
        table_frame = ttk.LabelFrame(parent, text="🗂️ Chunks en Base de Datos", padding=5)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear Treeview para mostrar chunks de la BD
        columns = ("ID", "Contenido (Preview)", "Embedding")
        self.db_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        
        # Configurar columnas
        self.db_tree.heading("ID", text="ID")
        self.db_tree.heading("Contenido (Preview)", text="Contenido (Preview)")
        self.db_tree.heading("Embedding", text="Embedding")
        
        self.db_tree.column("ID", width=40, minwidth=30)
        self.db_tree.column("Contenido (Preview)", width=150, minwidth=100)
        self.db_tree.column("Embedding", width=80, minwidth=60)
        
        # Scrollbar para la tabla
        db_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.db_tree.yview)
        self.db_tree.configure(yscrollcommand=db_scrollbar.set)
        
        self.db_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        db_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón para actualizar la vista de la base de datos
        ttk.Button(parent, text="🔄 Actualizar BD", command=self.refresh_database_view).pack(pady=(10, 0))
    
    def setup_right_panel(self, parent):
        """Configura el panel derecho con funcionalidades de búsqueda vectorial"""
        # @docs: Panel de búsquedas vectoriales para testing del sistema RAG
        # Documentado en docs/README_IA.md sección RAG
        
        # Sección 1: Consulta de búsqueda
        query_frame = ttk.LabelFrame(parent, text="🔍 Consulta de Búsqueda", padding=5)
        query_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Campo de texto para la consulta
        ttk.Label(query_frame, text="Texto de consulta:").pack(anchor=tk.W)
        self.query_text = scrolledtext.ScrolledText(query_frame, height=3, wrap=tk.WORD)
        self.query_text.pack(fill=tk.X, pady=(5, 10))
        
        # Controles de búsqueda
        search_controls = ttk.Frame(query_frame)
        search_controls.pack(fill=tk.X)
        
        ttk.Label(search_controls, text="Top K:").pack(side=tk.LEFT)
        self.top_k_var = tk.IntVar(value=5)
        top_k_spinbox = ttk.Spinbox(search_controls, from_=1, to=20, width=5, textvariable=self.top_k_var)
        top_k_spinbox.pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Button(search_controls, text="🔍 Buscar", command=self.perform_search).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(search_controls, text="🧹 Limpiar", command=self.clear_search).pack(side=tk.LEFT, padx=(5, 0))
        
        # Sección 2: Resultados de búsqueda
        results_frame = ttk.LabelFrame(parent, text="📋 Resultados de Búsqueda", padding=5)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Tabla de resultados
        result_columns = ("Rank", "Similitud", "Contenido")
        self.results_tree = ttk.Treeview(results_frame, columns=result_columns, show="headings", height=8)
        
        # Configurar columnas de resultados
        self.results_tree.heading("Rank", text="#")
        self.results_tree.heading("Similitud", text="Similitud")
        self.results_tree.heading("Contenido", text="Contenido")
        
        self.results_tree.column("Rank", width=30, minwidth=25)
        self.results_tree.column("Similitud", width=70, minwidth=60)
        self.results_tree.column("Contenido", width=200, minwidth=150)
        
        # Scrollbar para resultados
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind doble clic para ver contenido completo
        self.results_tree.bind("<Double-1>", self.show_full_result)
        
        # Sección 3: Información de búsqueda
        info_frame = ttk.LabelFrame(parent, text="ℹ️ Información de Búsqueda", padding=5)
        info_frame.pack(fill=tk.X)
        
        self.search_info_text = scrolledtext.ScrolledText(info_frame, height=4, state=tk.DISABLED, wrap=tk.WORD)
        self.search_info_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_status_bar(self):
        """Configura la barra de estado en la parte inferior"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))
        
        self.status_var = tk.StringVar()
        self.status_var.set("✅ Listo - Selecciona un archivo .txt para comenzar")
        
        status_label = ttk.Label(self.status_frame, textvariable=self.status_var, 
                                relief=tk.SUNKEN, anchor=tk.W)
        status_label.pack(fill=tk.X)
    
    def set_status(self, message: str, is_error: bool = False):
        """Actualiza la barra de estado"""
        prefix = "❌ Error: " if is_error else "✅ "
        self.status_var.set(prefix + message)
        print(f"Status: {message}")
    
    def select_file(self):
        """Abre el diálogo para seleccionar un archivo de texto"""
        try:
            file_path = filedialog.askopenfilename(
                title="Seleccionar archivo de texto",
                filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
            )
            
            if file_path:
                self.file_path_var.set(file_path)
                self.load_file(file_path)
                
        except Exception as e:
            self.set_status(f"Error al seleccionar archivo: {str(e)}", True)
            print(f"Error in select_file: {traceback.format_exc()}")
    
    def load_file(self, file_path: str):
        """Carga el contenido del archivo seleccionado"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.current_text = f.read()
            
            self.set_status(f"Archivo cargado: {len(self.current_text)} caracteres")
            
            # Auto-procesar si hay texto
            if self.current_text.strip():
                self.process_chunks()
                
        except Exception as e:
            self.set_status(f"Error al cargar archivo: {str(e)}", True)
            print(f"Error in load_file: {traceback.format_exc()}")
    
    def on_parameter_change(self, *args):
        """Callback cuando cambian los parámetros de chunking"""
        try:
            # Actualizar las etiquetas de los valores
            self.size_label.config(text=str(self.chunk_size_var.get()))
            self.overlap_label.config(text=str(self.chunk_overlap_var.get()))
            
            # Mostrar/ocultar configuración agentic según la estrategia
            self.toggle_agentic_config()
            
            # Auto-procesar si hay texto cargado y la estrategia no es agentic
            if self.current_text.strip():
                if self.strategy_var.get() == 'agentic':
                    self.set_status("Configuración agentic actualizada. Pulsa 'Procesar con LLM' para ejecutar.")
                else:
                    self.process_chunks()
                
        except Exception as e:
            logger.error(f"Error in on_parameter_change: {traceback.format_exc()}")

    def toggle_agentic_config(self):
        """Muestra u oculta la configuración agentic según la estrategia seleccionada"""
        if self.strategy_var.get() == "agentic":
            self.agentic_frame.grid(row=4, column=0, columnspan=2, sticky='ew', pady=(10, 0), padx=5)
            self.set_status("Modo Agentic activado. Configure el proveedor y procese.")
        else:
            self.agentic_frame.grid_remove()

    def toggle_agentic_provider_config(self, *args):
        """Muestra u oculta la configuración específica del proveedor LLM."""
        provider = self.agentic_provider_var.get()
        if provider == "gemini":
            self.gemini_config_frame.grid()
            self.local_config_frame.grid_remove()
        elif provider == "local":
            self.local_config_frame.grid()
            self.gemini_config_frame.grid_remove()
        else:
            self.gemini_config_frame.grid_remove()
            self.local_config_frame.grid_remove()
    
    def on_debug_change(self):
        """Callback cuando cambia el modo debug"""
        is_debug = self.debug_var.get()
        set_debug_mode(is_debug)
        logger.info(f"Modo debug {'activado' if is_debug else 'desactivado'}")
        self.set_status(f"Modo debug {'activado' if is_debug else 'desactivado'}")
    
    def process_chunks(self):
        """Procesa el texto actual con los parámetros de chunking configurados"""
        try:
            if not self.current_text.strip():
                self.set_status("No hay texto para procesar", True)
                return
            
            # Validar parámetros
            chunk_size = self.chunk_size_var.get()
            chunk_overlap = self.chunk_overlap_var.get()
            strategy = self.strategy_var.get()
            
            if chunk_overlap >= chunk_size:
                self.set_status("El solapamiento debe ser menor que el tamaño del chunk", True)
                return
            
            # Crear chunker con la estrategia seleccionada (no agéntica)
            self.chunker = TextChunker(strategy=strategy)
            
            # Procesar chunks
            self.current_chunks = self.chunker.chunk(self.current_text, chunk_size, chunk_overlap)
            
            # Actualizar la vista
            self.update_chunks_view()
            
            # Mostrar estadísticas con información de la estrategia
            total_chars = sum(len(chunk.content) for chunk in self.current_chunks)
            avg_length = total_chars / len(self.current_chunks) if self.current_chunks else 0
            
            strategy_names = {
                'caracteres': 'Caracteres',
                'palabras': 'Palabras', 
                'semantico': 'Semántico',
                'agentic': 'Agéntico (LLM)'
            }
            
            strategy_display = strategy_names.get(strategy, strategy)
            
            self.set_status(f"Procesado con {strategy_display}: {len(self.current_chunks)} chunks, "
                          f"promedio {avg_length:.1f} caracteres")
            
        except Exception as e:
            self.set_status(f"Error al procesar chunks: {str(e)}", True)
            print(f"Error in process_chunks: {traceback.format_exc()}")
    
    def run_agentic_chunking(self):
        """Ejecuta el chunking específicamente con la estrategia agéntica, sin fallback."""
        provider = self.agentic_provider_var.get()
        try:
            if not self.current_text.strip():
                self.set_status("No hay texto para procesar", True)
                return

            chunk_size = self.chunk_size_var.get()
            chunk_overlap = self.chunk_overlap_var.get()

            if chunk_overlap >= chunk_size:
                self.set_status("El solapamiento debe ser menor que el tamaño del chunk", True)
                return

            self.set_status(f"[INFO] Iniciando chunking agéntico con {provider.capitalize()}...")
            self.root.update_idletasks()  # Forzar actualización de la GUI

            if provider == "gemini":
                model_name = self.gemini_model_var.get()
                self.current_chunks = chunk_text_with_gemini(
                    text=self.current_text,
                    model_name=model_name,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
            elif provider == "local":
                api_url = self.local_api_url_var.get()
                model_name = self.local_model_name_var.get()
                self.current_chunks = chunk_text_with_local_llm(
                    text=self.current_text, 
                    api_url=api_url, 
                    model_name=model_name,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
            else:
                self.current_chunks = []

            self.update_chunks_view()

            # Mostrar estadísticas
            total_chars = sum(len(chunk.content) for chunk in self.current_chunks)
            avg_length = total_chars / len(self.current_chunks) if self.current_chunks else 0
            self.set_status(f"[OK] Agéntico ({provider.capitalize()}): {len(self.current_chunks)} chunks, "
                          f"promedio {avg_length:.1f} caracteres")

        except Exception as e:
            self.set_status(f"Error en chunking agéntico ({provider}): {str(e)}", True)
            logger.error(f"Error in run_agentic_chunking with {provider}: {traceback.format_exc()}")

    def update_chunks_view(self):
        """Actualiza la vista de chunks en el Treeview"""
        self.chunks_tree.delete(*self.chunks_tree.get_children())
        
        for i, chunk in enumerate(self.current_chunks):
            title = getattr(chunk.metadata, 'semantic_title', 'N/A')
            summary = getattr(chunk.metadata, 'summary', 'N/A')
            content_preview = chunk.content.replace('\n', ' ').strip()[:100] + '...'
            char_range = f"{chunk.metadata.char_start_index}-{chunk.metadata.char_end_index}"
            chars_info = f"{len(chunk.content)} ({char_range})"
            self.chunks_tree.insert("", tk.END, values=(i, title, summary, content_preview, chars_info), iid=str(i))
        
        self.set_status(f"Chunks generados: {len(self.current_chunks)}")
    
    def show_full_chunk(self, event):
        """Muestra los detalles completos del chunk en una ventana emergente."""
        selected = self.chunks_tree.selection()
        if not selected:
            return
        index = int(selected[0])
        chunk = self.current_chunks[index]

        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Detalles del Chunk #{index}")
        detail_window.geometry("600x450")

        info_frame = ttk.LabelFrame(detail_window, text="Metadatos", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(info_frame, text=f"Título: {getattr(chunk.metadata, 'semantic_title', 'N/A')}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Resumen: {getattr(chunk.metadata, 'summary', 'N/A')}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Caracteres: {len(chunk.content)}").pack(anchor=tk.W)
        ttk.Label(info_frame, text=f"Posición: {chunk.metadata.char_start_index}-{chunk.metadata.char_end_index}").pack(anchor=tk.W)

        content_frame = ttk.LabelFrame(detail_window, text="Contenido", padding=10)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD)
        content_text.pack(fill=tk.BOTH, expand=True)
        content_text.insert(tk.END, chunk.content)
        content_text.config(state=tk.DISABLED)

        close_button = ttk.Button(detail_window, text="Cerrar", command=detail_window.destroy)
        close_button.pack(pady=10)
    
    def export_csv(self):
        """Exporta los chunks actuales a un archivo CSV"""
        try:
            if not self.current_chunks:
                self.set_status("No hay chunks para exportar", True)
                return
            
            file_path = filedialog.asksaveasfilename(
                title="Guardar chunks como CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Escribir encabezados
                writer.writerow(["Chunk Index", "Chunk Content", "Length", "Parameters"])
                
                # Escribir datos
                for i, chunk in enumerate(self.current_chunks):
                    # Incluir parámetros usados
                    params = f"size={self.chunk_size_var.get()}, overlap={self.chunk_overlap_var.get()}, mode={self.mode_var.get()}"
                    writer.writerow([i + 1, chunk, len(chunk), params])
                
                self.set_status(f"Exportado a {file_path}: {len(self.current_chunks)} chunks")
                
        except Exception as e:
            self.set_status(f"Error al exportar CSV: {str(e)}", True)
            print(f"Error in export_csv: {traceback.format_exc()}")
            
    def save_to_database(self):
        """Genera embeddings para los chunks actuales y los guarda en la base de datos"""
        try:
            if not self.current_chunks:
                self.set_status("No hay chunks para guardar en la base de datos", True)
                return
            
            # Confirmar la operación
            if not messagebox.askyesno("Confirmar", 
                                      f"¿Deseas generar embeddings y guardar {len(self.current_chunks)} chunks en la base de datos?\n\n" +
                                      f"NOTA: Esta operación puede tardar varios minutos y utilizará recursos de GPU si está disponible."):
                return
            
            # Iniciar proceso en un hilo separado para no bloquear la UI
            threading.Thread(target=self._process_and_save_embeddings, daemon=True).start()
            
        except Exception as e:
            self.set_status(f"Error al iniciar guardado en BD: {str(e)}", True)
            print(f"Error in save_to_database: {traceback.format_exc()}")
    
    def _process_and_save_embeddings(self):
        """Proceso en segundo plano para generar embeddings y guardar en BD"""
        try:
            # Actualizar estado
            self.root.after(0, lambda: self.set_status(f"Iniciando generación de embeddings para {len(self.current_chunks)} chunks..."))
            
            # Crear embedder según configuración
            embedder = EmbedderFactory.create_embedder(EMBEDDER_TYPE)
            
            # Generar embeddings (esto puede usar GPU si está disponible)
            self.root.after(0, lambda: self.set_status(f"Generando embeddings con {EMBEDDER_TYPE}..."))
            
            # Extraer el contenido de texto para el embedder
            chunk_contents = [c.content for c in self.current_chunks]
            embeddings = embedder.embed(chunk_contents)
            
            # Preparar datos para la base de datos (texto y embedding)
            documents = list(zip(chunk_contents, embeddings))
            
            # Guardar en la base de datos
            self.root.after(0, lambda: self.set_status(f"Guardando {len(documents)} chunks en la base de datos..."))
            db = SQLiteVecDatabase(DB_PATH, DB_TABLE_NAME)
            db.add_documents(documents)
            
            # Actualizar vista de la base de datos
            self.root.after(0, lambda: self.refresh_database_view())
            
            # Mostrar mensaje de éxito
            self.root.after(0, lambda: self.set_status(f"✅ Guardados {len(documents)} chunks en la base de datos con éxito"))
            self.root.after(0, lambda: messagebox.showinfo("Operación completada", 
                                                         f"Se han guardado {len(documents)} chunks en la base de datos con éxito."))
            
        except Exception as e:
            self.root.after(0, lambda: self.set_status(f"Error al guardar en BD: {str(e)}", True))
            print(f"Error in _process_and_save_embeddings: {traceback.format_exc()}")            
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error al guardar en la base de datos:\n{str(e)}"))
    
    def refresh_database_view(self):
        """Actualiza la vista de la base de datos RAG en un hilo separado"""
        def update_db():
            try:
                self.set_status("Actualizando vista de base de datos...")
                
                # Verificar si existe la base de datos
                if not os.path.exists(DB_PATH):
                    self.update_db_stats("❌ Base de datos no encontrada: " + DB_PATH)
                    return
                
                # Conectar a la base de datos
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                # Verificar si existe la tabla
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (DB_TABLE_NAME,))
                if not cursor.fetchone():
                    self.update_db_stats(f"❌ Tabla '{DB_TABLE_NAME}' no encontrada en la base de datos")
                    conn.close()
                    return
                
                # Obtener estadísticas
                cursor.execute(f"SELECT COUNT(*) FROM {DB_TABLE_NAME}")
                total_rows = cursor.fetchone()[0]
                
                if total_rows == 0:
                    self.update_db_stats("📊 Base de datos vacía - No hay chunks almacenados")
                    self.update_db_example("")
                    self.update_db_table([])
                    conn.close()
                    return
                
                # Obtener longitudes de contenido
                cursor.execute(f"SELECT LENGTH(content) FROM {DB_TABLE_NAME}")
                lengths = [row[0] for row in cursor.fetchall()]
                
                avg_length = sum(lengths) / len(lengths)
                max_length = max(lengths)
                min_length = min(lengths)
                
                # Obtener ejemplo de chunk y embedding
                cursor.execute(f"SELECT id, content, embedding FROM {DB_TABLE_NAME} LIMIT 1")
                example_row = cursor.fetchone()
                
                example_text = ""
                if example_row:
                    chunk_id, content, embedding_blob = example_row
                    
                    # Decodificar embedding
                    embedding_info = "No disponible"
                    if embedding_blob:
                        try:
                            # Intentar decodificar como array de floats
                            embedding_size = len(embedding_blob) // 4  # 4 bytes por float
                            embedding = struct.unpack(f'{embedding_size}f', embedding_blob)
                            embedding_info = f"Dimensiones: {len(embedding)}, Primeros 5 valores: {embedding[:5]}"
                        except:
                            embedding_info = f"Tamaño en bytes: {len(embedding_blob)}"
                    
                    example_text = f"ID: {chunk_id}\n\nContenido (primeros 200 chars):\n{content[:200]}...\n\nEmbedding:\n{embedding_info}"
                
                # Obtener datos para la tabla
                cursor.execute(f"SELECT id, content, embedding FROM {DB_TABLE_NAME} LIMIT 20")
                table_data = []
                for row in cursor.fetchall():
                    chunk_id, content, embedding_blob = row
                    content_preview = content[:50].replace('\n', ' ') + "..." if len(content) > 50 else content
                    
                    # Información del embedding
                    if embedding_blob:
                        embedding_size = len(embedding_blob)
                        try:
                            # Intentar decodificar para obtener dimensiones
                            dimensions = len(embedding_blob) // 4  # 4 bytes por float
                            embedding_info = f"{dimensions}D ({embedding_size}b)"
                        except:
                            embedding_info = f"{embedding_size} bytes"
                    else:
                        embedding_info = "Sin embedding"
                    
                    table_data.append((chunk_id, content_preview, embedding_info))
                
                conn.close()
                
                # Actualizar UI en el hilo principal
                stats_text = f"""📊 Estadísticas de la Base de Datos RAG

🗃️ Total de chunks: {total_rows}
📏 Longitud promedio: {avg_length:.1f} caracteres
📏 Longitud máxima: {max_length} caracteres  
📏 Longitud mínima: {min_length} caracteres
💾 Base de datos: {DB_PATH}
📋 Tabla: {DB_TABLE_NAME}

✅ Última actualización: {self.get_current_time()}"""
                
                self.root.after(0, lambda: self.update_db_stats(stats_text))
                self.root.after(0, lambda: self.update_db_example(example_text))
                self.root.after(0, lambda: self.update_db_table(table_data))
                self.root.after(0, lambda: self.set_status("Vista de base de datos actualizada"))
                
            except Exception as e:
                error_msg = f"Error al consultar base de datos: {str(e)}"
                self.root.after(0, lambda: self.set_status(error_msg, True))
                print(f"Error in refresh_database_view: {traceback.format_exc()}")
        
        # Ejecutar en hilo separado para no bloquear la UI
        threading.Thread(target=update_db, daemon=True).start()
    
    def update_db_stats(self, text: str):
        """Actualiza el texto de estadísticas de la base de datos"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, text)
        self.stats_text.config(state=tk.DISABLED)
    
    def update_db_example(self, text: str):
        """Actualiza el texto de ejemplo de la base de datos"""
        self.example_text.config(state=tk.NORMAL)
        self.example_text.delete(1.0, tk.END)
        self.example_text.insert(tk.END, text)
        self.example_text.config(state=tk.DISABLED)
    
    def update_db_table(self, data: List[Tuple]):
        """Actualiza la tabla de chunks de la base de datos"""
        # Limpiar tabla actual
        for item in self.db_tree.get_children():
            self.db_tree.delete(item)
        
        # Añadir datos
        for row in data:
            self.db_tree.insert("", tk.END, values=row)
    
    def perform_search(self):
        """Realiza una búsqueda vectorial en la base de datos RAG"""
        # @docs: Función de búsqueda semántica usando embeddings
        query = self.query_text.get(1.0, tk.END).strip()
        
        if not query:
            self.set_status("Por favor, ingresa una consulta de búsqueda", True)
            return
        
        try:
            self.set_status("Realizando búsqueda vectorial...")
            
            # Generar embedding para la consulta
            embedder = EmbedderFactory.create_embedder(EMBEDDER_TYPE)
            query_embeddings = embedder.embed([query])
            query_embedding = query_embeddings[0]
            
            # Realizar búsqueda en la base de datos
            db = SQLiteVecDatabase()
            top_k = self.top_k_var.get()
            results = db.search_similar(query_embedding, top_k)
            
            # Actualizar la tabla de resultados
            self.update_search_results(results, query)
            
            # Actualizar información de búsqueda
            info_text = f"""🔍 Información de Búsqueda

📝 Consulta: "{query}"
🔢 Top K: {top_k}
📊 Resultados encontrados: {len(results)}
🧠 Tipo de embedder: {EMBEDDER_TYPE}
⏰ Búsqueda realizada: {self.get_current_time()}

💡 Tip: Haz doble clic en un resultado para ver el contenido completo."""
            
            self.update_search_info(info_text)
            self.set_status(f"Búsqueda completada: {len(results)} resultados encontrados")
            
        except Exception as e:
            error_msg = f"Error en la búsqueda: {str(e)}"
            self.set_status(error_msg, True)
            print(f"Error in perform_search: {traceback.format_exc()}")
    
    def clear_search(self):
        """Limpia los campos y resultados de búsqueda"""
        self.query_text.delete(1.0, tk.END)
        
        # Limpiar tabla de resultados
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Limpiar información de búsqueda
        self.search_info_text.config(state=tk.NORMAL)
        self.search_info_text.delete(1.0, tk.END)
        self.search_info_text.insert(tk.END, "ℹ️ Información de búsqueda aparecerá aquí después de realizar una consulta.")
        self.search_info_text.config(state=tk.DISABLED)
        
        self.set_status("Búsqueda limpiada")
    
    def update_search_results(self, results: List[Tuple[str, float]], query: str):
        """Actualiza la tabla de resultados de búsqueda"""
        # Limpiar resultados anteriores
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Añadir nuevos resultados
        for i, (content, similarity) in enumerate(results, 1):
            # Truncar contenido para la vista previa
            content_preview = content[:100] + "..." if len(content) > 100 else content
            content_preview = content_preview.replace('\n', ' ').replace('\r', ' ')
            
            # Formatear similitud como porcentaje
            similarity_percent = f"{similarity:.1%}"
            
            self.results_tree.insert("", tk.END, values=(i, similarity_percent, content_preview))
    
    def show_full_result(self, event):
        """Muestra el resultado completo en una ventana emergente"""
        selection = self.results_tree.selection()
        if not selection:
            return
        
        item = self.results_tree.item(selection[0])
        rank = item['values'][0]
        similarity = item['values'][1]
        
        # Obtener el contenido completo desde la base de datos
        try:
            # Realizar la búsqueda nuevamente para obtener el contenido completo
            query = self.query_text.get(1.0, tk.END).strip()
            if query:
                embedder = EmbedderFactory.create_embedder(EMBEDDER_TYPE)
                query_embeddings = embedder.embed([query])
                query_embedding = query_embeddings[0]
                
                db = SQLiteVecDatabase()
                results = db.search_similar(query_embedding, self.top_k_var.get())
                
                if rank <= len(results):
                    full_content = results[rank-1][0]
                    
                    # Crear ventana emergente
                    popup = tk.Toplevel(self.root)
                    popup.title(f"Resultado #{rank} - Similitud: {similarity}")
                    popup.geometry("600x400")
                    
                    # Texto con scroll
                    text_widget = scrolledtext.ScrolledText(popup, wrap=tk.WORD, padx=10, pady=10)
                    text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                    text_widget.insert(tk.END, full_content)
                    text_widget.config(state=tk.DISABLED)
                    
                    # Botón cerrar
                    ttk.Button(popup, text="Cerrar", command=popup.destroy).pack(pady=(0, 10))
                    
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mostrar el resultado completo: {str(e)}")
    
    def update_search_info(self, text: str):
        """Actualiza el texto de información de búsqueda"""
        self.search_info_text.config(state=tk.NORMAL)
        self.search_info_text.delete(1.0, tk.END)
        self.search_info_text.insert(tk.END, text)
        self.search_info_text.config(state=tk.DISABLED)
    
    def get_current_time(self) -> str:
        """Obtiene la hora actual formateada"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")


def main():
    """Función principal para ejecutar la aplicación"""
    try:
        # Verificar que los módulos RAG estén disponibles
        print("Iniciando RAG Chunking Playground...")
        print(f"Base de datos RAG: {DB_PATH}")
        print(f"Tabla: {DB_TABLE_NAME}")
        
        # Crear y ejecutar la aplicación
        root = tk.Tk()
        app = ChunkingPlayground(root)
        
        # Configurar el cierre de la aplicación
        def on_closing():
            print("Cerrando RAG Chunking Playground...")
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Iniciar el bucle principal
        root.mainloop()
        
    except Exception as e:
        print(f"Error fatal al iniciar la aplicación: {e}")
        print(traceback.format_exc())
        messagebox.showerror("Error Fatal", f"No se pudo iniciar la aplicación:\n{str(e)}")


if __name__ == "__main__":
    main()

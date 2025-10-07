
#!/usr/bin/env python3
"""
GUI de Testing para Chunking Agéntico
Herramienta especializada para depurar y probar el chunking agéntico sin fallbacks.

Funcionalidades:
- Prueba individual de cada modelo (Gemini, Local)
- Logs de debug en tiempo real
- Comparación lado a lado de resultados
- Sin fallback automático - muestra errores reales
- Configuración detallada de parámetros

Autor: Sistema RAG v2.6.1
Fecha: 2025-07-09
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import sys
import threading
import traceback
import logging
from typing import List, Dict, Any, Optional
import json

# Añadir el directorio padre al path para importar módulos del proyecto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from rag_engine.agentic_chunking import (
        chunk_text_with_gemini, 
        chunk_text_with_local_llm,
        debug_log
    )
    from rag_engine.chunker import Chunk
    from rag_engine.logger import logger, set_debug_mode
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


class LogHandler(logging.Handler):
    """Handler personalizado para capturar logs y mostrarlos en la GUI"""
    
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        
    def emit(self, record):
        try:
            msg = self.format(record)
            # Ejecutar en el hilo principal de la GUI
            self.text_widget.after(0, self._append_log, msg)
        except Exception:
            pass
    
    def _append_log(self, message):
        """Añade el mensaje al widget de texto"""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, message + "\n")
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)


class AgenticTestingGUI:
    """GUI especializada para testing de chunking agéntico"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Agentic Chunking Testing Tool v1.0")
        self.root.geometry("1400x900")
        
        # Variables de estado
        self.current_text = ""
        self.gemini_chunks = []
        self.local_chunks = []
        
        # Configurar logging
        set_debug_mode(True)
        
        # Configurar la interfaz
        self.setup_ui()
        
        # Configurar captura de logs
        self.setup_logging()
        
        print("Agentic Testing GUI iniciado correctamente")
    
    def setup_ui(self):
        """Configura toda la interfaz de usuario"""
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Panel superior: Configuración y controles
        top_frame = ttk.LabelFrame(main_frame, text="🔧 Configuración de Testing", padding=10)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.setup_config_panel(top_frame)
        
        # Panel medio: Logs de debug
        middle_frame = ttk.LabelFrame(main_frame, text="📋 Logs de Debug", padding=10)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.setup_logs_panel(middle_frame)
        
        # Panel inferior: Resultados comparativos
        bottom_frame = ttk.LabelFrame(main_frame, text="📊 Resultados Comparativos", padding=10)
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_results_panel(bottom_frame)
    
    def setup_config_panel(self, parent):
        """Configura el panel de configuración"""
        
        # Fila 1: Carga de archivo
        file_frame = ttk.Frame(parent)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_frame, text="Archivo:").pack(side=tk.LEFT)
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, state="readonly")
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        ttk.Button(file_frame, text="Seleccionar", command=self.select_file).pack(side=tk.RIGHT)
        
        # Fila 2: Parámetros de chunking
        params_frame = ttk.Frame(parent)
        params_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Tamaño de chunk
        ttk.Label(params_frame, text="Tamaño:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.chunk_size_var = tk.IntVar(value=1000)
        chunk_size_scale = ttk.Scale(params_frame, from_=200, to=2000, variable=self.chunk_size_var, orient=tk.HORIZONTAL)
        chunk_size_scale.grid(row=0, column=1, sticky=tk.EW, padx=(0, 5))
        self.chunk_size_label = ttk.Label(params_frame, text="1000")
        self.chunk_size_label.grid(row=0, column=2, padx=(5, 20))
        
        # Solapamiento
        ttk.Label(params_frame, text="Overlap:").grid(row=0, column=3, sticky=tk.W, padx=(0, 5))
        self.chunk_overlap_var = tk.IntVar(value=200)
        chunk_overlap_scale = ttk.Scale(params_frame, from_=0, to=500, variable=self.chunk_overlap_var, orient=tk.HORIZONTAL)
        chunk_overlap_scale.grid(row=0, column=4, sticky=tk.EW, padx=(0, 5))
        self.overlap_label = ttk.Label(params_frame, text="200")
        self.overlap_label.grid(row=0, column=5, padx=(5, 0))
        
        params_frame.columnconfigure(1, weight=1)
        params_frame.columnconfigure(4, weight=1)
        
        # Callbacks para actualizar labels
        self.chunk_size_var.trace('w', self.update_param_labels)
        self.chunk_overlap_var.trace('w', self.update_param_labels)
        
        # Fila 3: Configuración de modelos
        models_frame = ttk.Frame(parent)
        models_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Gemini
        gemini_frame = ttk.LabelFrame(models_frame, text="Google Gemini", padding=5)
        gemini_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        ttk.Label(gemini_frame, text="Modelo:").grid(row=0, column=0, sticky=tk.W)
        self.gemini_model_var = tk.StringVar(value="gemini-2.5-pro")
        gemini_combo = ttk.Combobox(gemini_frame, textvariable=self.gemini_model_var, 
                                   values=["gemini-2.5-pro", "gemini-2.0-flash-exp", "gemini-2.5-flash", "gemini-2.5-flash-lite"])
        gemini_combo.grid(row=0, column=1, sticky=tk.EW, padx=(5, 0))
        gemini_frame.columnconfigure(1, weight=1)
        
        # Local LLM
        local_frame = ttk.LabelFrame(models_frame, text="LLM Local", padding=5)
        local_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        ttk.Label(local_frame, text="URL:").grid(row=0, column=0, sticky=tk.W)
        self.local_url_var = tk.StringVar(value="http://localhost:8000/v1/chat/completions")
        local_url_entry = ttk.Entry(local_frame, textvariable=self.local_url_var)
        local_url_entry.grid(row=0, column=1, sticky=tk.EW, padx=(5, 0))
        
        ttk.Label(local_frame, text="Modelo:").grid(row=1, column=0, sticky=tk.W)
        self.local_model_var = tk.StringVar(value="local-model")
        local_model_entry = ttk.Entry(local_frame, textvariable=self.local_model_var)
        local_model_entry.grid(row=1, column=1, sticky=tk.EW, padx=(5, 0))
        
        local_frame.columnconfigure(1, weight=1)
        
        # Fila 4: Botones de acción
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="🚀 Test Gemini", command=self.test_gemini).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="🖥️ Test Local", command=self.test_local).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="⚡ Test Ambos", command=self.test_both).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Button(buttons_frame, text="🧹 Limpiar Logs", command=self.clear_logs).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(buttons_frame, text="💾 Exportar", command=self.export_results).pack(side=tk.RIGHT)
    
    def setup_logs_panel(self, parent):
        """Configura el panel de logs"""
        
        self.logs_text = scrolledtext.ScrolledText(parent, height=15, wrap=tk.WORD, 
                                                  font=("Consolas", 9), state=tk.DISABLED)
        self.logs_text.pack(fill=tk.BOTH, expand=True)
    
    def setup_results_panel(self, parent):
        """Configura el panel de resultados comparativos"""
        
        # Frame para las dos columnas de resultados
        results_frame = ttk.Frame(parent)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Columna Gemini
        gemini_frame = ttk.LabelFrame(results_frame, text="Resultados Gemini", padding=5)
        gemini_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.gemini_tree = ttk.Treeview(gemini_frame, columns=("chunk", "title", "chars"), show="headings", height=8)
        self.gemini_tree.heading("chunk", text="#")
        self.gemini_tree.heading("title", text="Título Semántico")
        self.gemini_tree.heading("chars", text="Chars")
        self.gemini_tree.column("chunk", width=40)
        self.gemini_tree.column("title", width=300)
        self.gemini_tree.column("chars", width=80)
        
        gemini_scroll = ttk.Scrollbar(gemini_frame, orient=tk.VERTICAL, command=self.gemini_tree.yview)
        self.gemini_tree.configure(yscrollcommand=gemini_scroll.set)
        
        self.gemini_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        gemini_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Columna Local
        local_frame = ttk.LabelFrame(results_frame, text="Resultados Local", padding=5)
        local_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.local_tree = ttk.Treeview(local_frame, columns=("chunk", "title", "chars"), show="headings", height=8)
        self.local_tree.heading("chunk", text="#")
        self.local_tree.heading("title", text="Título Semántico")
        self.local_tree.heading("chars", text="Chars")
        self.local_tree.column("chunk", width=40)
        self.local_tree.column("title", width=300)
        self.local_tree.column("chars", width=80)
        
        local_scroll = ttk.Scrollbar(local_frame, orient=tk.VERTICAL, command=self.local_tree.yview)
        self.local_tree.configure(yscrollcommand=local_scroll.set)
        
        self.local_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        local_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind para mostrar detalles
        self.gemini_tree.bind("<Double-1>", lambda e: self.show_chunk_details(self.gemini_chunks, self.gemini_tree))
        self.local_tree.bind("<Double-1>", lambda e: self.show_chunk_details(self.local_chunks, self.local_tree))
    
    def setup_logging(self):
        """Configura la captura de logs para mostrarlos en la GUI"""
        
        # Crear handler personalizado
        self.log_handler = LogHandler(self.logs_text)
        self.log_handler.setLevel(logging.DEBUG)
        
        # Formato de logs
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.log_handler.setFormatter(formatter)
        
        # Añadir handler al logger principal
        root_logger = logging.getLogger()
        root_logger.addHandler(self.log_handler)
        root_logger.setLevel(logging.DEBUG)
    
    def update_param_labels(self, *args):
        """Actualiza las etiquetas de los parámetros"""
        self.chunk_size_label.config(text=str(self.chunk_size_var.get()))
        self.overlap_label.config(text=str(self.chunk_overlap_var.get()))
    
    def select_file(self):
        """Selecciona un archivo de texto"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de texto",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.load_file(file_path)
    
    def load_file(self, file_path: str):
        """Carga el contenido del archivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.current_text = f.read()
            
            self.log_message(f"Archivo cargado: {len(self.current_text)} caracteres")
            
        except Exception as e:
            self.log_message(f"Error cargando archivo: {e}", is_error=True)
    
    def log_message(self, message: str, is_error: bool = False):
        """Añade un mensaje a los logs"""
        if is_error:
            logger.error(message)
        else:
            logger.info(message)
    
    def test_gemini(self):
        """Prueba el chunking con Gemini"""
        if not self.current_text.strip():
            messagebox.showwarning("Advertencia", "Primero carga un archivo de texto")
            return
        
        def run_test():
            try:
                self.log_message("=== INICIANDO TEST CON GEMINI ===")
                
                chunks = chunk_text_with_gemini(
                    text=self.current_text,
                    chunk_size=self.chunk_size_var.get(),
                    chunk_overlap=self.chunk_overlap_var.get(),
                    model_name=self.gemini_model_var.get()
                )
                
                self.gemini_chunks = chunks
                self.root.after(0, self.update_gemini_results)
                
            except Exception as e:
                self.log_message(f"ERROR EN TEST GEMINI: {e}", is_error=True)
                self.log_message(f"Traceback: {traceback.format_exc()}", is_error=True)
        
        threading.Thread(target=run_test, daemon=True).start()
    
    def test_local(self):
        """Prueba el chunking con LLM local"""
        if not self.current_text.strip():
            messagebox.showwarning("Advertencia", "Primero carga un archivo de texto")
            return
        
        def run_test():
            try:
                self.log_message("=== INICIANDO TEST CON LLM LOCAL ===")
                
                chunks = chunk_text_with_local_llm(
                    text=self.current_text,
                    chunk_size=self.chunk_size_var.get(),
                    chunk_overlap=self.chunk_overlap_var.get(),
                    api_url=self.local_url_var.get(),
                    model_name=self.local_model_var.get()
                )
                
                self.local_chunks = chunks
                self.root.after(0, self.update_local_results)
                
            except Exception as e:
                self.log_message(f"ERROR EN TEST LOCAL: {e}", is_error=True)
                self.log_message(f"Traceback: {traceback.format_exc()}", is_error=True)
        
        threading.Thread(target=run_test, daemon=True).start()
    
    def test_both(self):
        """Prueba ambos modelos secuencialmente"""
        if not self.current_text.strip():
            messagebox.showwarning("Advertencia", "Primero carga un archivo de texto")
            return
        
        self.log_message("=== INICIANDO TEST COMPARATIVO ===")
        self.test_gemini()
        # Esperar un poco antes de iniciar el segundo test
        self.root.after(2000, self.test_local)
    
    def update_gemini_results(self):
        """Actualiza la tabla de resultados de Gemini"""
        # Limpiar tabla
        for item in self.gemini_tree.get_children():
            self.gemini_tree.delete(item)
        
        # Añadir chunks
        for i, chunk in enumerate(self.gemini_chunks, 1):
            title = getattr(chunk.metadata, 'semantic_title', 'Sin título')
            chars = len(chunk.content)
            self.gemini_tree.insert("", tk.END, values=(i, title, chars))
        
        self.log_message(f"Resultados Gemini actualizados: {len(self.gemini_chunks)} chunks")
    
    def update_local_results(self):
        """Actualiza la tabla de resultados del LLM local"""
        # Limpiar tabla
        for item in self.local_tree.get_children():
            self.local_tree.delete(item)
        
        # Añadir chunks
        for i, chunk in enumerate(self.local_chunks, 1):
            title = getattr(chunk.metadata, 'semantic_title', 'Sin título')
            chars = len(chunk.content)
            self.local_tree.insert("", tk.END, values=(i, title, chars))
        
        self.log_message(f"Resultados Local actualizados: {len(self.local_chunks)} chunks")
    
    def show_chunk_details(self, chunks: List[Chunk], tree: ttk.Treeview):
        """Muestra los detalles de un chunk seleccionado"""
        selection = tree.selection()
        if not selection:
            return
        
        item = tree.item(selection[0])
        chunk_index = int(item['values'][0]) - 1
        
        if 0 <= chunk_index < len(chunks):
            chunk = chunks[chunk_index]
            
            # Crear ventana de detalles
            detail_window = tk.Toplevel(self.root)
            detail_window.title(f"Detalles del Chunk #{chunk_index + 1}")
            detail_window.geometry("800x600")
            
            # Información del chunk
            info_frame = ttk.LabelFrame(detail_window, text="Metadatos", padding=10)
            info_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
            
            ttk.Label(info_frame, text=f"Título: {getattr(chunk.metadata, 'semantic_title', 'N/A')}").pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"Resumen: {getattr(chunk.metadata, 'summary', 'N/A')}").pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"Caracteres: {len(chunk.content)}").pack(anchor=tk.W)
            ttk.Label(info_frame, text=f"Posición: {chunk.metadata.char_start_index}-{chunk.metadata.char_end_index}").pack(anchor=tk.W)
            
            # Contenido del chunk
            content_frame = ttk.LabelFrame(detail_window, text="Contenido", padding=10)
            content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
            
            content_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD)
            content_text.pack(fill=tk.BOTH, expand=True)
            content_text.insert(tk.END, chunk.content)
            content_text.config(state=tk.DISABLED)
    
    def clear_logs(self):
        """Limpia los logs"""
        self.logs_text.config(state=tk.NORMAL)
        self.logs_text.delete(1.0, tk.END)
        self.logs_text.config(state=tk.DISABLED)
        self.log_message("Logs limpiados")
    
    def export_results(self):
        """Exporta los resultados a un archivo JSON"""
        if not self.gemini_chunks and not self.local_chunks:
            messagebox.showwarning("Advertencia", "No hay resultados para exportar")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Exportar resultados",
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            try:
                results = {
                    "gemini_chunks": [
                        {
                            "content": chunk.content,
                            "semantic_title": getattr(chunk.metadata, 'semantic_title', ''),
                            "summary": getattr(chunk.metadata, 'summary', ''),
                            "char_start": chunk.metadata.char_start_index,
                            "char_end": chunk.metadata.char_end_index
                        }
                        for chunk in self.gemini_chunks
                    ],
                    "local_chunks": [
                        {
                            "content": chunk.content,
                            "semantic_title": getattr(chunk.metadata, 'semantic_title', ''),
                            "summary": getattr(chunk.metadata, 'summary', ''),
                            "char_start": chunk.metadata.char_start_index,
                            "char_end": chunk.metadata.char_end_index
                        }
                        for chunk in self.local_chunks
                    ],
                    "parameters": {
                        "chunk_size": self.chunk_size_var.get(),
                        "chunk_overlap": self.chunk_overlap_var.get(),
                        "gemini_model": self.gemini_model_var.get(),
                        "local_url": self.local_url_var.get(),
                        "local_model": self.local_model_var.get()
                    }
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                
                self.log_message(f"Resultados exportados a: {file_path}")
                
            except Exception as e:
                self.log_message(f"Error exportando: {e}", is_error=True)


def main():
    """Función principal"""
    try:
        print("Iniciando Agentic Testing GUI...")
        
        root = tk.Tk()
        app = AgenticTestingGUI(root)
        
        def on_closing():
            print("Cerrando Agentic Testing GUI...")
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
        
    except Exception as e:
        print(f"Error fatal: {e}")
        print(traceback.format_exc())
        messagebox.showerror("Error Fatal", f"No se pudo iniciar la aplicación:\n{str(e)}")


if __name__ == "__main__":
    main()

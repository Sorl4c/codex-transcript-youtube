"""
Módulo de Interfaz Gráfica Unificada para la gestión de transcripciones y resúmenes de vídeos.

Este módulo proporciona una única ventana para:
- Pegar URLs de YouTube.
- Procesar vídeos en lote (transcripción y resumen).
- Visualizar, filtrar y buscar resultados.
- Ver y editar resúmenes.

Uso:
  python main.py --unified-ui
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue
import sys

# Módulos del proyecto
import db
import downloader
import parser
from ia.summarize_transcript import process_transcript as get_summary
import traceback
import time

class UnifiedApp(tk.Tk):
    """Clase principal para la aplicación de interfaz gráfica unificada."""

    def __init__(self, api_url=None):
        super().__init__()
        self.title("Gestor Unificado de Vídeos y Resúmenes")
        self.geometry("1400x800")
        self.minsize(1000, 600)  # Tamaño mínimo para mejor usabilidad
        
        # Manejar el evento de redimensionamiento
        self.bind('<Configure>', lambda e: self.after(100, self.adjust_preview_width))

        # Inicializar la base de datos
        db.init_db()

        # Cola para comunicación entre hilos
        self.update_queue = queue.Queue()
        
        # Inicializar variables de ordenación
        self.sort_column = 'Fecha'  # Columna por defecto para ordenar
        self.sort_direction = 'desc'  # Dirección por defecto: descendente
        self.current_video_id = None

        self.create_widgets()
        self.load_initial_data()

        # Procesar actualizaciones de la cola
        self.after(100, self.process_queue)
        
    def on_tree_double_click(self, event):
        """Maneja el evento de doble clic en la tabla."""
        # Obtener el ítem clickeado
        item = self.tree.identify_row(event.y)
        if item:
            # Seleccionar el ítem
            self.tree.selection_set(item)
            # Mostrar los detalles del vídeo
            self.on_item_select(None)  # Pasamos None ya que no usamos el evento

    def create_widgets(self):
        """Crea y organiza los widgets en la ventana principal."""
        # --- Frame Principal (con panel lateral) ---
        main_container = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame para el contenido principal (izquierda)
        main_frame = ttk.Frame(main_container, padding="5")
        main_container.add(main_frame, weight=3)  # 3/4 del ancho
        
        # Frame para el panel lateral (derecha)
        self.side_panel = ttk.Frame(main_container, padding="5")
        main_container.add(self.side_panel, weight=1)  # 1/4 del ancho
        
        # Configurar el panel de vista previa
        self.setup_preview_panel()

        # --- Frame de Entrada ---
        input_frame = ttk.LabelFrame(main_frame, text="Entrada de Vídeos", padding="10")
        input_frame.pack(fill=tk.X, pady=5)

        # Contenedor principal para controles de entrada
        controls_frame = ttk.Frame(input_frame)
        controls_frame.pack(fill=tk.X, expand=True)
        
        # Área de texto para URLs
        self.url_input = scrolledtext.ScrolledText(controls_frame, height=5, width=80)
        self.url_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Contenedor para controles a la derecha
        right_controls = ttk.Frame(controls_frame)
        right_controls.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        
        # --- Selección de Modelo ---
        model_selection_frame = ttk.LabelFrame(right_controls, text="Configuración", padding=5)
        model_selection_frame.pack(fill=tk.X, pady=2)

        model_label = ttk.Label(model_selection_frame, text="Modelo IA:")
        model_label.pack(anchor="w")

        self.model_var = tk.StringVar(value="Modelo Local")
        self.model_combo = ttk.Combobox(
            model_selection_frame,
            textvariable=self.model_var,
            values=["Modelo Local", "Gemini API"],
            state="readonly",
            width=15
        )
        self.model_combo.pack(fill=tk.X, pady=(0, 5))

        # Opción para mantener marcas de tiempo
        self.keep_timestamps_var = tk.BooleanVar(value=False)
        keep_timestamps_check = ttk.Checkbutton(
            model_selection_frame,
            text="Mantener marcas de tiempo",
            variable=self.keep_timestamps_var,
            help="Si está marcado, las marcas de tiempo no se eliminarán"
        )
        keep_timestamps_check.pack(anchor="w", pady=2)

        # --- Botones de Acción ---
        button_frame = ttk.Frame(right_controls)
        button_frame.pack(fill=tk.X, pady=(5, 0))

        process_button = ttk.Button(
            button_frame, 
            text="Procesar Lote", 
            command=self.start_processing_thread,
            width=15
        )
        process_button.pack(fill=tk.X, pady=2)

        delete_button = ttk.Button(
            button_frame, 
            text="Borrar Vídeo", 
            command=self.delete_selected_video,
            width=15
        )
        delete_button.pack(fill=tk.X, pady=2)

        # --- Frame de Resultados (Tabla) ---
        results_frame = ttk.LabelFrame(main_frame, text="Resultados", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.tree = ttk.Treeview(results_frame, columns=("ID", "Estado", "Canal", "Título", "Fecha", "Resumen"), show="headings")
        self.tree.heading("ID", text="ID", command=lambda: self.sort_by_column("ID"))
        self.tree.heading("Estado", text="Estado")
        self.tree.heading("Canal", text="Canal", command=lambda: self.sort_by_column("Canal"))
        self.tree.heading("Título", text="Título", command=lambda: self.sort_by_column("Título"))
        self.tree.heading("Fecha", text="Fecha", command=lambda: self.sort_by_column("Fecha"))
        self.tree.heading("Resumen", text="Resumen")

        self.tree.column("ID", width=50, stretch=tk.NO)
        self.tree.column("Estado", width=100, stretch=tk.NO)
        self.tree.column("Canal", width=200)
        self.tree.column("Título", width=400)
        self.tree.column("Fecha", width=120)
        self.tree.column("Resumen", width=300)

        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        # --- Frame de Filtros ---
        filter_frame = ttk.LabelFrame(main_frame, text="Búsqueda y Filtros", padding="10")
        filter_frame.pack(fill=tk.X, pady=5)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(filter_frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.search_entry.bind("<Return>", self.filter_data)

        self.filter_by_var = tk.StringVar(value="title")
        self.filter_by_combo = ttk.Combobox(filter_frame, textvariable=self.filter_by_var, values=["title", "channel"], state="readonly")
        self.filter_by_combo.pack(side=tk.LEFT, padx=(0, 10))

        filter_button = ttk.Button(filter_frame, text="Buscar", command=self.filter_data)
        filter_button.pack(side=tk.LEFT)

        clear_filter_button = ttk.Button(filter_frame, text="Limpiar", command=self.load_initial_data)
        clear_filter_button.pack(side=tk.LEFT, padx=(10, 0))

        # --- Frame de Detalles ---
        details_frame = ttk.LabelFrame(main_frame, text="Detalles del Vídeo", padding="10")
        details_frame.pack(fill=tk.X, pady=5)

        self.transcript_label = ttk.Label(details_frame, text="Transcripción:")
        self.transcript_label.pack(anchor="w")
        self.transcript_text = scrolledtext.ScrolledText(details_frame, height=8, state="disabled")
        self.transcript_text.pack(fill=tk.X, expand=True, pady=(0, 10))

        self.summary_label = ttk.Label(details_frame, text="Resumen (editable):")
        self.summary_label.pack(anchor="w")
        self.summary_text = scrolledtext.ScrolledText(details_frame, height=8)
        self.summary_text.pack(fill=tk.X, expand=True, pady=(0, 10))

        self.update_summary_button = ttk.Button(details_frame, text="Actualizar Resumen", command=self.update_summary, state="disabled")
        self.update_summary_button.pack(pady=5)

    def sort_by_column(self, col):
        """Ordena la tabla por la columna especificada."""
        # Mapeo de nombres de columna de la GUI a nombres de columna de la BD
        column_map = {
            'ID': 'id',
            'Canal': 'channel',
            'Título': 'title',
            'Fecha': 'upload_date'
        }
        db_col = column_map.get(col)
        if not db_col:
            return # No hacer nada si la columna no es ordenable

        if self.sort_column == col:
            self.sort_direction = 'asc' if self.sort_direction == 'desc' else 'desc'
        else:
            self.sort_column = col
            self.sort_direction = 'asc'

        self.load_initial_data()

    def load_initial_data(self):
        """Carga los datos iniciales de la base de datos en la tabla."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Mapeo para la llamada a la BD
        column_map = {'ID': 'id', 'Canal': 'channel', 'Título': 'title', 'Fecha': 'upload_date'}
        order_by_db = column_map.get(self.sort_column, 'upload_date')

        videos = db.get_all_videos(order_by=order_by_db, order_dir=self.sort_direction.upper())
        for video in videos:
            # Obtener el resumen de la base de datos si no está en el diccionario
            if 'summary' not in video:
                video_data = db.get_video_by_id(video['id'])
                if video_data and 'summary' in video_data:
                    video['summary'] = video_data['summary']
            
            # Crear vista previa del resumen
            resumen_preview = ''
            if video.get('summary'):
                resumen_preview = video['summary'][:100].replace('\n', ' ')
                if len(video['summary']) > 100:
                    resumen_preview += '...'
            
            self.tree.insert(
                "", 
                "end", 
                iid=str(video['id']),  # Asegurar que el iid es string
                values=(
                    video['id'], 
                    "Listo", 
                    video.get('channel', ''), 
                    video.get('title', ''), 
                    video.get('upload_date', ''), 
                    resumen_preview
                )
            )

    def setup_preview_panel(self):
        """Configura el panel lateral de vista previa del resumen."""
        # Frame para el título y botones de control
        header_frame = ttk.Frame(self.side_panel)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Título del panel
        ttk.Label(header_frame, text="Vista Previa del Resumen", 
                 font=('TkDefaultFont', 10, 'bold')).pack(side=tk.LEFT)
        
        # Frame principal con borde
        preview_container = ttk.LabelFrame(self.side_panel, text="", padding=0)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        # Área de texto con scroll
        self.preview_text = tk.Text(
            preview_container, 
            wrap=tk.WORD,
            bg='white',
            relief=tk.FLAT,
            padx=5,
            pady=5,
            font=('TkDefaultFont', 9)
        )
        
        # Configurar scrollbar
        scrollbar = ttk.Scrollbar(preview_container, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar con el scrollbar
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Deshabilitar edición
        self.preview_text.config(state=tk.DISABLED)
        
        # Estilo para el texto
        self.preview_text.tag_configure('title', font=('TkDefaultFont', 10, 'bold'))
        self.preview_text.tag_configure('normal', font=('TkDefaultFont', 9))
        
        # Texto inicial
        self.update_preview("Selecciona un vídeo para ver la vista previa del resumen")
    
    def update_preview(self, content):
        """Actualiza el contenido del panel de vista previa."""
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        
        if content:
            # Procesar el contenido para aplicar formato básico
            lines = content.split('\n')
            for line in lines:
                if line.strip().startswith('**') and line.strip().endswith('**'):
                    # Es un título
                    self.preview_text.insert(tk.END, line.strip('*') + '\n', 'title')
                else:
                    # Es texto normal
                    self.preview_text.insert(tk.END, line + '\n', 'normal')
        
        self.preview_text.config(state=tk.DISABLED)
        
        # Auto-ajustar el ancho del texto
        self.after(100, self.adjust_preview_width)
    
    def adjust_preview_width(self):
        """Ajusta el ancho del texto al ancho del panel."""
        width = self.preview_text.winfo_width()
        if width > 10:  # Asegurarse de que el ancho es válido
            self.preview_text.config(wrap=tk.WORD, width=width // 8)  # Aproximación a caracteres

    def on_item_select(self, event):
        """Maneja la selección de un ítem en la tabla."""
        selected_items = self.tree.selection()
        if not selected_items:
            return

        video_id = self.tree.item(selected_items[0], "values")[0]
        video_data = db.get_video_by_id(int(video_id))
        
        # Actualizar la vista previa si hay un resumen
        if video_data and 'summary' in video_data and video_data['summary']:
            self.update_preview(video_data['summary'])

        if video_data:
            try:
                # Habilitar y limpiar widgets
                self.transcript_text.config(state="normal")
                self.transcript_text.delete("1.0", tk.END)
                self.transcript_text.insert(tk.END, video_data.get("transcript", "No disponible."))
                self.transcript_text.config(state="disabled")

                self.summary_text.delete("1.0", tk.END)
                summary = video_data.get("summary")
                if summary:
                    self.summary_text.insert(tk.END, summary)
                self.update_summary_button.config(state="normal")
            except Exception as e:
                print(f"[UI] Error al cargar detalles del vídeo: {e}")
                self.clear_details()
        else:
            self.clear_details()

    def delete_selected_video(self):
        """Elimina el vídeo seleccionado de la tabla y la base de datos."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin selección", "Por favor, selecciona un vídeo para borrar.")
            return

        item_id = selected_items[0]
        video_id = self.tree.item(item_id, "values")[0]

        # Pedir confirmación
        confirm = messagebox.askyesno(
            "Confirmar borrado", 
            f"¿Estás seguro de que quieres borrar el vídeo ID {video_id}? Esta acción no se puede deshacer."
        )

        if confirm:
            if db.delete_video(video_id):
                self.tree.delete(item_id)
                self.clear_details()
                messagebox.showinfo("Éxito", f"Vídeo ID {video_id} borrado correctamente.")
            else:
                messagebox.showerror("Error", f"No se pudo borrar el vídeo ID {video_id} de la base de datos.")

    def clear_details(self):
        """Limpia el panel de detalles."""
        self.transcript_text.config(state="normal")
        self.transcript_text.delete("1.0", tk.END)
        self.transcript_text.config(state="disabled")
        self.summary_text.delete("1.0", tk.END)
        self.update_summary_button.config(state="disabled")

    def update_summary(self):
        """Actualiza el resumen en la base de datos."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Sin selección", "Por favor, selecciona un vídeo para actualizar.")
            return

        video_id = int(selected_items[0])
        new_summary = self.summary_text.get("1.0", tk.END).strip()

        if db.update_video_summary(video_id, new_summary):
            messagebox.showinfo("Éxito", "Resumen actualizado correctamente.")
        else:
            messagebox.showerror("Error", "No se pudo actualizar el resumen.")

    def start_processing_thread(self):
        """Inicia el hilo de procesamiento de URLs, pasando el modelo seleccionado."""
        """Inicia el hilo de procesamiento de URLs."""
        urls = self.url_input.get("1.0", tk.END).strip().splitlines()
        urls = [url for url in urls if url.strip()]  # Filtrar líneas vacías
        if not urls:
            messagebox.showwarning("Entrada vacía", "Por favor, introduce al menos una URL.")
            return

        selected_model = self.model_var.get()
        pipeline_type = 'gemini' if selected_model == "Gemini API" else 'native'

        processing_thread = threading.Thread(target=self.process_urls, args=(urls, pipeline_type), daemon=True)
        processing_thread.start()

    def filter_data(self, event=None):
        """Filtra los datos de la tabla según el criterio de búsqueda."""
        search_term = self.search_var.get()
        filter_by = self.filter_by_var.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        # Mapeo para la llamada a la BD
        column_map = {'ID': 'id', 'Canal': 'channel', 'Título': 'title', 'Fecha': 'upload_date'}
        order_by_db = column_map.get(self.sort_column, 'upload_date')

        videos = db.filter_videos(
            by_field=filter_by, 
            value=search_term, 
            order_by=order_by_db, 
            order_dir=self.sort_direction.upper()
        )
        
        for video in videos:
            # Obtener el resumen de la base de datos si no está en el diccionario
            if 'summary' not in video:
                video_data = db.get_video_by_id(video['id'])
                if video_data and 'summary' in video_data:
                    video['summary'] = video_data['summary']
            
            # Crear vista previa del resumen
            resumen_preview = ''
            if video.get('summary'):
                resumen_preview = video['summary'][:100].replace('\n', ' ')
                if len(video['summary']) > 100:
                    resumen_preview += '...'
            
            self.tree.insert(
                "", 
                "end", 
                iid=str(video['id']),  # Asegurar que el iid es string
                values=(
                    video['id'], 
                    "Listo", 
                    video.get('channel', ''), 
                    video.get('title', ''), 
                    video.get('upload_date', ''), 
                    resumen_preview
                )
            )

    def process_urls(self, urls, pipeline_type: str):
        """Función ejecutada en un hilo para procesar cada URL."""
        for i, url in enumerate(urls):
            temp_id = f"new_{i}_{time.time()}"
            try:
                # 1. Añadir a la tabla con estado "En Cola"
                self.update_queue.put({'type': 'add', 'temp_id': temp_id, 'url': url})

                # 2. Descargar
                self.update_queue.put({'type': 'update_status', 'temp_id': temp_id, 'status': 'Descargando...'})
                vtt_content, _, video_metadata = downloader.download_vtt(url)
                if not vtt_content or not video_metadata:
                    raise ValueError("No se pudo descargar el vídeo o sus subtítulos.")

                # 3. Transcribir
                self.update_queue.put({'type': 'update_status', 'temp_id': temp_id, 'status': 'Transcribiendo...'})
                keep_timestamps = self.keep_timestamps_var.get()
                remove_timestamps = not keep_timestamps
                plain_text = parser.vtt_to_plain_text(vtt_content, remove_timestamps)
                formatted_text = parser.format_transcription(plain_text, title=video_metadata['title'], url=url)

                # 4. Resumir
                self.update_queue.put({'type': 'update_status', 'temp_id': temp_id, 'status': 'Resumiendo...'})
                try:
                    print(f"[DEBUG] Intentando generar resumen para: {video_metadata['title']}")
                    print(f"[DEBUG] Longitud de la transcripción: {len(formatted_text)} caracteres")
                    
                    # Llamar a la función de resumen con manejo de errores
                    summary_result = get_summary(formatted_text, pipeline_type=pipeline_type)
                    
                    # La función puede devolver (texto, prompt_text, payload) o solo el texto
                    if isinstance(summary_result, tuple):
                        summary_text = summary_result[0]  # Tomamos solo el texto del resumen
                    else:
                        summary_text = summary_result
                        
                    print(f"[DEBUG] Resumen generado correctamente. Longitud: {len(summary_text)} caracteres")
                except Exception as e:
                    print(f"[ERROR] Error al generar el resumen: {str(e)}")
                    print(traceback.format_exc())
                    summary_text = "[No se pudo generar el resumen]"

                # 5. Guardar en BD
                db_data = {
                    'url': video_metadata['url'],
                    'channel': video_metadata['channel'],
                    'title': video_metadata['title'],
                    'upload_date': video_metadata['upload_date'],
                    'transcript': formatted_text,
                    'summary': summary_text,
                    'key_ideas': None, # Placeholder
                    'ai_categorization': None # Placeholder
                }
                db.insert_video(db_data)
                final_video_data = db.get_video_by_url(url)

                # 6. Actualizar tabla con estado "Listo"
                self.update_queue.put({'type': 'update_final', 'temp_id': temp_id, 'video_data': final_video_data})

            except Exception as e:
                print(traceback.format_exc())
                self.update_queue.put({'type': 'error', 'temp_id': temp_id, 'message': str(e)})

    def process_queue(self):
        """Procesa mensajes de la cola para actualizar la UI desde el hilo principal."""
        try:
            while True:
                msg = self.update_queue.get_nowait()
                msg_type = msg.get('type')

                if msg_type == 'add':
                    self.tree.insert("", 0, iid=msg['temp_id'], values=("-", "En cola", "-", msg['url'], "-"))
                
                elif msg_type == 'update_status':
                    if self.tree.exists(msg['temp_id']):
                        current_values = list(self.tree.item(msg['temp_id'], 'values'))
                        current_values[1] = msg['status']
                        self.tree.item(msg['temp_id'], values=tuple(current_values))

                elif msg_type == 'update_final':
                    if self.tree.exists(msg['temp_id']):
                        video = msg['video_data']
                        if video:
                            # Obtener el índice actual del ítem temporal
                            index = self.tree.index(msg['temp_id'])
                            # Crear una vista previa del resumen (primeros 100 caracteres)
                            resumen_preview = (video['summary'][:100].replace('\n', ' ') + '...') if video.get('summary') else ''
                            
                            # Eliminar el ítem temporal
                            self.tree.delete(msg['temp_id'])
                            
                            # Insertar el ítem definitivo con todos los datos
                            self.tree.insert("", index, iid=video['id'], values=(
                                video['id'], 
                                "Listo", 
                                video.get('channel', ''), 
                                video.get('title', ''), 
                                video.get('upload_date', ''),
                                resumen_preview  # Añadimos la vista previa del resumen
                            ))
                            
                            # Seleccionar automáticamente el vídeo recién añadido
                            self.tree.selection_set(video['id'])
                            self.on_item_select(None)
                        else:
                            # Si no se encuentran datos del vídeo en la BD, se marca como error.
                            current_values = list(self.tree.item(msg['temp_id'], 'values'))
                            current_values[1] = "Error DB"
                            self.tree.item(msg['temp_id'], values=tuple(current_values))

                elif msg_type == 'error':
                    if self.tree.exists(msg['temp_id']):
                        current_values = list(self.tree.item(msg['temp_id'], 'values'))
                        current_values[1] = "Error"
                        self.tree.item(msg['temp_id'], values=tuple(current_values))
                        # Opcional: mostrar error en una columna o tooltip

        except queue.Empty:
            pass
        finally:
            self.after(100, self.process_queue)

# El punto de entrada principal ahora está en main.py

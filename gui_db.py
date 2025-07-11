import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from db import get_all_videos, filter_videos, get_video_by_id
from datetime import datetime

class DBViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Visor de la Base de Datos de Subtítulos")
        self.geometry("1200x700")

        # --- Layout --- #
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Panel de Filtros ---
        filter_frame = ttk.LabelFrame(main_frame, text="Filtros", padding="10")
        filter_frame.pack(fill=tk.X, pady=5)

        ttk.Label(filter_frame, text="Filtrar por:").pack(side=tk.LEFT, padx=5)
        self.filter_field = ttk.Combobox(filter_frame, values=["title", "channel"], state="readonly")
        self.filter_field.set("title")
        self.filter_field.pack(side=tk.LEFT, padx=5)

        self.filter_value = ttk.Entry(filter_frame, width=40)
        self.filter_value.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        ttk.Button(filter_frame, text="Buscar", command=self.apply_filter).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_frame, text="Limpiar", command=self.clear_filter).pack(side=tk.LEFT, padx=5)

        # --- Vista de Tabla y Panel de Texto ---
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        content_frame.grid_columnconfigure(0, weight=2)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # --- Tabla de Vídeos ---
        tree_frame = ttk.Frame(content_frame)
        tree_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Canal", "Título", "Fecha"), show='headings')
        # Configurar encabezados con ordenación
        self.tree.heading("ID", text="ID", command=lambda: self.sort_column("ID", False, is_numeric=True))
        self.tree.heading("Canal", text="Canal", command=lambda: self.sort_column("Canal", False))
        self.tree.heading("Título", text="Título", command=lambda: self.sort_column("Título", False))
        self.tree.heading("Fecha", text="Fecha", command=lambda: self.sort_column("Fecha", False, is_date=True))

        self.tree.column("ID", width=50, stretch=tk.NO)
        self.tree.column("Canal", width=200)
        self.tree.column("Título", width=400)
        self.tree.column("Fecha", width=120)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
        self.tree.pack(fill='both', expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_video_select)

        # --- Panel de Texto del Transcript ---
        text_frame = ttk.LabelFrame(content_frame, text="Transcripción Completa", padding="10")
        text_frame.grid(row=0, column=1, sticky="nsew")

        self.transcript_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, state='disabled')
        self.transcript_text.pack(fill=tk.BOTH, expand=True)

        self.load_videos()

    def format_date(self, date_str):
        """Formatea la fecha al formato español (DD/MM/YYYY)."""
        try:
            date_obj = datetime.strptime(date_str, '%Y%m%d')
            return date_obj.strftime('%d/%m/%Y')
        except (ValueError, TypeError):
            return date_str

    def sort_column(self, col, reverse, is_date=False, is_numeric=False):
        """Ordena la columna al hacer clic en el encabezado."""
        # Obtener todos los elementos
        data = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        
        # Ordenar los datos
        try:
            if is_date:
                # Ordenar fechas
                data.sort(key=lambda x: datetime.strptime(x[0], '%d/%m/%Y') if x[0] else datetime.min, reverse=reverse)
            elif is_numeric:
                # Ordenar números
                data.sort(key=lambda x: int(x[0]) if x[0].isdigit() else float('inf'), reverse=reverse)
            else:
                # Ordenar texto
                data.sort(reverse=reverse, key=lambda x: str(x[0]).lower() if x[0] else '')
        except (ValueError, AttributeError):
            # En caso de error, ordenar como texto
            data.sort(reverse=reverse, key=lambda x: str(x[0]).lower() if x[0] else '')
        
        # Reorganizar los elementos en el orden ordenado
        for index, (val, item) in enumerate(data):
            self.tree.move(item, '', index)
        
        # Invertir el orden para la próxima vez
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse, is_date))

    def load_videos(self, videos=None):
        """Carga o recarga los vídeos en la tabla."""
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        if videos is None:
            videos = get_all_videos()
        
        for video in videos:
            formatted_date = self.format_date(video['upload_date'])
            self.tree.insert("", "end", values=(
                video['id'], 
                video['channel'], 
                video['title'], 
                formatted_date
            ))

    def apply_filter(self):
        """Filtra los vídeos según el campo y valor seleccionados."""
        field = self.filter_field.get()
        value = self.filter_value.get()
        if not value.strip():
            messagebox.showwarning("Entrada vacía", "Por favor, introduce un valor para buscar.")
            return
        try:
            filtered_videos = filter_videos(by_field=field, value=value)
            self.load_videos(filtered_videos)
            self.transcript_text.config(state='normal')
            self.transcript_text.delete(1.0, tk.END)
            self.transcript_text.config(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo aplicar el filtro: {e}")

    def clear_filter(self):
        """Limpia el filtro y recarga todos los vídeos."""
        self.filter_value.delete(0, tk.END)
        self.load_videos()
        self.transcript_text.config(state='normal')
        self.transcript_text.delete(1.0, tk.END)
        self.transcript_text.config(state='disabled')

    def on_video_select(self, event):
        """Muestra la transcripción del vídeo seleccionado."""
        selected_items = self.tree.selection()
        if not selected_items:
            return

        item = self.tree.item(selected_items[0])
        video_id = item['values'][0]
        
        video_details = get_video_by_id(video_id)
        
        self.transcript_text.config(state='normal')
        self.transcript_text.delete(1.0, tk.END)
        if video_details and video_details['transcript']:
            self.transcript_text.insert(tk.END, video_details['transcript'])
        else:
            self.transcript_text.insert(tk.END, "Transcripción no disponible.")
        self.transcript_text.config(state='disabled')

if __name__ == "__main__":
    try:
        from db import init_db
        init_db()
        app = DBViewer()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Error Crítico", f"No se pudo iniciar la aplicación: {e}")

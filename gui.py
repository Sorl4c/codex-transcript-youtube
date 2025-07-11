import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import threading
import queue

from batch_processor import process_urls_to_single_file
from utils import is_url

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Procesador de Subtítulos de YouTube")
        self.geometry("800x600")

        self.output_path = ""
        self.log_queue = queue.Queue()

        # --- Widgets ---
        self.create_widgets()
        self.after(100, self.process_log_queue)

    def create_widgets(self):
        # Frame para la entrada de URLs
        urls_frame = tk.Frame(self, pady=10)
        urls_frame.pack(fill=tk.X, padx=10)
        tk.Label(urls_frame, text="Pega aquí las URLs de YouTube (una por línea):").pack(anchor='w')
        self.urls_text = scrolledtext.ScrolledText(urls_frame, height=10, width=80)
        self.urls_text.pack(fill=tk.BOTH, expand=True)

        # Frame para los controles
        controls_frame = tk.Frame(self, pady=10)
        controls_frame.pack(fill=tk.X, padx=10)

        self.output_path_label = tk.Label(controls_frame, text="Archivo de salida: No seleccionado", wraplength=500, justify=tk.LEFT)
        self.output_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        select_file_button = tk.Button(controls_frame, text="Seleccionar Salida", command=self.select_output_file)
        select_file_button.pack(side=tk.RIGHT, padx=(0, 5))

        # Botón de procesar
        self.process_button = tk.Button(self, text="Iniciar Proceso", command=self.start_processing, font=("Helvetica", 12, "bold"))
        self.process_button.pack(pady=10)

        # Frame para la consola de logs
        log_frame = tk.Frame(self, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        tk.Label(log_frame, text="Registro de Actividad:").pack(anchor='w')
        self.log_console = scrolledtext.ScrolledText(log_frame, state='disabled', bg='black', fg='white')
        self.log_console.pack(fill=tk.BOTH, expand=True)

    def select_output_file(self):
        path = filedialog.asksaveasfilename(
            title="Guardar transcripción como...",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            self.output_path = path
            self.output_path_label.config(text=f"Archivo de salida: {self.output_path}")

    def start_processing(self):
        urls = self.urls_text.get("1.0", tk.END).strip().split('\n')
        urls = [url.strip() for url in urls if url.strip() and is_url(url.strip())]

        if not urls:
            messagebox.showwarning("Entrada Inválida", "Por favor, introduce al menos una URL válida.")
            return

        if not self.output_path:
            messagebox.showwarning("Salida no especificada", "Por favor, selecciona un archivo de salida.")
            return

        self.process_button.config(state='disabled', text="Procesando...")
        self.log_console.config(state='normal')
        self.log_console.delete("1.0", tk.END)
        self.log_console.config(state='disabled')

        # Ejecutar en un hilo para no bloquear la GUI
        thread = threading.Thread(target=self.run_batch_process, args=(urls,))
        thread.start()

    def run_batch_process(self, urls):
        # Redirigir stdout para capturar logs
        import sys
        original_stdout = sys.stdout
        sys.stdout = self

        try:
            process_urls_to_single_file(urls, self.output_path, 'es')
        except Exception as e:
            self.log_message(f"[FATAL ERROR] Un error inesperado ha ocurrido: {e}")
        finally:
            # Restaurar stdout y reactivar el botón
            sys.stdout = original_stdout
            self.process_button.config(state='normal', text="Iniciar Proceso")
            self.log_message("\n--- Proceso finalizado ---")
            messagebox.showinfo("Completado", "El proceso ha finalizado. Revisa el registro para más detalles.")

    def write(self, text):
        """Captura el output de print y lo envía a la cola."""
        self.log_queue.put(text)

    def flush(self):
        pass

    def process_log_queue(self):
        """Procesa la cola de logs y actualiza la GUI."""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_message(message)
        except queue.Empty:
            pass
        self.after(100, self.process_log_queue)

    def log_message(self, message):
        self.log_console.config(state='normal')
        self.log_console.insert(tk.END, message)
        self.log_console.see(tk.END)
        self.log_console.config(state='disabled')

if __name__ == "__main__":
    app = App()
    app.mainloop()

"""
Versión Orientada a Objetos de la interfaz Streamlit para gestión de vídeos.
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
import re
import json
import traceback
import pyperclip
import logging
import time
import os

# Módulos del proyecto
import db
from downloader import download_vtt
from parser import vtt_to_plain_text, format_transcription
from ia.summarize_transcript import process_transcript as get_summary
from rag_interface import get_rag_interface, RAGInterface

logger = logging.getLogger("gui_streamlit")
logger.setLevel(logging.INFO)

# Evitar duplicar handlers si ya existen
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(name)s %(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# --- Clases de Modelo de Datos ---

class Video:
    """Clase para encapsular los datos de un vídeo."""
    def __init__(self, video_data: Dict):
        self.id: Optional[int] = video_data.get('id')
        self.title: str = video_data.get('title', 'Sin título')
        self.channel: str = video_data.get('channel', 'Desconocido')
        self.upload_date: str = video_data.get('upload_date', '')
        self.transcript: str = video_data.get('transcript', '')
        self.summary: str = video_data.get('summary', '')
        self.url: str = video_data.get('url', '')
        self.video_id: str = video_data.get('video_id', '')
        self.key_ideas: Optional[str] = video_data.get('key_ideas')
        self.ai_categorization: Optional[str] = video_data.get('ai_categorization')

# --- Clases de Lógica de Negocio ---

class DatabaseManager:
    """Maneja todas las operaciones con la base de datos."""
    def __init__(self):
        start = time.perf_counter()
        self.db_module = db
        self.db_module.init_db()
        logger.info("DatabaseManager inicializado en %.2fs", time.perf_counter() - start)

    def get_all_videos(self) -> List[Dict]:
        return self.db_module.get_all_videos()

    @st.cache_data(ttl=300)
    def get_videos_df(_self, search_query: str, sort_column: str, sort_direction: str) -> pd.DataFrame:
        """Obtiene vídeos como DataFrame, aplicando filtro y ordenación."""
        column_mapping = {'Fecha': 'upload_date', 'Título': 'title', 'Canal': 'channel'}
        db_sort_column = column_mapping.get(sort_column, 'upload_date')
        videos_data = _self.get_all_videos()
        if not videos_data:
            return pd.DataFrame()
        df = pd.DataFrame(videos_data)
        if search_query:
            df = df[df['title'].str.contains(search_query, case=False, na=False) | 
                    df['channel'].str.contains(search_query, case=False, na=False)]
        if db_sort_column in df.columns:
            df = df.sort_values(by=db_sort_column, ascending=(sort_direction == 'asc'))
        return df

    def get_video_by_id(self, video_id: int) -> Optional[Dict]:
        return self.db_module.get_video_by_id(video_id)

    def get_video_by_url(self, video_id: str) -> Optional[Dict]:
        return self.db_module.get_video_by_url(video_id)

    def insert_video(self, video_data: Dict):
        self.db_module.insert_video(video_data)

    def delete_video(self, video_id: int):
        self.db_module.delete_video(video_id)

    def update_summary(self, video_id: int, summary: str):
        self.db_module.update_summary(video_id, summary)

class YouTubeProcessor:
    """Maneja el procesamiento de URLs de YouTube."""
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        start = time.perf_counter()
        self.rag_interface = get_rag_interface()
        logger.info(
            "YouTubeProcessor inicializado en %.2fs (RAG disponible=%s)",
            time.perf_counter() - start,
            self.rag_interface.is_available()
        )

    @staticmethod
    def get_video_id_from_url(url: str) -> str:
        if not url or not isinstance(url, str): return ""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/|youtube\.com/e/|youtube\.com/watch\?.*&v=)([^#\&\?\n]*)',
            r'youtube\.com/shorts/([^#\&\?\n]*)', r'youtube\.com/live/([^#\&\?\n]*)'
        ]
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match and len(match.groups()) > 0: return match.group(1)
        return url.strip()

    def process_urls_locally(self, urls: List[str], status_container, keep_timestamps: bool = False, ingest_in_rag: bool = False):
        total_urls = len(urls)
        progress_bar = status_container.progress(0, text="Iniciando proceso local...")
        for i, url in enumerate(urls):
            video_id = self.get_video_id_from_url(url)
            if not video_id: continue
            if self.db_manager.get_video_by_url(video_id):
                status_container.info(f"El vídeo '{video_id}' ya existe.")
                progress_bar.progress((i + 1) / total_urls)
                continue
            with st.spinner(f"Descargando datos para {video_id}..."):
                vtt_content, _, video_info = download_vtt(video_id)
                if vtt_content and video_info:
                    remove_timestamps = not keep_timestamps
                    plain_text = vtt_to_plain_text(vtt_content, remove_timestamps)
                    formatted_transcript = format_transcription(plain_text, title=video_info.get('title', 'Sin título'), url=url)
                    video_data = {
                        'url': url,
                        'channel': video_info.get('channel', 'N/A'),
                        'title': video_info.get('title', 'Sin título'),
                        'upload_date': video_info.get('upload_date', 'N/A'),
                        'transcript': formatted_transcript,
                        'summary': '',
                        'key_ideas': '',
                        'ai_categorization': ''
                    }
                    self.db_manager.insert_video(video_data)

                    # Ingestar en RAG si está solicitado
                    if ingest_in_rag and self.rag_interface.is_available():
                        with st.spinner(f"Ingestando '{video_info.get('title')}' en RAG..."):
                            rag_result = self.rag_interface.ingest_transcript(
                                video_id=video_id,
                                title=video_info.get('title', 'Sin título'),
                                transcript=plain_text,
                                strategy='semantico',
                                use_docling=True
                            )
                            if rag_result['status'] == 'success':
                                status_container.success(f"'{video_info.get('title')}' guardado e ingresado en RAG.")
                            else:
                                status_container.warning(f"'{video_info.get('title')}' guardado, pero error en RAG: {rag_result['message']}")
                    else:
                        status_container.success(f"'{video_info.get('title')}' guardado.")
                else: status_container.error(f"Fallo al descargar para: {url}")
            progress_bar.progress((i + 1) / total_urls)
        progress_bar.progress(1.0, text="¡Proceso local completado!")

    def process_urls_with_api(self, urls: List[str], feedback_container, keep_timestamps: bool = False, ingest_in_rag: bool = False):
        total_urls = len(urls)
        feedback_container.info(f"Iniciando procesamiento con API para {total_urls} URL(s)...")
        for i, url in enumerate(urls):
            url_feedback = feedback_container.container(border=True)
            url_feedback.write(f"**Procesando URL ({i+1}/{total_urls}):** `{url}`")
            try:
                vtt_content, _, metadata = download_vtt(url)
                if not vtt_content:
                    url_feedback.warning("No se encontraron subtítulos."); continue
                remove_timestamps = not keep_timestamps
                plain_text = vtt_to_plain_text(vtt_content, remove_timestamps)
                summary_text = get_summary(plain_text, pipeline_type='gemini')[0]
                if summary_text and "Error:" not in summary_text:
                    formatted_transcript = format_transcription(plain_text)
                    video_data = {
                        'url': url, 'channel': metadata.get('channel', 'N/A'),
                        'title': metadata.get('title', 'Título no disponible'), 'upload_date': metadata.get('upload_date', None),
                        'transcript': formatted_transcript, 'summary': summary_text,
                        'key_ideas': None, 'ai_categorization': None
                    }
                    self.db_manager.insert_video(video_data)

                    # Ingestar en RAG si está solicitado
                    if ingest_in_rag and self.rag_interface.is_available():
                        video_id = self.get_video_id_from_url(url)
                        with url_feedback.spinner(f"Ingestando '{metadata.get('title')}' en RAG..."):
                            rag_result = self.rag_interface.ingest_transcript(
                                video_id=video_id,
                                title=metadata.get('title', 'Título no disponible'),
                                transcript=plain_text,
                                strategy='semantico',
                                use_docling=True
                            )
                            if rag_result['status'] == 'success':
                                url_feedback.success(f"¡Vídeo '{metadata.get('title')}' procesado e ingresado en RAG!")
                            else:
                                url_feedback.warning(f"¡Vídeo '{metadata.get('title')}' procesado, pero error en RAG: {rag_result['message']}")
                    else:
                        url_feedback.success(f"¡Vídeo '{metadata.get('title')}' procesado!")
                else: url_feedback.error(f"Error de la API: {summary_text}")
            except Exception as e: url_feedback.error(f"Error crítico: {e}")

# --- Clase Principal de la Aplicación ---

class StreamlitApp:
    def __init__(self):
        init_start = time.perf_counter()
        logger.info("StreamlitApp.__init__ inicio (PID=%s)", os.getpid())

        self.db_manager = DatabaseManager()
        self.yt_processor = YouTubeProcessor(self.db_manager)

        rag_start = time.perf_counter()
        self.rag_interface = get_rag_interface()
        logger.info(
            "StreamlitApp obtuvo RAGInterface en %.2fs (disponible=%s)",
            time.perf_counter() - rag_start,
            self.rag_interface.is_available()
        )
        self.setup_page_config()
        self.init_session_state()
        logger.info("StreamlitApp.__init__ completado en %.2fs", time.perf_counter() - init_start)

    def setup_page_config(self):
        st.set_page_config(page_title="Gestor de Vídeos (OOP)", page_icon="🎥", layout="wide")

    def init_session_state(self):
        for key, value in [('sort_column', 'Fecha'), ('sort_direction', 'desc'), ('selected_video_id', None)]:
            if key not in st.session_state: st.session_state[key] = value

    def run(self):
        logger.info(
            "StreamlitApp.run ejecutándose (nav actual=%s)",
            st.session_state.get("nav_oop")
        )
        st.sidebar.title("Navegación OOP")
        page = st.sidebar.radio("Ir a", ["Videoteca", "Agregar Vídeos", "Búsqueda RAG", "Análisis Detallado"], key="nav_oop")
        if page == "Videoteca": self.display_videoteca_page()
        elif page == "Agregar Vídeos": self.display_add_videos_page()
        elif page == "Búsqueda RAG": self.display_rag_search_page()
        elif page == "Análisis Detallado": self.display_detailed_analysis_page()

    def display_add_videos_page(self):
        st.header("➕ Agregar Nuevos Vídeos")
        url_input = st.text_area("URLs (una por línea):", height=150, key="url_input_oop")
        processing_mode = st.radio("Modo:", ("Local", "API"), index=1, horizontal=True, key="mode_oop")
        keep_timestamps = st.checkbox("Mantener marcas de tiempo", key="keep_timestamps_oop", help="Si está marcado, las marcas de tiempo de los subtítulos no se eliminarán")

        # Opción de ingestión RAG
        rag_available = self.rag_interface.is_available()
        if rag_available:
            ingest_in_rag = st.checkbox("Ingestar en RAG", key="ingest_rag_oop",
                                       help="Ingestar transcripciones en el sistema RAG para búsqueda semántica")
            # Mostrar estadísticas RAG
            with st.expander("📊 Estadísticas RAG"):
                rag_stats = self.rag_interface.get_stats()
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Documentos en RAG", rag_stats.total_documents)
                    st.metric("Base de datos", rag_stats.database_type)
                with col2:
                    st.metric("Embeddings", rag_stats.embedder_type)
                    st.metric("Tamaño BD", f"{rag_stats.database_size_mb:.2f} MB")
        else:
            st.warning("⚠️ Sistema RAG no disponible. Las transcripciones no se ingestarán automáticamente.")
            ingest_in_rag = False

        if st.button("Procesar Vídeos", key="process_oop"):
            urls = [url.strip() for url in url_input.split('\n') if url.strip()]
            if not urls: st.warning("Por favor, introduce al menos una URL."); return
            if processing_mode == "Local":
                self.yt_processor.process_urls_locally(urls, st.container(), keep_timestamps, ingest_in_rag)
            else:
                self.yt_processor.process_urls_with_api(urls, st.container(), keep_timestamps, ingest_in_rag)

    def display_videoteca_page(self):
        st.header("📚 Videoteca (OOP)")

        # Filtros de búsqueda y ordenación
        col1, col2, col3 = st.columns([3, 2, 2])
        with col1:
            search_query = st.text_input("🔍 Buscar por título o canal:", key="search_oop")
        with col2:
            sort_column_map = {'Fecha': 'upload_date', 'Título': 'title', 'Canal': 'channel'}
            sort_column_display = st.selectbox(
                "Ordenar por:",
                list(sort_column_map.keys()),
                index=0,
                key="sort_column_oop"
            )
            sort_column = sort_column_map[sort_column_display]
        with col3:
            sort_direction_map = {'Descendente': 'desc', 'Ascendente': 'asc'}
            sort_direction_display = st.radio(
                "Orden:",
                list(sort_direction_map.keys()),
                index=0,
                horizontal=True,
                key="sort_direction_oop"
            )
            sort_direction = sort_direction_map[sort_direction_display]

        # Obtener y filtrar vídeos
        videos_df = self.db_manager.get_videos_df(search_query, sort_column, sort_direction)

        if videos_df.empty:
            st.info("No se encontraron vídeos que coincidan con la búsqueda.")
            if search_query:
                if st.button("Mostrar todos los vídeos"):
                    st.session_state.search_oop = ""
                    st.rerun()
            return

        st.subheader("Lista de vídeos")
        st.write("Haz clic en una fila para seleccionarla y ver sus detalles.")

        # Reset index to ensure it's unique and sequential for selection
        videos_df_reset = videos_df.reset_index(drop=True)

        display_columns = ['id', 'title', 'channel', 'upload_date']
        column_rename = {'id': 'ID', 'title': 'Título', 'channel': 'Canal', 'upload_date': 'Fecha'}
        
        # Use a key for the dataframe to access its state
        df_key = "videoteca_df"
        
        st.dataframe(
            videos_df_reset[display_columns].rename(columns=column_rename),
            use_container_width=True,
            hide_index=True,
            key=df_key,
            selection_mode="single-row",
            on_select="rerun"  # This will rerun the script on selection change
        )
        st.caption(f"Mostrando {len(videos_df_reset)} vídeos")
        
        st.divider()

        # Check for selection in session state
        selected_id = None
        if df_key in st.session_state:
            selection = st.session_state[df_key]['selection']
            if selection['rows']:
                selected_index = selection['rows'][0]
                # Explicitly cast to a standard Python int to avoid type issues with db queries
                selected_id = int(videos_df_reset.iloc[selected_index]['id'])
                
        if selected_id:
            st.subheader("Detalles del vídeo seleccionado")
            self.display_video_details(selected_id)

    def display_rag_search_page(self):
        """Mostrar la página de búsqueda RAG."""
        st.header("🔍 Búsqueda RAG (Recuperación Aumentada)")

        if not self.rag_interface.is_available():
            st.error("❌ Sistema RAG no disponible. Por favor, verifica que todas las dependencias estén instaladas.")
            st.info("Para habilitar RAG, asegúrate de que las siguientes dependencias estén en requirements.txt:")
            st.code("""
sentence-transformers>=5.1.0
sqlite-vec>=0.1.6
scikit-learn>=1.7.0
rank-bm25>=0.2.0
docling>=2.0.0
""")
            return

        # Panel de configuración
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            question = st.text_input("❓ Tu pregunta:", placeholder="Ej: ¿Qué ejercicios se recomiendan para principiantes?", key="rag_question")
        with col2:
            mode = st.selectbox("🔧 Modo de búsqueda:", options=self.rag_interface.get_available_modes(), index=2, key="rag_mode")
        with col3:
            top_k = st.slider("📊 Resultados:", min_value=1, max_value=10, value=5, key="rag_top_k")

        # Botón de búsqueda
        search_button = st.button("🔍 Buscar", type="primary", key="rag_search")

        # Panel de estadísticas
        with st.expander("📊 Estadísticas del Sistema RAG", expanded=False):
            rag_stats = self.rag_interface.get_stats()
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📄 Documentos", rag_stats.total_documents)
            with col2:
                st.metric("🧠 Embeddings", rag_stats.embedder_type)
            with col3:
                st.metric("💾 Base de Datos", rag_stats.database_type)
            with col4:
                st.metric("📏 Tamaño BD", f"{rag_stats.database_size_mb:.2f} MB")

        # Área de resultados
        if search_button and question:
            with st.spinner(f"Buscando con modo '{mode}'..."):
                results, error = self.rag_interface.query(question, mode=mode, top_k=top_k)

            if error:
                st.error(f"❌ Error en la búsqueda: {error}")
            elif not results:
                st.warning("⚠️ No se encontraron resultados. Intenta con otra pregunta o ingest más transcripciones.")
            else:
                st.success(f"✅ Se encontraron {len(results)} resultados:")

                for i, result in enumerate(results, 1):
                    with st.expander(f"📄 Resultado #{i} (Score: {result.score:.4f})", expanded=i==1):
                        # Metadata del resultado
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown("**Contenido:**")
                            st.write(result.content)
                        with col2:
                            st.markdown("**Metadata:**")
                            st.write(f"**Score:** {result.score:.4f}")

                            # Mostrar rankings para búsqueda híbrida
                            if result.vector_rank is not None or result.bm25_rank is not None:
                                if result.vector_rank is not None:
                                    st.write(f"**Vector Rank:** #{result.vector_rank}")
                                    st.write(f"**Vector Score:** {result.vector_score:.4f}")
                                if result.bm25_rank is not None:
                                    st.write(f"**BM25 Rank:** #{result.bm25_rank}")
                                    st.write(f"**BM25 Score:** {result.bm25_score:.4f}")

                        # Botón de copiar
                        if st.button(f"📋 Copiar Resultado #{i}", key=f"copy_rag_{i}"):
                            pyperclip.copy(result.content)
                            st.toast("¡Contenido copiado al portapapeles!")

                        st.divider()

    def display_detailed_analysis_page(self):
        st.header("🔬 Análisis Detallado")
        videos_data = self.db_manager.get_all_videos()
        if not videos_data: st.info("No hay vídeos para analizar."); return
        df = pd.DataFrame(videos_data)
        channels = sorted(df['channel'].unique().tolist())
        selected_channel = st.selectbox("1. Selecciona un canal:", options=["Todos"] + channels)
        filtered_df = df[df['channel'] == selected_channel] if selected_channel != "Todos" else df
        if filtered_df.empty: st.warning("No hay vídeos para el canal."); return

        video_options = {f"{row['title']} (ID: {row['id']})": row['id'] for _, row in filtered_df.iterrows()}
        selected_display = st.selectbox("2. Selecciona un vídeo:", options=[""] + list(video_options.keys()), key="vid_select_analysis")
        if selected_display:
            self.display_video_details(video_options[selected_display])

    def display_video_details(self, video_id):
        video_data = self.db_manager.get_video_by_id(video_id)
        if not video_data: st.error(f"No se encontró el vídeo ID {video_id}."); return
        video = Video(video_data)

        st.subheader(video.title)
        st.caption(f"Canal: {video.channel} | Fecha: {video.upload_date}")
        summary_tab, transcript_tab = st.tabs(["📝 Resumen", "📄 Transcripción"])
        with summary_tab:
            if not video.summary:
                st.info("Este vídeo aún no tiene un resumen.")
                if st.button("✨ Generar Resumen Ahora", key=f"gen_{video.id}"):
                    with st.spinner("Generando resumen..."):
                        new_summary, _, _ = get_summary(video.transcript, pipeline_type='native')
                        self.db_manager.update_summary(video.id, new_summary)
                    st.success("¡Resumen generado!"); st.rerun()
            else:
                st.text_area("Resumen", video.summary, height=300, key=f"sum_{video.id}")
                if st.button("Copiar Resumen", key=f"copy_sum_{video.id}"):
                    pyperclip.copy(video.summary); st.toast("¡Resumen copiado!")
        with transcript_tab:
            st.text_area("Transcripción", video.transcript, height=300, key=f"trans_{video.id}")
            if st.button("Copiar Transcripción", key=f"copy_trans_{video.id}"):
                pyperclip.copy(video.transcript); st.toast("¡Transcripción copiada!")
        st.divider()
        if st.button("🗑️ Eliminar Vídeo", key=f"del_{video.id}", type="primary"):
            self.db_manager.delete_video(video.id)
            st.success(f"Vídeo '{video.title}' eliminado.")
            st.session_state.selected_video_id = None; st.rerun()

if __name__ == "__main__":
    bootstrap_start = time.perf_counter()
    logger.info("Creando instancia de StreamlitApp...")
    app = StreamlitApp()
    logger.info("StreamlitApp creada en %.2fs", time.perf_counter() - bootstrap_start)
    app.run()

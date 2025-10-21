#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de Integración RAG + Streamlit GUI

Este test verifica que la integración del sistema RAG con la interfaz
Streamlit funcione correctamente.
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

# Añadir el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from rag_interface import RAGInterface, get_rag_interface, RAGResult, RAGStats
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False


class TestRAGInterface(unittest.TestCase):
    """Tests para la interfaz RAG."""

    def setUp(self):
        """Configuración inicial de los tests."""
        if not RAG_AVAILABLE:
            self.skipTest("RAG not available")

    def test_get_rag_interface(self):
        """Test que se puede obtener la instancia RAG."""
        interface = get_rag_interface()
        self.assertIsInstance(interface, RAGInterface)

    def test_rag_interface_initialization(self):
        """Test de inicialización de la interfaz RAG."""
        interface = RAGInterface()
        self.assertIsInstance(interface, RAGInterface)

    def test_is_available(self):
        """Test de disponibilidad del sistema RAG."""
        interface = get_rag_interface()
        # El test depende de si RAG está realmente disponible
        # Solo verificamos que el método exista
        self.assertIsInstance(interface.is_available(), bool)

    def test_get_stats(self):
        """Test de obtención de estadísticas."""
        interface = get_rag_interface()
        stats = interface.get_stats()
        self.assertIsInstance(stats, RAGStats)
        self.assertIsInstance(stats.total_documents, int)
        self.assertIsInstance(stats.embedder_type, str)
        self.assertIsInstance(stats.database_type, str)
        self.assertIsInstance(stats.database_path, str)
        self.assertIsInstance(stats.database_size_mb, float)
        self.assertIsInstance(stats.available, bool)

    def test_get_available_strategies(self):
        """Test de obtención de estrategias disponibles."""
        interface = get_rag_interface()
        strategies = interface.get_available_strategies()
        self.assertIsInstance(strategies, list)
        self.assertIn('caracteres', strategies)
        self.assertIn('palabras', strategies)
        self.assertIn('semantico', strategies)
        self.assertIn('agentic', strategies)

    def test_get_available_modes(self):
        """Test de obtención de modos disponibles."""
        interface = get_rag_interface()
        modes = interface.get_available_modes()
        self.assertIsInstance(modes, list)
        self.assertIn('vector', modes)
        self.assertIn('keyword', modes)
        self.assertIn('hybrid', modes)

    @patch('rag_interface.RAGInterface.is_available')
    def test_ingest_transcript_unavailable(self, mock_is_available):
        """Test de ingestión cuando RAG no está disponible."""
        mock_is_available.return_value = False
        interface = RAGInterface()

        result = interface.ingest_transcript(
            video_id="test_id",
            title="Test Video",
            transcript="This is a test transcript."
        )

        self.assertEqual(result['status'], 'error')
        self.assertIn('not available', result['message'])

    @patch('rag_interface.RAGInterface.is_available')
    def test_query_unavailable(self, mock_is_available):
        """Test de consulta cuando RAG no está disponible."""
        mock_is_available.return_value = False
        interface = RAGInterface()

        results, error = interface.query("test question")

        self.assertEqual(results, [])
        self.assertIn('not available', error)


class TestStreamlitIntegration(unittest.TestCase):
    """Tests para la integración con Streamlit."""

    def setUp(self):
        """Configuración inicial de los tests."""
        if not RAG_AVAILABLE:
            self.skipTest("RAG not available")

    @patch('streamlit.success')
    @patch('streamlit.warning')
    @patch('streamlit.error')
    @patch('streamlit.info')
    @patch('streamlit.button')
    @patch('streamlit.text_area')
    @patch('streamlit.radio')
    @patch('streamlit.checkbox')
    @patch('streamlit.spinner')
    def test_add_videos_page_integration(self, mock_spinner, mock_checkbox, mock_radio,
                                       mock_text_area, mock_button, mock_info,
                                       mock_error, mock_warning, mock_success):
        """Test de integración de la página agregar videos con RAG."""
        # Mock de Streamlit
        mock_text_area.return_value = "https://example.com/test\n"
        mock_radio.return_value = "Local"
        mock_checkbox.return_value = True
        mock_button.return_value = True
        mock_success.return_value = None
        mock_warning.return_value = None
        mock_error.return_value = None
        mock_info.return_value = None
        mock_spinner.return_value.__enter__ = Mock()
        mock_spinner.return_value.__exit__ = Mock()

        try:
            from gui_streamlit import StreamlitApp
            app = StreamlitApp()

            # Verificar que la aplicación tiene la interfaz RAG
            self.assertIsInstance(app.rag_interface, RAGInterface)

            # Verificar que la interfaz RAG está disponible
            self.assertTrue(app.rag_interface.is_available())

        except ImportError:
            self.skipTest("Streamlit GUI not available")

    @patch('streamlit.text_input')
    @patch('streamlit.selectbox')
    @patch('streamlit.slider')
    @patch('streamlit.button')
    @patch('streamlit.spinner')
    @patch('streamlit.success')
    @patch('streamlit.warning')
    @patch('streamlit.error')
    @patch('streamlit.expander')
    @patch('streamlit.metric')
    def test_rag_search_page_integration(self, mock_metric, mock_expander, mock_error,
                                       mock_warning, mock_success, mock_spinner,
                                       mock_button, mock_slider, mock_selectbox,
                                       mock_text_input):
        """Test de integración de la página de búsqueda RAG."""
        # Mock de Streamlit
        mock_text_input.return_value = "¿Qué es el machine learning?"
        mock_selectbox.return_value = "hybrid"
        mock_slider.return_value = 5
        mock_button.return_value = True
        mock_success.return_value = None
        mock_warning.return_value = None
        mock_error.return_value = None
        mock_spinner.return_value.__enter__ = Mock()
        mock_spinner.return_value.__exit__ = Mock()
        mock_expander.return_value.__enter__ = Mock()
        mock_expander.return_value.__exit__ = Mock()
        mock_metric.return_value = None

        try:
            from gui_streamlit import StreamlitApp
            app = StreamlitApp()

            # Verificar que la página de búsqueda RAG exista
            self.assertTrue(hasattr(app, 'display_rag_search_page'))

            # Llamar al método de la página
            app.display_rag_search_page()

        except ImportError:
            self.skipTest("Streamlit GUI not available")


class TestRAGStreamlitWorkflow(unittest.TestCase):
    """Tests para el flujo completo RAG + Streamlit."""

    def setUp(self):
        """Configuración inicial de los tests."""
        if not RAG_AVAILABLE:
            self.skipTest("RAG not available")

    def test_complete_workflow_mock(self):
        """Test del flujo completo usando mocks."""
        try:
            from gui_streamlit import StreamlitApp, YouTubeProcessor, DatabaseManager
            from rag_interface import get_rag_interface

            # Mock de componentes
            with patch.object(DatabaseManager, 'get_video_by_url') as mock_get_video, \
                 patch('rag_interface.download_vtt') as mock_download, \
                 patch('rag_interface.vtt_to_plain_text') as mock_vtt_to_text, \
                 patch('rag_interface.format_transcription') as mock_format:

                # Configurar mocks
                mock_get_video.return_value = None  # Video no existe
                mock_download.return_value = ("vtt_content", None, {
                    'title': 'Test Video',
                    'channel': 'Test Channel',
                    'upload_date': '2023-01-01'
                })
                mock_vtt_to_text.return_value = "This is a test transcript."
                mock_format.return_value = "Formatted transcript"

                # Crear componentes
                db_manager = DatabaseManager()
                yt_processor = YouTubeProcessor(db_manager)
                rag_interface = get_rag_interface()

                # Verificar que los componentes estén integrados
                self.assertIsInstance(yt_processor.rag_interface, RAGInterface)

                # Test de ingestión
                if rag_interface.is_available():
                    result = rag_interface.ingest_transcript(
                        video_id="test_id",
                        title="Test Video",
                        transcript="This is a test transcript."
                    )
                    self.assertIn('status', result)

                # Test de consulta
                if rag_interface.is_available():
                    results, error = rag_interface.query("test question")
                    self.assertIsInstance(results, list)
                    # error puede ser None o un string, ambos son válidos

        except ImportError as e:
            self.skipTest(f"GUI components not available: {e}")


def run_integration_tests():
    """Ejecutar todos los tests de integración."""
    print("🧪 Ejecutando tests de integración RAG + Streamlit...")
    print("=" * 60)

    # Crear suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Agregar tests
    suite.addTests(loader.loadTestsFromTestCase(TestRAGInterface))
    suite.addTests(loader.loadTestsFromTestCase(TestStreamlitIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestRAGStreamlitWorkflow))

    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ Todos los tests de integración pasaron correctamente")
        return 0
    else:
        print(f"❌ {len(result.failures)} tests fallaron, {len(result.errors)} errores")
        return 1


if __name__ == "__main__":
    exit_code = run_integration_tests()
    sys.exit(exit_code)
import unittest
from unittest.mock import patch, MagicMock, call
import os
import sys

# Añadir el directorio raíz al path para poder importar desde 'ia'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Importar el módulo a probar
from ia.gemini_api import summarize_text_gemini, configure_gemini

# Necesitamos importar el módulo de excepciones de google para simular el error
from google.api_core import exceptions as google_exceptions

class TestGeminiApi(unittest.TestCase):

    def setUp(self):
        """Configuración inicial para cada test."""
        self.sample_text = "This is a sample text to be summarized."
        self.sample_prompt = "Summarize this: {text}"
        self.api_key = "test-api-key"

    @patch('ia.gemini_api.genai')
    def test_summarize_text_gemini_success(self, mock_genai):
        """Prueba una llamada exitosa a summarize_text_gemini."""
        # Configurar el mock para simular la librería de Google
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        # Simular la respuesta de la API
        mock_response = MagicMock()
        mock_response.text = "This is the summary."
        mock_model.generate_content.return_value = mock_response

        # Simular el conteo de tokens
        mock_model.count_tokens.side_effect = [MagicMock(total_tokens=10), MagicMock(total_tokens=4)]

        # Llamar a la función
        result = summarize_text_gemini(
            text_content=self.sample_text,
            prompt_template=self.sample_prompt,
            model_name="gemini-2.0-flash-exp",
            api_key=self.api_key
        )

        # Verificaciones
        self.assertIsNone(result.get('error'))
        self.assertEqual(result['summary_text'], "This is the summary.")
        self.assertEqual(result['input_tokens'], 10)
        self.assertEqual(result['output_tokens'], 4)
        mock_genai.configure.assert_called_with(api_key=self.api_key)
        mock_model.generate_content.assert_called_once()

    @patch('ia.gemini_api.time.sleep', return_value=None) # Evitar esperas en el test
    @patch('ia.gemini_api.genai')
    def test_summarize_text_gemini_with_retry(self, mock_genai, mock_sleep):
        """Prueba el mecanismo de reintentos ante un error de cuota."""
        # Configurar el mock para que falle dos veces y tenga éxito a la tercera
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model

        # Simular el error de cuota
        quota_error = google_exceptions.ResourceExhausted("429 You exceeded your current quota.")
        
        # Simular la respuesta exitosa final
        mock_response = MagicMock()
        mock_response.text = "Successful summary after retries."

        # La función generate_content fallará dos veces y luego funcionará
        mock_model.generate_content.side_effect = [quota_error, quota_error, mock_response]

        # Simular conteo de tokens
        mock_model.count_tokens.side_effect = [MagicMock(total_tokens=10), MagicMock(total_tokens=5)]

        # Llamar a la función
        result = summarize_text_gemini(
            text_content=self.sample_text,
            prompt_template=self.sample_prompt,
            api_key=self.api_key
        )

        # Verificaciones
        self.assertIsNone(result.get('error'))
        self.assertEqual(result['summary_text'], "Successful summary after retries.")
        self.assertEqual(mock_model.generate_content.call_count, 3) # Verificar que se reintentó

    @patch.dict(os.environ, {"GEMINI_API_KEY": "env-api-key"})
    @patch('ia.gemini_api.genai')
    def test_configure_gemini_from_env(self, mock_genai):
        """Prueba que la configuración de Gemini usa la variable de entorno."""
        # Llamar a la función sin pasar una api_key explícita
        configure_gemini()
        # Verificar que se llamó a genai.configure con la clave del entorno
        mock_genai.configure.assert_called_with(api_key="env-api-key")

if __name__ == '__main__':
    unittest.main()

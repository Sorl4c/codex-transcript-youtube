import unittest
import os
from datetime import datetime

# Añadir el directorio raíz del proyecto al path para importar módulos
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db import init_db, insert_video, get_all_videos, filter_videos, get_video_by_id

class TestDatabase(unittest.TestCase):

    def setUp(self):
        """Crea una base de datos temporal y limpia para cada prueba."""
        self.db_name = 'test_temp_subtitles.db'
        # Asegurarse de que no exista un archivo de una ejecución anterior
        if os.path.exists(self.db_name):
            os.remove(self.db_name)
        init_db(self.db_name)

    def tearDown(self):
        """Elimina la base de datos temporal después de cada prueba."""
        if os.path.exists(self.db_name):
            os.remove(self.db_name)

    def test_insert_and_get_video(self):
        """Prueba la inserción y recuperación de un vídeo."""
        test_data = {
            'url': 'http://youtube.com/test1',
            'channel': 'Test Channel',
            'title': 'Test Video',
            'upload_date': datetime.now().strftime('%Y%m%d'),
            'transcript': 'This is a test transcript.',
            'summary': None, 'key_ideas': None, 'ai_categorization': None
        }
        insert_video(test_data, db_name=self.db_name)
        
        videos = get_all_videos(db_name=self.db_name)
        self.assertEqual(len(videos), 1)
        self.assertEqual(videos[0]['title'], 'Test Video')

    def test_filter_video_by_title(self):
        """Prueba el filtrado de vídeos por título."""
        # Insertar datos de prueba
        insert_video({
            'url': 'http://youtube.com/test2', 'channel': 'Another Channel',
            'title': 'Specific Title To Find', 'upload_date': '20230101',
            'transcript': 'Transcript 1', 'summary': None, 'key_ideas': None, 'ai_categorization': None
        }, db_name=self.db_name)
        insert_video({
            'url': 'http://youtube.com/test3', 'channel': 'Another Channel',
            'title': 'Another Video', 'upload_date': '20230102',
            'transcript': 'Transcript 2', 'summary': None, 'key_ideas': None, 'ai_categorization': None
        }, db_name=self.db_name)

        filtered = filter_videos('title', 'Specific', db_name=self.db_name)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['title'], 'Specific Title To Find')

    def test_duplicate_url_integrity(self):
        """Prueba que una URL duplicada no crea una nueva entrada."""
        test_data = {
            'url': 'http://youtube.com/duplicate',
            'channel': 'Original Channel', 'title': 'Original Title',
            'upload_date': '20230101', 'transcript': 'Original transcript.',
            'summary': None, 'key_ideas': None, 'ai_categorization': None
        }
        insert_video(test_data, db_name=self.db_name)  # Primera inserción
        insert_video(test_data, db_name=self.db_name)  # Segunda (debe ser ignorada)

        videos = get_all_videos(db_name=self.db_name)
        self.assertEqual(len(videos), 1)

    def test_get_video_by_id(self):
        """Prueba la recuperación de un vídeo por su ID."""
        test_data = {
            'url': 'http://youtube.com/test_id', 'channel': 'ID Channel',
            'title': 'ID Test', 'upload_date': '20230101',
            'transcript': 'ID transcript.', 'summary': None, 'key_ideas': None, 'ai_categorization': None
        }
        insert_video(test_data, db_name=self.db_name)
        
        # Obtener el ID del vídeo insertado
        video_id = get_all_videos(db_name=self.db_name)[0]['id']
        
        retrieved_video = get_video_by_id(video_id, db_name=self.db_name)
        self.assertIsNotNone(retrieved_video)
        self.assertEqual(retrieved_video['title'], 'ID Test')

if __name__ == '__main__':
    unittest.main()

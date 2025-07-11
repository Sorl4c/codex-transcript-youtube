import sqlite3
import os

# --- Configuración ---
DB_NAME = 'subtitles.db'

# --- Funciones de Conexión ---
def get_db_connection(db_name=DB_NAME):
    """Crea y devuelve una conexión a la base de datos SQLite.

    Configura la conexión para que devuelva las filas como diccionarios,
    permitiendo el acceso a las columnas por su nombre.

    Args:
        db_name (str): El nombre del archivo de la base de datos.

    Returns:
        sqlite3.Connection: Objeto de conexión a la base de datos.
    """
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conn

# --- Funciones de Inicialización ---
def init_db(db_name=DB_NAME):
    """Inicializa la base de datos.

    Crea la tabla 'videos' si no existe, definiendo el esquema para almacenar
    la información de los vídeos. Es seguro llamar a esta función varias veces.

    Args:
        db_name (str): El nombre del archivo de la base de datos.
    """
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            channel TEXT NOT NULL,
            title TEXT NOT NULL,
            upload_date TEXT NOT NULL,
            transcript TEXT,
            summary TEXT,
            key_ideas TEXT,
            ai_categorization TEXT
        );
    ''')
    conn.commit()
    conn.close()
    # No imprimir mensaje en tests para mantener la salida limpia
    if db_name == DB_NAME:
        print(f"[DB] Base de datos '{db_name}' verificada/inicializada.")

# --- Funciones CRUD ---
def insert_video(data: dict, db_name=DB_NAME):
    """Inserta un nuevo registro de vídeo en la base de datos.

    Utiliza un diccionario de datos para rellenar los campos. Si la URL del vídeo
    ya existe en la base de datos (debido a la restricción UNIQUE), la inserción
    falla silenciosamente para evitar duplicados.

    Args:
        data (dict): Un diccionario con los datos del vídeo.
        db_name (str): El nombre del archivo de la base de datos.
    """
    conn = get_db_connection(db_name)
    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO videos (url, channel, title, upload_date, transcript, summary, key_ideas, ai_categorization)
            VALUES (:url, :channel, :title, :upload_date, :transcript, :summary, :key_ideas, :ai_categorization)
        ''', data)
        conn.commit()
        if db_name == DB_NAME:
            print(f"[DB] Vídeo '{data.get('title')}' guardado.")
    except sqlite3.IntegrityError:
        if db_name == DB_NAME:
            print(f"[DB] La URL '{data.get('url')}' ya existe.")
    except Exception as e:
        print(f"[DB] Error al insertar vídeo: {e}")
    finally:
        conn.close()

def get_all_videos(db_name=DB_NAME, order_by='upload_date', order_dir='DESC'):
    """Recupera una lista de todos los vídeos de la base de datos.

    Permite la ordenación por una columna y dirección específicas. Incluye una
    lista blanca de columnas para prevenir inyecciones SQL.

    Args:
        db_name (str): Nombre del archivo de la base de datos.
        order_by (str): Columna por la que ordenar.
        order_dir (str): Dirección de ordenación ('ASC' o 'DESC').

    Returns:
        list: Una lista de diccionarios, donde cada diccionario es un vídeo.
    """
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    # Validar columnas para evitar inyección SQL
    allowed_columns = ['id', 'channel', 'title', 'upload_date']
    if order_by not in allowed_columns:
        order_by = 'upload_date' # Valor por defecto seguro

    if order_dir.upper() not in ['ASC', 'DESC']:
        order_dir = 'DESC' # Valor por defecto seguro

    query = f'SELECT id, channel, title, upload_date FROM videos ORDER BY {order_by} {order_dir}'
    cursor.execute(query)
    videos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return videos

def get_video_by_id(video_id: int, db_name=DB_NAME):
    """Recupera todos los datos de un único vídeo por su ID.

    Args:
        video_id (int): El ID del vídeo a recuperar.
        db_name (str): El nombre del archivo de la base de datos.

    Returns:
        dict or None: Un diccionario con los datos del vídeo, o None si no se encuentra.
    """
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM videos WHERE id = ?', (video_id,))
    video_row = cursor.fetchone()
    conn.close()
    return dict(video_row) if video_row else None

def get_video_by_url(url: str, db_name=DB_NAME):
    """Recupera un vídeo por su URL única.

    Args:
        url (str): La URL del vídeo a buscar.
        db_name (str): El nombre del archivo de la base de datos.

    Returns:
        dict or None: Un diccionario con los datos del vídeo, o None si no se encuentra.
    """
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM videos WHERE url = ?', (url,))
    video_row = cursor.fetchone()
    conn.close()
    return dict(video_row) if video_row else None

def filter_videos(by_field: str, value: str, db_name=DB_NAME, order_by='upload_date', order_dir='DESC'):
    """Filtra vídeos por un campo y valor específicos usando una búsqueda LIKE.

    Args:
        by_field (str): El campo por el que filtrar ('channel' o 'title').
        value (str): El valor a buscar dentro del campo.
        db_name (str): El nombre del archivo de la base de datos.
        order_by (str): Columna por la que ordenar los resultados.
        order_dir (str): Dirección de la ordenación.

    Returns:
        list: Una lista de diccionarios con los vídeos que coinciden.

    Raises:
        ValueError: Si se intenta filtrar por un campo no permitido.
    """
    if by_field not in ['channel', 'title']:
        raise ValueError("El campo de filtrado debe ser 'channel' o 'title'.")
    
    conn = get_db_connection(db_name)
    cursor = conn.cursor()

    # Validar columnas para evitar inyección SQL
    allowed_columns = ['id', 'channel', 'title', 'upload_date']
    if order_by not in allowed_columns:
        order_by = 'upload_date' # Valor por defecto seguro

    if order_dir.upper() not in ['ASC', 'DESC']:
        order_dir = 'DESC' # Valor por defecto seguro

    query = f'SELECT id, channel, title, upload_date FROM videos WHERE {by_field} LIKE ? ORDER BY {order_by} {order_dir}'
    cursor.execute(query, (f'%{value}%',))
    videos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return videos


def delete_video(video_id: int, db_name=DB_NAME) -> bool:
    """Elimina un vídeo de la base de datos por su ID.

    Args:
        video_id (int): ID del vídeo a eliminar.
        db_name (str): Nombre del archivo de la base de datos.

    Returns:
        bool: True si la eliminación fue exitosa, False en caso contrario.
    """
    """
    Elimina un vídeo de la base de datos por su ID.

    Args:
        video_id: ID del vídeo a eliminar.
        db_name: Nombre de la base de datos (opcional, para testing).

    Returns:
        bool: True si la eliminación fue exitosa, False en caso contrario.
    """
    conn = None
    try:
        conn = get_db_connection(db_name)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM videos WHERE id = ?', (video_id,))
        conn.commit()
        if cursor.rowcount > 0:
            if db_name == DB_NAME:
                print(f"[DB] Vídeo con ID {video_id} eliminado.")
            return True
        else:
            if db_name == DB_NAME:
                print(f"[DB] No se encontró vídeo con ID {video_id} para eliminar.")
            return False
    except sqlite3.Error as e:
        print(f"[DB] Error al eliminar el vídeo: {e}")
        return False
    finally:
        if conn:
            conn.close()


def update_video_summary(video_id: int, summary: str, db_name=DB_NAME) -> bool:
    """Actualiza el campo 'summary' de un vídeo existente.

    Args:
        video_id (int): ID del vídeo a actualizar.
        summary (str): El nuevo texto del resumen a guardar.
        db_name (str): Nombre del archivo de la base de datos.

    Returns:
        bool: True si la actualización fue exitosa, False en caso contrario.
    """
    """
    Actualiza el campo 'summary' de un vídeo existente.
    
    Args:
        video_id: ID del vídeo a actualizar
        summary: Texto del resumen a guardar
        db_name: Nombre de la base de datos (opcional, para testing)
        
    Returns:
        bool: True si la actualización fue exitosa, False en caso contrario
    """
    if not summary or not isinstance(summary, str):
        print("[DB] Error: El resumen proporcionado no es válido.")
        return False
        
    conn = None
    try:
        conn = get_db_connection(db_name)
        cursor = conn.cursor()
        
        # Verificar si el video existe
        cursor.execute('SELECT id FROM videos WHERE id = ?', (video_id,))
        if not cursor.fetchone():
            print(f"[DB] Error: No se encontró un vídeo con ID {video_id}")
            return False
            
        # Actualizar el resumen
        cursor.execute(
            'UPDATE videos SET summary = ? WHERE id = ?',
            (summary, video_id)
        )
        conn.commit()
        
        if cursor.rowcount > 0:
            if db_name == DB_NAME:
                print(f"[DB] Resumen actualizado para el vídeo ID {video_id}")
            return True
        return False
        
    except sqlite3.Error as e:
        print(f"[DB] Error al actualizar el resumen: {e}")
        return False
    finally:
        if conn:
            conn.close()


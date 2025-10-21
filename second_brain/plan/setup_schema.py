#!/usr/bin/env python3
"""
Script para crear schema PostgreSQL con dimensión paramétrica - Adaptado para Docker
"""
import os
import psycopg
from psycopg_pool import ConnectionPool

def create_schema_with_dimension():
    """Crear schema con dimensión configurada desde variables de entorno (Docker version)"""

    # Leer configuración desde .env.rag
    env_file = '.env.rag'
    config = {}

    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value.strip()

    # Configuración de conexión (Docker)
    embedding_dim = int(config.get('EMBEDDING_DIM', '384'))
    db_name = config.get('POSTGRES_DB', 'rag_experiments')

    print(f"🔧 Creando schema para PostgreSQL: {db_name} (Docker)")
    print(f"📏 Dimensión de embeddings: {embedding_dim}")
    print(f"🔗 Host: {config.get('POSTGRES_HOST', 'localhost')}")
    print(f"👤 Usuario: {config.get('POSTGRES_USER', 'rag_user')}")

    # Leer y modificar schema SQL
    script_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(script_dir, 'setup_schema.sql')

    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    # Reemplazar dimensión fija con variable
    schema_sql = schema_sql.replace('vector(384)', f'vector({embedding_dim})')

    # Construir connection string para Docker
    conn_string = (
        f"host={config.get('POSTGRES_HOST', 'localhost')} "
        f"port={config.get('POSTGRES_PORT', '5432')} "
        f"dbname={db_name} "
        f"user={config.get('POSTGRES_USER', 'rag_user')} "
        f"password={config.get('POSTGRES_PASSWORD', '')}"
    )

    print(f"🔌 Conectando a PostgreSQL (Docker)...")

    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute(schema_sql)
            conn.commit()

        print(f"✅ Schema creado exitosamente con dimensión {embedding_dim}")

        # Verificar tablas creadas
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT table_name, column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name IN ('documents', 'document_embeddings')
                    ORDER BY table_name, ordinal_position
                """)
                results = cur.fetchall()

                print(f"📊 Tablas y columnas creadas:")
                current_table = ""
                for table, column, dtype in results:
                    if table != current_table:
                        print(f"   📋 {table}:")
                        current_table = table
                    print(f"      - {column}: {dtype}")

    except Exception as e:
        print(f"❌ Error creando schema: {e}")
        print("💡 Verifica que:")
        print("   - Docker está corriendo (docker ps | grep postgres)")
        print("   - Las credenciales en .env.rag son correctas")
        print("   - La base de datos rag_experiments existe")
        raise

if __name__ == "__main__":
    create_schema_with_dimension()
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def get_db():
    """Crea y devuelve una conexión a la base de datos RDS"""
    try:
        connection = pymysql.connect(
            host=os.getenv("DATABASE_URL", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "test"),
            port=int(os.getenv("DB_PORT", "3306")),
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"Error conectando a RDS: {e}")
        raise
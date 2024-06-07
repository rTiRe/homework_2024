from dotenv import load_dotenv
from os import getenv

load_dotenv()

pg_fields = ['POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB']

HOST, PORT, USER, PASSWORD, DBNAME = [getenv(param) for param in pg_fields]
PORT = int(PORT) if PORT and PORT.isdigit() else None
host = HOST if getenv('DEBUG_MODE') == 'false' else 'localhost'

FLASK_PORT = getenv('FLASK_PORT')
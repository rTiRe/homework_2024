from dotenv import load_dotenv
from os import getenv

load_dotenv()

pg_fields = ['POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB']

HOST, PORT, USER, PASSWORD, DBNAME = [getenv(param) for param in pg_fields]
PORT = int(PORT) if PORT and PORT.isdigit() else None
host = HOST if getenv('DEBUG_MODE') == 'false' else 'localhost'

APP_HOST = getenv('APP_HOST') if getenv('APP_HOST') else '127.0.0.1'
try:
    APP_PORT = int(getenv('APP_PORT')) if getenv('APP_PORT') else 8000
except ValueError:
    APP_PORT = 8000
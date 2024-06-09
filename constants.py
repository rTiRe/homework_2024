from dotenv import load_dotenv
from os import getenv

load_dotenv()

pg_fields = ['POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB']
smtp_fields = ['SMTP_HOST', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD']

HOST, PORT, USER, PASSWORD, DBNAME = [getenv(param) for param in pg_fields]
PORT = int(PORT) if PORT and PORT.isdigit() else None
HOST = HOST if getenv('DEBUG_MODE') == 'false' else 'localhost'

SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD = [getenv(param) for param in smtp_fields]
SMTP_PORT = int(SMTP_PORT) if SMTP_PORT and SMTP_PORT.isdigit() else 587

APP_HOST = getenv('APP_HOST', '127.0.0.1')
APP_PORT = getenv('APP_PORT')
try:
    APP_PORT = int(APP_PORT) if APP_PORT and APP_PORT.isdigit() else 8000
except ValueError:
    APP_PORT = 8000
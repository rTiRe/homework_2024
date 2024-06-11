"""Module with the eviroment constants."""

from os import getenv

from dotenv import load_dotenv

DEFAULT_SMTP_PORT = 587
DEFAULT_APP_PORT = 8000

load_dotenv()

pg_fields = ['POSTGRES_HOST', 'POSTGRES_PORT', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_DB']
smtp_fields = ['SMTP_HOST', 'SMTP_PORT', 'SMTP_USERNAME', 'SMTP_PASSWORD']

postgres_fields = [getenv(field) for field in pg_fields]
DBNAME = postgres_fields.pop(-1)
HOST, PORT, USER, PASSWORD, = postgres_fields
PORT = int(PORT) if PORT and PORT.isdigit() else None
HOST = HOST if getenv('DEBUG_MODE') == 'false' else 'localhost'

SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD = [getenv(field) for field in smtp_fields]
SMTP_PORT = int(SMTP_PORT) if SMTP_PORT and SMTP_PORT.isdigit() else DEFAULT_SMTP_PORT

APP_HOST = getenv('APP_HOST', '127.0.0.1')
APP_PORT = getenv('APP_PORT')
try:
    APP_PORT = int(APP_PORT) if APP_PORT and APP_PORT.isdigit() else DEFAULT_APP_PORT
except ValueError:
    APP_PORT = DEFAULT_APP_PORT

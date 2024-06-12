FROM python:3.10.13

WORKDIR /crypto_homework

COPY api/ /crypto_homework/api
COPY api_models/ /crypto_homework/api_models
COPY templates/ /crypto_homework/templates
COPY utils/ /crypto_homework/utils
COPY alembic/ /crypto_homework/alembic
COPY main.py .
COPY models.py .
COPY requirements.txt .
COPY alembic.ini .
COPY .env .

RUN pip install -r requirements.txt
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    NLTK_DATA=/usr/local/share/nltk_data

WORKDIR /app

# Installation editable : config.py calcule BASE_DIR depuis le chemin du package (models/, logs/)
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install -e .

# Lexique VADER embarque dans l'image (pas de telechargement au demarrage)
RUN python -c "import nltk; nltk.download('vader_lexicon')"

COPY models ./models
COPY backend ./backend

EXPOSE 8000

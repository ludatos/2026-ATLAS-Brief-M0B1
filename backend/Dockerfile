FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /usr/local/bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.cache/huggingface \
    NLTK_DATA=/usr/local/share/nltk_data

WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

# Installation editable : config.py calcule BASE_DIR depuis le chemin du package (models/, logs/)
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --locked --no-dev

# Lexique VADER embarque dans l'image (pas de telechargement au demarrage)
RUN python -c "import nltk; nltk.download('vader_lexicon')"

COPY models ./models
COPY backend ./backend

EXPOSE 8000

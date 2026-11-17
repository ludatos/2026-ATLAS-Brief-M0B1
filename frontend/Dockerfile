FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Le frontend n'a besoin que de streamlit et requests (il appelle le backend en HTTP)
RUN pip install "streamlit>=1.49,<2" requests

COPY frontend ./frontend

EXPOSE 8501

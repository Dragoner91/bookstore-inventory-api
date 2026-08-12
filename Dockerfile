FROM python:3.12-slim

# sin esto los logs quedan en el buffer y Render no los muestra
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# las dependencias antes que el codigo, para que el cambio de un .py no
# invalide la capa de pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# sh -c porque Render inyecta $PORT y la forma exec no expande variables
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

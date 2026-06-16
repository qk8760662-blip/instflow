FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi uvicorn httpx
COPY main.py .
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]

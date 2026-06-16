cat > /mnt/user-data/outputs/Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
EOF

cat > /mnt/user-data/outputs/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.2
pydantic==2.5.0
EOF

echo "Done"

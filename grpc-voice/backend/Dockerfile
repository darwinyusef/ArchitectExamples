FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Generar archivos proto
RUN python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./proto \
    --grpc_python_out=./proto \
    proto/audio_service.proto

# Crear directorio para archivos temporales
RUN mkdir -p temp_audio

# Exponer puertos
EXPOSE 8000 50051

# Comando para iniciar el servidor
CMD ["python", "main.py"]

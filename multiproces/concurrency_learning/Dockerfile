# Dockerfile para ejecutar las aplicaciones Python
# (Opcional - si quieres containerizar también las apps Python)

FROM python:3.11-slim

# Metadata
LABEL maintainer="Python Concurrency Learning"
LABEL description="Container for Python concurrency demos"

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    procps \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Exponer puertos para métricas
EXPOSE 8000 8001 8002 8003 8765

# Script de inicio por defecto
CMD ["python3", "advanced/race_conditions/01_race_conditions.py"]

# Dockerfile para Notebooks de ML/Data Engineering
FROM python:3.10-slim

# Metadata
LABEL maintainer="your-email@example.com"
LABEL description="Jupyter environment con Spark, DuckDB, PyTorch, TensorFlow, MLflow"

# Argumentos de build
ARG SPARK_VERSION=3.5.0
ARG HADOOP_VERSION=3

# Variables de entorno
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64 \
    SPARK_HOME=/opt/spark \
    PATH=$PATH:/opt/spark/bin:/opt/spark/sbin

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    openjdk-11-jdk \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Instalar Apache Spark
RUN wget -q https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    && tar -xzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    && mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark \
    && rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

# Crear directorio de trabajo
WORKDIR /workspace

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Configurar Jupyter
RUN jupyter notebook --generate-config && \
    echo "c.NotebookApp.ip = '0.0.0.0'" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.allow_root = True" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.open_browser = False" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.token = ''" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.password = ''" >> ~/.jupyter/jupyter_notebook_config.py

# Crear directorios para MLflow
RUN mkdir -p /workspace/mlruns /workspace/data

# Exponer puertos
# 8888: Jupyter
# 5000: MLflow UI
# 4040: Spark UI
EXPOSE 8888 5000 4040

# Comando por defecto
CMD ["jupyter", "notebook", "--port=8888", "--no-browser", "--allow-root"]

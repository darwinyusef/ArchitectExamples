# 🚀 Guía de Instalación - Notebooks ML/Data Engineering

Guía completa para configurar el entorno de desarrollo para los notebooks de Machine Learning y Data Engineering.

## 📋 Tabla de Contenidos

- [Opción 1: Docker (Recomendado)](#opción-1-docker-recomendado)
- [Opción 2: Instalación Local](#opción-2-instalación-local)
- [Configuración de GPU](#configuración-de-gpu)
- [Verificación de Instalación](#verificación-de-instalación)
- [Troubleshooting](#troubleshooting)

---

## 🐳 Opción 1: Docker (Recomendado)

### ✅ Ventajas de Docker

- ✅ Instalación rápida y consistente
- ✅ No contamina tu sistema con dependencias
- ✅ Incluye Spark, Java y todas las dependencias pre-configuradas
- ✅ Fácil de resetear o actualizar
- ✅ Incluye PostgreSQL para notebooks avanzados
- ✅ MLflow server pre-configurado

### 📦 Prerequisitos

1. **Docker Desktop** (incluye docker-compose)
   - **Windows**: [Docker Desktop para Windows](https://docs.docker.com/desktop/install/windows-install/)
   - **macOS**: [Docker Desktop para Mac](https://docs.docker.com/desktop/install/mac-install/)
   - **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)

2. **Verificar instalación**:
```bash
docker --version
docker-compose --version
```

### 🚀 Instalación con Docker

#### 1. Clonar o navegar al repositorio

```bash
cd /path/to/notebooks
```

#### 2. Construir y ejecutar contenedores

```bash
# Construir imágenes (primera vez o después de cambios)
docker-compose build

# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f jupyter
```

#### 3. Acceder a Jupyter

Abre tu navegador en: **http://localhost:8888**

#### 4. Servicios disponibles

| Servicio | URL | Descripción |
|----------|-----|-------------|
| Jupyter Notebook | http://localhost:8888 | Notebooks interactivos |
| MLflow UI | http://localhost:5000 | Tracking de experimentos (local) |
| MLflow Server | http://localhost:5001 | Server con PostgreSQL backend |
| Spark UI | http://localhost:4040 | UI de Spark (cuando hay jobs corriendo) |
| PostgreSQL | localhost:5432 | Base de datos (usuario: mluser, password: mlpassword) |

#### 5. Comandos útiles

```bash
# Detener contenedores
docker-compose down

# Detener y eliminar volúmenes (resetear todo)
docker-compose down -v

# Reconstruir después de cambios
docker-compose build --no-cache

# Ver contenedores corriendo
docker ps

# Acceder a shell del contenedor
docker exec -it ml-notebooks bash

# Ver logs de servicio específico
docker-compose logs -f postgres
```

#### 6. Trabajar con notebooks

Los notebooks en tu directorio local están montados en el contenedor:

```bash
# Tus notebooks locales
./01_spark_airflow_mlflow.ipynb

# Se reflejan automáticamente en
# /workspace/01_spark_airflow_mlflow.ipynb (dentro del contenedor)
```

**Cualquier cambio en notebooks se guarda automáticamente en tu máquina local.**

#### 7. Persistencia de datos

Los siguientes directorios persisten entre reinicios:

- `mlruns/`: Experimentos de MLflow
- `data/`: Datasets y archivos generados
- Datos de PostgreSQL

---

## 💻 Opción 2: Instalación Local

### ✅ Ventajas de Instalación Local

- ✅ Menor overhead (más rápido)
- ✅ Acceso directo al sistema de archivos
- ✅ Mejor para desarrollo intensivo

### 📦 Prerequisitos

#### 1. Python 3.10+

**Verificar versión:**
```bash
python3 --version
# Debe ser >= 3.10
```

**Instalar Python** (si es necesario):

- **macOS**:
```bash
brew install python@3.10
```

- **Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
```

- **Windows**: [Descargar Python](https://www.python.org/downloads/)

#### 2. Java 11+ (requerido para Spark)

**Verificar versión:**
```bash
java -version
# Debe ser >= 11
```

**Instalar Java**:

- **macOS**:
```bash
brew install openjdk@11
echo 'export JAVA_HOME=/usr/local/opt/openjdk@11' >> ~/.zshrc
```

- **Ubuntu/Debian**:
```bash
sudo apt install openjdk-11-jdk
echo 'export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64' >> ~/.bashrc
```

- **Windows**: [AdoptOpenJDK](https://adoptopenjdk.net/)

#### 3. PostgreSQL (opcional - solo para notebooks 06)

**macOS**:
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian**:
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows**: [PostgreSQL Installer](https://www.postgresql.org/download/windows/)

### 🚀 Instalación Local

#### 1. Crear entorno virtual

```bash
cd /path/to/notebooks

# Crear virtual environment
python3 -m venv venv

# Activar
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

#### 2. Actualizar pip

```bash
pip install --upgrade pip setuptools wheel
```

#### 3. Instalar dependencias

**Instalación básica (CPU):**
```bash
pip install -r requirements.txt
```

**Instalación con GPU (CUDA 11.8):**
```bash
# Instalar PyTorch con CUDA primero
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Luego el resto
pip install -r requirements.txt
```

**Instalación con GPU (CUDA 12.1):**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

#### 4. Instalar Apache Spark

**Opción A: Usar PySpark (más simple)**
```bash
# Ya incluido en requirements.txt
# No requiere instalación adicional
```

**Opción B: Instalación manual de Spark (para usuarios avanzados)**

**macOS/Linux:**
```bash
# Descargar Spark
wget https://archive.apache.org/dist/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz

# Extraer
tar -xzf spark-3.5.0-bin-hadoop3.tgz
sudo mv spark-3.5.0-bin-hadoop3 /opt/spark

# Configurar variables de entorno
echo 'export SPARK_HOME=/opt/spark' >> ~/.bashrc  # o ~/.zshrc
echo 'export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin' >> ~/.bashrc
source ~/.bashrc
```

**Windows:**
1. Descargar Spark desde [Apache Spark](https://spark.apache.org/downloads.html)
2. Extraer a `C:\spark`
3. Agregar `C:\spark\bin` al PATH del sistema

#### 5. Iniciar Jupyter

```bash
# Desde el directorio de notebooks
jupyter notebook

# O usar JupyterLab (interfaz moderna)
jupyter lab
```

Abre tu navegador en: **http://localhost:8888**

#### 6. Iniciar MLflow UI (opcional)

```bash
# En terminal separada
mlflow ui --port 5000
```

Abre: **http://localhost:5000**

---

## 🎮 Configuración de GPU

### NVIDIA GPU (CUDA)

#### 1. Verificar GPU

```bash
nvidia-smi
```

#### 2. Instalar CUDA Toolkit

**Descargar**: [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)

**Versiones recomendadas:**
- CUDA 11.8 (más compatible)
- CUDA 12.1 (más reciente)

#### 3. Instalar cuDNN

**Descargar**: [NVIDIA cuDNN](https://developer.nvidia.com/cudnn)

#### 4. Instalar PyTorch con CUDA

**CUDA 11.8:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**CUDA 12.1:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### 5. Verificar GPU en PyTorch

```python
import torch
print(f"CUDA disponible: {torch.cuda.is_available()}")
print(f"Dispositivo: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
```

### Apple Silicon (M1/M2/M3)

PyTorch con aceleración MPS (Metal Performance Shaders):

```bash
pip install torch torchvision torchaudio
```

**Verificar:**
```python
import torch
print(f"MPS disponible: {torch.backends.mps.is_available()}")
```

**Usar en notebooks:**
```python
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
```

---

## ✅ Verificación de Instalación

### Script de verificación

Crea `verify_setup.py`:

```python
#!/usr/bin/env python3
"""Verificar instalación de dependencias"""

import sys

def check_package(package_name, import_name=None):
    import_name = import_name or package_name
    try:
        __import__(import_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name}")
        return False

print("🔍 Verificando instalación...\n")

packages = {
    "NumPy": "numpy",
    "Pandas": "pandas",
    "PyArrow": "pyarrow",
    "PySpark": "pyspark",
    "DuckDB": "duckdb",
    "PyTorch": "torch",
    "TensorFlow": "tensorflow",
    "Scikit-learn": "sklearn",
    "MLflow": "mlflow",
    "ONNX": "onnx",
    "ONNX Runtime": "onnxruntime",
    "Prophet": "prophet",
    "SciPy": "scipy",
    "Matplotlib": "matplotlib",
    "Seaborn": "seaborn",
    "Plotly": "plotly",
    "LangChain": "langchain",
    "LangGraph": "langgraph",
    "Jupyter": "jupyter",
}

results = []
for name, import_name in packages.items():
    results.append(check_package(name, import_name))

print(f"\n📊 Resultado: {sum(results)}/{len(results)} paquetes instalados")

# Verificar GPU
print("\n🎮 GPU:")
try:
    import torch
    if torch.cuda.is_available():
        print(f"✅ CUDA: {torch.cuda.get_device_name(0)}")
    elif torch.backends.mps.is_available():
        print(f"✅ MPS (Apple Silicon)")
    else:
        print(f"⚠️  Solo CPU disponible")
except:
    print("❌ No se pudo verificar GPU")

# Verificar Spark
print("\n⚡ Spark:")
try:
    from pyspark.sql import SparkSession
    spark = SparkSession.builder.appName("test").getOrCreate()
    print(f"✅ Spark {spark.version}")
    spark.stop()
except Exception as e:
    print(f"❌ Error: {e}")

sys.exit(0 if all(results) else 1)
```

**Ejecutar:**
```bash
python verify_setup.py
```

---

## 🔧 Troubleshooting

### Problema: Java no encontrado

**Síntomas:**
```
JAVA_HOME is not set
```

**Solución:**
```bash
# Encontrar Java
/usr/libexec/java_home -V  # macOS
which java  # Linux

# Configurar JAVA_HOME
export JAVA_HOME=/path/to/java
```

### Problema: Spark no inicia

**Síntomas:**
```
Error: Could not find or load main class org.apache.spark.deploy.SparkSubmit
```

**Solución:**
```bash
# Verificar SPARK_HOME
echo $SPARK_HOME

# Configurar
export SPARK_HOME=/opt/spark
export PATH=$PATH:$SPARK_HOME/bin
```

### Problema: MLflow no encuentra experimentos

**Síntomas:**
```
No experiment found
```

**Solución:**
```python
# En notebook, configurar tracking URI
import mlflow
mlflow.set_tracking_uri("./mlruns")
```

### Problema: Prophet falla en instalación

**Síntomas:**
```
ERROR: Failed building wheel for prophet
```

**Solución (macOS):**
```bash
brew install cmake
pip install pystan==2.19.1.1
pip install prophet
```

**Solución (Ubuntu):**
```bash
sudo apt install build-essential
pip install prophet
```

### Problema: TensorFlow GPU no detecta GPU

**Síntomas:**
```python
tf.config.list_physical_devices('GPU')  # []
```

**Solución:**
```bash
# Verificar CUDA
nvidia-smi

# Reinstalar TensorFlow
pip uninstall tensorflow
pip install tensorflow[and-cuda]
```

### Problema: Docker no puede montar volúmenes

**Síntomas:**
```
Error response from daemon: error while creating mount source path
```

**Solución:**
- **Windows/Mac**: Verificar que Docker Desktop tiene acceso al directorio en Settings → Resources → File Sharing
- Reiniciar Docker Desktop

### Problema: Puerto 8888 ya en uso

**Síntomas:**
```
Port 8888 is already in use
```

**Solución:**
```bash
# Opción 1: Cambiar puerto
jupyter notebook --port 8889

# Opción 2: Matar proceso
lsof -i :8888  # ver PID
kill -9 <PID>

# Docker:
# Editar docker-compose.yml: "8889:8888"
```

---

## 📚 Recursos Adicionales

### Documentación Oficial

- [Apache Spark](https://spark.apache.org/docs/latest/)
- [DuckDB](https://duckdb.org/docs/)
- [PyTorch](https://pytorch.org/docs/)
- [TensorFlow](https://www.tensorflow.org/guide)
- [MLflow](https://mlflow.org/docs/latest/index.html)
- [ONNX](https://onnx.ai/onnx/)

### Tutoriales

- [Spark by Examples](https://sparkbyexamples.com/)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)
- [MLflow Tutorial](https://mlflow.org/docs/latest/tutorials-and-examples/index.html)

---

## 🆘 Soporte

Si encuentras problemas:

1. **Revisar logs**:
   ```bash
   # Docker
   docker-compose logs jupyter

   # Jupyter local
   # Ver terminal donde iniciaste jupyter notebook
   ```

2. **Verificar versiones**:
   ```bash
   python --version
   java -version
   docker --version
   ```

3. **Reinstalar desde cero**:
   ```bash
   # Docker
   docker-compose down -v
   docker-compose build --no-cache
   docker-compose up -d

   # Local
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Abrir issue en GitHub** con:
   - Sistema operativo
   - Versiones de Python, Java, Docker
   - Comando que genera error
   - Logs completos

---

## ✨ Siguiente Paso

Una vez instalado, comienza con:

### Para Principiantes:
```
09_mlflow_basico.ipynb
```

### Para Usuarios con Experiencia:
```
01_spark_airflow_mlflow.ipynb
```

### Para Experimentar con RNN:
```
18_duckdb_rnn_timeseries.ipynb
```

---

**¡Feliz aprendizaje! 🚀📊🤖**

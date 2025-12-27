# 🚀 Inicio Rápido - 3 Proyectos MCP

Guía rápida para poner en marcha cada proyecto en menos de 5 minutos.

---

## Prerequisitos Globales

```bash
# Verificar instalaciones
python --version    # Python 3.11+
docker --version    # Docker
docker-compose --version
```

---

## 1️⃣ PostgreSQL MCP (2 minutos)

### Paso 1: Navegar al proyecto
```bash
cd mcp-postgresql
```

### Paso 2: Iniciar PostgreSQL
```bash
docker-compose up -d
```

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Iniciar servidor MCP
```bash
python server.py
```

### ✅ Verificar que funciona
```bash
# En otra terminal
curl http://localhost:5432  # PostgreSQL corriendo

# O verificar con psql
docker exec -it mcp-postgres psql -U postgres -c "SELECT * FROM users;"
```

### 🎯 Probar con LLM
Pregunta al LLM:
- "¿Cuántos usuarios hay en la base de datos?"
- "Muéstrame todos los productos"
- "Inserta un usuario con email test@example.com"

---

## 2️⃣ ML Pipeline MCP (5 minutos)

### Paso 1: Navegar al proyecto
```bash
cd mcp-ml-pipeline
```

### Paso 2: Crear directorios necesarios
```bash
mkdir -p airflow/dags airflow/logs airflow/plugins
chmod +x init-db.sh
```

### Paso 3: Iniciar todos los servicios
```bash
docker-compose up -d
```

### Paso 4: Esperar inicialización (IMPORTANTE)
```bash
# Los servicios toman 2-3 minutos en inicializar
echo "Esperando 2 minutos..."
sleep 120

# Verificar que Airflow está listo
docker-compose logs airflow-webserver | grep "Listening at"
```

### Paso 5: Instalar dependencias Python
```bash
pip install -r requirements.txt
```

### Paso 6: Iniciar servidor MCP
```bash
python server.py
```

### ✅ Verificar que funciona
```bash
# Airflow Web UI
open http://localhost:8080
# Usuario: airflow / Contraseña: airflow

# MLflow UI
open http://localhost:5000

# Spark Master UI
open http://localhost:8081
```

### 🎯 Probar con LLM
Pregunta al LLM:
- "Lista todos los experimentos de MLflow"
- "Lista los DAGs disponibles en Airflow"
- "Dispara el DAG ml_pipeline"

---

## 3️⃣ RAG LangGraph MCP (1 minuto)

### Paso 1: Navegar al proyecto
```bash
cd mcp-rag-langchain
```

### Paso 2: Configurar OpenAI API Key
```bash
cp .env.example .env

# EDITAR .env y agregar tu API key
# nano .env  o  vim .env  o tu editor favorito
```

`.env`:
```bash
OPENAI_API_KEY=sk-tu-api-key-aqui-desde-platform.openai.com
OPENAI_MODEL=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-small
```

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Iniciar servidor MCP
```bash
python server.py
```

### ✅ Verificar que funciona
El servidor debe iniciar sin errores y mostrar:
```
MCP Server 'RAG-LangGraph' running
```

### 🎯 Probar con LLM
Pregunta al LLM:
- "Carga los documentos de la carpeta ./documents"
- "¿Qué es FastMCP según los documentos?"
- "Usa razonamiento multi-paso para explicar cómo funciona RAG"

---

## 🐛 Troubleshooting Rápido

### PostgreSQL

**Error: Puerto 5432 ocupado**
```bash
# Editar docker-compose.yml, cambiar puerto
ports:
  - "5433:5432"

# Editar .env
POSTGRES_PORT=5433
```

**Error: No conecta a la BD**
```bash
# Verificar que el contenedor está corriendo
docker ps | grep postgres

# Ver logs
docker-compose logs postgres

# Reiniciar
docker-compose restart postgres
```

### ML Pipeline

**Error: Servicios no inician**
```bash
# Ver logs de todos los servicios
docker-compose logs

# Verificar RAM disponible (necesitas 8GB)
docker stats

# Reiniciar todo
docker-compose down
docker-compose up -d
```

**Error: Airflow no responde**
```bash
# Esperar más tiempo (puede tomar hasta 5 min la primera vez)
sleep 180

# O ver progreso
docker-compose logs -f airflow-webserver
```

**Error: Puerto 8080 ocupado**
```bash
# Editar docker-compose.yml
# Cambiar puerto de Airflow
ports:
  - "8081:8080"  # Usar 8081 en lugar de 8080
```

### RAG LangGraph

**Error: "OPENAI_API_KEY no está configurada"**
```bash
# Verificar que .env existe
cat .env

# Verificar que la variable está cargada
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"

# O exportar manualmente
export OPENAI_API_KEY=sk-...
python server.py
```

**Error: Rate limit de OpenAI**
```bash
# Esperar 60 segundos
# O cambiar a modelo más barato en .env
OPENAI_MODEL=gpt-3.5-turbo
```

**Error: ChromaDB no funciona**
```bash
# Eliminar y recrear
rm -rf chroma_db/
python server.py
# Volver a cargar documentos
```

---

## 📊 Checklist de Verificación

### PostgreSQL ✓
- [ ] Docker compose corriendo
- [ ] Contenedor `mcp-postgres` activo
- [ ] Puerto 5432 escuchando
- [ ] Servidor MCP iniciado sin errores
- [ ] Tablas de ejemplo cargadas

### ML Pipeline ✓
- [ ] 5 contenedores corriendo (postgres, mlflow, airflow-web, airflow-scheduler, spark-master, spark-worker)
- [ ] Airflow UI accesible (http://localhost:8080)
- [ ] MLflow UI accesible (http://localhost:5000)
- [ ] Spark UI accesible (http://localhost:8081)
- [ ] Servidor MCP iniciado sin errores
- [ ] DAG `ml_pipeline` visible en Airflow

### RAG LangGraph ✓
- [ ] OPENAI_API_KEY configurada en .env
- [ ] Dependencias instaladas (langgraph, langchain-openai, etc.)
- [ ] Servidor MCP iniciado sin errores
- [ ] Carpeta documents/ con example.txt
- [ ] Puede crear embeddings con OpenAI

---

## 🎮 Comandos de Un Solo Paso

### PostgreSQL - Setup Completo
```bash
cd mcp-postgresql && \
docker-compose up -d && \
pip install -r requirements.txt && \
python server.py
```

### ML Pipeline - Setup Completo
```bash
cd mcp-ml-pipeline && \
mkdir -p airflow/dags airflow/logs airflow/plugins && \
chmod +x init-db.sh && \
docker-compose up -d && \
echo "⏳ Esperando inicialización (2 min)..." && \
sleep 120 && \
pip install -r requirements.txt && \
python server.py
```

### RAG - Setup Completo (requiere editar .env manualmente)
```bash
cd mcp-rag-langchain && \
cp .env.example .env && \
echo "⚠️  EDITA .env con tu OPENAI_API_KEY antes de continuar" && \
read -p "Presiona Enter cuando hayas editado .env..." && \
pip install -r requirements.txt && \
python server.py
```

---

## 📱 Accesos Rápidos (URLs)

### PostgreSQL
- Base de datos: `localhost:5432`
- Usuario: `postgres`
- Password: `postgres`

### ML Pipeline
- 🌐 Airflow: http://localhost:8080 (airflow/airflow)
- 📊 MLflow: http://localhost:5000
- ⚡ Spark Master: http://localhost:8081
- 🗄️ PostgreSQL: `localhost:5433` (airflow/airflow)

### RAG LangGraph
- ☁️ OpenAI: https://platform.openai.com/
- 📝 Documentos: `./documents/`
- 💾 ChromaDB: `./chroma_db/` (generado automáticamente)

---

## 🎯 Primeros Pasos Recomendados

### 1. PostgreSQL (Empezar aquí - más fácil)
```
1. Iniciar servidor
2. Pregunta: "¿Qué tablas hay?"
3. Pregunta: "Muéstrame todos los usuarios"
4. Pregunta: "Inserta un producto llamado 'Tablet' con precio 299.99"
```

### 2. RAG LangGraph (Siguiente - intermedio)
```
1. Configurar OPENAI_API_KEY
2. Iniciar servidor
3. Pregunta: "Carga los documentos de ./documents"
4. Pregunta: "¿Qué es un sistema RAG?"
5. Pregunta: "Explica paso a paso las ventajas de RAG"
```

### 3. ML Pipeline (Último - más complejo)
```
1. Iniciar todos los servicios (esperar 2-3 min)
2. Verificar UIs (Airflow, MLflow, Spark)
3. Pregunta: "Lista los experimentos de MLflow"
4. Pregunta: "Lista los DAGs de Airflow"
5. Pregunta: "Dispara el DAG ml_pipeline"
```

---

## 💡 Tips Finales

### Optimización de Recursos
```bash
# Si tienes poca RAM, inicia solo uno a la vez

# Detener PostgreSQL
cd mcp-postgresql && docker-compose down

# Detener ML Pipeline (libera ~6GB RAM)
cd mcp-ml-pipeline && docker-compose down

# RAG no usa Docker, no consume recursos
```

### Persistencia de Datos
```bash
# PostgreSQL - datos en volumen 'postgres_data'
# ML Pipeline - datos en volúmenes 'postgres_data', 'mlflow_data', 'airflow_data', 'spark_data'
# RAG - datos en 'chroma_db/' (local)

# Para limpiar TODO
docker-compose down -v  # ⚠️ Elimina datos
```

### Logs y Debugging
```bash
# Ver logs de un servicio
docker-compose logs -f <servicio>

# Ejemplos:
docker-compose logs -f postgres
docker-compose logs -f airflow-webserver
docker-compose logs -f mlflow
```

---

**¡Todo listo! Selecciona un proyecto y comienza a experimentar con MCP** 🚀

Para más detalles, consulta el README de cada proyecto.

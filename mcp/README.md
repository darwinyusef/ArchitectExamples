# Proyectos MCP - Model Context Protocol

Colección de 3 servidores MCP profesionales usando FastMCP, cada uno enfocado en diferentes casos de uso empresariales.

## 📋 Proyectos

### 1. 🗄️ MCP PostgreSQL con Cliente LLM
**Carpeta**: `mcp-postgresql/`

Servidor MCP que permite a un LLM interactuar completamente con PostgreSQL mediante lenguaje natural.

**Características**:
- Ejecutar queries SQL personalizadas
- Obtener esquemas de bases de datos
- Operaciones CRUD completas
- Listar tablas con metadatos
- Prevención de SQL injection
- Docker Compose incluido

**Stack**:
- FastMCP
- PostgreSQL 16
- psycopg2
- Docker

**Iniciar**:
```bash
cd mcp-postgresql
docker-compose up -d
pip install -r requirements.txt
python server.py
```

**Uso con LLM**:
```
"¿Cuántos usuarios hay en la base de datos?"
"Muéstrame todos los productos con precio mayor a 100"
"Inserta un nuevo usuario con email test@example.com"
```

---

### 2. 🤖 MCP ML Pipeline (Spark + MLflow + Airflow)
**Carpeta**: `mcp-ml-pipeline/`

Pipeline completo de Machine Learning con procesamiento distribuido, tracking de experimentos y orquestación, todo controlado por LLM.

**Características**:
- Entrenamiento de modelos con Spark MLlib
- Tracking de experimentos con MLflow
- Comparación y versionado de modelos
- Orquestación de pipelines con Airflow
- Monitoreo en tiempo real vía WebSockets
- Procesamiento distribuido de datos

**Stack**:
- FastMCP
- Apache Spark 3.5
- MLflow 2.10
- Apache Airflow 2.8
- PostgreSQL (backend)
- Docker Compose

**Iniciar**:
```bash
cd mcp-ml-pipeline
mkdir -p airflow/dags airflow/logs airflow/plugins
chmod +x init-db.sh
docker-compose up -d
pip install -r requirements.txt
python server.py
```

**Servicios**:
- Airflow: http://localhost:8080 (user: airflow / pass: airflow)
- MLflow: http://localhost:5000
- Spark Master: http://localhost:8081

**Uso con LLM**:
```
"Entrena un modelo con los datos en /data/sales.csv"
"Compara todos los modelos del experimento 'ventas' por RMSE"
"Dispara el pipeline de ML y monitorea el progreso"
"¿Cuál es el mejor modelo basado en R²?"
```

---

### 3. 📚 MCP RAG con LangGraph y OpenAI
**Carpeta**: `mcp-rag-langchain/`

Sistema RAG profesional usando **LangGraph** para orquestar flujos con grafos de estado y **OpenAI** para embeddings y generación.

**Características**:
- RAG con arquitectura de grafos (LangGraph)
- Embeddings con OpenAI (text-embedding-3-small)
- LLM con GPT-4 Turbo
- Razonamiento multi-paso
- Historial de conversación
- Vector store con ChromaDB
- Soporte para TXT, PDF, Markdown
- Búsqueda semántica avanzada

**Stack**:
- FastMCP
- LangGraph
- LangChain
- OpenAI (GPT-4)
- ChromaDB

**Iniciar**:
```bash
cd mcp-rag-langchain
cp .env.example .env
# Editar .env y agregar OPENAI_API_KEY
pip install -r requirements.txt
python server.py
```

**Grafo RAG**:
```
Retrieve → Prepare Context → Generate Answer
(con estado compartido entre nodos)
```

**Uso con LLM**:
```
"Carga los documentos de la carpeta ./docs"
"¿Qué es LangGraph y cómo funciona?"
"Explícame paso a paso cómo usar razonamiento multi-paso"
"Compara las ventajas de A vs B" (usa multi_step_reasoning)
```

---

## 🚀 Inicio Rápido Global

### Requisitos previos

- Python 3.11+
- Docker y Docker Compose
- 8GB RAM mínimo (16GB recomendado para ML Pipeline)
- 20GB espacio en disco

### Instalación base

```bash
# Clonar o descargar el proyecto
cd mcp

# Cada proyecto tiene su propio requirements.txt
# Recomendado: usar entornos virtuales separados

# Proyecto 1: PostgreSQL
cd mcp-postgresql
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# Proyecto 2: ML Pipeline
cd ../mcp-ml-pipeline
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Proyecto 3: RAG
cd ../mcp-rag-langchain
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📊 Comparación de Proyectos

| Proyecto | Complejidad | Recursos | Costos | Casos de Uso |
|----------|-------------|----------|--------|--------------|
| PostgreSQL | Baja | 1GB RAM, 1 CPU | Gratis (Docker) | CRUD, Analytics, Reporting |
| ML Pipeline | Alta | 8GB RAM, 4 CPU | Gratis (Docker) | ML Training, Experimentation, Automation |
| RAG LangGraph | Media | 2GB RAM, 1 CPU | ~$10-20/mes (OpenAI) | Q&A, Knowledge Base, Multi-step Reasoning |

## 🛠️ Tecnologías Utilizadas

### Común a todos
- **FastMCP**: Framework para servidores MCP
- **Docker**: Containerización
- **Python 3.11+**: Lenguaje base

### Por proyecto

**PostgreSQL**:
- psycopg2: Driver de PostgreSQL
- PostgreSQL 16: Base de datos

**ML Pipeline**:
- PySpark: Procesamiento distribuido
- MLflow: Experimentos ML
- Airflow: Orquestación
- Bitnami Spark: Cluster Spark

**RAG**:
- LangGraph: Orquestación con grafos
- LangChain: Framework RAG
- ChromaDB: Vector database
- OpenAI: LLM y embeddings (GPT-4, text-embedding-3)

## 📖 Documentación

Cada proyecto tiene su propio README detallado con:
- Instalación paso a paso
- Guía de uso
- Ejemplos prácticos
- Troubleshooting
- Personalización

## 🎯 Casos de Uso por Industria

### PostgreSQL MCP
- **E-commerce**: Consultas de inventario y ventas
- **Finanzas**: Reportes y análisis de transacciones
- **Healthcare**: Consultas de registros médicos
- **SaaS**: Analytics de usuarios y métricas

### ML Pipeline MCP
- **Retail**: Predicción de demanda y optimización de inventario
- **Finanzas**: Detección de fraude y scoring crediticio
- **Marketing**: Segmentación y predicción de churn
- **Manufactura**: Mantenimiento predictivo

### RAG MCP
- **Legal**: Búsqueda en documentos legales
- **Soporte**: Knowledge base para agentes
- **Educación**: Asistente para material educativo
- **Investigación**: Búsqueda en papers académicos

## 🔒 Seguridad

⚠️ **IMPORTANTE**: Todos estos proyectos están configurados para **desarrollo local**.

Para producción, implementar:
- Autenticación y autorización
- Encriptación TLS/SSL
- Validación de inputs
- Rate limiting
- Secrets management
- Network isolation
- Backups automáticos
- Monitoring y alertas

## 🤝 Contribuciones

Estos proyectos son ejemplos educativos basados en el curso de FastMCP de Platzi.

## 📝 Licencia

Proyectos educativos - Usar bajo tu propia responsabilidad.

## 🆘 Soporte

Para problemas específicos de cada proyecto, consultar el README individual:
- [PostgreSQL README](./mcp-postgresql/README.md)
- [ML Pipeline README](./mcp-ml-pipeline/README.md)
- [RAG README](./mcp-rag-langchain/README.md)

## 📚 Recursos Adicionales

- [Curso MCP Platzi](./curso-mcp-main/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

**Creado con ❤️ usando FastMCP**

¿Preguntas? Consulta los READMEs individuales de cada proyecto o el código fuente comentado.

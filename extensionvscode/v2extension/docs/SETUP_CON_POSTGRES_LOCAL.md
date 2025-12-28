# Setup con PostgreSQL Local

Ya tienes PostgreSQL instalado localmente. Esta guía te muestra cómo configurar el proyecto para usarlo.

## 🎯 Configuración Actual

- ✅ PostgreSQL: **Local** (ya instalado)
- ✅ Redis: **Remoto** (YOUR_REDIS_OR_RABBITMQ_HOST:6379)
- 🐳 RabbitMQ: Docker
- 🐳 MinIO: Docker
- 🐳 Backend: Docker (o local)

---

## Paso 1: Verificar PostgreSQL Local (30 segundos)

```bash
# Verificar que PostgreSQL está corriendo
psql --version

# Conectar a PostgreSQL
psql -U YOUR_DB_USER

# Dentro de psql:
\l              # Listar bases de datos
\q              # Salir
```

Si PostgreSQL no está corriendo:
```bash
# macOS (Homebrew)
brew services start postgresql@15

# Linux (systemd)
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verificar estado
brew services list  # macOS
sudo systemctl status postgresql  # Linux
```

---

## Paso 2: Crear Base de Datos (1 minuto)

```bash
# Opción 1: Desde línea de comandos
createdb -U YOUR_DB_USER ai_goals_tracker

# Opción 2: Desde psql
psql -U YOUR_DB_USER
CREATE DATABASE ai_goals_tracker;
\q

# Opción 3: Con usuario específico
createdb -U tu_usuario ai_goals_tracker
```

### Instalar Extensión pgvector

```bash
# Conectar a la base de datos
psql -U YOUR_DB_USER -d ai_goals_tracker

# Crear extensión
CREATE EXTENSION IF NOT EXISTS vector;

# Verificar
\dx
# Debes ver 'vector' en la lista

\q
```

Si pgvector no está instalado:

```bash
# macOS (Homebrew)
brew install pgvector

# Linux (Ubuntu/Debian)
sudo apt install postgresql-15-pgvector

# Luego crear la extensión como arriba
```

---

## Paso 3: Configurar Variables de Entorno (30 segundos)

### Migrar API Key (si no lo has hecho)

```bash
./migrate-api-key.sh
```

### Actualizar DATABASE_URL en .env

```bash
# Editar .env
nano .env
```

Cambiar:
```bash
# De (Docker):
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_goals_tracker

# A (Local):
DATABASE_URL=postgresql+asyncpg://postgres:tu_password@localhost:5432/ai_goals_tracker
```

**Notas**:
- Si PostgreSQL local no tiene password, usar: `postgres@localhost`
- Si usas otro usuario: `tu_usuario:tu_password@localhost`
- Puerto por defecto: 5432 (cambiar si es diferente)

### Ejemplo de .env Completo

```bash
# Redis (Remoto)
REDIS_URL=redis://YOUR_REDIS_OR_RABBITMQ_HOST:6379/0

# PostgreSQL (Local)
DATABASE_URL=postgresql+asyncpg://postgres@localhost:5432/ai_goals_tracker

# OpenAI (de v1extension)
OPENAI_API_KEY=sk-tu-key-aqui

# Security
SECRET_KEY=tu-secret-key-de-32-chars

# RabbitMQ (Docker)
RABBITMQ_URL=amqp://guest:guest@localhost:5672/

# MinIO (Docker)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

---

## Paso 4: Actualizar docker-compose.yml (30 segundos)

Tenemos que comentar PostgreSQL en docker-compose para que no intente iniciarlo:

```bash
# Editar docker-compose.yml
nano docker-compose.yml
```

Comentar la sección de PostgreSQL:

```yaml
  # ==================== PostgreSQL with pgvector ====================
  # COMENTADO: Usando PostgreSQL local
  # postgres:
  #   image: pgvector/pgvector:pg15
  #   container_name: ai_goals_postgres
  #   ...
```

Y en la sección `backend`, comentar la dependencia de postgres:

```yaml
  backend:
    # ...
    depends_on:
      # postgres:
      #   condition: service_healthy
      rabbitmq:
        condition: service_healthy
      minio:
        condition: service_healthy
```

**Nota**: Ya he configurado docker-compose para que puedas hacer esto fácilmente.

---

## Paso 5: Iniciar Servicios (sin PostgreSQL) (1 minuto)

```bash
# Iniciar solo RabbitMQ, MinIO y Backend
docker-compose up -d rabbitmq minio backend
```

O usar el script de inicio que detectará automáticamente:

```bash
./start-with-remote-redis.sh
```

---

## Paso 6: Verificar Conexión (1 minuto)

### Test 1: PostgreSQL Local

```bash
# Conectar desde línea de comandos
psql -U YOUR_DB_USER -d ai_goals_tracker -c "SELECT version();"

# Debe mostrar la versión de PostgreSQL
```

### Test 2: Backend con PostgreSQL Local

```bash
# Health check
curl http://localhost:8000/api/v1/health/detailed
```

Si todo está bien, deberías ver:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "services": {
    "redis": true,      ✅ Remoto
    "rabbitmq": true    ✅ Docker
  }
}
```

### Test 3: Crear una Tabla de Prueba

```bash
psql -U YOUR_DB_USER -d ai_goals_tracker

-- Crear tabla de prueba
CREATE TABLE test_connection (
    id SERIAL PRIMARY KEY,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar dato
INSERT INTO test_connection (message) VALUES ('AI Goals Tracker V2 connected!');

-- Verificar
SELECT * FROM test_connection;

-- Limpiar
DROP TABLE test_connection;

\q
```

---

## Paso 7: Ejecutar Migraciones (cuando estén listas)

Cuando implementes los modelos de SQLAlchemy:

```bash
cd backend

# Instalar dependencias
poetry install

# Inicializar Alembic
poetry run alembic init migrations

# Crear migración inicial
poetry run alembic revision --autogenerate -m "Initial schema"

# Aplicar migraciones
poetry run alembic upgrade head
```

---

## Configuración Actual del Sistema

| Servicio | Tipo | Ubicación | Puerto |
|----------|------|-----------|--------|
| PostgreSQL | **Local** | localhost | 5432 |
| Redis | **Remoto** | YOUR_REDIS_OR_RABBITMQ_HOST | 6379 |
| RabbitMQ | Docker | localhost | 5672, 15672 |
| MinIO | Docker | localhost | 9000, 9001 |
| Backend | Docker | localhost | 8000 |

---

## Ventajas de esta Configuración

✅ **PostgreSQL Local**
- Más rápido que Docker
- Fácil acceso con psql
- Herramientas locales (pgAdmin, DBeaver)
- Datos persistentes nativamente

✅ **Redis Remoto**
- Estado compartido
- Colaboración en equipo
- Datos accesibles desde múltiples instancias

✅ **RabbitMQ/MinIO en Docker**
- Fácil de iniciar/detener
- No ensucia el sistema
- Configuración aislada

---

## Comandos Útiles

### PostgreSQL Local

```bash
# Conectar
psql -U YOUR_DB_USER -d ai_goals_tracker

# Backup
pg_dump -U YOUR_DB_USER ai_goals_tracker > backup.sql

# Restore
psql -U YOUR_DB_USER -d ai_goals_tracker < backup.sql

# Ver bases de datos
psql -U YOUR_DB_USER -c "\l"

# Ver tablas
psql -U YOUR_DB_USER -d ai_goals_tracker -c "\dt"
```

### Servicios Docker (sin PostgreSQL)

```bash
# Iniciar solo RabbitMQ y MinIO
docker-compose up -d rabbitmq minio

# Ver logs
docker-compose logs -f backend

# Detener
docker-compose down
```

### Backend con PostgreSQL Local

```bash
# Opción 1: En Docker (recomendado)
docker-compose up -d backend

# Opción 2: Localmente
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

---

## Troubleshooting

### Error: Backend no se conecta a PostgreSQL

**Solución 1**: Verificar que DATABASE_URL es correcta

```bash
cat .env | grep DATABASE_URL

# Debe ser:
# DATABASE_URL=postgresql+asyncpg://postgres@localhost:5432/ai_goals_tracker
```

**Solución 2**: Verificar que PostgreSQL acepta conexiones

```bash
# Ver configuración de PostgreSQL
psql -U YOUR_DB_USER -c "SHOW listen_addresses;"

# Debe mostrar: listen_addresses = '*' o 'localhost'
```

**Solución 3**: Verificar pg_hba.conf

```bash
# macOS (Homebrew)
cat /opt/homebrew/var/postgresql@15/pg_hba.conf | grep "host.*127.0.0.1"

# Linux
cat /etc/postgresql/15/main/pg_hba.conf | grep "host.*127.0.0.1"

# Debe tener:
# host    all    all    127.0.0.1/32    trust
# o
# host    all    all    127.0.0.1/32    md5
```

### Error: Extensión pgvector no encontrada

```bash
# Instalar pgvector
brew install pgvector  # macOS
sudo apt install postgresql-15-pgvector  # Linux

# Luego:
psql -U YOUR_DB_USER -d ai_goals_tracker -c "CREATE EXTENSION vector;"
```

### Error: Backend en Docker no alcanza PostgreSQL local

El backend en Docker necesita acceder a PostgreSQL en el host:

```bash
# En .env, cambiar localhost a host.docker.internal (macOS/Windows)
DATABASE_URL=postgresql+asyncpg://postgres@host.docker.internal:5432/ai_goals_tracker

# O en Linux, usar la IP del host
DATABASE_URL=postgresql+asyncpg://postgres@172.17.0.1:5432/ai_goals_tracker
```

---

## Script de Verificación Completa

```bash
#!/bin/bash

echo "🔍 Verificando configuración completa..."

# 1. PostgreSQL Local
echo "1. PostgreSQL Local"
psql -U YOUR_DB_USER -d ai_goals_tracker -c "SELECT 1;" && echo "   ✅ Conectado" || echo "   ❌ Error"

# 2. Redis Remoto
echo "2. Redis Remoto"
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379 PING && echo "   ✅ Conectado" || echo "   ❌ Error"

# 3. RabbitMQ
echo "3. RabbitMQ"
curl -s http://localhost:15672 > /dev/null && echo "   ✅ Accesible" || echo "   ❌ Error"

# 4. Backend
echo "4. Backend"
curl -s http://localhost:8000/health > /dev/null && echo "   ✅ Respondiendo" || echo "   ❌ Error"

echo ""
echo "✅ Verificación completa"
```

---

## Próximos Pasos

1. ✅ Verificar que PostgreSQL local está corriendo
2. ✅ Crear base de datos `ai_goals_tracker`
3. ✅ Instalar extensión pgvector
4. ✅ Actualizar `.env` con DATABASE_URL correcta
5. ✅ Iniciar servicios con `docker-compose up -d rabbitmq minio backend`
6. ✅ Verificar conexión con `curl http://localhost:8000/health`

---

**Configuración**: PostgreSQL Local + Redis Remoto + RabbitMQ/MinIO Docker
**Status**: ✅ Optimizado para desarrollo con servicios locales

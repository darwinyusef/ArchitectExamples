# Configuración Actual - AI Goals Tracker V2

## 🌐 Servicios Configurados

Tu proyecto está pre-configurado con estos servicios remotos y locales:

| Servicio | Tipo | Host | Puerto | Credenciales |
|----------|------|------|--------|--------------|
| **Redis** | Remoto | Ver .env | 6379 | Ver .env |
| **PostgreSQL** | Local | localhost | 5432 | Ver .env |
| **RabbitMQ** | Remoto | Ver .env | 5672, 15672 | Ver .env |
| **MinIO** | Docker | localhost | 9000, 9001 | minioadmin/minioadmin |

---

## 🚀 Setup Rápido (2 minutos)

### Paso 1: Migrar API Key de OpenAI

```bash
cd v2extension
./migrate-api-key.sh
```

### Paso 2: Crear Base de Datos PostgreSQL Local

```bash
# Verificar que PostgreSQL está corriendo
psql -U YOUR_DB_USER -c "SELECT version();"

# Crear base de datos
createdb -U YOUR_DB_USER ai_goals_tracker

# Conectar y crear extensión pgvector
psql -U YOUR_DB_USER -d ai_goals_tracker
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### Paso 3: Iniciar MinIO (único servicio Docker necesario)

```bash
# Solo MinIO necesita Docker (para storage S3)
docker-compose up -d minio
```

### Paso 4: Iniciar Backend

```bash
cd backend

# Instalar dependencias
poetry install

# Ejecutar backend
poetry run uvicorn app.main:app --reload
```

¡Listo! Todos los servicios están conectados.

---

## 📋 Configuración de .env

⚠️ **IMPORTANTE**: Tu archivo `.env` contiene credenciales sensibles. Ver archivo `.env.example` para template.

**NO subir .env a GitHub**. El archivo `.gitignore` ya lo protege.

```bash
# Redis Remoto
REDIS_URL=redis://YOUR_REDIS_HOST:6379/0

# PostgreSQL Local
DATABASE_URL=postgresql+asyncpg://YOUR_DB_USER:YOUR_DB_PASSWORD@localhost:5432/ai_goals_tracker

# RabbitMQ Remoto
RABBITMQ_URL=amqp://YOUR_RABBITMQ_USER:YOUR_RABBITMQ_PASSWORD@YOUR_RABBITMQ_HOST:5672/

# MinIO Local (Docker)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# OpenAI (migrada de v1extension)
OPENAI_API_KEY=sk-YOUR_API_KEY_HERE

# Security (generada automáticamente con: openssl rand -hex 32)
SECRET_KEY=YOUR_GENERATED_SECRET_KEY
```

---

## 🔍 Verificar Servicios

### 1. Redis Remoto

```bash
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379 PING
# Debe responder: PONG ✅
```

### 2. PostgreSQL Local

```bash
psql -U YOUR_DB_USER -d ai_goals_tracker -c "SELECT version();"
# Debe mostrar: PostgreSQL 15.x ✅
```

### 3. RabbitMQ Remoto

```bash
# Ver UI
open http://YOUR_REDIS_OR_RABBITMQ_HOST:15672
# Login: guest/guest ✅

# O probar conexión
curl -u guest:guest http://YOUR_REDIS_OR_RABBITMQ_HOST:15672/api/overview
```

### 4. MinIO Local

```bash
# Ver UI
open http://localhost:9001
# Login: minioadmin/minioadmin ✅
```

### 5. Backend

```bash
curl http://localhost:8000/health
# Debe responder: {"status":"healthy",...} ✅
```

---

## 🎯 Ventajas de Esta Configuración

### Redis Remoto (YOUR_REDIS_OR_RABBITMQ_HOST)
✅ Estado compartido entre múltiples desarrolladores
✅ Datos persistentes
✅ Perfecto para demos y testing colaborativo

### PostgreSQL Local
✅ Más rápido que remoto
✅ Control total de la base de datos
✅ Fácil acceso con psql, pgAdmin, DBeaver
✅ Datos bajo tu control

### RabbitMQ Remoto (YOUR_REDIS_OR_RABBITMQ_HOST)
✅ No necesitas configurar RabbitMQ localmente
✅ Cola de eventos compartida
✅ UI accesible remotamente

### MinIO Local (Docker)
✅ Storage S3 para desarrollo
✅ Fácil de reiniciar
✅ No ensucia el sistema

---

## 📊 URLs Importantes

### Servicios Remotos
- **RabbitMQ UI**: http://YOUR_REDIS_OR_RABBITMQ_HOST:15672
  - Usuario: guest
  - Password: guest

### Servicios Locales
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001
  - Usuario: minioadmin
  - Password: minioadmin

### PostgreSQL
```bash
# Conectar
psql -U YOUR_DB_USER -d ai_goals_tracker

# GUI tools
# - pgAdmin 4
# - DBeaver
# - TablePlus
```

### Redis
```bash
# CLI
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379

# GUI tools
# - RedisInsight
# - Medis
# - Redis Desktop Manager
```

---

## 🛠 Comandos de Administración

### PostgreSQL

```bash
# Conectar
psql -U YOUR_DB_USER -d ai_goals_tracker

# Backup
pg_dump -U YOUR_DB_USER ai_goals_tracker > backup_$(date +%Y%m%d).sql

# Restore
psql -U YOUR_DB_USER -d ai_goals_tracker < backup.sql

# Ver tablas
psql -U YOUR_DB_USER -d ai_goals_tracker -c "\dt"

# Ver tamaño de DB
psql -U YOUR_DB_USER -d ai_goals_tracker -c "SELECT pg_size_pretty(pg_database_size('ai_goals_tracker'));"
```

### Redis Remoto

```bash
# Conectar
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379

# Ver todas las keys
KEYS *

# Ver keys de AI Goals Tracker
KEYS user_session:*
KEYS goal_state:*
KEYS ws_connections:*

# Monitorear en tiempo real
MONITOR

# Info del servidor
INFO

# Limpiar keys de prueba
DEL test_key
```

### RabbitMQ Remoto

```bash
# Ver colas (API)
curl -u guest:guest http://YOUR_REDIS_OR_RABBITMQ_HOST:15672/api/queues

# Ver exchanges
curl -u guest:guest http://YOUR_REDIS_OR_RABBITMQ_HOST:15672/api/exchanges

# Ver conexiones activas
curl -u guest:guest http://YOUR_REDIS_OR_RABBITMQ_HOST:15672/api/connections
```

### MinIO Local

```bash
# Acceder a console
open http://localhost:9001

# O usar mc (MinIO Client)
brew install minio/stable/mc  # macOS
mc alias set local http://localhost:9000 minioadmin minioadmin
mc ls local
```

---

## 🔧 Troubleshooting

### Backend no se conecta a Redis

```bash
# Verificar conectividad
ping YOUR_REDIS_OR_RABBITMQ_HOST
telnet YOUR_REDIS_OR_RABBITMQ_HOST 6379

# Probar con redis-cli
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379 PING

# Ver logs del backend
poetry run uvicorn app.main:app --log-level debug
```

### Backend no se conecta a PostgreSQL

```bash
# Verificar que PostgreSQL está corriendo
pg_isready -U YOUR_DB_USER

# Verificar credenciales
psql -U YOUR_DB_USER -d ai_goals_tracker

# Ver logs de PostgreSQL
# macOS:
tail -f /opt/homebrew/var/log/postgresql@15.log

# Linux:
tail -f /var/log/postgresql/postgresql-15-main.log
```

### Backend no se conecta a RabbitMQ

```bash
# Verificar conectividad
telnet YOUR_REDIS_OR_RABBITMQ_HOST 5672

# Ver UI
open http://YOUR_REDIS_OR_RABBITMQ_HOST:15672

# Probar con amqp-tools
sudo apt install amqp-tools  # Linux
brew install amqp-tools  # macOS

amqp-declare-queue -u amqp://guest:guest@YOUR_REDIS_OR_RABBITMQ_HOST:5672/ -q test
```

---

## 📝 Script de Verificación Completa

Guarda esto como `verify-services.sh`:

```bash
#!/bin/bash

echo "🔍 Verificando todos los servicios..."
echo ""

# Redis Remoto
echo "1. Redis Remoto (YOUR_REDIS_OR_RABBITMQ_HOST:6379)"
if redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379 PING &>/dev/null; then
    echo "   ✅ Conectado"
else
    echo "   ❌ No accesible"
fi

# PostgreSQL Local
echo "2. PostgreSQL Local (localhost:5432)"
if psql -U YOUR_DB_USER -d ai_goals_tracker -c "SELECT 1;" &>/dev/null; then
    echo "   ✅ Conectado"
else
    echo "   ❌ No accesible"
fi

# RabbitMQ Remoto
echo "3. RabbitMQ Remoto (YOUR_REDIS_OR_RABBITMQ_HOST:15672)"
if curl -s -u guest:guest http://YOUR_REDIS_OR_RABBITMQ_HOST:15672/api/overview &>/dev/null; then
    echo "   ✅ Accesible"
else
    echo "   ❌ No accesible"
fi

# MinIO Local
echo "4. MinIO Local (localhost:9000)"
if curl -s http://localhost:9000/minio/health/live &>/dev/null; then
    echo "   ✅ Accesible"
else
    echo "   ❌ No accesible (ejecutar: docker-compose up -d minio)"
fi

# Backend
echo "5. Backend (localhost:8000)"
if curl -s http://localhost:8000/health &>/dev/null; then
    echo "   ✅ Respondiendo"
else
    echo "   ❌ No está corriendo"
fi

echo ""
echo "✅ Verificación completa"
```

Ejecutar:
```bash
chmod +x verify-services.sh
./verify-services.sh
```

---

## 🎯 Flujo de Trabajo Recomendado

### Inicio del Día

```bash
# 1. Verificar PostgreSQL
pg_isready -U YOUR_DB_USER

# 2. Iniciar MinIO si no está corriendo
docker-compose up -d minio

# 3. Verificar servicios remotos
./verify-services.sh

# 4. Iniciar backend
cd backend && poetry run uvicorn app.main:app --reload
```

### Durante el Desarrollo

```bash
# Terminal 1: Backend
cd backend
poetry run uvicorn app.main:app --reload

# Terminal 2: Logs y monitoring
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379 MONITOR

# Terminal 3: Database
psql -U YOUR_DB_USER -d ai_goals_tracker

# Terminal 4: Frontend
cd frontend
npm run watch
code . # F5 para debug
```

### Fin del Día

```bash
# Detener MinIO si quieres
docker-compose down

# PostgreSQL y servicios remotos siguen corriendo
# (no necesitas detenerlos)
```

---

## 📚 Próximos Pasos

1. ✅ Ejecutar `./migrate-api-key.sh`
2. ✅ Crear base de datos: `createdb -U YOUR_DB_USER ai_goals_tracker`
3. ✅ Ejecutar `./verify-services.sh`
4. ✅ Iniciar backend: `cd backend && poetry run uvicorn app.main:app --reload`
5. ✅ Probar: `curl http://localhost:8000/health`

---

**Configuración Actual**: ✅ OPTIMIZADA
- Redis: Remoto (compartido)
- PostgreSQL: Local (control total)
- RabbitMQ: Remoto (sin setup)
- MinIO: Docker (fácil de manejar)

**Estado**: 🚀 LISTO PARA DESARROLLAR

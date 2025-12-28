# 🚀 Inicio Rápido - AI Goals Tracker V2

## Configuración del Proyecto

Tu proyecto está **PRE-CONFIGURADO** con:

| Servicio | Ubicación | Credenciales |
|----------|-----------|--------------|
| **Redis** | Remoto (ver .env) | Configurar en .env |
| **PostgreSQL** | localhost:5432 | Configurar en .env |
| **RabbitMQ** | Remoto (ver .env) | Configurar en .env |
| **Storage** | Local (./data/storage) | - |

---

## ⚡ Setup en 3 Pasos (2 minutos)

### 1. Migrar OpenAI API Key (30 seg)

```bash
cd v2extension
./migrate-api-key.sh
```

Esto:
- ✅ Obtiene la API key de v1extension
- ✅ Genera SECRET_KEY automáticamente
- ✅ Crea .env con toda la configuración

### 2. Crear Base de Datos (30 seg)

```bash
# Crear DB
createdb -U YOUR_DB_USER ai_goals_tracker

# Crear extensión pgvector
psql -U YOUR_DB_USER -d ai_goals_tracker -c "CREATE EXTENSION vector;"
```

### 3. Iniciar Backend (1 min)

```bash
cd backend

# Instalar dependencias (solo primera vez)
poetry install

# Ejecutar backend
poetry run uvicorn app.main:app --reload
```

**¡Listo!** Backend corriendo en http://localhost:8000

---

## 🎯 Verificación Rápida

```bash
# Test 1: Backend
curl http://localhost:8000/health
# ✅ Debe responder: {"status":"healthy",...}

# Test 2: Redis remoto
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379 PING
# ✅ Debe responder: PONG

# Test 3: PostgreSQL local
psql -U YOUR_DB_USER -d ai_goals_tracker -c "SELECT 1;"
# ✅ Debe responder: 1

# Test 4: RabbitMQ remoto
open http://YOUR_REDIS_OR_RABBITMQ_HOST:15672
# ✅ Login: guest/guest
```

---

## 📋 Archivo .env Final

Después de ejecutar `./migrate-api-key.sh`, tu `.env` debe verse así:

```bash
# Redis Remoto
REDIS_URL=redis://YOUR_REDIS_HOST:6379/0

# PostgreSQL Local
DATABASE_URL=postgresql+asyncpg://YOUR_DB_USER:YOUR_DB_PASSWORD@localhost:5432/ai_goals_tracker

# RabbitMQ Remoto
RABBITMQ_URL=amqp://YOUR_RABBITMQ_USER:YOUR_RABBITMQ_PASSWORD@YOUR_RABBITMQ_HOST:5672/

# Storage Local
STORAGE_TYPE=local
STORAGE_LOCAL_PATH=./data/storage

# OpenAI (de v1extension)
OPENAI_API_KEY=sk-proj-YOUR_API_KEY_HERE

# Security (generada automáticamente)
SECRET_KEY=YOUR_GENERATED_SECRET_KEY_64_CHARS
```

---

## 🌐 URLs Importantes

### Backend
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### RabbitMQ Remoto
- UI: Ver credenciales en .env
- User: Ver credenciales en .env
- Pass: Ver credenciales en .env

### PostgreSQL Local
```bash
# Ver credenciales en .env
psql -U YOUR_DB_USER -d ai_goals_tracker
```

### Redis Remoto
```bash
# Ver URL en .env
redis-cli -h YOUR_REDIS_HOST -p 6379
```

---

## 🎮 Frontend (VS Code Extension)

```bash
cd frontend
npm install
npm run compile
code .
```

Presionar `F5` para ejecutar la extensión.

---

## 💡 Comandos Útiles

### Backend en Desarrollo

```bash
cd backend

# Watch mode (recarga automática)
poetry run uvicorn app.main:app --reload

# Con logs detallados
poetry run uvicorn app.main:app --reload --log-level debug
```

### Frontend en Desarrollo

```bash
cd frontend

# Watch mode (compilación automática)
npm run watch

# En otra terminal, abrir VS Code
code .  # F5 para debug
```

### Ver Datos

```bash
# PostgreSQL
psql -U YOUR_DB_USER -d ai_goals_tracker

# Redis
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379

# Storage local
ls -lh backend/data/storage/
```

---

## 🔧 Troubleshooting

### Backend no inicia

```bash
# Ver logs detallados
cd backend
poetry run python -c "from app.core.config import settings; print(settings)"

# Verificar .env
cat .env | grep -E "REDIS|DATABASE|RABBITMQ"
```

### No puede conectar a Redis

```bash
# Probar conectividad
ping YOUR_REDIS_OR_RABBITMQ_HOST
telnet YOUR_REDIS_OR_RABBITMQ_HOST 6379

# Probar con redis-cli
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379 PING
```

### No puede conectar a PostgreSQL

```bash
# Verificar que está corriendo
pg_isready -U YOUR_DB_USER

# Verificar password
psql -U YOUR_DB_USER -c "SELECT 1;"

# Si falla, resetear password
# Ver: SETUP_CON_POSTGRES_LOCAL.md
```

---

## 📚 Documentación Adicional

- `CONFIGURACION_ACTUAL.md` - Detalle de servicios configurados
- `SETUP_CON_POSTGRES_LOCAL.md` - Setup de PostgreSQL local
- `STORAGE_SETUP.md` - Storage local y migración a MinIO
- `README_REDIS.md` - Todo sobre Redis remoto
- `SETUP_COMPLETO.md` - Guía paso a paso completa

---

## ✅ Checklist Final

- [ ] Ejecutar `./migrate-api-key.sh`
- [ ] Crear DB: `createdb -U YOUR_DB_USER ai_goals_tracker`
- [ ] Crear extensión: `psql -U YOUR_DB_USER -d ai_goals_tracker -c "CREATE EXTENSION vector;"`
- [ ] Instalar deps: `cd backend && poetry install`
- [ ] Iniciar backend: `poetry run uvicorn app.main:app --reload`
- [ ] Probar: `curl http://localhost:8000/health`
- [ ] Frontend: `cd frontend && npm install && npm run compile`
- [ ] Ejecutar frontend: `code . # F5`

---

**Setup Time**: ~2 minutos
**Configuración**: ✅ PRE-CONFIGURADA
**Estado**: 🚀 LISTO PARA CODEAR

---

## 🎯 ¿Qué Sigue?

1. ✅ Explorar API Docs: http://localhost:8000/docs
2. ✅ Ver arquitectura: `cat ARQUITECTURA-TECNICA.md`
3. ✅ Leer guía de desarrollo: `cat GETTING_STARTED.md`
4. ✅ Empezar a codear! 🚀

---

**¡Todo está listo!** Solo ejecuta `./migrate-api-key.sh` y ya puedes empezar a desarrollar.

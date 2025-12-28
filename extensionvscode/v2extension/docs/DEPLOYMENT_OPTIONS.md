# Deployment Options - AI Goals Tracker V2

El proyecto soporta diferentes configuraciones de deployment según tus necesidades.

## Opción 1: Todo Local (Desarrollo)

**Usar cuando**: Desarrollando localmente sin internet

```bash
# .env
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_goals_tracker
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
MINIO_ENDPOINT=localhost:9000

# Iniciar todo con Docker
docker-compose --profile local up -d
```

**Servicios iniciados**:
- ✅ PostgreSQL (local)
- ✅ Redis (local)
- ✅ RabbitMQ (local)
- ✅ MinIO (local)
- ✅ Backend API (local)

## Opción 2: Redis Remoto + Resto Local (Recomendado para Demo)

**Usar cuando**: Quieres datos persistentes compartidos pero todo lo demás local

```bash
# .env
REDIS_URL=redis://YOUR_REDIS_OR_RABBITMQ_HOST:6379/0
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_goals_tracker
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
MINIO_ENDPOINT=localhost:9000

# Iniciar sin Redis local
docker-compose up -d
# Redis local NO se iniciará (profile: local)
```

**Servicios iniciados**:
- ✅ PostgreSQL (local)
- 🌐 Redis (remoto: YOUR_REDIS_OR_RABBITMQ_HOST)
- ✅ RabbitMQ (local)
- ✅ MinIO (local)
- ✅ Backend API (local)

**Ventajas**:
- Estado compartido entre múltiples instancias
- Datos persistentes en Redis
- Útil para demos y testing colaborativo

## Opción 3: Servicios Mixtos (Híbrido)

**Usar cuando**: Tienes algunos servicios en la nube

```bash
# .env
REDIS_URL=redis://YOUR_REDIS_OR_RABBITMQ_HOST:6379/0
DATABASE_URL=postgresql+asyncpg://user:pass@your-db.amazonaws.com:5432/ai_goals
RABBITMQ_URL=amqp://user:pass@your-rabbitmq.cloudamqp.com/
MINIO_ENDPOINT=your-bucket.s3.amazonaws.com

# Solo iniciar backend
docker-compose up backend
```

**Servicios**:
- 🌐 PostgreSQL (AWS RDS, Supabase, etc.)
- 🌐 Redis (Redis Cloud, ElastiCache, etc.)
- 🌐 RabbitMQ (CloudAMQP, AWS MQ, etc.)
- 🌐 MinIO/S3 (AWS S3, MinIO Cloud, etc.)
- ✅ Backend API (local o en contenedor)

## Opción 4: Todo en la Nube (Producción)

**Usar cuando**: Deploy completo en producción

```bash
# .env
REDIS_URL=redis://:password@production-redis.cloud:6379/0
DATABASE_URL=postgresql+asyncpg://user:pass@production-db.cloud:5432/ai_goals
RABBITMQ_URL=amqps://user:pass@production-rabbitmq.cloud/
MINIO_ENDPOINT=production-bucket.s3.amazonaws.com

# Deploy backend en Kubernetes, ECS, o similar
# NO usar docker-compose en producción
```

## Comparación de Opciones

| Opción | Redis | DB | RabbitMQ | MinIO | Caso de Uso |
|--------|-------|-----|----------|-------|-------------|
| 1 | Local | Local | Local | Local | Desarrollo offline |
| 2 | **Remoto** | Local | Local | Local | **Demo/Testing** ✨ |
| 3 | Remoto | Remoto | Remoto | Remoto | Staging |
| 4 | Cloud | Cloud | Cloud | Cloud | Producción |

## Configuración por Entorno

### Development (Local)

```bash
# .env.development
DEBUG=true
LOG_LEVEL=DEBUG
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_goals_tracker
```

### Testing/Demo (Redis Remoto)

```bash
# .env.testing
DEBUG=true
LOG_LEVEL=INFO
REDIS_URL=redis://YOUR_REDIS_OR_RABBITMQ_HOST:6379/0  # ✨ Redis compartido
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/ai_goals_tracker
```

### Staging (Servicios Cloud)

```bash
# .env.staging
DEBUG=false
LOG_LEVEL=INFO
REDIS_URL=redis://:pass@staging-redis.cloud:6379/0
DATABASE_URL=postgresql+asyncpg://user:pass@staging-db.cloud:5432/ai_goals
RABBITMQ_URL=amqps://user:pass@staging-mq.cloud/
```

### Production

```bash
# .env.production
DEBUG=false
LOG_LEVEL=WARNING
REDIS_URL=rediss://:pass@prod-redis.cloud:6380/0  # TLS
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db.cloud:5432/ai_goals
RABBITMQ_URL=amqps://user:pass@prod-mq.cloud/
# + Más configuraciones de seguridad
```

## Comandos por Opción

### Opción 1: Todo Local

```bash
# Iniciar todos los servicios
docker-compose --profile local up -d

# Ver logs
docker-compose logs -f

# Detener todo
docker-compose --profile local down
```

### Opción 2: Redis Remoto (Recomendado)

```bash
# Verificar conexión a Redis remoto
python backend/scripts/test_redis.py redis://YOUR_REDIS_OR_RABBITMQ_HOST:6379/0

# Iniciar servicios (sin Redis local)
docker-compose up -d

# Backend se conectará a Redis remoto automáticamente
curl http://localhost:8000/api/v1/health/detailed

# Ver estado de Redis remoto
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379 INFO
```

### Opción 3: Híbrido

```bash
# Solo backend (asumiendo servicios remotos)
docker-compose up backend -d

# O ejecutar backend fuera de Docker
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

### Opción 4: Producción

```bash
# Build imagen
docker build -t ai-goals-tracker:v2.0.0 backend/

# Push a registry
docker push your-registry/ai-goals-tracker:v2.0.0

# Deploy con Kubernetes/ECS/etc.
kubectl apply -f k8s/deployment.yaml
```

## Verificar Configuración Actual

```bash
# Ver qué servicios están corriendo
docker-compose ps

# Probar conexión a Redis
python backend/scripts/test_redis.py

# Health check completo
curl http://localhost:8000/api/v1/health/detailed

# Ver configuración del backend
docker-compose exec backend env | grep -E "REDIS|DATABASE|RABBITMQ"
```

## Troubleshooting por Opción

### Opción 1 (Todo Local)

**Problema**: Redis no inicia
```bash
# Ver logs
docker-compose logs redis

# Recrear contenedor
docker-compose down redis
docker-compose --profile local up -d redis
```

### Opción 2 (Redis Remoto)

**Problema**: No puede conectar a Redis remoto
```bash
# Probar conectividad
ping YOUR_REDIS_OR_RABBITMQ_HOST
telnet YOUR_REDIS_OR_RABBITMQ_HOST 6379

# Verificar firewall
# Verificar que REDIS_URL en .env es correcto
```

**Problema**: Backend no ve Redis como healthy
```bash
# Verificar health check
curl http://localhost:8000/api/v1/health/detailed

# Si redis: false, revisar logs
docker-compose logs backend | grep -i redis
```

### Opción 3 (Híbrido)

**Problema**: Algunos servicios no conectan
```bash
# Verificar cada URL en .env
# Probar conectividad a cada servicio
nc -zv your-db-host.com 5432
nc -zv your-rabbitmq-host.com 5672
```

## Recomendaciones

### Para Desarrollo Individual
- ✅ **Opción 1** (Todo Local)
- Más rápido
- No depende de internet
- Fácil de resetear

### Para Demo/Testing Colaborativo
- ✅ **Opción 2** (Redis Remoto) ⭐
- Estado compartido
- Múltiples developers pueden colaborar
- Datos persistentes

### Para QA/Staging
- ✅ **Opción 3** (Híbrido)
- Simula producción
- Más estable que local
- Fácil de configurar

### Para Producción
- ✅ **Opción 4** (Todo Cloud)
- Alta disponibilidad
- Escalable
- Backups automáticos
- Monitoreo integrado

---

**Configuración Actual Recomendada**: Opción 2 (Redis Remoto)
**Redis Server**: `YOUR_REDIS_OR_RABBITMQ_HOST:6379`

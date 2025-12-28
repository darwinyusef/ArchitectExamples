# Docker Setup - AI Goals Tracker V2

## Requisitos Previos

- Docker Desktop instalado
- Docker Compose v2+
- 4GB RAM mínimo disponible
- OpenAI API Key

## Servicios Incluidos

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **Backend API** | 8000 | FastAPI application |
| **PostgreSQL** | 5432 | Database with pgvector |
| **Redis** | 6379 | Cache & rate limiting (opcional - puede usar remoto) |
| **RabbitMQ** | 5672, 15672 | Message broker (15672 = Management UI) |
| **MinIO** | 9000, 9001 | S3-compatible storage (9001 = Console) |

## Setup Rápido

### 1. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```bash
# .env
OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=your-secret-key-min-32-characters-long
REDIS_URL=redis://64.23.150.221:6379/0
```

### 2. Levantar Servicios

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Ver estado de servicios
docker-compose ps
```

### 3. Verificar que todo está corriendo

```bash
# Check backend health
curl http://localhost:8000/health

# Check API docs
open http://localhost:8000/docs

# Check RabbitMQ Management
open http://localhost:15672
# Usuario: guest / Contraseña: guest

# Check MinIO Console
open http://localhost:9001
# Usuario: minioadmin / Contraseña: minioadmin
```

## Comandos Útiles

### Gestión de Contenedores

```bash
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (CUIDADO: borra la DB)
docker-compose down -v

# Reconstruir backend
docker-compose build backend
docker-compose up -d backend

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Migraciones de Base de Datos

```bash
# Las migraciones se ejecutan automáticamente al iniciar el backend
# Pero si necesitas ejecutarlas manualmente:

docker-compose exec backend alembic upgrade head

# Ver historial de migraciones
docker-compose exec backend alembic history

# Crear nueva migración
docker-compose exec backend alembic revision --autogenerate -m "descripcion"

# Rollback última migración
docker-compose exec backend alembic downgrade -1
```

### Acceso a PostgreSQL

```bash
# Conectar a PostgreSQL desde host
psql postgresql://postgres:postgres@localhost:5432/ai_goals_tracker

# O desde dentro del contenedor
docker-compose exec postgres psql -U postgres -d ai_goals_tracker

# Verificar extensión pgvector
docker-compose exec postgres psql -U postgres -d ai_goals_tracker -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Acceso a Redis

```bash
# Conectar a Redis CLI
docker-compose exec redis redis-cli

# Ver todas las keys de rate limiting
docker-compose exec redis redis-cli KEYS "rate_limit:*"

# Ver bucket de un usuario
docker-compose exec redis redis-cli HGETALL "rate_limit:test-user:api_call"

# Limpiar todas las keys de rate limiting
docker-compose exec redis redis-cli --scan --pattern "rate_limit:*" | xargs docker-compose exec redis redis-cli DEL
```

### Debugging

```bash
# Entrar al contenedor del backend
docker-compose exec backend sh

# Ver variables de entorno
docker-compose exec backend env | grep -E "DATABASE|REDIS|OPENAI"

# Verificar conectividad desde backend
docker-compose exec backend ping postgres
docker-compose exec backend nc -zv rabbitmq 5672

# Ver recursos consumidos
docker stats

# Reiniciar un servicio
docker-compose restart backend
```

## Opciones de Redis

El proyecto soporta 2 configuraciones de Redis:

### Opción 1: Redis Local (en Docker)

Editar `docker-compose.yml`:

```yaml
redis:
  # Remover profiles section para que siempre se inicie
  # profiles:
  #   - local

backend:
  environment:
    REDIS_URL: redis://redis:6379/0
  depends_on:
    redis:
      condition: service_healthy
```

### Opción 2: Redis Remoto (Default)

Ya configurado para usar: `redis://64.23.150.221:6379/0`

No necesita cambios, solo asegúrate que el servidor remoto esté accesible.

## Troubleshooting

### Error: "port is already allocated"

```bash
# Algún puerto está ocupado
# Verificar qué proceso usa el puerto
lsof -i :8000
lsof -i :5432

# Matar el proceso o cambiar el puerto en docker-compose.yml
```

### Error: "Cannot connect to PostgreSQL"

```bash
# Verificar que PostgreSQL esté saludable
docker-compose ps

# Ver logs de PostgreSQL
docker-compose logs postgres

# Reiniciar PostgreSQL
docker-compose restart postgres
```

### Error: "alembic: command not found"

```bash
# Reconstruir imagen del backend
docker-compose build backend
docker-compose up -d backend
```

### Error: "OpenAI API key not set"

```bash
# Verificar .env
cat .env | grep OPENAI

# Reiniciar backend después de agregar la key
docker-compose restart backend
```

### Backend no inicia (crash loop)

```bash
# Ver logs detallados
docker-compose logs backend

# Problemas comunes:
# 1. Falta OPENAI_API_KEY en .env
# 2. PostgreSQL no está listo
# 3. Error en migraciones
# 4. Error en imports

# Ejecutar bash interactivo para debug
docker-compose run --rm backend sh
```

## Desarrollo Local

### Hot Reload

El backend tiene hot reload activado. Los cambios en `./backend/app/` se reflejan automáticamente.

```bash
# Editar archivo
vim backend/app/api/routes/goals.py

# El servidor se reinicia automáticamente
# Ver en los logs:
docker-compose logs -f backend
```

### Ejecutar Backend Fuera de Docker

Si prefieres ejecutar el backend localmente:

```bash
cd backend

# Instalar dependencias
poetry install

# Activar entorno
poetry shell

# Configurar .env
cp .env.example .env
# Editar .env con tus valores

# Solo levantar servicios de infraestructura
docker-compose up -d postgres rabbitmq minio

# Ejecutar migraciones
alembic upgrade head

# Iniciar backend
python -m app.main

# O con uvicorn directamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Backup y Restore

### Backup de PostgreSQL

```bash
# Backup completo
docker-compose exec postgres pg_dump -U postgres ai_goals_tracker > backup_$(date +%Y%m%d).sql

# Backup solo schema
docker-compose exec postgres pg_dump -U postgres --schema-only ai_goals_tracker > schema.sql

# Backup solo datos
docker-compose exec postgres pg_dump -U postgres --data-only ai_goals_tracker > data.sql
```

### Restore

```bash
# Restore desde backup
cat backup_20250128.sql | docker-compose exec -T postgres psql -U postgres -d ai_goals_tracker

# O copiar archivo al contenedor
docker cp backup.sql ai_goals_postgres:/tmp/backup.sql
docker-compose exec postgres psql -U postgres -d ai_goals_tracker -f /tmp/backup.sql
```

## Limpieza

### Limpiar Todo (CUIDADO)

```bash
# Detener y eliminar contenedores + volúmenes
docker-compose down -v

# Eliminar imágenes
docker-compose down --rmi all

# Limpiar sistema completo de Docker
docker system prune -a --volumes
```

### Limpiar Solo Data

```bash
# Detener servicios
docker-compose down

# Eliminar volúmenes
docker volume rm v2extension_postgres_data
docker volume rm v2extension_redis_data
docker volume rm v2extension_rabbitmq_data
docker volume rm v2extension_minio_data

# Reiniciar desde cero
docker-compose up -d
```

## Monitoreo

### Ver Métricas de Contenedores

```bash
# Stats en tiempo real
docker stats

# Uso de disco
docker system df

# Ver logs de todos los servicios
docker-compose logs --tail=100 -f
```

### Healthchecks

Todos los servicios tienen healthchecks configurados:

```bash
# Ver estado de salud
docker-compose ps

# Servicios saludables muestran: healthy
# Si muestra (unhealthy) hay un problema
```

## Production Tips

Para producción, considera:

1. **Usar Redis local** - Más rápido y confiable
2. **Volumes persistentes** - Backup regular de PostgreSQL
3. **Secrets management** - No usar .env en producción
4. **Reverse proxy** - Nginx frente al backend
5. **SSL/TLS** - Certificados para HTTPS
6. **Monitoring** - Prometheus + Grafana
7. **Logging** - Centralizado con ELK stack
8. **Replicas** - Múltiples instancias del backend

Ejemplo producción:

```yaml
backend:
  deploy:
    replicas: 3
    resources:
      limits:
        cpus: '2'
        memory: 2G
  environment:
    DEBUG: "false"
    WORKERS: "4"
    LOG_LEVEL: "WARNING"
```

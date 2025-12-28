# Redis Setup - AI Goals Tracker V2

## Servidor Redis Remoto

**URL**: `redis://YOUR_REDIS_OR_RABBITMQ_HOST:6379`

Este proyecto puede conectarse tanto a Redis local (Docker) como a un servidor Redis remoto.

## Configuración

### Opción 1: Usar Redis Remoto (Producción/Demo)

Editar `backend/.env`:

```bash
REDIS_URL=redis://YOUR_REDIS_OR_RABBITMQ_HOST:6379/0
```

### Opción 2: Usar Redis Local (Desarrollo)

Editar `backend/.env`:

```bash
REDIS_URL=redis://localhost:6379/0
```

Y ejecutar Redis con Docker Compose:

```bash
docker-compose up -d redis
```

## Probar Conexión a Redis Remoto

### Desde línea de comandos (redis-cli)

```bash
# Instalar redis-cli
# macOS
brew install redis

# Linux (Ubuntu/Debian)
sudo apt-get install redis-tools

# Conectar
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379

# Una vez conectado, probar:
PING
# Debe responder: PONG

# Ver todas las keys
KEYS *

# Ver info del servidor
INFO

# Seleccionar database 0
SELECT 0

# Salir
EXIT
```

### Desde Python

```python
import redis

# Conectar
r = redis.from_url("redis://YOUR_REDIS_OR_RABBITMQ_HOST:6379/0")

# Probar conexión
r.ping()  # Debe retornar True

# Set/Get
r.set("test_key", "Hello from AI Goals Tracker!")
value = r.get("test_key")
print(value)  # b'Hello from AI Goals Tracker!'

# Ver todas las keys
keys = r.keys("*")
print(keys)
```

### Desde la aplicación FastAPI

```bash
# Asegurarse que .env tiene la URL correcta
REDIS_URL=redis://YOUR_REDIS_OR_RABBITMQ_HOST:6379/0

# Iniciar backend
cd backend
poetry run uvicorn app.main:app --reload

# Probar health check (incluye Redis)
curl http://localhost:8000/api/v1/health/detailed
```

Deberías ver:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "services": {
    "redis": true,
    "rabbitmq": false  // Si no tienes RabbitMQ remoto
  }
}
```

## Estructura de Keys en Redis

El proyecto usa estos patrones de keys:

### User Sessions
```
user_session:{user_id}
```
Ejemplo:
```json
{
  "connection_id": "ws_conn_123",
  "current_goal_id": "uuid",
  "current_task_id": "uuid",
  "mood_score": 0.8,
  "last_activity": "2025-12-28T00:00:00Z"
}
```

### WebSocket Connections
```
ws_connections:{connection_id}
```
Ejemplo:
```json
{
  "user_id": "uuid",
  "connected_at": "2025-12-28T00:00:00Z",
  "ip": "127.0.0.1"
}
```

### LangGraph Goal State
```
goal_state:{execution_id}
```
Ejemplo:
```json
{
  "goal_id": "uuid",
  "user_id": "uuid",
  "current_node": "nodo_4_feedback",
  "state_data": {...},
  "history": [...]
}
```

### Token Blacklist
```
blacklist:{token}
```
Valor: `"1"` (con TTL)

### Rate Limiting
```
rate_limit:{user_id}
```
Valor: contador (con TTL)

## Ver Datos en Redis

```bash
# Conectar
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379

# Ver todas las sesiones de usuario
KEYS user_session:*

# Ver una sesión específica
GET user_session:test-user-123

# Ver todas las conexiones WebSocket
KEYS ws_connections:*

# Ver estados de goals
KEYS goal_state:*

# Ver tokens en blacklist
KEYS blacklist:*

# Ver rate limits
KEYS rate_limit:*

# Contar keys por patrón
EVAL "return #redis.call('keys', ARGV[1])" 0 "user_session:*"
```

## Limpiar Redis (Reset)

```bash
# Conectar
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379

# CUIDADO: Esto eliminará TODAS las keys
FLUSHDB

# O eliminar solo keys de AI Goals Tracker
EVAL "return redis.call('del', unpack(redis.call('keys', ARGV[1])))" 0 "user_session:*"
EVAL "return redis.call('del', unpack(redis.call('keys', ARGV[1])))" 0 "ws_connections:*"
EVAL "return redis.call('del', unpack(redis.call('keys', ARGV[1])))" 0 "goal_state:*"
```

## Monitoreo en Tiempo Real

```bash
# Ver comandos en tiempo real
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379 MONITOR

# Ver estadísticas
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379 INFO stats

# Ver memoria usada
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379 INFO memory
```

## Configuración Avanzada

### Usar Redis con Autenticación

Si el servidor Redis requiere password:

```bash
# En .env
REDIS_URL=redis://:password@YOUR_REDIS_OR_RABBITMQ_HOST:6379/0
```

### Usar Redis con TLS/SSL

```bash
# En .env
REDIS_URL=rediss://YOUR_REDIS_OR_RABBITMQ_HOST:6380/0
```

### Configurar Timeout

Editar `backend/app/core/redis_client.py`:

```python
_redis_client = await redis.from_url(
    settings.REDIS_URL,
    max_connections=settings.REDIS_MAX_CONNECTIONS,
    encoding="utf-8",
    decode_responses=True,
    socket_timeout=5,  # Agregar timeout
    socket_connect_timeout=5,  # Timeout de conexión
)
```

## Troubleshooting

### Error: Connection refused

```bash
# Verificar que el servidor esté accesible
ping YOUR_REDIS_OR_RABBITMQ_HOST

# Probar telnet al puerto
telnet YOUR_REDIS_OR_RABBITMQ_HOST 6379

# Si no responde, verificar firewall
```

### Error: NOAUTH Authentication required

```bash
# El servidor requiere password
# Agregar password en REDIS_URL
REDIS_URL=redis://:tu-password@YOUR_REDIS_OR_RABBITMQ_HOST:6379/0
```

### Error: Connection timeout

```bash
# Aumentar timeout en redis_client.py
socket_timeout=10
socket_connect_timeout=10
```

### Redis lento

```bash
# Ver slow queries
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379 SLOWLOG GET 10

# Ver latencia
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379 --latency
```

## Comparación: Local vs Remoto

| Aspecto | Redis Local | Redis Remoto |
|---------|-------------|--------------|
| Latencia | <1ms | 10-50ms |
| Disponibilidad | Solo en tu máquina | 24/7 (si servidor está up) |
| Datos | Volátiles (Docker) | Persistentes |
| Configuración | Automática (Docker Compose) | Manual |
| Costo | Gratis | Según proveedor |

## Recomendaciones

### Para Desarrollo Local
- Usar Redis local con Docker
- Más rápido
- No depende de internet
- Fácil de resetear

### Para Demo/Testing
- Usar Redis remoto
- Datos compartidos entre instancias
- Accesible desde cualquier lugar
- Persistencia

### Para Producción
- Usar Redis gestionado (AWS ElastiCache, Redis Cloud)
- Clustering para alta disponibilidad
- Backups automáticos
- Monitoreo incluido

## Scripts Útiles

### Backup de Redis

```bash
# Conectar y hacer snapshot
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379 BGSAVE

# Exportar todas las keys a JSON (script Python)
python scripts/redis_backup.py
```

### Restore de Redis

```bash
# Importar desde JSON
python scripts/redis_restore.py backup.json
```

## Próximos Pasos

1. Verificar conexión a Redis remoto
2. Configurar `.env` con la URL correcta
3. Probar backend con Redis remoto
4. Monitorear uso de memoria
5. Configurar TTL apropiados para cada tipo de key

---

**Servidor Redis**: `YOUR_REDIS_OR_RABBITMQ_HOST:6379`
**Database**: 0 (por defecto)
**Uso actual**: AI Goals Tracker V2

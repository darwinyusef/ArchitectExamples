# Redis Configuration - AI Goals Tracker V2

## 🌐 Servidor Redis Remoto Configurado

Tu proyecto está configurado para usar un servidor Redis remoto:

```
Host: YOUR_REDIS_OR_RABBITMQ_HOST
Port: 6379
URL: redis://YOUR_REDIS_OR_RABBITMQ_HOST:6379/0
```

## 🚀 Inicio Rápido

### Opción 1: Script Automático (Recomendado)

```bash
./start-with-remote-redis.sh
```

Este script:
1. ✅ Verifica configuración
2. ✅ Prueba conexión a Redis remoto
3. ✅ Inicia servicios (PostgreSQL, RabbitMQ, MinIO, Backend)
4. ✅ Verifica que todo esté funcionando

### Opción 2: Manual

```bash
# 1. Crear .env
cp .env.example .env

# 2. Verificar que REDIS_URL apunta al servidor remoto
grep REDIS_URL .env
# Debe mostrar: REDIS_URL=redis://YOUR_REDIS_OR_RABBITMQ_HOST:6379/0

# 3. Iniciar servicios
docker-compose up -d

# 4. Verificar
curl http://localhost:8000/api/v1/health/detailed
```

## 🧪 Probar Conexión a Redis

### Desde Python

```bash
cd backend
python scripts/test_redis.py
```

Deberías ver:
```
✅ Test 1: PING
   Resultado: True
✅ Test 2: INFO Server
   Redis Version: 7.x.x
✅ Test 3: SET/GET
...
✅ TODAS LAS PRUEBAS PASARON
```

### Desde redis-cli

```bash
# Instalar redis-cli
brew install redis  # macOS
# o
sudo apt install redis-tools  # Linux

# Conectar
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379

# Comandos útiles
> PING
PONG

> INFO server
# ... información del servidor

> KEYS *
# ... listar todas las keys

> GET user_session:test-user-123
# ... ver una sesión

> EXIT
```

## 📊 Monitorear Redis en Tiempo Real

```bash
# Ver todos los comandos ejecutándose
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379 MONITOR

# Ver estadísticas
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379 INFO stats

# Ver memoria usada
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379 INFO memory
```

## 🔍 Explorar Datos

### Ver Sesiones de Usuario

```bash
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379

> KEYS user_session:*
1) "user_session:test-user-123"

> HGETALL user_session:test-user-123
1) "connection_id"
2) "ws_conn_abc123"
3) "current_goal_id"
4) "goal-xyz"
...
```

### Ver Conexiones WebSocket

```bash
> KEYS ws_connections:*
> GET ws_connections:abc-123-xyz
```

### Ver Estados de Goals (LangGraph)

```bash
> KEYS goal_state:*
> GET goal_state:execution-123
```

## 🧹 Limpiar Datos de Prueba

```bash
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379

# Listar keys de AI Goals Tracker
> KEYS ai_goals_tracker:*
> KEYS user_session:*
> KEYS goal_state:*

# Eliminar una key específica
> DEL user_session:test-user-123

# CUIDADO: Eliminar TODAS las keys (solo en desarrollo)
> FLUSHDB
```

## ⚙️ Configuración en el Código

### Backend ya está configurado

El archivo `backend/.env.example` ya tiene:

```bash
REDIS_URL=redis://YOUR_REDIS_OR_RABBITMQ_HOST:6379/0
```

### Ver configuración actual

```bash
# Ver qué REDIS_URL está usando el backend
docker-compose exec backend env | grep REDIS_URL
```

### Cambiar entre Redis local y remoto

Editar `backend/.env`:

```bash
# Usar Redis remoto (actual)
REDIS_URL=redis://YOUR_REDIS_OR_RABBITMQ_HOST:6379/0

# O usar Redis local
# REDIS_URL=redis://localhost:6379/0
```

## 📈 Ventajas del Redis Remoto

✅ **Datos compartidos**: Múltiples instancias pueden compartir estado
✅ **Persistencia**: Los datos sobreviven a reinicios de Docker
✅ **Colaboración**: Varios developers pueden ver los mismos datos
✅ **Testing**: Perfecto para demos y pruebas
✅ **Sin Docker local**: No necesitas Redis en tu máquina

## ⚠️ Consideraciones

- **Latencia**: ~10-50ms vs <1ms local
- **Seguridad**: No usar en producción sin autenticación
- **Datos**: Compartidos con otros que usen el mismo servidor
- **Internet**: Requiere conexión a internet

## 🔒 Seguridad

### Para Producción

Si usas Redis remoto en producción, asegúrate de:

1. **Usar password**:
   ```bash
   REDIS_URL=redis://:your-password@YOUR_REDIS_OR_RABBITMQ_HOST:6379/0
   ```

2. **Usar TLS/SSL**:
   ```bash
   REDIS_URL=rediss://YOUR_REDIS_OR_RABBITMQ_HOST:6380/0
   ```

3. **Firewall**: Limitar acceso por IP
4. **Monitoring**: Configurar alertas
5. **Backups**: Configurar snapshots automáticos

## 🆘 Troubleshooting

### Error: Connection refused

```bash
# Verificar conectividad
ping YOUR_REDIS_OR_RABBITMQ_HOST
telnet YOUR_REDIS_OR_RABBITMQ_HOST 6379

# Si no responde:
# 1. Verificar que la IP es correcta
# 2. Verificar que no hay firewall bloqueando
# 3. Verificar que Redis está corriendo en el servidor
```

### Error: Connection timeout

```bash
# Aumentar timeout en app/core/redis_client.py
socket_timeout=10
socket_connect_timeout=10
```

### Backend dice "redis: false" en health check

```bash
# Ver logs del backend
docker-compose logs backend | grep -i redis

# Verificar REDIS_URL
docker-compose exec backend env | grep REDIS_URL

# Probar conexión manualmente
docker-compose exec backend python -c "
import redis
r = redis.from_url('redis://YOUR_REDIS_OR_RABBITMQ_HOST:6379/0')
print(r.ping())
"
```

## 📚 Documentación Relacionada

- `REDIS_SETUP.md` - Guía completa de Redis
- `DEPLOYMENT_OPTIONS.md` - Diferentes opciones de deployment
- `QUICKSTART.md` - Inicio rápido del proyecto

## 🎯 Próximos Pasos

1. ✅ Ejecutar `./start-with-remote-redis.sh`
2. ✅ Verificar que backend se conecta a Redis
3. ✅ Probar operaciones básicas con `python backend/scripts/test_redis.py`
4. ✅ Iniciar frontend y probar conexión WebSocket
5. ✅ Ver datos en Redis con `redis-cli`

---

**Redis Server**: `YOUR_REDIS_OR_RABBITMQ_HOST:6379`
**Status**: ✅ Configurado y listo para usar

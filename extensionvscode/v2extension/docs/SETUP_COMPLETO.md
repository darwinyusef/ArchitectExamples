# Setup Completo - AI Goals Tracker V2

Guía paso a paso para configurar el proyecto usando la API key de v1extension.

## 🎯 Resumen

1. Migrar OpenAI API Key desde v1extension
2. Configurar variables de entorno
3. Iniciar servicios con Redis remoto
4. Verificar funcionamiento
5. Iniciar frontend

---

## Paso 1: Migrar OpenAI API Key (30 segundos)

La API key de OpenAI está configurada en v1extension. Vamos a migrarla automáticamente:

```bash
cd v2extension
./migrate-api-key.sh
```

Este script:
1. ✅ Busca la API key en v1extension
2. ✅ Genera un SECRET_KEY aleatorio
3. ✅ Crea/actualiza `.env` con las keys
4. ✅ Actualiza `backend/.env` también

### Alternativa: Manual

Si prefieres configurar manualmente:

```bash
# Obtener API key de v1extension
cat ../v1extension/settings.example.json | grep openaiApiKey

# O desde VS Code settings
# macOS:
cat "$HOME/Library/Application Support/Code/User/settings.json" | grep openaiApiKey

# Crear .env
cp .env.example .env

# Editar .env
nano .env

# Agregar:
OPENAI_API_KEY=sk-tu-key-de-v1extension
SECRET_KEY=$(openssl rand -hex 32)
```

---

## Paso 2: Verificar Configuración (10 segundos)

```bash
# Verificar que .env tiene las keys
cat .env | grep -E "OPENAI_API_KEY|SECRET_KEY|REDIS_URL"
```

Deberías ver:
```bash
OPENAI_API_KEY=sk-...  # Tu key de v1extension
SECRET_KEY=...         # String aleatorio de 64 caracteres
REDIS_URL=redis://YOUR_REDIS_OR_RABBITMQ_HOST:6379/0  # Redis remoto
```

---

## Paso 3: Iniciar Servicios (2 minutos)

```bash
./start-with-remote-redis.sh
```

Este script:
1. ✅ Verifica que .env esté configurado
2. ✅ Prueba conexión a Redis remoto
3. ✅ Inicia PostgreSQL, RabbitMQ, MinIO, Backend
4. ✅ Verifica que todos los servicios estén healthy

Deberías ver:
```
✅ Redis remoto accesible (YOUR_REDIS_OR_RABBITMQ_HOST:6379)
✅ Docker está corriendo
✅ PostgreSQL listo
✅ Backend API respondiendo

🌐 URLs disponibles:
   - Backend API:      http://localhost:8000
   - API Docs:         http://localhost:8000/docs
   ...
```

---

## Paso 4: Verificar Funcionamiento (1 minuto)

### Test 1: Backend Health

```bash
curl http://localhost:8000/health
```

Debe responder:
```json
{
  "status": "healthy",
  "service": "AI Goals Tracker API",
  "version": "2.0.0"
}
```

### Test 2: Health Check Detallado

```bash
curl http://localhost:8000/api/v1/health/detailed
```

Debe mostrar:
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "services": {
    "redis": true,      ✅
    "rabbitmq": true    ✅
  }
}
```

### Test 3: Redis Remoto

```bash
python backend/scripts/test_redis.py
```

Debe pasar todos los tests:
```
✅ Test 1: PING
✅ Test 2: INFO Server
✅ Test 3: SET/GET
...
✅ TODAS LAS PRUEBAS PASARON
```

### Test 4: Probar API Docs

```bash
open http://localhost:8000/docs
```

Deberías ver la interfaz interactiva de FastAPI.

---

## Paso 5: Iniciar Frontend (2 minutos)

```bash
cd frontend
npm install
npm run compile
```

Luego en VS Code:

```bash
code .
```

Presionar `F5` para ejecutar la extensión en modo debug.

Se abrirá una nueva ventana de VS Code con la extensión cargada:
1. ✅ Buscar icono "AI Goals Tracker" en la barra lateral
2. ✅ Ver estado de conexión
3. ✅ Conectar al backend (automático)

---

## Verificación Completa

### Checklist de Servicios

```bash
# 1. PostgreSQL
docker-compose exec postgres pg_isready
# Debe responder: /var/run/postgresql:5432 - accepting connections ✅

# 2. Redis Remoto
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379 PING
# Debe responder: PONG ✅

# 3. RabbitMQ
curl http://localhost:15672
# Debe mostrar la UI ✅

# 4. MinIO
curl http://localhost:9001
# Debe mostrar la UI ✅

# 5. Backend
curl http://localhost:8000/health
# Debe responder JSON ✅
```

### Checklist de Configuración

```bash
# OpenAI API Key configurada
grep OPENAI_API_KEY .env
# Debe mostrar: OPENAI_API_KEY=sk-... ✅

# Secret Key configurada
grep SECRET_KEY .env
# Debe mostrar: SECRET_KEY=... (64 chars) ✅

# Redis URL correcta
grep REDIS_URL .env
# Debe mostrar: REDIS_URL=redis://YOUR_REDIS_OR_RABBITMQ_HOST:6379/0 ✅
```

---

## Solución de Problemas

### Problema: migrate-api-key.sh no encuentra la key

**Solución**:
```bash
# Buscar manualmente
cat ../v1extension/settings.example.json | grep openaiApiKey

# O desde VS Code settings (macOS)
cat "$HOME/Library/Application Support/Code/User/settings.json" | grep openaiApiKey

# Copiar la key y agregarla manualmente a .env
echo "OPENAI_API_KEY=sk-tu-key-aqui" >> .env
```

### Problema: Backend no se conecta a Redis remoto

**Solución**:
```bash
# Probar conectividad
ping YOUR_REDIS_OR_RABBITMQ_HOST
telnet YOUR_REDIS_OR_RABBITMQ_HOST 6379

# Verificar REDIS_URL en .env
cat .env | grep REDIS_URL

# Ver logs del backend
docker-compose logs backend | grep -i redis
```

### Problema: Backend dice "redis: false"

**Solución**:
```bash
# Verificar que Redis remoto está accesible
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379 PING

# Reiniciar backend
docker-compose restart backend

# Ver logs
docker-compose logs -f backend
```

### Problema: Frontend no compila

**Solución**:
```bash
cd frontend

# Limpiar node_modules
rm -rf node_modules package-lock.json

# Reinstalar
npm install

# Compilar
npm run compile
```

---

## Comandos Útiles

### Ver Logs

```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo PostgreSQL
docker-compose logs -f postgres
```

### Reiniciar Servicios

```bash
# Todos
docker-compose restart

# Solo backend
docker-compose restart backend
```

### Detener Todo

```bash
docker-compose down

# Con borrado de volúmenes (reset completo)
docker-compose down -v
```

---

## Flujo de Trabajo Diario

### Inicio del Día

```bash
# 1. Verificar que Docker está corriendo
docker ps

# 2. Iniciar servicios si no están corriendo
docker-compose up -d

# 3. Verificar health
curl http://localhost:8000/health

# 4. Abrir frontend en VS Code
cd frontend && code .
```

### Desarrollo

```bash
# Terminal 1: Ver logs del backend
docker-compose logs -f backend

# Terminal 2: Desarrollo del backend
cd backend
poetry run uvicorn app.main:app --reload

# Terminal 3: Desarrollo del frontend
cd frontend
npm run watch
```

### Fin del Día

```bash
# Detener servicios (datos se mantienen)
docker-compose down

# O dejarlos corriendo para el día siguiente
# (recomendado si usas Redis remoto)
```

---

## URLs de Referencia

### Aplicación
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Servicios
- RabbitMQ: http://localhost:15672 (guest/guest)
- MinIO: http://localhost:9001 (minioadmin/minioadmin)

### Redis Remoto
```bash
redis-cli -h YOUR_REDIS_OR_RABBITMQ_HOST -p 6379
```

---

## Próximos Pasos

Después del setup:

1. **Leer la arquitectura**
   ```bash
   cat ARQUITECTURA-TECNICA.md
   ```

2. **Explorar el código**
   - Backend: `backend/app/`
   - Frontend: `frontend/src/`

3. **Ejecutar tests**
   ```bash
   python backend/scripts/test_redis.py
   ```

4. **Empezar a desarrollar**
   - Ver `GETTING_STARTED.md` para ejemplos
   - Implementar modelos de DB
   - Crear tools de LangGraph

---

**¡Setup Completado!** 🎉

Tienes:
- ✅ OpenAI API Key migrada desde v1extension
- ✅ Servicios corriendo (PostgreSQL, RabbitMQ, MinIO, Backend)
- ✅ Redis remoto conectado
- ✅ Frontend compilado y listo

**Siguiente**: `./start-with-remote-redis.sh` y empezar a codear!

# Solución: Error de Conexión a Redis

## El Problema

```
redis.exceptions.ConnectionError: Error 22 connecting to localhost:6379.
El equipo remoto rechazó la conexión de red.
ERROR: Application startup failed. Exiting.
```

## ✅ Solución Implementada

He modificado la API para que **Redis sea completamente opcional**. Ahora la aplicación:

1. ✅ **Inicia sin Redis**: No falla si Redis no está disponible
2. ✅ **Funciona normalmente**: Todas las cotizaciones funcionan
3. ⚠️ **Sin cache ni pub/sub**: Características de Redis deshabilitadas automáticamente

## 🚀 Cómo Iniciar la API Ahora

```bash
# Simplemente inicia la API (sin Redis)
python api_fastapi_laser.py
```

**Verás esto:**
```
Cargando modelo ONNX: costos_cajas_laser.onnx
✅ Modelo ONNX cargado exitosamente
⚠️  Redis no disponible: Error 22 connecting to localhost:6379...
⚠️  La API funcionará sin cache ni pub/sub
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**La API funciona perfectamente sin Redis!** 🎉

## 🌐 Acceder a la Aplicación

Abre tu navegador:
- **Cotizaciones**: http://localhost:8000
- **MLOps Dashboard**: http://localhost:8000/mlops
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🔍 Verificar Estado

```bash
curl http://localhost:8000/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "modelo_onnx": "ok",
  "redis": "not available (optional)",
  "timestamp": "2024-01-15T10:30:00"
}
```

## 📊 Qué Funciona Sin Redis

### ✅ Funcionan Perfectamente:
- ✅ Interfaz web de cotizaciones
- ✅ Cotizaciones individuales y en lote
- ✅ Productos predefinidos
- ✅ **MLOps Dashboard completo**
- ✅ Exploración de experimentos MLflow
- ✅ Comparación de runs
- ✅ Descarga de artefactos
- ✅ Toda la API REST
- ✅ Historial en navegador (localStorage)

### ⚠️ No Disponibles Sin Redis:
- ❌ Cache de cotizaciones (endpoint `/api/v1/cotizar/{id}`)
- ❌ Sistema pub/sub (servicios separados)
- ❌ Historial persistente en servidor

## 🔧 Si Quieres Usar Redis (Opcional)

### Opción 1: Redis Local (Windows)

1. **Descargar Redis para Windows:**
   - https://github.com/microsoftarchive/redis/releases
   - Descargar `Redis-x64-3.0.504.msi`

2. **Instalar y ejecutar:**
   ```bash
   redis-server
   ```

3. **Configurar `.env`:**
   ```bash
   REDIS_URL=redis://localhost:6379/0
   ```

4. **Reiniciar API:**
   ```bash
   python api_fastapi_laser.py
   ```

### Opción 2: Redis con Docker

```bash
docker run -d -p 6379:6379 redis:alpine
```

### Opción 3: Redis Remoto

Edita `.env`:
```bash
REDIS_URL=redis://tu-servidor.com:6379/0
```

## 🧪 Probar Ahora

```bash
# 1. Iniciar API
python api_fastapi_laser.py

# 2. Probar cotización
curl -X POST "http://localhost:8000/api/v1/cotizar" \
  -H "Content-Type: application/json" \
  -d '{"tiempo_seg": 360, "material_cm2": 24, "energia_kwh": 0.025}'

# 3. Abrir interfaz web
# http://localhost:8000
```

## 🎯 Recomendación

**Para desarrollo:**
- ✅ Sin Redis está perfecto
- Todo funciona
- Más simple

**Para producción:**
- ✅ Usar Redis
- Mejor performance con cache
- Microservicios disponibles

## ✨ Resumen

| Característica | Sin Redis | Con Redis |
|----------------|-----------|-----------|
| Cotizaciones | ✅ | ✅ |
| MLOps Dashboard | ✅ | ✅ |
| Interfaz Web | ✅ | ✅ |
| API REST | ✅ | ✅ |
| Cache de resultados | ❌ | ✅ |
| Pub/Sub | ❌ | ✅ |
| Microservicios | ❌ | ✅ |

**¡Ahora puedes usar la aplicación inmediatamente!** 🚀

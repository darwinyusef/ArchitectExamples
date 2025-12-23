# 🐳 Docker Quick Reference

Guía rápida de referencia para los archivos Docker Compose del proyecto.

---

## 📦 Archivos Docker Compose

| Archivo | Descripción | Cuándo Usar |
|---------|-------------|-------------|
| `docker-compose.full.yml` | **Sistema completo** con Whisper | Producción, testing completo |
| `docker-compose.dev.yml` | Solo servicios externos | Desarrollo activo |
| `docker-compose.whisper.yml` | Solo Whisper API | Probar Whisper standalone |
| `docker-compose.yml` | Sistema sin Whisper | Ya tienes Whisper |

---

## 🚀 Comandos Rápidos

### Con Script `manage.sh` (Recomendado)

```bash
# Sistema completo
./manage.sh start full

# Solo servicios (desarrollo)
./manage.sh start dev

# Solo Whisper
./manage.sh start whisper

# Ver estado
./manage.sh status

# Ver logs
./manage.sh logs backend

# Verificar salud
./manage.sh health

# Detener todo
./manage.sh stop

# Limpiar todo
./manage.sh clean
```

### Con Docker Compose Directo

```bash
# INICIAR
docker-compose -f docker-compose.full.yml up -d      # Sistema completo
docker-compose -f docker-compose.dev.yml up -d       # Solo servicios
docker-compose -f docker-compose.whisper.yml up -d   # Solo Whisper
docker-compose up -d                                 # Sistema básico

# DETENER
docker-compose -f docker-compose.full.yml down

# LOGS
docker-compose -f docker-compose.full.yml logs -f backend

# ESTADO
docker-compose -f docker-compose.full.yml ps

# RECONSTRUIR
docker-compose -f docker-compose.full.yml up -d --build
```

---

## 🎯 Escenarios Comunes

### Escenario 1: Primera Vez (Todo nuevo)
```bash
# Opción A: Con script
./manage.sh start full

# Opción B: Directo
docker-compose -f docker-compose.full.yml up -d
```

**Esperar 2-3 min** para que Whisper descargue el modelo la primera vez.

---

### Escenario 2: Desarrollo Activo
```bash
# 1. Iniciar servicios
./manage.sh start dev
# o
docker-compose -f docker-compose.dev.yml up -d

# 2. Backend local (terminal 1)
cd backend
source venv/bin/activate
python main.py

# 3. Frontend local (terminal 2)
cd frontend
npm run dev
```

---

### Escenario 3: Ya Tengo Whisper Corriendo
```bash
# Configurar URL en .env
echo "WHISPER_API_URL=http://localhost:9000" >> backend/.env

# Iniciar sin Whisper
docker-compose up -d
```

---

### Escenario 4: Solo Probar Whisper
```bash
./manage.sh start whisper
# o
docker-compose -f docker-compose.whisper.yml up -d

# Test
curl http://localhost:9000/health
open http://localhost:9000/docs
```

---

## 🔌 Puertos Usados

| Servicio | Puerto | URL |
|----------|--------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend API | 8001 | http://localhost:8001 |
| Backend API Docs | 8001 | http://localhost:8001/docs |
| gRPC Server | 50051 | localhost:50051 |
| Envoy (gRPC-Web) | 8080 | http://localhost:8080 |
| Envoy Admin | 9901 | http://localhost:9901 |
| RabbitMQ AMQP | 5672 | amqp://localhost:5672 |
| RabbitMQ UI | 15672 | http://localhost:15672 |
| Whisper API | 9000 | http://localhost:9000 |
| Whisper Docs | 9000 | http://localhost:9000/docs |

---

## 📊 Servicios por Configuración

### `docker-compose.full.yml` ⭐
- ✅ Backend (FastAPI + gRPC)
- ✅ Frontend (React)
- ✅ RabbitMQ
- ✅ Whisper API
- ✅ Envoy Proxy
- ✅ Consumer (opcional con `--profile with-consumer`)

### `docker-compose.dev.yml`
- ✅ RabbitMQ
- ✅ Whisper API
- ✅ Envoy Proxy
- ❌ Backend (correr localmente)
- ❌ Frontend (correr localmente)

### `docker-compose.whisper.yml`
- ✅ Whisper API
- ❌ Todo lo demás

### `docker-compose.yml`
- ✅ Backend (FastAPI + gRPC)
- ✅ Frontend (React)
- ✅ RabbitMQ
- ✅ Envoy Proxy
- ❌ Whisper (usar externo)

---

## 🛠️ Comandos Útiles

### Ver Logs
```bash
# Todos los servicios
docker-compose -f docker-compose.full.yml logs -f

# Un servicio
docker-compose -f docker-compose.full.yml logs -f backend

# Últimas 50 líneas
docker-compose -f docker-compose.full.yml logs --tail=50 backend
```

### Ejecutar Comandos
```bash
# Shell en backend
docker-compose -f docker-compose.full.yml exec backend bash

# Ejecutar script
docker-compose -f docker-compose.full.yml exec backend python test_api.py

# Ver archivos proto generados
docker-compose -f docker-compose.full.yml exec backend ls -la proto/
```

### Reiniciar Servicios
```bash
# Reiniciar un servicio
docker-compose -f docker-compose.full.yml restart backend

# Reiniciar todo
docker-compose -f docker-compose.full.yml restart
```

### Verificar Estado
```bash
# Estado de servicios
docker-compose -f docker-compose.full.yml ps

# Recursos usados
docker stats

# Health checks
./manage.sh health
```

---

## 🐛 Troubleshooting Rápido

### Puerto Ocupado
```bash
# Ver qué usa el puerto
lsof -i :8001

# Cambiar puerto en docker-compose.full.yml
# O matar el proceso
kill -9 <PID>
```

### Whisper No Inicia
```bash
# Ver logs
docker-compose -f docker-compose.full.yml logs whisper

# Primera vez tarda 1-2 min descargando modelo
# Esperar mensaje: "Application startup complete"
```

### Backend No Conecta a RabbitMQ
```bash
# Verificar RabbitMQ esté healthy
docker-compose -f docker-compose.full.yml ps rabbitmq

# Reiniciar en orden
docker-compose -f docker-compose.full.yml restart rabbitmq
sleep 5
docker-compose -f docker-compose.full.yml restart backend
```

### Limpiar Todo
```bash
# Con script
./manage.sh clean

# O directo (sin volúmenes)
docker-compose -f docker-compose.full.yml down

# Con volúmenes
docker-compose -f docker-compose.full.yml down -v

# Con volúmenes e imágenes
docker-compose -f docker-compose.full.yml down -v --rmi all
```

---

## ⚙️ Configuración

### Cambiar Modelo de Whisper

Editar `docker-compose.full.yml`:
```yaml
whisper:
  environment:
    - ASR_MODEL=small  # tiny, base, small, medium, large
```

Reiniciar:
```bash
docker-compose -f docker-compose.full.yml restart whisper
```

### Cambiar Puerto del Backend

Editar `docker-compose.full.yml`:
```yaml
backend:
  ports:
    - "8002:8001"  # Cambiar puerto externo
```

### Usar GPU para Whisper

Editar `docker-compose.full.yml`:
```yaml
whisper:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

---

## 📝 Health Checks

Verificar que servicios estén saludables:

```bash
# Backend
curl http://localhost:8001/health

# Whisper
curl http://localhost:9000/health

# RabbitMQ
curl http://localhost:15672

# Envoy
curl http://localhost:9901/ready

# Frontend
curl http://localhost:3000
```

O usar el script:
```bash
./manage.sh health
```

---

## 🔄 Workflow Típico

### Desarrollo
```bash
# 1. Iniciar servicios
./manage.sh start dev

# 2. Backend (terminal 1)
cd backend && source venv/bin/activate && python main.py

# 3. Frontend (terminal 2)
cd frontend && npm run dev

# 4. Ver logs cuando necesites
./manage.sh logs rabbitmq
```

### Testing
```bash
# 1. Iniciar todo
./manage.sh start full

# 2. Esperar que todo esté healthy
./manage.sh health

# 3. Probar en navegador
open http://localhost:3000

# 4. Ver logs
./manage.sh logs backend
```

### Producción
```bash
# 1. Revisar configuración
cat backend/.env

# 2. Iniciar
docker-compose -f docker-compose.full.yml up -d

# 3. Verificar
./manage.sh status
./manage.sh health

# 4. Monitorear
./manage.sh logs
```

---

## 📚 Más Información

- **[DOCKER_GUIDE.md](./DOCKER_GUIDE.md)** - Guía completa de Docker
- **[QUICKSTART.md](./QUICKSTART.md)** - Inicio rápido
- **[README.md](./README.md)** - Documentación principal

---

## 💡 Tips

✅ **DO:**
- Usar `./manage.sh` para operaciones comunes
- Verificar health después de iniciar servicios
- Usar `docker-compose.dev.yml` para desarrollo
- Revisar logs cuando algo falle

❌ **DON'T:**
- Olvidar esperar a que Whisper descargue el modelo
- Mezclar diferentes docker-compose sin detener primero
- Eliminar volúmenes sin hacer backup
- Exponer servicios a internet sin seguridad

---

**Última actualización:** Diciembre 2024

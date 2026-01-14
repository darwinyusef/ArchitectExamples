# 🐳 Guía de Docker Compose

Esta guía explica los diferentes archivos Docker Compose disponibles y cuándo usar cada uno.

---

## 📋 Archivos Disponibles

### 1. `docker-compose.yml` (Original - Completo)
Sistema completo con backend construido desde código fuente.

**Incluye:**
- ✅ Backend (FastAPI + gRPC) - build local
- ✅ Frontend (React) - build local
- ✅ RabbitMQ
- ✅ Envoy proxy
- ❌ Whisper (usa local o API externa)

**Cuándo usar:** Cuando quieres todo el sistema pero ya tienes Whisper configurado.

---

### 2. `docker-compose.whisper.yml` (Solo Whisper)
Solo el servicio de Whisper API.

**Incluye:**
- ✅ Whisper API standalone

**Cuándo usar:**
- Solo necesitas Whisper
- Desarrollo local del backend/frontend
- Complementar otros Docker Compose

**Iniciar:**
```bash
docker-compose -f docker-compose.whisper.yml up -d
```

**Verificar:**
```bash
# Whisper funcionando
curl http://localhost:9000/health

# Ver docs
open http://localhost:9000/docs
```

---

### 3. `docker-compose.full.yml` (Sistema Completo) ⭐ RECOMENDADO
**TODO** el sistema incluyendo Whisper.

**Incluye:**
- ✅ Backend (FastAPI + gRPC)
- ✅ Frontend (React)
- ✅ RabbitMQ
- ✅ Whisper API
- ✅ Envoy proxy
- ✅ Consumer (opcional)

**Cuándo usar:** Producción o cuando quieres todo funcionando con un comando.

**Iniciar:**
```bash
# Sistema completo
docker-compose -f docker-compose.full.yml up -d

# Con consumer de RabbitMQ
docker-compose -f docker-compose.full.yml --profile with-consumer up -d
```

**Servicios disponibles:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs
- gRPC: localhost:50051
- gRPC-Web: http://localhost:8080
- RabbitMQ UI: http://localhost:15672
- Whisper API: http://localhost:9000
- Envoy Admin: http://localhost:9901

---

### 4. `docker-compose.dev.yml` (Solo Servicios Externos)
Solo servicios externos, backend/frontend locales.

**Incluye:**
- ✅ RabbitMQ
- ✅ Whisper API
- ✅ Envoy proxy
- ❌ Backend (correr localmente)
- ❌ Frontend (correr localmente)

**Cuándo usar:** Desarrollo activo del backend/frontend con hot-reload.

**Workflow:**
```bash
# 1. Iniciar servicios
docker-compose -f docker-compose.dev.yml up -d

# 2. Backend (terminal 1)
cd backend
source venv/bin/activate
python main.py

# 3. Frontend (terminal 2)
cd frontend
npm run dev
```

---

## 🚀 Guía Rápida por Escenario

### Escenario 1: Primera vez, quiero probar todo
```bash
docker-compose -f docker-compose.full.yml up -d
```
Esperar 2-3 minutos para que Whisper descargue el modelo.

---

### Escenario 2: Desarrollo activo
```bash
# Iniciar solo servicios
docker-compose -f docker-compose.dev.yml up -d

# Backend local
cd backend && python main.py

# Frontend local
cd frontend && npm run dev
```

---

### Escenario 3: Solo necesito Whisper
```bash
docker-compose -f docker-compose.whisper.yml up -d
```

---

### Escenario 4: Ya tengo Whisper corriendo
```bash
# Configurar .env
echo "WHISPER_API_URL=http://localhost:9000" >> backend/.env

# Iniciar sistema sin Whisper
docker-compose up -d
```

---

## 🛠️ Comandos Útiles

### Ver logs
```bash
# Todos los servicios
docker-compose -f docker-compose.full.yml logs -f

# Un servicio específico
docker-compose -f docker-compose.full.yml logs -f backend

# Últimas 100 líneas
docker-compose -f docker-compose.full.yml logs --tail=100 backend
```

### Estado de servicios
```bash
docker-compose -f docker-compose.full.yml ps
```

### Detener servicios
```bash
# Detener
docker-compose -f docker-compose.full.yml down

# Detener y eliminar volúmenes
docker-compose -f docker-compose.full.yml down -v
```

### Reconstruir servicios
```bash
# Reconstruir todo
docker-compose -f docker-compose.full.yml up -d --build

# Reconstruir solo backend
docker-compose -f docker-compose.full.yml up -d --build backend
```

### Ejecutar comandos en contenedores
```bash
# Shell en backend
docker-compose -f docker-compose.full.yml exec backend bash

# Ver archivos Python generados
docker-compose -f docker-compose.full.yml exec backend ls -la proto/

# Test API desde contenedor
docker-compose -f docker-compose.full.yml exec backend python test_api.py
```

### Reiniciar un servicio
```bash
docker-compose -f docker-compose.full.yml restart backend
```

### Ver recursos usados
```bash
docker stats
```

---

## 🔧 Configuración

### Cambiar modelo de Whisper

**En docker-compose.full.yml:**
```yaml
whisper:
  environment:
    - ASR_MODEL=small  # tiny, base, small, medium, large
```

**Reiniciar:**
```bash
docker-compose -f docker-compose.full.yml up -d whisper
```

### Usar GPU para Whisper

**Requisitos:**
- NVIDIA GPU
- nvidia-docker instalado

**En docker-compose.full.yml:**
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

### Cambiar puertos

**En docker-compose.full.yml:**
```yaml
backend:
  ports:
    - "8002:8001"  # Cambiar puerto externo
```

---

## 🐛 Troubleshooting

### Whisper no inicia / se queda cargando
```bash
# Ver logs
docker-compose -f docker-compose.full.yml logs -f whisper

# Primera vez descarga el modelo (1-2 min)
# Esperar hasta ver: "Application startup complete"
```

### Backend no conecta a RabbitMQ
```bash
# Verificar que RabbitMQ esté healthy
docker-compose -f docker-compose.full.yml ps

# Ver logs de RabbitMQ
docker-compose -f docker-compose.full.yml logs rabbitmq

# Reiniciar orden correcto
docker-compose -f docker-compose.full.yml up -d rabbitmq
docker-compose -f docker-compose.full.yml up -d backend
```

### Frontend no carga
```bash
# Verificar que node_modules se instaló
docker-compose -f docker-compose.full.yml exec frontend ls -la node_modules

# Reconstruir frontend
docker-compose -f docker-compose.full.yml up -d --build frontend

# Ver logs
docker-compose -f docker-compose.full.yml logs -f frontend
```

### Puerto ocupado
```bash
# Ver qué usa el puerto
lsof -i :8001

# Cambiar puerto en docker-compose
# O detener el proceso que lo usa
```

### Limpiar todo y empezar de cero
```bash
# Detener y eliminar todo
docker-compose -f docker-compose.full.yml down -v

# Eliminar imágenes
docker-compose -f docker-compose.full.yml down --rmi all

# Reiniciar
docker-compose -f docker-compose.full.yml up -d --build
```

---

## 📊 Health Checks

Verificar que todos los servicios estén saludables:

```bash
# RabbitMQ
curl http://localhost:15672

# Whisper
curl http://localhost:9000/health

# Backend
curl http://localhost:8001/health

# Envoy
curl http://localhost:9901/ready

# Frontend
curl http://localhost:3000
```

---

## 🔐 Seguridad (Producción)

### Cambiar credenciales de RabbitMQ

```yaml
rabbitmq:
  environment:
    - RABBITMQ_DEFAULT_USER=mi_usuario
    - RABBITMQ_DEFAULT_PASS=mi_password_seguro
```

### Usar variables de entorno

```bash
# Crear .env
cat > .env << EOF
RABBITMQ_USER=admin
RABBITMQ_PASS=secure_password
EOF
```

```yaml
rabbitmq:
  environment:
    - RABBITMQ_DEFAULT_USER=${RABBITMQ_USER}
    - RABBITMQ_DEFAULT_PASS=${RABBITMQ_PASS}
```

---

## 📈 Monitoreo

### Ver uso de recursos en tiempo real
```bash
docker stats
```

### Ver logs estructurados
```bash
docker-compose -f docker-compose.full.yml logs -f --timestamps
```

### Verificar health de todos los servicios
```bash
docker-compose -f docker-compose.full.yml ps
```

Servicios con `(healthy)` están funcionando correctamente.

---

## 🚀 Deploy a Producción

### 1. Configurar variables de entorno
```bash
cp backend/.env.example backend/.env
# Editar con valores de producción
```

### 2. Usar imágenes de producción
Modificar Dockerfile para optimizar:
```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder
# ... build steps ...

FROM python:3.11-slim
COPY --from=builder ...
```

### 3. Configurar reverse proxy (Nginx)
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api {
        proxy_pass http://localhost:8001;
    }
}
```

### 4. Iniciar con restart policy
```yaml
services:
  backend:
    restart: always
```

---

## 📝 Resumen de Comandos

```bash
# DESARROLLO
docker-compose -f docker-compose.dev.yml up -d

# PRODUCCIÓN COMPLETA
docker-compose -f docker-compose.full.yml up -d

# SOLO WHISPER
docker-compose -f docker-compose.whisper.yml up -d

# VER LOGS
docker-compose -f docker-compose.full.yml logs -f [servicio]

# DETENER
docker-compose -f docker-compose.full.yml down

# LIMPIAR TODO
docker-compose -f docker-compose.full.yml down -v --rmi all

# RECONSTRUIR
docker-compose -f docker-compose.full.yml up -d --build
```

---

## 🎯 Recomendaciones

**Para desarrollo:**
- Usa `docker-compose.dev.yml`
- Correr backend/frontend localmente para hot-reload

**Para testing:**
- Usa `docker-compose.full.yml`
- Todo en contenedores

**Para producción:**
- Usa `docker-compose.full.yml` con ajustes
- Configurar SSL/TLS
- Usar secrets para credenciales
- Implementar logging centralizado
- Agregar monitoring (Prometheus + Grafana)

---

## 📚 Más Información

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- Ver `QUICKSTART.md` para inicio rápido
- Ver `SETUP.md` para instalación detallada

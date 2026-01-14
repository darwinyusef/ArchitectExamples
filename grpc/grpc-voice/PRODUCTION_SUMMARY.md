# 📦 Resumen de Configuración para Producción

Resumen ejecutivo de la configuración de producción para `transcript.aquicreamos.com`.

---

## 🎯 Visión General

**Microservicio:** Transcripción de voz con gRPC
**Dominio:** `transcript.aquicreamos.com`
**Protocolo:** HTTPS (Let's Encrypt)
**Whisper Model:** tiny (optimizado para velocidad)
**Integración:** RabbitMQ para conectar con backend principal

---

## 📂 Archivos Clave de Producción

```
grpc-voice/
├── docker-compose.prod.yml          # ⭐ Compose principal de producción
├── .env.prod.example                # Plantilla de variables de entorno
├── init-letsencrypt.sh              # Script SSL automático
├── DEPLOY_GUIDE.md                  # Guía completa de deploy
│
├── nginx/
│   ├── nginx.conf                   # Config principal de Nginx
│   └── conf.d/
│       └── transcript.aquicreamos.com.conf  # Virtual host HTTPS
│
├── backend/
│   └── Dockerfile.prod              # Dockerfile optimizado (multi-stage)
│
├── frontend/
│   ├── Dockerfile.prod              # Build + Nginx
│   └── nginx.conf                   # Config de Nginx para SPA
│
└── envoy.prod.yaml                  # Config Envoy para gRPC-Web
```

---

## 🚀 Deploy Rápido

### Requisitos Previos
```bash
# DNS configurado
dig +short transcript.aquicreamos.com  # Debe retornar IP del servidor

# Docker instalado
docker --version
docker-compose --version
```

### 1. Configurar Variables
```bash
cp .env.prod.example .env.prod
nano .env.prod
```

**Configurar:**
- `DOMAIN=transcript.aquicreamos.com`
- `EMAIL=admin@aquicreamos.com`
- `RABBITMQ_USER=admin`
- `RABBITMQ_PASS=password_seguro`

### 2. Obtener Certificados SSL
```bash
chmod +x init-letsencrypt.sh
./init-letsencrypt.sh transcript.aquicreamos.com admin@aquicreamos.com 0
```

### 3. Deploy
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### 4. Verificar
```bash
# Health check
curl https://transcript.aquicreamos.com/api/health

# Abrir en navegador
open https://transcript.aquicreamos.com
```

---

## 🌐 Arquitectura de Red

```
Internet (HTTPS)
    ↓
[Nginx :80/:443]
    ├── / → Frontend (React SPA)
    ├── /api/ → Backend (FastAPI :8001)
    └── /grpc/ → Envoy (:8080) → gRPC Backend (:50051)

Backend (:8001, :50051)
    ├── Whisper API (:9000) - Modelo tiny
    └── RabbitMQ (:5672) - Local o Externo
```

**Puertos Expuestos:**
- `80` - HTTP (redirige a HTTPS)
- `443` - HTTPS (único puerto público)

**Puertos Internos:**
- `8001` - Backend API (interno)
- `50051` - gRPC Server (interno)
- `8080` - Envoy gRPC-Web (interno)
- `9000` - Whisper API (interno)
- `5672` - RabbitMQ (interno o externo)

---

## 🔐 Seguridad

### SSL/TLS
- ✅ Let's Encrypt (renovación automática)
- ✅ TLS 1.2 / 1.3
- ✅ HSTS habilitado
- ✅ Certificados gestionados por Certbot

### Headers de Seguridad
```nginx
Strict-Transport-Security: max-age=31536000
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
```

### CORS
Configurado para permitir solo orígenes específicos:
```
https://transcript.aquicreamos.com
https://aquicreamos.com
```

### Contenedores
- ✅ Usuario no-root
- ✅ Límites de recursos (CPU/RAM)
- ✅ Health checks automáticos
- ✅ Logs centralizados

---

## 📊 Configuración de Whisper

**Modelo:** `tiny`
- **Tamaño:** ~75 MB
- **RAM:** ~1 GB
- **Velocidad:** ~10x real-time
- **Precisión:** Buena para español/inglés

**Alternativas:**
- `base` - Mejor precisión, más lento (2 GB RAM)
- `small` - Mejor precisión, más lento (4 GB RAM)

Cambiar en `.env.prod`:
```env
WHISPER_MODEL=base
```

---

## 🐰 Integración con RabbitMQ

### Opción 1: RabbitMQ Local (por defecto)

El Docker Compose incluye RabbitMQ.

**Acceso desde backend principal:**
```
Host: transcript.aquicreamos.com
Port: 5672 (exponer en firewall si es necesario)
User: según .env.prod
Pass: según .env.prod
Exchange: transcriptions
Queue: transcription_queue
Routing Key: transcription.new
```

### Opción 2: RabbitMQ Externo (recomendado)

Conectar al RabbitMQ del backend principal.

**Configurar en `.env.prod`:**
```env
RABBITMQ_EXTERNAL_HOST=rabbitmq.aquicreamos.com
RABBITMQ_EXTERNAL_PORT=5672
RABBITMQ_EXTERNAL_USER=transcript_service
RABBITMQ_EXTERNAL_PASS=secure_password
```

**Modificar `docker-compose.prod.yml`:**
```yaml
# Comentar servicio rabbitmq local
# rabbitmq:
#   ...

# Actualizar backend
backend:
  environment:
    - RABBITMQ_URL=amqp://${RABBITMQ_EXTERNAL_USER}:${RABBITMQ_EXTERNAL_PASS}@${RABBITMQ_EXTERNAL_HOST}:5672/
```

### Formato de Mensajes Publicados

```json
{
  "session_id": "uuid-1234",
  "text": "Transcripción del audio",
  "language": "es",
  "duration": 10.5,
  "timestamp": 1234567890,
  "is_final": true,
  "metadata": {
    "duration": 10.5,
    "language_detected": "es",
    "words_count": 15
  },
  "segments": [
    {
      "start": 0.0,
      "end": 5.0,
      "text": "Primera parte..."
    }
  ]
}
```

**Consumir desde Backend Principal:**
```python
# En tu backend principal
import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters('rabbitmq.aquicreamos.com')
)
channel = connection.channel()
channel.queue_bind(
    exchange='transcriptions',
    queue='mi_queue_personalizada',
    routing_key='transcription.#'
)

def callback(ch, method, properties, body):
    import json
    data = json.loads(body)
    print(f"Nueva transcripción: {data['text']}")
    # Procesar transcripción...

channel.basic_consume(
    queue='mi_queue_personalizada',
    on_message_callback=callback,
    auto_ack=True
)

channel.start_consuming()
```

---

## 🔄 Ciclo de Vida

### Inicio
```bash
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### Detener
```bash
docker-compose -f docker-compose.prod.yml down
```

### Reiniciar
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Actualizar
```bash
git pull
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

### Ver Logs
```bash
docker-compose -f docker-compose.prod.yml logs -f [servicio]
```

---

## 📈 Monitoreo

### Health Checks

```bash
# Microservicio completo
curl https://transcript.aquicreamos.com/health

# Backend API
curl https://transcript.aquicreamos.com/api/health

# Frontend
curl https://transcript.aquicreamos.com/
```

### Métricas
```bash
# Recursos de contenedores
docker stats

# Logs estructurados
docker-compose -f docker-compose.prod.yml logs --timestamps
```

---

## 🆘 Comandos Útiles

```bash
# Ver estado de servicios
docker-compose -f docker-compose.prod.yml ps

# Ejecutar comando en contenedor
docker-compose -f docker-compose.prod.yml exec backend bash

# Ver configuración de Nginx
docker-compose -f docker-compose.prod.yml exec nginx cat /etc/nginx/conf.d/transcript.aquicreamos.com.conf

# Renovar SSL manualmente
docker-compose -f docker-compose.prod.yml run --rm certbot renew

# Limpiar logs
docker-compose -f docker-compose.prod.yml exec backend sh -c "truncate -s 0 /app/logs/*"

# Backup de certificados
tar -czf ssl-backup-$(date +%Y%m%d).tar.gz certbot/
```

---

## 📝 Checklist Pre-Deploy

- [ ] DNS apunta a servidor
- [ ] Firewall configurado (puertos 80, 443)
- [ ] `.env.prod` configurado
- [ ] Credenciales de RabbitMQ configuradas
- [ ] Docker y Docker Compose instalados
- [ ] Email válido para Let's Encrypt

---

## 📚 Documentación

- **[DEPLOY_GUIDE.md](./DEPLOY_GUIDE.md)** - Guía completa de deploy
- **[DOCKER_GUIDE.md](./DOCKER_GUIDE.md)** - Guía de Docker Compose
- **[README.md](./README.md)** - Documentación principal
- **[docs/GRPC_BACKEND_GUIDE.md](./docs/GRPC_BACKEND_GUIDE.md)** - Guía de gRPC
- **[docs/INDEX.md](./docs/INDEX.md)** - Índice completo

---

## 🎯 Características de Producción

✅ **Optimizaciones:**
- Multi-stage Docker builds (imágenes pequeñas)
- Compresión Gzip
- Cache de assets estáticos
- Health checks automáticos
- Logs centralizados
- Renovación automática de SSL

✅ **Seguridad:**
- HTTPS obligatorio
- Headers de seguridad
- CORS configurado
- Usuario no-root en contenedores
- Credenciales en variables de entorno

✅ **Escalabilidad:**
- Límites de recursos configurables
- Workers de Whisper configurables
- Fácil escalar horizontalmente con load balancer

✅ **Monitoreo:**
- Health checks HTTP
- Logs estructurados
- Métricas de recursos
- Alertas (configurar con herramientas externas)

---

## 🔗 URLs de Producción

- **Frontend:** https://transcript.aquicreamos.com
- **API:** https://transcript.aquicreamos.com/api
- **gRPC-Web:** https://transcript.aquicreamos.com/grpc
- **Health:** https://transcript.aquicreamos.com/health
- **API Docs:** https://transcript.aquicreamos.com/api/docs

---

**El microservicio está listo para integrarse con tu backend principal vía RabbitMQ** 🚀

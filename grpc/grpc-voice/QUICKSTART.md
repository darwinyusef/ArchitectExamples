# 🚀 Inicio Rápido

## Configuración Rápida (5 minutos)

### Prerrequisitos
- Tener RabbitMQ corriendo en `localhost:5672`
- Tener tu servicio Whisper corriendo (o usar modelo local)

### Paso 1: Backend

```bash
cd backend

# Crear .env
cp .env.example .env

# Editar .env si necesitas cambiar configuraciones
# Por defecto usa:
# - Puerto FastAPI: 8001 (ya que 8000 está ocupado)
# - Puerto gRPC: 50051
# - Whisper modelo: base (local)
# - RabbitMQ: localhost:5672

# Ejecutar setup
chmod +x setup.sh
./setup.sh

# Iniciar servidor
source venv/bin/activate
python main.py
```

El servidor estará disponible en:
- **FastAPI**: http://localhost:8001
- **gRPC**: localhost:50051
- **Docs API**: http://localhost:8001/docs

### Paso 2: Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar dev server
npm run dev
```

El frontend estará disponible en: **http://localhost:3000**

---

## 🎯 Probar el Sistema

### 1. Desde el Frontend (Interfaz Web)

1. Abrir http://localhost:3000
2. **Opción A - Grabar audio**:
   - Click en "🎤 Grabar"
   - Click en "Iniciar Grabación"
   - Hablar al micrófono
   - Click en "Detener"
   - Click en "Transcribir"

3. **Opción B - Subir archivo**:
   - Click en "📁 Subir Archivo"
   - Arrastrar un archivo MP3/WAV o hacer click para seleccionar
   - Click en "Transcribir"

4. Ver la transcripción en el panel derecho

### 2. Desde API REST (cURL)

```bash
# Transcribir un archivo de audio
curl -X POST http://localhost:8001/transcribe \
  -F "file=@audio.mp3" \
  -F "language=es"
```

### 3. Health Check

```bash
curl http://localhost:8001/health
```

Respuesta esperada:
```json
{
  "status": "healthy",
  "services": {
    "whisper": "ok",
    "rabbitmq": "ok",
    "grpc": "running"
  }
}
```

---

## 📊 Verificar RabbitMQ

Las transcripciones se publican automáticamente a RabbitMQ:

1. Abrir RabbitMQ Management: http://localhost:15672
2. Login: `guest` / `guest`
3. Ir a "Queues"
4. Buscar `transcription_queue`
5. Click en la queue
6. Ver mensajes en "Get messages"

**Formato del mensaje:**
```json
{
  "session_id": "uuid",
  "text": "transcripción del audio",
  "language": "es",
  "duration": 10.5,
  "timestamp": 1234567890,
  "is_final": true,
  "metadata": {
    "duration": 10.5,
    "language_detected": "es",
    "words_count": 15
  }
}
```

---

## 🐳 Alternativa: Usar Docker

Si prefieres usar Docker en lugar de setup manual:

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Detener
docker-compose down
```

**Servicios disponibles:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- gRPC: localhost:50051
- RabbitMQ: http://localhost:15672
- Envoy (gRPC-Web): http://localhost:8080

---

## 🔧 Configuración Personalizada

### Cambiar Modelo de Whisper

En `backend/.env`:
```env
# Opciones: tiny, base, small, medium, large
WHISPER_MODEL=small

# Usar GPU si está disponible
WHISPER_DEVICE=cuda
```

### Usar API Externa de Whisper

Si tienes un servicio Whisper corriendo:
```env
WHISPER_API_URL=http://tu-servidor:9000
```

### Cambiar Configuración de RabbitMQ

```env
RABBITMQ_URL=amqp://user:pass@servidor:5672/
RABBITMQ_EXCHANGE=mi_exchange
RABBITMQ_QUEUE=mi_queue
RABBITMQ_ROUTING_KEY=mi_routing_key
```

---

## ❓ Troubleshooting

### Error: "Cannot connect to RabbitMQ"
```bash
# Verificar que RabbitMQ esté corriendo
docker ps | grep rabbitmq
# O si es local:
sudo systemctl status rabbitmq-server
```

### Error: "Port 8001 is already in use"
Cambiar el puerto en `backend/.env`:
```env
API_PORT=8002
```

Y en `frontend/src/services/audioService.ts`:
```typescript
constructor(apiUrl: string = 'http://localhost:8002')
```

### Error: "Microphone permission denied"
- Usar `https://` o `localhost`
- Dar permisos de micrófono en el navegador

### Backend no inicia
```bash
# Verificar instalación
cd backend
source venv/bin/activate
pip list | grep -E "fastapi|grpcio|whisper"

# Reinstalar si es necesario
pip install -r requirements.txt
```

---

## 📚 Próximos Pasos

- [Documentación Completa](./README.md)
- [Guía de Setup Detallada](./SETUP.md)
- [Arquitectura del Sistema](./docs/architecture.md) (por crear)

---

## 🎉 ¡Listo!

Tu sistema de transcripción de voz con gRPC está funcionando.

**Características:**
✅ Grabación de audio en tiempo real
✅ Subida de archivos de audio
✅ Transcripción con Whisper
✅ Publicación a RabbitMQ
✅ API REST + gRPC
✅ Interfaz web moderna

Para más información, consulta el [README.md](./README.md)

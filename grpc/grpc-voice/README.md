# 🎙️ gRPC Voice Streaming with Whisper

Sistema completo de transcripción de audio en tiempo real usando **gRPC**, **Whisper AI** y **RabbitMQ**.

## ✨ Características

- 🎤 **Grabación de audio en vivo** desde el navegador
- 📁 **Subida de archivos de audio** (MP3, WAV, M4A, WebM)
- 🤖 **Transcripción con Whisper AI** (OpenAI)
- ⚡ **Streaming en tiempo real** con gRPC
- 📨 **Publicación automática a RabbitMQ**
- 🌐 **API REST + gRPC**
- 💻 **Interfaz web moderna** con React
- 🐳 **Deploy con Docker** incluido

## 🏗️ Arquitectura

```
┌─────────────────┐
│  React Frontend │  (Puerto 3000)
│  - Audio Record │
│  - File Upload  │
└────────┬────────┘
         │ HTTP/gRPC-Web
         ▼
┌─────────────────┐
│ FastAPI Backend │  (Puerto 8001)
│  - REST API     │
│  - gRPC Server  │  (Puerto 50051)
└────────┬────────┘
         │
    ┌────┴─────────────┐
    │                  │
    ▼                  ▼
┌──────────┐    ┌──────────┐
│ Whisper  │    │ RabbitMQ │
│   AI     │    │  Queue   │
└──────────┘    └──────────┘
```

## 📁 Estructura del Proyecto

```
grpc-voice/
├── backend/
│   ├── proto/
│   │   └── audio_service.proto     # Definición gRPC
│   ├── services/
│   │   ├── grpc_service.py         # Servidor gRPC
│   │   ├── whisper_service.py      # Integración Whisper
│   │   └── rabbitmq_service.py     # Cliente RabbitMQ
│   ├── main.py                     # FastAPI + gRPC server
│   ├── config.py                   # Configuración
│   ├── consumer_example.py         # Ejemplo consumer RabbitMQ
│   └── test_api.py                 # Tests
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AudioRecorder.tsx   # Grabadora de audio
│   │   │   ├── FileUploader.tsx    # Subida de archivos
│   │   │   └── TranscriptionDisplay.tsx
│   │   ├── hooks/
│   │   │   └── useAudioRecorder.ts
│   │   ├── services/
│   │   │   └── audioService.ts     # Cliente API
│   │   └── App.tsx
│   └── package.json
├── docker-compose.yml              # Orquestación Docker
├── envoy.yaml                      # Proxy gRPC-Web
├── README.md
├── QUICKSTART.md                   # Inicio rápido
└── SETUP.md                        # Guía detallada
```

## 🚀 Inicio Rápido

### Opción 1: Setup Manual

**Prerrequisitos:**
- Python 3.9+
- Node.js 18+
- RabbitMQ corriendo en `localhost:5672`

**Backend:**
```bash
cd backend
chmod +x setup.sh
./setup.sh
source venv/bin/activate
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Opción 2: Docker (Recomendado)

Tenemos **4 configuraciones de Docker Compose** según tus necesidades:

#### A. Sistema Completo (TODO incluido) ⭐
```bash
docker-compose -f docker-compose.full.yml up -d
```
Incluye: Backend + Frontend + RabbitMQ + **Whisper** + Envoy

#### B. Solo Servicios Externos (Para desarrollo)
```bash
docker-compose -f docker-compose.dev.yml up -d
```
Incluye: RabbitMQ + Whisper + Envoy (Backend/Frontend locales)

#### C. Solo Whisper
```bash
docker-compose -f docker-compose.whisper.yml up -d
```

#### D. Sistema sin Whisper (Original)
```bash
docker-compose up -d
```
Requiere Whisper externo o local.

**Servicios disponibles:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- Backend Docs: http://localhost:8001/docs
- gRPC: localhost:50051
- RabbitMQ UI: http://localhost:15672 (guest/guest)
- Whisper API: http://localhost:9000
- Envoy gRPC-Web: http://localhost:8080

Ver **[DOCKER_GUIDE.md](./DOCKER_GUIDE.md)** para más detalles.

### Opción 3: Producción (transcript.aquicreamos.com) 🌐

**Deploy a producción con HTTPS:**
```bash
# 1. Configurar variables
cp .env.prod.example .env.prod
nano .env.prod

# 2. Obtener certificados SSL
./init-letsencrypt.sh transcript.aquicreamos.com admin@aquicreamos.com 0

# 3. Deploy
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

**Servicios en producción:**
- Frontend: https://transcript.aquicreamos.com
- API: https://transcript.aquicreamos.com/api
- gRPC-Web: https://transcript.aquicreamos.com/grpc

Ver **[DEPLOY_GUIDE.md](./DEPLOY_GUIDE.md)** y **[PRODUCTION_SUMMARY.md](./PRODUCTION_SUMMARY.md)** para más detalles.

Ver [QUICKSTART.md](./QUICKSTART.md) para más detalles.

## 📖 Uso

### Desde la Interfaz Web

1. Abrir http://localhost:3000
2. **Grabar audio**: Click en "🎤 Grabar" → Hablar → "Detener" → "Transcribir"
3. **Subir archivo**: Click en "📁 Subir Archivo" → Seleccionar MP3/WAV → "Transcribir"
4. Ver transcripción en tiempo real

### Desde API REST

```bash
curl -X POST http://localhost:8001/transcribe \
  -F "file=@audio.mp3" \
  -F "language=es"
```

**Respuesta:**
```json
{
  "success": true,
  "transcription": "Hola, esto es una prueba",
  "language": "es",
  "duration": 3.5,
  "words_count": 5
}
```

### Consumir de RabbitMQ

```bash
cd backend
python consumer_example.py
```

Ver mensajes en RabbitMQ Management: http://localhost:15672

## ⚙️ Configuración

### Variables de Entorno (`backend/.env`)

```env
# Puertos
API_PORT=8001
GRPC_PORT=50051

# Whisper
WHISPER_MODEL=base          # tiny, base, small, medium, large
WHISPER_DEVICE=cpu          # cpu o cuda
# WHISPER_API_URL=http://...  # Si usas API externa

# RabbitMQ
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
RABBITMQ_EXCHANGE=transcriptions
RABBITMQ_QUEUE=transcription_queue
RABBITMQ_ROUTING_KEY=transcription.new

# Audio
MAX_AUDIO_SIZE_MB=25
```

## 🔌 API Endpoints

### REST API

- `GET /` - Root endpoint
- `GET /health` - Health check
- `POST /transcribe` - Transcribir audio
  - Form data: `file` (audio), `language` (opcional)

### gRPC Service

```protobuf
service AudioStreamService {
  // Streaming bidireccional
  rpc StreamAudio(stream AudioChunk) returns (stream TranscriptionResponse);

  // Método unario
  rpc TranscribeAudio(AudioFile) returns (TranscriptionResponse);
}
```

Ver `backend/proto/audio_service.proto` para detalles.

## 🧪 Testing

```bash
# Test API
cd backend
python test_api.py

# Test con archivo de audio
python test_api.py path/to/audio.mp3

# Health check
curl http://localhost:8001/health
```

## 📊 RabbitMQ Integration

Las transcripciones se publican automáticamente a RabbitMQ:

**Formato del mensaje:**
```json
{
  "session_id": "uuid-1234",
  "text": "transcripción del audio",
  "language": "es",
  "duration": 10.5,
  "timestamp": 1234567890,
  "is_final": true,
  "metadata": {
    "duration": 10.5,
    "language_detected": "es",
    "words_count": 15
  },
  "segments": [...]
}
```

**Configuración:**
- Exchange: `transcriptions` (topic)
- Queue: `transcription_queue`
- Routing Key: `transcription.new`

## 🛠️ Desarrollo

### Generar archivos proto (Backend)

```bash
cd backend
python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./proto \
    --grpc_python_out=./proto \
    proto/audio_service.proto
```

### Generar archivos proto (Frontend - opcional)

```bash
cd frontend
npm run proto
```

## 🐛 Troubleshooting

Ver [SETUP.md](./SETUP.md#troubleshooting) para soluciones comunes.

**Problemas frecuentes:**
- Puerto 8001 ocupado → Cambiar `API_PORT` en `.env`
- RabbitMQ no conecta → Verificar que esté corriendo
- Permisos de micrófono → Usar HTTPS o localhost
- Whisper lento → Usar modelo más pequeño (`tiny` o `base`)

## 📚 Documentación

### Primeros Pasos
- **[QUICKSTART.md](./QUICKSTART.md)** - Inicio rápido (5 minutos)
- **[SETUP.md](./SETUP.md)** - Guía de instalación detallada

### Deploy
- **[DEPLOY_GUIDE.md](./DEPLOY_GUIDE.md)** - Guía completa de deploy a producción
- **[PRODUCTION_SUMMARY.md](./PRODUCTION_SUMMARY.md)** - Resumen de configuración de producción
- **[DOCKER_GUIDE.md](./DOCKER_GUIDE.md)** - Guía completa de Docker Compose
- **[DOCKER_QUICK_REFERENCE.md](./DOCKER_QUICK_REFERENCE.md)** - Referencia rápida de Docker

### Aprendizaje
- **[docs/GRPC_BACKEND_GUIDE.md](./docs/GRPC_BACKEND_GUIDE.md)** - Guía de gRPC en Python
- **[docs/GRPC_FRONTEND_GUIDE.md](./docs/GRPC_FRONTEND_GUIDE.md)** - Guía de gRPC-Web en React
- **[docs/INDEX.md](./docs/INDEX.md)** - Índice completo de documentación

### Referencia
- **[backend/proto/audio_service.proto](./backend/proto/audio_service.proto)** - Definición gRPC
- **[API Docs](http://localhost:8001/docs)** - Swagger UI (desarrollo)
- **[API Docs Prod](https://transcript.aquicreamos.com/api/docs)** - Swagger UI (producción)

## 🤝 Contribuir

1. Fork el proyecto
2. Crear branch (`git checkout -b feature/amazing`)
3. Commit cambios (`git commit -m 'Add amazing feature'`)
4. Push al branch (`git push origin feature/amazing`)
5. Abrir Pull Request

## 📝 Licencia

MIT License - Ver [LICENSE](./LICENSE) para más detalles.

## 🙏 Agradecimientos

- [Whisper](https://github.com/openai/whisper) - OpenAI
- [gRPC](https://grpc.io/) - Google
- [FastAPI](https://fastapi.tiangolo.com/)
- [RabbitMQ](https://www.rabbitmq.com/)

---

**Hecho con ❤️ usando Whisper, gRPC y RabbitMQ**

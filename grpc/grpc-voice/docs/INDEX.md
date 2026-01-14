# 📚 Documentación del Proyecto

Índice completo de la documentación del proyecto gRPC Voice Streaming.

---

## 🚀 Primeros Pasos

### Para Empezar Rápido
- **[QUICKSTART.md](../QUICKSTART.md)** - Guía de inicio rápido (5 minutos)
  - Setup backend
  - Setup frontend
  - Pruebas básicas
  - Verificación de servicios

### Para Setup Detallado
- **[SETUP.md](../SETUP.md)** - Guía de instalación completa
  - Instalación manual paso a paso
  - Setup con Docker
  - Configuración de servicios
  - Troubleshooting común

---

## 📖 Documentación Principal

### Visión General
- **[README.md](../README.md)** - Descripción del proyecto
  - Características
  - Arquitectura del sistema
  - Estructura del proyecto
  - API endpoints
  - Configuración

---

## 🎓 Guías de Aprendizaje

### gRPC - Backend (Python)
- **[GRPC_BACKEND_GUIDE.md](./GRPC_BACKEND_GUIDE.md)**
  - ¿Qué es gRPC?
  - Definir servicios con Protocol Buffers
  - Implementar servidor gRPC en Python
  - Tipos de métodos RPC (unary, streaming, bidirectional)
  - Manejo de errores
  - Metadata y headers
  - Interceptores
  - Testing
  - Best practices

### gRPC - Frontend (React/TypeScript)
- **[GRPC_FRONTEND_GUIDE.md](./GRPC_FRONTEND_GUIDE.md)**
  - ¿Qué es gRPC-Web?
  - REST API vs gRPC-Web
  - Setup de gRPC-Web
  - Implementar cliente gRPC-Web
  - Configurar Envoy proxy
  - Streaming en tiempo real
  - Manejo de errores
  - Testing
  - Cuándo usar cada opción

---

## 🏗️ Arquitectura

### Componentes del Sistema

```
┌─────────────────────────────────────────┐
│           FRONTEND (React)              │
│                                         │
│  - Audio Recorder                       │
│  - File Uploader                        │
│  - Transcription Display                │
│                                         │
│  Technologies:                          │
│  • React + TypeScript                   │
│  • Vite                                 │
│  • Fetch API / gRPC-Web (opcional)     │
└────────────┬────────────────────────────┘
             │
             │ HTTP/REST (Puerto 3000 → 8001)
             │ gRPC-Web (Puerto 3000 → 8080 → 50051)
             │
┌────────────▼────────────────────────────┐
│         BACKEND (FastAPI + gRPC)        │
│                                         │
│  Services:                              │
│  • FastAPI REST API (Puerto 8001)      │
│  • gRPC Server (Puerto 50051)          │
│  • Whisper Integration                 │
│  • RabbitMQ Publisher                  │
│                                         │
│  Technologies:                          │
│  • FastAPI                              │
│  • gRPC + Protocol Buffers             │
│  • OpenAI Whisper                      │
│  • aio-pika (RabbitMQ)                 │
└───────┬────────────────┬────────────────┘
        │                │
        │                │
        ▼                ▼
┌───────────────┐  ┌──────────────┐
│    Whisper    │  │   RabbitMQ   │
│      AI       │  │              │
│               │  │  Exchange:   │
│  Models:      │  │  transcriptions
│  • tiny       │  │              │
│  • base       │  │  Queue:      │
│  • small      │  │  transcription_queue
│  • medium     │  │              │
│  • large      │  │  Routing:    │
│               │  │  transcription.new
└───────────────┘  └──────────────┘
```

### Flujos de Datos

#### 1. Subir Archivo (REST)
```
Usuario selecciona archivo
    ↓
React FileUploader
    ↓ POST /transcribe
Backend FastAPI
    ↓
Whisper AI (transcripción)
    ↓
RabbitMQ (publicar)
    ↓ Response
React (mostrar transcripción)
```

#### 2. Grabación en Vivo (REST - Actual)
```
Usuario graba audio
    ↓
MediaRecorder API (navegador)
    ↓
React AudioRecorder (acumula audio)
    ↓
Usuario detiene grabación
    ↓ POST /transcribe (audio completo)
Backend FastAPI
    ↓
Whisper AI
    ↓
RabbitMQ
    ↓ Response
React (mostrar transcripción)
```

#### 3. Streaming en Tiempo Real (gRPC - Futuro)
```
Usuario empieza a grabar
    ↓
MediaRecorder API (chunks cada 1s)
    ↓ stream AudioChunk (continuo)
gRPC Client
    ↓
Envoy Proxy (8080)
    ↓
gRPC Server (50051)
    ↓
Whisper AI (procesar chunks)
    ↓
RabbitMQ (publicar transcripciones parciales)
    ↓ stream TranscriptionResponse (continuo)
React (actualizar transcripción en tiempo real)
```

---

## 📁 Estructura de Archivos

```
grpc-voice/
├── docs/                           # 📚 Documentación
│   ├── INDEX.md                    # Este archivo
│   ├── GRPC_BACKEND_GUIDE.md      # Guía gRPC backend
│   └── GRPC_FRONTEND_GUIDE.md     # Guía gRPC frontend
│
├── backend/                        # 🐍 Backend Python
│   ├── proto/                      # Protocol Buffers
│   │   ├── audio_service.proto    # Definición del servicio
│   │   ├── audio_service_pb2.py   # Generado: mensajes
│   │   └── audio_service_pb2_grpc.py # Generado: servicios
│   │
│   ├── services/                   # Servicios
│   │   ├── grpc_service.py        # Servidor gRPC
│   │   ├── whisper_service.py     # Integración Whisper
│   │   └── rabbitmq_service.py    # Cliente RabbitMQ
│   │
│   ├── main.py                     # FastAPI + gRPC server
│   ├── config.py                   # Configuración
│   ├── requirements.txt            # Dependencias Python
│   ├── Dockerfile                  # Docker backend
│   ├── setup.sh                    # Script de setup
│   ├── consumer_example.py         # Ejemplo consumer RabbitMQ
│   ├── test_api.py                 # Tests
│   └── .env.example                # Variables de entorno
│
├── frontend/                       # ⚛️ Frontend React
│   ├── src/
│   │   ├── components/             # Componentes React
│   │   │   ├── AudioRecorder.tsx
│   │   │   ├── AudioRecorder.css
│   │   │   ├── FileUploader.tsx
│   │   │   ├── FileUploader.css
│   │   │   ├── TranscriptionDisplay.tsx
│   │   │   └── TranscriptionDisplay.css
│   │   │
│   │   ├── hooks/                  # Custom hooks
│   │   │   └── useAudioRecorder.ts
│   │   │
│   │   ├── services/               # Servicios API
│   │   │   └── audioService.ts    # Cliente REST
│   │   │
│   │   ├── App.tsx                 # Componente principal
│   │   ├── App.css
│   │   ├── main.tsx                # Entry point
│   │   └── index.css
│   │
│   ├── package.json                # Dependencias Node
│   ├── tsconfig.json               # Config TypeScript
│   ├── vite.config.ts              # Config Vite
│   └── Dockerfile                  # Docker frontend
│
├── docker-compose.yml              # 🐳 Orquestación Docker
├── envoy.yaml                      # Configuración Envoy proxy
├── .gitignore
├── README.md                       # Documentación principal
├── QUICKSTART.md                   # Guía de inicio rápido
└── SETUP.md                        # Guía de setup detallada
```

---

## 🔧 Tecnologías Utilizadas

### Backend
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| Python | 3.11+ | Lenguaje principal |
| FastAPI | 0.104+ | Framework REST API |
| gRPC | 1.59+ | Framework RPC |
| Whisper | latest | Transcripción de audio |
| RabbitMQ | 3.12+ | Message queue |
| aio-pika | 9.3+ | Cliente RabbitMQ async |
| Pydantic | 2.5+ | Validación de datos |

### Frontend
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| React | 18+ | UI framework |
| TypeScript | 5.2+ | Tipado estático |
| Vite | 5+ | Build tool |
| gRPC-Web | 1.5+ | Cliente gRPC (opcional) |

### Infraestructura
| Tecnología | Propósito |
|------------|-----------|
| Docker | Containerización |
| Docker Compose | Orquestación |
| Envoy | Proxy gRPC-Web |

---

## 🔌 API Reference

### REST API Endpoints

#### `GET /`
Root endpoint - Health check básico

**Response:**
```json
{
  "status": "ok",
  "service": "gRPC Voice Streaming API",
  "version": "1.0.0"
}
```

#### `GET /health`
Health check detallado

**Response:**
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

#### `POST /transcribe`
Transcribir archivo de audio

**Request:**
- Content-Type: `multipart/form-data`
- Body:
  - `file`: Audio file (MP3, WAV, M4A, WebM)
  - `language`: (opcional) Código de idioma (es, en, etc.)

**Response:**
```json
{
  "success": true,
  "transcription": "Texto transcrito del audio",
  "language": "es",
  "duration": 10.5,
  "words_count": 15
}
```

### gRPC Service

```protobuf
service AudioStreamService {
  // Método unario: transcribir archivo completo
  rpc TranscribeAudio(AudioFile) returns (TranscriptionResponse);

  // Streaming bidireccional: enviar chunks, recibir transcripciones
  rpc StreamAudio(stream AudioChunk) returns (stream TranscriptionResponse);
}
```

Ver [audio_service.proto](../backend/proto/audio_service.proto) para detalles completos.

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
python test_api.py                    # Test básico
python test_api.py audio.mp3          # Test con archivo
```

### Manual Testing
```bash
# Health check
curl http://localhost:8001/health

# Transcribir archivo
curl -X POST http://localhost:8001/transcribe \
  -F "file=@test.mp3" \
  -F "language=es"
```

### gRPC Testing
```bash
# Con grpcurl
grpcurl -plaintext localhost:50051 list
grpcurl -plaintext localhost:50051 audiostream.AudioStreamService/TranscribeAudio
```

---

## 🐛 Troubleshooting

### Problemas Comunes

| Problema | Solución |
|----------|----------|
| Puerto 8001 ocupado | Cambiar `API_PORT` en `.env` |
| RabbitMQ no conecta | Verificar `docker ps \| grep rabbitmq` |
| Whisper lento | Usar modelo más pequeño (`tiny` o `base`) |
| Permisos de micrófono | Usar HTTPS o localhost |
| Error al generar proto | Instalar `grpcio-tools` |

Ver [SETUP.md - Troubleshooting](../SETUP.md#troubleshooting) para más detalles.

---

## 📊 Monitoreo

### RabbitMQ Management
- URL: http://localhost:15672
- Usuario: `guest`
- Contraseña: `guest`

**Verificar mensajes:**
1. Ir a "Queues"
2. Click en `transcription_queue`
3. Ver mensajes en "Get messages"

### Logs del Backend
```bash
# En desarrollo
tail -f logs/app.log

# Con Docker
docker-compose logs -f backend
```

---

## 🚀 Despliegue

### Desarrollo
```bash
# Backend
cd backend && python main.py

# Frontend
cd frontend && npm run dev
```

### Producción (Docker)
```bash
docker-compose up -d
```

### Variables de Entorno

**Backend (.env):**
```env
API_PORT=8001
GRPC_PORT=50051
WHISPER_MODEL=base
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

---

## 📝 Contribuir

1. Fork el proyecto
2. Crear branch feature
3. Commit cambios
4. Push al branch
5. Abrir Pull Request

---

## 📚 Recursos Externos

### Documentación Oficial
- [gRPC](https://grpc.io/docs/)
- [Protocol Buffers](https://developers.google.com/protocol-buffers)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Whisper](https://github.com/openai/whisper)
- [RabbitMQ](https://www.rabbitmq.com/documentation.html)
- [React](https://react.dev/)

### Tutoriales
- [gRPC Python Quickstart](https://grpc.io/docs/languages/python/quickstart/)
- [gRPC-Web Guide](https://github.com/grpc/grpc-web)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)

---

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/tu-repo/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/tu-repo/discussions)

---

**Última actualización:** Diciembre 2024

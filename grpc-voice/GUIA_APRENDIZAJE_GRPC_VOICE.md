# Guía de Aprendizaje: gRPC Voice - Proyecto Completo

## Índice
1. [Introducción](#introducción)
2. [Arquitectura del Proyecto](#arquitectura-del-proyecto)
3. [Conceptos Clave](#conceptos-clave)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Paso a Paso: Entendiendo gRPC Voice](#paso-a-paso-entendiendo-grpc-voice)
6. [Componentes Principales](#componentes-principales)
7. [Flujo de Datos](#flujo-de-datos)
8. [Instalación y Ejecución](#instalación-y-ejecución)
9. [Ejercicios Prácticos](#ejercicios-prácticos)
10. [Troubleshooting](#troubleshooting)

---

## Introducción

**gRPC Voice** es un proyecto completo que demuestra el uso avanzado de gRPC en un caso de uso real: **transcripción de audio en tiempo real**.

### ¿Qué hace este proyecto?

- Graba audio desde el navegador o acepta archivos de audio
- Envía el audio al backend usando gRPC (streaming)
- Transcribe el audio usando Whisper AI
- Publica las transcripciones a RabbitMQ
- Muestra la transcripción en tiempo real en la interfaz web

### Tecnologías utilizadas

**Backend:**
- Python 3.9+
- FastAPI (API REST)
- gRPC (comunicación eficiente)
- Whisper AI (transcripción)
- RabbitMQ (mensajería)

**Frontend:**
- React + TypeScript
- gRPC-Web (cliente gRPC para navegador)
- Web Audio API (grabación)

**Infraestructura:**
- Docker + Docker Compose
- Envoy Proxy (convierte HTTP/1.1 a HTTP/2 para gRPC-Web)
- Nginx (producción)

---

## Arquitectura del Proyecto

### Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────┐
│                   NAVEGADOR                         │
│  ┌──────────────┐          ┌──────────────┐        │
│  │ AudioRecorder│          │ FileUploader │        │
│  │  (Web Audio) │          │   (Input)    │        │
│  └──────┬───────┘          └──────┬───────┘        │
│         │                          │                │
│         └──────────┬───────────────┘                │
│                    │                                │
│         ┌──────────▼──────────┐                    │
│         │   audioService.ts   │                    │
│         │  (gRPC-Web Client)  │                    │
│         └──────────┬──────────┘                    │
└────────────────────┼────────────────────────────────┘
                     │ HTTP/1.1
                     ▼
         ┌───────────────────────┐
         │    Envoy Proxy        │  Puerto 8080
         │  (gRPC-Web → gRPC)    │
         └───────────┬───────────┘
                     │ HTTP/2 (gRPC)
                     ▼
         ┌───────────────────────┐
         │   FastAPI Backend     │  Puerto 8001
         │  ┌─────────────────┐  │
         │  │  REST API       │  │  /transcribe (POST)
         │  └─────────────────┘  │
         │  ┌─────────────────┐  │
         │  │  gRPC Server    │  │  Puerto 50051
         │  │ ┌─────────────┐ │  │
         │  │ │StreamAudio()│ │  │  Bidirectional
         │  │ └─────────────┘ │  │
         │  └────────┬────────┘  │
         │           │           │
         │  ┌────────▼────────┐  │
         │  │ Whisper Service │  │
         │  │   (OpenAI AI)   │  │
         │  └────────┬────────┘  │
         │           │           │
         │  ┌────────▼────────┐  │
         │  │ RabbitMQ Client │  │
         │  └────────┬────────┘  │
         └───────────┼───────────┘
                     │
            ┌────────┴────────┐
            │                 │
            ▼                 ▼
    ┌───────────┐     ┌──────────────┐
    │ Whisper   │     │   RabbitMQ   │  Puerto 5672
    │ Container │     │   (Queue)    │  UI: 15672
    │ (GPU/CPU) │     │              │
    └───────────┘     └──────┬───────┘
                             │
                      ┌──────▼──────┐
                      │  Consumer   │
                      │  Example    │
                      └─────────────┘
```

### Flujo de Comunicación

1. **Usuario graba/sube audio** → Frontend (React)
2. **Audio → gRPC-Web** → Envoy Proxy
3. **Envoy convierte HTTP/1.1 → HTTP/2** → Backend gRPC
4. **Backend procesa con Whisper** → Transcripción
5. **Publica a RabbitMQ** → Queue
6. **Responde al cliente** → Muestra transcripción

---

## Conceptos Clave

### 1. gRPC vs gRPC-Web

| Aspecto | gRPC | gRPC-Web |
|---------|------|----------|
| **Uso** | Backend a Backend | Navegador a Backend |
| **Protocolo** | HTTP/2 nativo | HTTP/1.1 con traducción |
| **Streaming** | Todos los tipos | Limitado (no bidi completo) |
| **Proxy** | No necesario | Requiere Envoy/proxy |

**En este proyecto:**
- Frontend usa **gRPC-Web** (navegador no soporta HTTP/2 directo)
- Envoy traduce gRPC-Web → gRPC puro
- Backend recibe gRPC puro

### 2. Protocol Buffers en gRPC Voice

Ver `backend/proto/audio_service.proto`:

```protobuf
service AudioStreamService {
  // Bidirectional streaming
  rpc StreamAudio(stream AudioChunk) returns (stream TranscriptionResponse);

  // Unary RPC
  rpc TranscribeAudio(AudioFile) returns (TranscriptionResponse);
}
```

**Dos métodos:**
1. `StreamAudio`: Streaming bidireccional (chunks en tiempo real)
2. `TranscribeAudio`: Unary RPC (archivo completo)

### 3. Envoy Proxy

Envoy es un proxy que:
- Convierte HTTP/1.1 (del navegador) a HTTP/2 (gRPC)
- Maneja CORS para el navegador
- Enruta tráfico REST y gRPC

Configuración en `envoy.yaml`:

```yaml
listeners:
  - name: listener_0
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 8080
    filter_chains:
      - filters:
          - name: envoy.filters.network.http_connection_manager
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
              codec_type: AUTO
              stat_prefix: ingress_http
              route_config:
                name: local_route
                virtual_hosts:
                  - name: local_service
                    domains: ["*"]
                    routes:
                      - match:
                          prefix: "/"
                        route:
                          cluster: grpc_backend
                    cors:
                      allow_origin_string_match:
                        - prefix: "*"
                      allow_methods: GET, PUT, DELETE, POST, OPTIONS
                      allow_headers: keep-alive,user-agent,cache-control,content-type,content-transfer-encoding,x-accept-content-transfer-encoding,x-accept-response-streaming,x-user-agent,x-grpc-web,grpc-timeout
                      max_age: "1728000"
                      expose_headers: grpc-status,grpc-message
              http_filters:
                - name: envoy.filters.http.grpc_web
                  typed_config:
                    "@type": type.googleapis.com/envoy.extensions.filters.http.grpc_web.v3.GrpcWeb
                - name: envoy.filters.http.cors
                  typed_config:
                    "@type": type.googleapis.com/envoy.extensions.filters.http.cors.v3.Cors
                - name: envoy.filters.http.router
                  typed_config:
                    "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router

clusters:
  - name: grpc_backend
    connect_timeout: 0.25s
    type: LOGICAL_DNS
    http2_protocol_options: {}
    lb_policy: ROUND_ROBIN
    load_assignment:
      cluster_name: grpc_backend
      endpoints:
        - lb_endpoints:
            - endpoint:
                address:
                  socket_address:
                    address: backend
                    port_value: 50051
```

### 4. RabbitMQ Integration

**¿Por qué RabbitMQ?**
- Desacoplar transcripción de procesamiento posterior
- Permitir múltiples consumidores
- Garantizar entrega de mensajes

**Flujo:**
```
Transcripción → RabbitMQ Exchange (topic) → Queue → Consumer
```

---

## Estructura del Proyecto

```
grpc-voice/
├── backend/                      # Backend Python
│   ├── proto/
│   │   ├── audio_service.proto   # Definición gRPC ⭐
│   │   ├── audio_service_pb2.py  # Generado (mensajes)
│   │   └── audio_service_pb2_grpc.py  # Generado (servicios)
│   ├── services/
│   │   ├── grpc_service.py       # Implementación servidor gRPC ⭐
│   │   ├── whisper_service.py    # Integración Whisper AI ⭐
│   │   └── rabbitmq_service.py   # Cliente RabbitMQ ⭐
│   ├── main.py                   # Punto de entrada ⭐
│   ├── config.py                 # Configuración
│   ├── requirements.txt          # Dependencias Python
│   ├── consumer_example.py       # Ejemplo consumer RabbitMQ
│   └── test_api.py               # Tests
│
├── frontend/                     # Frontend React
│   ├── src/
│   │   ├── components/
│   │   │   ├── AudioRecorder.tsx # Grabador de audio ⭐
│   │   │   ├── FileUploader.tsx  # Subida de archivos
│   │   │   └── TranscriptionDisplay.tsx
│   │   ├── hooks/
│   │   │   └── useAudioRecorder.ts  # Hook personalizado
│   │   ├── services/
│   │   │   └── audioService.ts   # Cliente API/gRPC ⭐
│   │   ├── App.tsx               # Componente principal
│   │   └── main.tsx
│   └── package.json
│
├── docker-compose.yml            # Docker básico
├── docker-compose.full.yml       # Docker completo (recomendado)
├── docker-compose.dev.yml        # Solo servicios externos
├── docker-compose.prod.yml       # Producción con HTTPS
├── envoy.yaml                    # Configuración Envoy ⭐
├── envoy.prod.yaml               # Envoy producción
├── init-letsencrypt.sh           # Script SSL
├── manage.sh                     # Script de gestión
│
├── README.md                     # Documentación principal
├── QUICKSTART.md                 # Inicio rápido
├── SETUP.md                      # Setup detallado
├── DEPLOY_GUIDE.md               # Guía de deploy
├── PRODUCTION_SUMMARY.md         # Resumen producción
├── DOCKER_GUIDE.md               # Guía Docker
└── docs/                         # Documentación adicional
    ├── GRPC_BACKEND_GUIDE.md     # Guía backend gRPC
    └── GRPC_FRONTEND_GUIDE.md    # Guía frontend gRPC-Web
```

**Archivos clave marcados con ⭐**

---

## Paso a Paso: Entendiendo gRPC Voice

### Paso 1: Definición del Servicio (.proto)

**Archivo:** `backend/proto/audio_service.proto`

```protobuf
syntax = "proto3";
package audiostream;

service AudioStreamService {
  // Bidirectional streaming
  rpc StreamAudio(stream AudioChunk) returns (stream TranscriptionResponse);

  // Unary
  rpc TranscribeAudio(AudioFile) returns (TranscriptionResponse);
}

message AudioChunk {
  bytes audio_data = 1;
  int32 chunk_index = 2;
  string session_id = 3;
  AudioMetadata metadata = 4;
}

message TranscriptionResponse {
  string text = 1;
  string session_id = 2;
  float confidence = 3;
  int64 timestamp = 4;
  bool is_final = 5;
  TranscriptionMetadata metadata = 6;
}
```

**Conceptos:**
- `stream AudioChunk`: El cliente puede enviar múltiples chunks
- `stream TranscriptionResponse`: El servidor puede enviar múltiples respuestas
- `bytes audio_data`: Datos binarios del audio

---

### Paso 2: Servidor gRPC (Python)

**Archivo:** `backend/services/grpc_service.py`

Implementación simplificada:

```python
import grpc
from concurrent import futures
import audio_service_pb2
import audio_service_pb2_grpc
from services.whisper_service import WhisperService
from services.rabbitmq_service import RabbitMQService

class AudioStreamServicer(audio_service_pb2_grpc.AudioStreamServiceServicer):
    def __init__(self):
        self.whisper_service = WhisperService()
        self.rabbitmq_service = RabbitMQService()

    def StreamAudio(self, request_iterator, context):
        """Bidirectional streaming"""
        audio_buffer = bytearray()
        session_id = None

        # Recibir chunks del cliente
        for chunk in request_iterator:
            session_id = chunk.session_id
            audio_buffer.extend(chunk.audio_data)

            # Opcional: transcribir parcialmente
            if len(audio_buffer) > threshold:
                partial = self.whisper_service.transcribe(bytes(audio_buffer))
                yield self._create_response(partial, session_id, is_final=False)

        # Transcripción final
        final_transcription = self.whisper_service.transcribe(bytes(audio_buffer))

        # Publicar a RabbitMQ
        self.rabbitmq_service.publish_transcription(final_transcription)

        # Responder al cliente
        yield self._create_response(final_transcription, session_id, is_final=True)

    def TranscribeAudio(self, request, context):
        """Unary RPC"""
        transcription = self.whisper_service.transcribe(request.audio_data)
        self.rabbitmq_service.publish_transcription(transcription)
        return self._create_response(transcription, request.filename, is_final=True)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    audio_service_pb2_grpc.add_AudioStreamServiceServicer_to_server(
        AudioStreamServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
```

**Puntos clave:**
1. `request_iterator`: Recibe chunks en streaming
2. `yield`: Envía respuestas en streaming
3. Buffering de audio antes de transcribir
4. Publicación a RabbitMQ

---

### Paso 3: Integración con Whisper AI

**Archivo:** `backend/services/whisper_service.py`

```python
import whisper
import tempfile

class WhisperService:
    def __init__(self, model_name="base"):
        self.model = whisper.load_model(model_name)

    def transcribe(self, audio_bytes, language="es"):
        # Guardar audio temporal
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(audio_bytes)
            temp_path = f.name

        # Transcribir con Whisper
        result = self.model.transcribe(
            temp_path,
            language=language,
            fp16=False  # CPU compatible
        )

        return {
            "text": result["text"],
            "language": result["language"],
            "segments": result["segments"],
            "duration": result.get("duration", 0)
        }
```

**Modelos Whisper:**
- `tiny`: Rápido, menor precisión
- `base`: Balance (recomendado para desarrollo)
- `small`: Mejor precisión
- `medium/large`: Máxima precisión, requiere GPU

---

### Paso 4: Cliente gRPC-Web (React/TypeScript)

**Archivo:** `frontend/src/services/audioService.ts`

```typescript
import { AudioStreamServiceClient } from '../proto/audio_service_grpc_web_pb';
import { AudioChunk, AudioFile, AudioMetadata } from '../proto/audio_service_pb';

const client = new AudioStreamServiceClient('http://localhost:8080');

export class AudioService {
  // Transcribir archivo completo (Unary)
  async transcribeFile(file: File, language: string = 'es') {
    const audioFile = new AudioFile();
    const arrayBuffer = await file.arrayBuffer();

    audioFile.setAudioData(new Uint8Array(arrayBuffer));
    audioFile.setFilename(file.name);

    const metadata = new AudioMetadata();
    metadata.setLanguage(language);
    audioFile.setMetadata(metadata);

    return new Promise((resolve, reject) => {
      client.transcribeAudio(audioFile, {}, (err, response) => {
        if (err) reject(err);
        else resolve(response.toObject());
      });
    });
  }

  // Streaming de audio (Bidirectional)
  streamAudio(audioBlob: Blob, sessionId: string, onResponse: (text: string) => void) {
    const stream = client.streamAudio({});

    // Escuchar respuestas del servidor
    stream.on('data', (response) => {
      onResponse(response.getText());
    });

    stream.on('error', (err) => {
      console.error('Stream error:', err);
    });

    stream.on('end', () => {
      console.log('Stream ended');
    });

    // Enviar chunks de audio
    this.sendAudioChunks(audioBlob, sessionId, stream);

    return stream;
  }

  private async sendAudioChunks(blob: Blob, sessionId: string, stream: any) {
    const chunkSize = 4096; // 4KB por chunk
    const arrayBuffer = await blob.arrayBuffer();
    const totalChunks = Math.ceil(arrayBuffer.byteLength / chunkSize);

    for (let i = 0; i < totalChunks; i++) {
      const start = i * chunkSize;
      const end = Math.min(start + chunkSize, arrayBuffer.byteLength);
      const chunk = new Uint8Array(arrayBuffer.slice(start, end));

      const audioChunk = new AudioChunk();
      audioChunk.setAudioData(chunk);
      audioChunk.setChunkIndex(i);
      audioChunk.setSessionId(sessionId);

      stream.write(audioChunk);
    }

    stream.end();
  }
}
```

**Flujo de streaming:**
1. Crear stream bidireccional
2. Dividir audio en chunks de 4KB
3. Enviar chunks secuencialmente
4. Recibir respuestas en tiempo real
5. Cerrar stream

---

### Paso 5: Grabación de Audio (Web Audio API)

**Archivo:** `frontend/src/hooks/useAudioRecorder.ts`

```typescript
import { useState, useCallback } from 'react';

export function useAudioRecorder() {
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [audioChunks, setAudioChunks] = useState<Blob[]>([]);

  const startRecording = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream, {
      mimeType: 'audio/webm' // o 'audio/mp4' según soporte
    });

    const chunks: Blob[] = [];

    recorder.ondataavailable = (e) => {
      chunks.push(e.data);
    };

    recorder.onstop = () => {
      const audioBlob = new Blob(chunks, { type: 'audio/webm' });
      setAudioChunks([audioBlob]);
    };

    recorder.start();
    setMediaRecorder(recorder);
    setIsRecording(true);
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  }, [mediaRecorder]);

  return { isRecording, startRecording, stopRecording, audioChunks };
}
```

---

### Paso 6: RabbitMQ Integration

**Archivo:** `backend/services/rabbitmq_service.py`

```python
import pika
import json
from config import settings

class RabbitMQService:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.URLParameters(settings.RABBITMQ_URL)
        )
        self.channel = self.connection.channel()

        # Declarar exchange y queue
        self.channel.exchange_declare(
            exchange=settings.RABBITMQ_EXCHANGE,
            exchange_type='topic',
            durable=True
        )

        self.channel.queue_declare(
            queue=settings.RABBITMQ_QUEUE,
            durable=True
        )

        self.channel.queue_bind(
            exchange=settings.RABBITMQ_EXCHANGE,
            queue=settings.RABBITMQ_QUEUE,
            routing_key=settings.RABBITMQ_ROUTING_KEY
        )

    def publish_transcription(self, transcription_data):
        message = json.dumps(transcription_data)

        self.channel.basic_publish(
            exchange=settings.RABBITMQ_EXCHANGE,
            routing_key=settings.RABBITMQ_ROUTING_KEY,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Mensaje persistente
                content_type='application/json'
            )
        )
```

**Consumer de ejemplo:** `backend/consumer_example.py`

```python
import pika
import json

def callback(ch, method, properties, body):
    transcription = json.loads(body)
    print(f"Transcripción recibida: {transcription['text']}")
    # Aquí puedes procesar la transcripción:
    # - Guardar en base de datos
    # - Enviar notificación
    # - Trigger de otro proceso
    ch.basic_ack(delivery_tag=method.delivery_tag)

connection = pika.BlockingConnection(pika.URLParameters('amqp://localhost:5672'))
channel = connection.channel()
channel.basic_consume(
    queue='transcription_queue',
    on_message_callback=callback
)

print('Esperando transcripciones...')
channel.start_consuming()
```

---

## Instalación y Ejecución

### Opción 1: Docker (Recomendado)

**Sistema completo:**

```bash
cd grpc-voice
docker-compose -f docker-compose.full.yml up -d
```

Servicios disponibles:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001/docs
- RabbitMQ UI: http://localhost:15672 (guest/guest)
- gRPC-Web: http://localhost:8080

**Verificar logs:**

```bash
# Ver todos los logs
docker-compose -f docker-compose.full.yml logs -f

# Ver solo backend
docker-compose -f docker-compose.full.yml logs -f backend

# Ver solo frontend
docker-compose -f docker-compose.full.yml logs -f frontend
```

---

### Opción 2: Setup Manual (Desarrollo)

**Backend:**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# Generar archivos proto
python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./proto \
    --grpc_python_out=./proto \
    proto/audio_service.proto

# Ejecutar
python main.py
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

**RabbitMQ (con Docker):**

```bash
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  rabbitmq:3-management
```

**Envoy (con Docker):**

```bash
docker run -d --name envoy \
  -p 8080:8080 \
  -v $(pwd)/envoy.yaml:/etc/envoy/envoy.yaml \
  envoyproxy/envoy:v1.28-latest
```

---

## Ejercicios Prácticos

### Ejercicio 1: Agregar Soporte para Nuevos Idiomas

1. Modifica `frontend/src/components/AudioRecorder.tsx` para seleccionar idioma
2. Pasa el idioma en `AudioMetadata`
3. Usa el idioma en Whisper service

### Ejercicio 2: Implementar Progreso de Transcripción

1. Agrega campo `progress` a `TranscriptionResponse`
2. Envía actualizaciones de progreso desde el servidor
3. Muestra barra de progreso en el frontend

### Ejercicio 3: Guardar Transcripciones en Base de Datos

1. Agrega SQLite/PostgreSQL al backend
2. Crea modelo de `Transcription`
3. Guarda cada transcripción
4. Crea endpoint para listar historial

### Ejercicio 4: Implementar Autenticación

1. Agrega JWT al backend
2. Valida token en gRPC metadata
3. Protege endpoints sensibles

### Ejercicio 5: Optimizar Chunks de Audio

1. Experimenta con diferentes tamaños de chunk
2. Mide latencia vs throughput
3. Implementa compresión de audio

---

## Troubleshooting

### Error: "Cannot connect to gRPC server"

**Problema:** Envoy no está corriendo o mal configurado

**Solución:**
```bash
# Verificar que Envoy esté corriendo
docker ps | grep envoy

# Ver logs de Envoy
docker logs envoy

# Reiniciar Envoy
docker restart envoy
```

### Error: "Whisper model not found"

**Problema:** Modelo de Whisper no descargado

**Solución:**
```bash
# Entrar al container
docker exec -it backend bash

# Descargar modelo manualmente
python -c "import whisper; whisper.load_model('base')"
```

### Error: "RabbitMQ connection refused"

**Problema:** RabbitMQ no está corriendo

**Solución:**
```bash
# Iniciar RabbitMQ
docker-compose -f docker-compose.full.yml up -d rabbitmq

# Verificar
docker logs rabbitmq
```

### Frontend no puede grabar audio

**Problema:** Permisos de micrófono o HTTPS requerido

**Solución:**
- Usar `localhost` (permitido sin HTTPS)
- O configurar HTTPS en desarrollo

---

## Recursos Adicionales

### Documentación del Proyecto

- [README.md](./README.md) - Descripción general
- [QUICKSTART.md](./QUICKSTART.md) - Inicio rápido
- [DOCKER_GUIDE.md](./DOCKER_GUIDE.md) - Guía completa de Docker
- [DEPLOY_GUIDE.md](./DEPLOY_GUIDE.md) - Deploy a producción

### Referencias Externas

- [gRPC Python](https://grpc.io/docs/languages/python/)
- [gRPC-Web](https://github.com/grpc/grpc-web)
- [Whisper AI](https://github.com/openai/whisper)
- [Envoy Proxy](https://www.envoyproxy.io/docs/envoy/latest/)
- [RabbitMQ Tutorials](https://www.rabbitmq.com/getstarted.html)

---

## Próximos Pasos

1. Completar el proyecto básico `grpc-basico` primero
2. Estudiar cada componente de `grpc-voice` individualmente
3. Ejecutar el proyecto completo
4. Modificar y experimentar con los ejercicios
5. Implementar tu propio servicio basado en este patrón

---

¡Éxito en tu aprendizaje de gRPC!

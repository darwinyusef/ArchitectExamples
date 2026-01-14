# Guía de gRPC - Backend (Python)

Esta guía explica cómo funciona gRPC en el backend de este proyecto.

## ¿Qué es gRPC?

**gRPC** (Google Remote Procedure Call) es un framework de comunicación de alto rendimiento que permite que aplicaciones cliente y servidor se comuniquen de manera eficiente.

**Ventajas:**
- ✅ Más rápido que REST (usa HTTP/2)
- ✅ Streaming bidireccional en tiempo real
- ✅ Tipado fuerte con Protocol Buffers
- ✅ Soporte para múltiples lenguajes
- ✅ Ideal para microservicios

**Comparación:**
```
REST API: Cliente → HTTP Request → Servidor → HTTP Response
gRPC:     Cliente ← → Streaming bidireccional ← → Servidor
```

---

## 1. Definir el Servicio (.proto)

Los servicios gRPC se definen en archivos `.proto` usando **Protocol Buffers**.

**Archivo:** `backend/proto/audio_service.proto`

```protobuf
syntax = "proto3";

package audiostream;

// Definición del servicio
service AudioStreamService {
  // Streaming bidireccional: cliente envía chunks, servidor responde
  rpc StreamAudio(stream AudioChunk) returns (stream TranscriptionResponse);

  // Método unario: un request, un response
  rpc TranscribeAudio(AudioFile) returns (TranscriptionResponse);
}

// Mensajes (estructuras de datos)
message AudioChunk {
  bytes audio_data = 1;        // Datos del audio
  int32 chunk_index = 2;       // Índice del chunk
  string session_id = 3;       // ID de sesión
  AudioMetadata metadata = 4;  // Metadata
}

message TranscriptionResponse {
  string text = 1;             // Texto transcrito
  string session_id = 2;       // ID de sesión
  float confidence = 3;        // Confianza (0-1)
  int64 timestamp = 4;         // Timestamp Unix
  bool is_final = 5;           // Si es final
  TranscriptionMetadata metadata = 6;
}
```

**Conceptos clave:**

- `syntax = "proto3"`: Versión de Protocol Buffers
- `service`: Define los métodos RPC
- `rpc`: Define un método remoto
- `stream`: Indica que es streaming (múltiples mensajes)
- `message`: Define una estructura de datos
- `= 1, = 2`: Números de campo (deben ser únicos)

---

## 2. Generar Código Python

Protocol Buffers genera código Python automáticamente:

```bash
cd backend

# Generar archivos Python desde .proto
python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./proto \
    --grpc_python_out=./proto \
    proto/audio_service.proto
```

**Esto genera:**
- `audio_service_pb2.py`: Mensajes (clases Python)
- `audio_service_pb2_grpc.py`: Servicios (stubs cliente/servidor)

---

## 3. Implementar el Servidor gRPC

**Archivo:** `backend/services/grpc_service.py`

### 3.1 Importar módulos generados

```python
from proto import audio_service_pb2, audio_service_pb2_grpc
import grpc
```

### 3.2 Crear la clase del servicio

Hereda de la clase generada:

```python
class AudioStreamServicer(audio_service_pb2_grpc.AudioStreamServiceServicer):
    """Implementación del servicio"""

    async def TranscribeAudio(
        self,
        request: audio_service_pb2.AudioFile,
        context: grpc.aio.ServicerContext
    ) -> audio_service_pb2.TranscriptionResponse:
        """Método unario: transcribir un archivo completo"""

        # 1. Obtener datos del request
        audio_data = request.audio_data
        filename = request.filename

        # 2. Procesar (transcribir con Whisper)
        transcription = await whisper_service.transcribe(audio_data)

        # 3. Crear response
        response = audio_service_pb2.TranscriptionResponse(
            text=transcription['text'],
            session_id=str(uuid.uuid4()),
            confidence=1.0,
            timestamp=int(time.time()),
            is_final=True
        )

        # 4. Retornar response
        return response
```

### 3.3 Implementar Streaming Bidireccional

```python
async def StreamAudio(
    self,
    request_iterator: Iterator[audio_service_pb2.AudioChunk],
    context: grpc.aio.ServicerContext
) -> Iterator[audio_service_pb2.TranscriptionResponse]:
    """Streaming bidireccional"""

    # Iterar sobre los chunks que envía el cliente
    async for chunk in request_iterator:
        # Procesar cada chunk
        audio_data = chunk.audio_data
        session_id = chunk.session_id

        # Transcribir
        result = await whisper_service.transcribe(audio_data)

        # Enviar respuesta al cliente (yield)
        response = audio_service_pb2.TranscriptionResponse(
            text=result['text'],
            session_id=session_id,
            is_final=False
        )

        yield response  # Enviar al cliente
```

**Conceptos:**
- `async for`: Recibir chunks del cliente
- `yield`: Enviar respuestas al cliente
- `Iterator`: Permite streaming continuo

### 3.4 Iniciar el servidor

```python
async def serve():
    # Crear servidor gRPC
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10)
    )

    # Registrar el servicio
    audio_service_pb2_grpc.add_AudioStreamServiceServicer_to_server(
        AudioStreamServicer(), server
    )

    # Configurar puerto
    listen_addr = f'[::]:{settings.grpc_port}'
    server.add_insecure_port(listen_addr)

    # Iniciar
    await server.start()
    await server.wait_for_termination()
```

---

## 4. Tipos de Métodos gRPC

### 4.1 Unario (Simple Request-Response)

```protobuf
rpc TranscribeAudio(AudioFile) returns (TranscriptionResponse);
```

**Python:**
```python
async def TranscribeAudio(self, request, context):
    # Procesar request
    result = process(request)
    # Retornar response
    return result
```

**Uso:**
- Un request → Un response
- Como REST API tradicional
- Ideal para operaciones simples

### 4.2 Server Streaming

```protobuf
rpc StreamTranscriptions(AudioFile) returns (stream TranscriptionResponse);
```

**Python:**
```python
async def StreamTranscriptions(self, request, context):
    for transcription in transcriptions:
        yield transcription
```

**Uso:**
- Un request → Múltiples responses
- Servidor envía datos continuamente
- Ejemplo: Live updates

### 4.3 Client Streaming

```protobuf
rpc UploadAudio(stream AudioChunk) returns (TranscriptionResponse);
```

**Python:**
```python
async def UploadAudio(self, request_iterator, context):
    chunks = []
    async for chunk in request_iterator:
        chunks.append(chunk)
    return process(chunks)
```

**Uso:**
- Múltiples requests → Un response
- Cliente envía datos continuamente
- Ejemplo: Upload de archivos grandes

### 4.4 Bidirectional Streaming (Lo que usamos)

```protobuf
rpc StreamAudio(stream AudioChunk) returns (stream TranscriptionResponse);
```

**Python:**
```python
async def StreamAudio(self, request_iterator, context):
    async for chunk in request_iterator:
        result = process(chunk)
        yield result
```

**Uso:**
- Múltiples requests ↔ Múltiples responses
- Comunicación en tiempo real
- Ejemplo: Chat, audio streaming

---

## 5. Manejo de Errores

```python
async def TranscribeAudio(self, request, context):
    try:
        result = await process(request)
        return result
    except ValueError as e:
        # Error de validación
        await context.abort(
            grpc.StatusCode.INVALID_ARGUMENT,
            f"Invalid input: {str(e)}"
        )
    except Exception as e:
        # Error interno
        await context.abort(
            grpc.StatusCode.INTERNAL,
            f"Internal error: {str(e)}"
        )
```

**Status Codes comunes:**
- `OK`: Todo bien
- `INVALID_ARGUMENT`: Parámetros inválidos
- `NOT_FOUND`: Recurso no encontrado
- `INTERNAL`: Error interno del servidor
- `UNAVAILABLE`: Servicio no disponible

---

## 6. Metadata (Headers)

Enviar y recibir metadata:

```python
async def TranscribeAudio(self, request, context):
    # Leer metadata del request
    metadata = dict(context.invocation_metadata())
    auth_token = metadata.get('authorization')

    # Enviar metadata en el response
    context.set_trailing_metadata([
        ('request-id', '12345'),
        ('processing-time', '1.5s')
    ])

    return response
```

---

## 7. Interceptores

Los interceptores permiten ejecutar código antes/después de cada RPC:

```python
class LoggingInterceptor(grpc.aio.ServerInterceptor):
    async def intercept_service(self, continuation, handler_call_details):
        # Antes del RPC
        logger.info(f"RPC called: {handler_call_details.method}")

        # Ejecutar RPC
        response = await continuation(handler_call_details)

        # Después del RPC
        logger.info("RPC completed")

        return response

# Usar el interceptor
server = grpc.aio.server(
    interceptors=[LoggingInterceptor()]
)
```

---

## 8. Configuración Avanzada

### 8.1 Tamaño de Mensajes

```python
server = grpc.aio.server(
    options=[
        ('grpc.max_send_message_length', 50 * 1024 * 1024),    # 50MB
        ('grpc.max_receive_message_length', 50 * 1024 * 1024)  # 50MB
    ]
)
```

### 8.2 Timeout

```python
# En el cliente
stub.TranscribeAudio(request, timeout=30)  # 30 segundos
```

### 8.3 Keep-Alive

```python
server = grpc.aio.server(
    options=[
        ('grpc.keepalive_time_ms', 10000),           # 10s
        ('grpc.keepalive_timeout_ms', 5000),         # 5s
        ('grpc.keepalive_permit_without_calls', 1)
    ]
)
```

---

## 9. Testing

### 9.1 Test Manual con grpcurl

```bash
# Instalar grpcurl
brew install grpcurl  # macOS

# Listar servicios
grpcurl -plaintext localhost:50051 list

# Llamar método
grpcurl -plaintext -d '{"filename": "test.mp3"}' \
    localhost:50051 \
    audiostream.AudioStreamService/TranscribeAudio
```

### 9.2 Test en Python

```python
import grpc
from proto import audio_service_pb2, audio_service_pb2_grpc

async def test_transcribe():
    # Crear canal
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        # Crear stub (cliente)
        stub = audio_service_pb2_grpc.AudioStreamServiceStub(channel)

        # Crear request
        request = audio_service_pb2.AudioFile(
            audio_data=b'...',
            filename='test.mp3'
        )

        # Llamar método
        response = await stub.TranscribeAudio(request)

        print(f"Transcription: {response.text}")
```

---

## 10. Integración con FastAPI

En nuestro proyecto, corremos FastAPI y gRPC juntos:

```python
async def main():
    # Iniciar gRPC en background
    grpc_task = asyncio.create_task(serve_grpc())

    # Iniciar FastAPI
    config = uvicorn.Config(app, host="0.0.0.0", port=8001)
    server = uvicorn.Server(config)
    await server.serve()
```

**Esto permite:**
- API REST para operaciones simples
- gRPC para streaming en tiempo real
- Ambos servicios corriendo en el mismo proceso

---

## 11. Best Practices

✅ **DO:**
- Usar streaming para datos grandes o en tiempo real
- Manejar errores con status codes apropiados
- Validar inputs antes de procesarlos
- Usar metadata para auth y tracking
- Implementar timeouts
- Loggear requests/responses importantes

❌ **DON'T:**
- Enviar mensajes muy grandes en unary calls
- Bloquear el event loop con operaciones síncronas
- Olvidar cerrar streams
- Usar gRPC para todo (REST es mejor para APIs públicas)

---

## 12. Recursos

- [gRPC Python Docs](https://grpc.io/docs/languages/python/)
- [Protocol Buffers Guide](https://developers.google.com/protocol-buffers)
- [gRPC Best Practices](https://grpc.io/docs/guides/performance/)

---

## Resumen

1. **Definir** el servicio en `.proto`
2. **Generar** código Python con `protoc`
3. **Implementar** la clase del servicio
4. **Iniciar** el servidor gRPC
5. **Integrar** con RabbitMQ/Whisper según necesites

gRPC es ideal para comunicación en tiempo real y microservicios. En este proyecto lo usamos para streaming de audio bidireccional.

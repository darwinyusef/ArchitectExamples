# Guía de gRPC - Frontend (React/TypeScript)

Esta guía explica cómo conectar un cliente React al servidor gRPC usando gRPC-Web.

## ¿Qué es gRPC-Web?

**gRPC-Web** es el cliente de gRPC para navegadores web. Los navegadores no pueden usar gRPC directamente, necesitan un proxy (Envoy) que traduzca las peticiones.

```
React App → HTTP/gRPC-Web → Envoy Proxy → gRPC Server
```

**Arquitectura completa:**
```
┌──────────────┐
│   React App  │
│              │
│  gRPC-Web    │  (Puerto 3000)
│  Client      │
└──────┬───────┘
       │ HTTP 1.1/2
       ▼
┌──────────────┐
│    Envoy     │  (Puerto 8080)
│    Proxy     │
└──────┬───────┘
       │ gRPC/HTTP2
       ▼
┌──────────────┐
│   Backend    │  (Puerto 50051)
│ gRPC Server  │
└──────────────┘
```

---

## 1. Alternativas para Frontend

### Opción 1: API REST (Más Simple) ✅ ACTUAL

**Lo que usamos ahora:**

```typescript
// frontend/src/services/audioService.ts
export class AudioService {
  async transcribeAudio(audioBlob: Blob): Promise<TranscriptionResult> {
    const formData = new FormData();
    formData.append('file', audioBlob, 'audio.mp3');

    const response = await fetch('http://localhost:8001/transcribe', {
      method: 'POST',
      body: formData,
    });

    return response.json();
  }
}
```

**Ventajas:**
- ✅ Muy simple, no necesita configuración
- ✅ Funciona en todos los navegadores
- ✅ Ideal para operaciones simples

**Desventajas:**
- ❌ No tiene streaming bidireccional
- ❌ Menos eficiente que gRPC

**Cuándo usar:** Operaciones simples como subir archivo y obtener transcripción.

---

### Opción 2: gRPC-Web (Streaming Real) 🔥

**Para streaming en tiempo real:**

```typescript
import { AudioStreamServiceClient } from './proto/audio_service_grpc_web_pb';
import { AudioChunk, TranscriptionResponse } from './proto/audio_service_pb';

const client = new AudioStreamServiceClient('http://localhost:8080');

// Streaming bidireccional
const stream = client.streamAudio();

// Enviar chunks
stream.on('data', (response: TranscriptionResponse) => {
  console.log('Transcription:', response.getText());
});

stream.on('error', (error) => {
  console.error('Error:', error);
});

// Enviar audio chunk
const chunk = new AudioChunk();
chunk.setAudioData(audioData);
chunk.setSessionId('session-123');
stream.write(chunk);
```

**Ventajas:**
- ✅ Streaming bidireccional real
- ✅ Más eficiente que REST
- ✅ Tipado fuerte con TypeScript

**Desventajas:**
- ❌ Requiere Envoy proxy
- ❌ Más complejo de configurar

**Cuándo usar:** Cuando necesitas streaming en tiempo real (ej: transcripción mientras grabas).

---

## 2. Setup de gRPC-Web (Opcional)

Si quieres implementar streaming real, sigue estos pasos:

### 2.1 Instalar Dependencias

```bash
cd frontend
npm install grpc-web google-protobuf
npm install --save-dev @types/google-protobuf
```

### 2.2 Instalar Herramientas

**macOS:**
```bash
brew install protobuf
npm install -g protoc-gen-grpc-web
```

**Ubuntu/Debian:**
```bash
apt-get install protobuf-compiler
npm install -g protoc-gen-grpc-web
```

### 2.3 Generar Código TypeScript

Crear script en `package.json`:

```json
{
  "scripts": {
    "proto": "protoc -I=../backend/proto --js_out=import_style=commonjs,binary:./src/proto --grpc-web_out=import_style=typescript,mode=grpcwebtext:./src/proto ../backend/proto/audio_service.proto"
  }
}
```

Ejecutar:
```bash
npm run proto
```

**Esto genera:**
- `audio_service_pb.js`: Mensajes
- `audio_service_pb.d.ts`: Types TypeScript
- `AudioStreamServiceServiceClientPb.ts`: Cliente gRPC-Web

---

## 3. Implementar Cliente gRPC-Web

### 3.1 Crear Servicio

**Archivo:** `frontend/src/services/grpcAudioService.ts`

```typescript
import { AudioStreamServiceClient } from '../proto/AudioStreamServiceServiceClientPb';
import { AudioFile, AudioChunk, TranscriptionResponse } from '../proto/audio_service_pb';

class GrpcAudioService {
  private client: AudioStreamServiceClient;

  constructor() {
    // Cliente conecta a Envoy proxy
    this.client = new AudioStreamServiceClient(
      'http://localhost:8080',
      null,
      null
    );
  }

  // Método unario
  async transcribeAudio(audioData: Uint8Array): Promise<string> {
    return new Promise((resolve, reject) => {
      const request = new AudioFile();
      request.setAudioData(audioData);
      request.setFilename('audio.mp3');

      this.client.transcribeAudio(request, {}, (err, response) => {
        if (err) {
          reject(err);
        } else {
          resolve(response.getText());
        }
      });
    });
  }

  // Streaming bidireccional
  streamAudio(
    onTranscription: (text: string) => void,
    onError: (error: Error) => void
  ) {
    const stream = this.client.streamAudio();

    // Escuchar respuestas
    stream.on('data', (response: TranscriptionResponse) => {
      onTranscription(response.getText());
    });

    stream.on('error', (error) => {
      onError(new Error(error.message));
    });

    stream.on('end', () => {
      console.log('Stream ended');
    });

    // Retornar funciones para enviar y cerrar
    return {
      send: (audioData: Uint8Array, sessionId: string) => {
        const chunk = new AudioChunk();
        chunk.setAudioData(audioData);
        chunk.setSessionId(sessionId);
        chunk.setChunkIndex(0);
        stream.write(chunk);
      },
      close: () => {
        stream.end();
      }
    };
  }
}

export const grpcAudioService = new GrpcAudioService();
```

### 3.2 Usar en Componente React

```typescript
import { useState, useEffect } from 'react';
import { grpcAudioService } from '../services/grpcAudioService';

function AudioStreamer() {
  const [transcription, setTranscription] = useState('');
  const [stream, setStream] = useState<any>(null);

  const startStreaming = () => {
    const newStream = grpcAudioService.streamAudio(
      // Callback para transcripciones
      (text) => {
        setTranscription(prev => prev + ' ' + text);
      },
      // Callback para errores
      (error) => {
        console.error('Stream error:', error);
      }
    );

    setStream(newStream);
  };

  const sendAudioChunk = (audioData: Uint8Array) => {
    if (stream) {
      stream.send(audioData, 'session-123');
    }
  };

  const stopStreaming = () => {
    if (stream) {
      stream.close();
      setStream(null);
    }
  };

  return (
    <div>
      <button onClick={startStreaming}>Start Streaming</button>
      <button onClick={stopStreaming}>Stop</button>
      <p>Transcription: {transcription}</p>
    </div>
  );
}
```

---

## 4. Configurar Envoy Proxy

El proxy Envoy traduce gRPC-Web a gRPC puro.

**Archivo:** `envoy.yaml` (ya incluido en el proyecto)

```yaml
static_resources:
  listeners:
  - name: listener_0
    address:
      socket_address:
        address: 0.0.0.0
        port_value: 8080  # Puerto para gRPC-Web
    filter_chains:
    - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          http_filters:
          - name: envoy.filters.http.grpc_web
          - name: envoy.filters.http.cors
          - name: envoy.filters.http.router

  clusters:
  - name: grpc_service
    connect_timeout: 0.25s
    type: logical_dns
    http2_protocol_options: {}
    load_assignment:
      endpoints:
      - lb_endpoints:
        - endpoint:
            address:
              socket_address:
                address: backend  # Hostname del backend
                port_value: 50051 # Puerto gRPC del backend
```

**Iniciar Envoy:**
```bash
docker-compose up -d envoy
```

---

## 5. Comparación: REST vs gRPC-Web

### REST API (Actual)

```typescript
// ✅ Simple
const result = await fetch('http://localhost:8001/transcribe', {
  method: 'POST',
  body: formData
});
```

**Flujo:**
1. Usuario graba audio
2. Audio completo → Backend
3. Backend transcribe
4. Response completa ← Frontend

**Tiempo:** Espera total hasta completar

---

### gRPC-Web Streaming

```typescript
// 🔥 Streaming real
const stream = client.streamAudio();
stream.on('data', (response) => {
  // Recibir transcripciones parciales en tiempo real
  console.log(response.getText());
});
```

**Flujo:**
1. Usuario comienza a grabar
2. Chunks de audio → Backend (mientras graba)
3. Backend transcribe chunks
4. Transcripciones parciales ← Frontend (en tiempo real)

**Tiempo:** Sin espera, resultados instantáneos

---

## 6. Ejemplo Completo: Streaming en Tiempo Real

### 6.1 Hook Personalizado

```typescript
// frontend/src/hooks/useGrpcStreaming.ts
import { useState, useCallback } from 'react';
import { grpcAudioService } from '../services/grpcAudioService';

export const useGrpcStreaming = () => {
  const [transcription, setTranscription] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [stream, setStream] = useState<any>(null);

  const startStream = useCallback(() => {
    const newStream = grpcAudioService.streamAudio(
      (text) => {
        setTranscription(prev => prev + ' ' + text);
      },
      (error) => {
        console.error('Error:', error);
        setIsStreaming(false);
      }
    );

    setStream(newStream);
    setIsStreaming(true);
  }, []);

  const sendChunk = useCallback((audioData: Uint8Array) => {
    if (stream) {
      stream.send(audioData, Date.now().toString());
    }
  }, [stream]);

  const stopStream = useCallback(() => {
    if (stream) {
      stream.close();
      setStream(null);
      setIsStreaming(false);
    }
  }, [stream]);

  return {
    transcription,
    isStreaming,
    startStream,
    sendChunk,
    stopStream
  };
};
```

### 6.2 Componente con Grabación en Tiempo Real

```typescript
import { useGrpcStreaming } from '../hooks/useGrpcStreaming';
import { useAudioRecorder } from '../hooks/useAudioRecorder';

function RealtimeTranscriber() {
  const { transcription, isStreaming, startStream, sendChunk, stopStream } =
    useGrpcStreaming();

  const handleStartRecording = async () => {
    // Iniciar stream gRPC
    startStream();

    // Capturar audio del micrófono
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
      // Enviar chunk al servidor en tiempo real
      if (event.data.size > 0) {
        event.data.arrayBuffer().then(buffer => {
          const uint8Array = new Uint8Array(buffer);
          sendChunk(uint8Array);
        });
      }
    };

    // Capturar chunks cada 1 segundo
    mediaRecorder.start(1000);
  };

  const handleStop = () => {
    stopStream();
  };

  return (
    <div>
      <button onClick={handleStartRecording}>
        🎤 Start Real-time Transcription
      </button>
      <button onClick={handleStop}>⏹ Stop</button>

      <div>
        <h3>Transcription (live):</h3>
        <p>{transcription}</p>
      </div>
    </div>
  );
}
```

---

## 7. Manejo de Errores

```typescript
class GrpcAudioService {
  async transcribeAudio(audioData: Uint8Array): Promise<string> {
    return new Promise((resolve, reject) => {
      const request = new AudioFile();
      request.setAudioData(audioData);

      this.client.transcribeAudio(request, {}, (err, response) => {
        if (err) {
          // Manejar diferentes códigos de error
          switch (err.code) {
            case 1: // CANCELLED
              reject(new Error('Request cancelled'));
              break;
            case 2: // UNKNOWN
              reject(new Error('Unknown error'));
              break;
            case 3: // INVALID_ARGUMENT
              reject(new Error('Invalid audio data'));
              break;
            case 14: // UNAVAILABLE
              reject(new Error('Service unavailable'));
              break;
            default:
              reject(new Error(`gRPC error: ${err.message}`));
          }
        } else {
          resolve(response.getText());
        }
      });
    });
  }
}
```

---

## 8. Metadata y Headers

```typescript
async transcribeAudio(audioData: Uint8Array): Promise<string> {
  const metadata = {
    'authorization': 'Bearer token123',
    'x-user-id': 'user-456'
  };

  return new Promise((resolve, reject) => {
    const request = new AudioFile();
    request.setAudioData(audioData);

    this.client.transcribeAudio(request, metadata, (err, response) => {
      // ...
    });
  });
}
```

---

## 9. Testing

```typescript
// Mock del cliente gRPC
jest.mock('../services/grpcAudioService');

describe('Audio Transcription', () => {
  it('should transcribe audio', async () => {
    const mockTranscription = 'Hello world';
    grpcAudioService.transcribeAudio = jest.fn()
      .mockResolvedValue(mockTranscription);

    const audioData = new Uint8Array([1, 2, 3]);
    const result = await grpcAudioService.transcribeAudio(audioData);

    expect(result).toBe(mockTranscription);
  });
});
```

---

## 10. Cuándo Usar Cada Opción

### Usar REST API (actual) cuando:
- ✅ Operación simple: subir archivo → obtener resultado
- ✅ No necesitas resultados en tiempo real
- ✅ Quieres mantener la implementación simple
- ✅ Compatibilidad con todos los navegadores

### Usar gRPC-Web cuando:
- ✅ Necesitas streaming en tiempo real
- ✅ Quieres ver transcripciones mientras grabas
- ✅ Manejas múltiples requests simultáneos
- ✅ Necesitas comunicación bidireccional

---

## 11. Migrar de REST a gRPC-Web

Para mejorar el proyecto actual:

1. **Instalar dependencias:**
```bash
npm install grpc-web google-protobuf
```

2. **Generar código:**
```bash
npm run proto
```

3. **Crear servicio gRPC:**
```typescript
// src/services/grpcAudioService.ts
// (código del punto 3.1)
```

4. **Actualizar componente:**
```typescript
// En lugar de:
await audioService.transcribeAudio(blob);

// Usar:
const stream = grpcAudioService.streamAudio(
  (text) => setTranscription(text),
  (error) => console.error(error)
);
```

5. **Iniciar Envoy:**
```bash
docker-compose up -d envoy
```

---

## 12. Best Practices

✅ **DO:**
- Usar REST para operaciones simples
- Usar gRPC-Web para streaming real
- Manejar errores apropiadamente
- Implementar retry logic
- Cerrar streams cuando termines
- Validar datos antes de enviar

❌ **DON'T:**
- Enviar chunks muy pequeños (< 1KB)
- Olvidar cerrar streams
- Bloquear el UI mientras envías datos
- Usar gRPC-Web si REST es suficiente

---

## 13. Debugging

### Ver requests en Browser DevTools:

1. Abrir DevTools → Network
2. Filtrar por `grpc`
3. Ver headers y payloads

### Logs en el cliente:

```typescript
const client = new AudioStreamServiceClient(
  'http://localhost:8080',
  null,
  {
    debug: true // Habilitar logs
  }
);
```

---

## 14. Recursos

- [gRPC-Web Docs](https://github.com/grpc/grpc-web)
- [Protocol Buffers](https://developers.google.com/protocol-buffers)
- [Envoy Proxy](https://www.envoyproxy.io/docs/envoy/latest/start/start)

---

## Resumen

**Estado Actual:**
- ✅ REST API funcionando (simple y efectivo)
- ✅ Perfecto para MVP

**Próximos Pasos (Opcional):**
1. Configurar Envoy proxy
2. Generar código gRPC-Web
3. Implementar streaming bidireccional
4. Obtener transcripciones en tiempo real

**¿Cuándo migrar?**
- Cuando necesites streaming real
- Cuando quieras resultados instantáneos
- Cuando tengas muchos usuarios simultáneos

Por ahora, el enfoque REST es perfecto para empezar. gRPC-Web es una optimización futura.

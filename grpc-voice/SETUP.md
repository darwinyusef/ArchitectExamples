# Guía de Instalación

## Pre-requisitos

### Servicios Externos
- RabbitMQ corriendo (puerto 5672)
- Whisper service corriendo (si usas API externa)

### Herramientas
- Python 3.9+
- Node.js 18+
- Docker & Docker Compose (opcional)

## Opción 1: Setup Manual

### Backend

1. Navegar al directorio del backend:
```bash
cd backend
```

2. Ejecutar script de setup:
```bash
chmod +x setup.sh
./setup.sh
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

4. Iniciar el servidor:
```bash
source venv/bin/activate
python main.py
```

El servidor estará disponible en:
- FastAPI: http://localhost:8000
- gRPC: localhost:50051

### Frontend

1. Navegar al directorio del frontend:
```bash
cd frontend
```

2. Instalar dependencias:
```bash
npm install
```

3. Iniciar el servidor de desarrollo:
```bash
npm run dev
```

El frontend estará disponible en: http://localhost:3000

## Opción 2: Setup con Docker

1. Construir e iniciar todos los servicios:
```bash
docker-compose up -d
```

2. Ver logs:
```bash
docker-compose logs -f
```

3. Detener servicios:
```bash
docker-compose down
```

Los servicios estarán disponibles en:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- gRPC: localhost:50051
- RabbitMQ Management: http://localhost:15672 (guest/guest)
- Envoy (gRPC-Web): http://localhost:8080

## Configuración de RabbitMQ

Si tienes RabbitMQ corriendo localmente:

1. Acceder al panel de administración:
   - URL: http://localhost:15672
   - Usuario: guest
   - Contraseña: guest

2. Crear exchange (opcional, se crea automáticamente):
   - Nombre: transcriptions
   - Tipo: topic
   - Durable: true

3. Crear queue (opcional, se crea automáticamente):
   - Nombre: transcription_queue
   - Durable: true

4. Bind queue to exchange:
   - Routing key: transcription.new

## Configuración de Whisper

### Opción 1: Usar modelo local (por defecto)

El backend cargará el modelo de Whisper localmente. Los modelos disponibles son:
- `tiny`: Más rápido, menos preciso
- `base`: Balance entre velocidad y precisión (por defecto)
- `small`: Mejor precisión, más lento
- `medium`: Alta precisión, requiere más recursos
- `large`: Máxima precisión, muy lento

Configurar en `.env`:
```env
WHISPER_MODEL=base
WHISPER_DEVICE=cpu  # o 'cuda' si tienes GPU
```

### Opción 2: Usar API externa de Whisper

Si tienes un servicio Whisper corriendo en otro servidor:

```env
WHISPER_API_URL=http://tu-servidor:9000
```

## Generar Archivos Proto para Frontend (Opcional)

Para usar gRPC-Web en el frontend:

1. Instalar protoc y el plugin de gRPC-Web:
```bash
# macOS
brew install protobuf
npm install -g grpc-web

# Ubuntu/Debian
apt-get install protobuf-compiler
npm install -g grpc-web
```

2. Generar archivos:
```bash
cd frontend
npm run proto
```

## Verificar Instalación

### Backend

1. Health check:
```bash
curl http://localhost:8000/health
```

2. Transcribir un archivo de prueba:
```bash
curl -X POST http://localhost:8000/transcribe \
  -F "file=@test_audio.mp3" \
  -F "language=es"
```

### Frontend

1. Abrir http://localhost:3000 en el navegador
2. Probar grabación de audio
3. Verificar que aparezcan las transcripciones

### RabbitMQ

1. Verificar que las transcripciones lleguen a la queue:
   - Ir a http://localhost:15672
   - Click en "Queues"
   - Verificar "transcription_queue"
   - Ver mensajes en "Get messages"

## Troubleshooting

### Error: "Cannot connect to RabbitMQ"

Verificar que RabbitMQ esté corriendo:
```bash
# Si usas Docker
docker ps | grep rabbitmq

# Si es instalación local
sudo systemctl status rabbitmq-server
```

### Error: "Whisper model download failed"

La primera vez que se ejecuta, Whisper descarga el modelo. Asegúrate de tener conexión a internet y espacio en disco.

### Error: "Permission denied: microphone"

El navegador necesita permisos para acceder al micrófono. Asegúrate de:
1. Usar HTTPS o localhost
2. Dar permisos cuando el navegador lo solicite

### Frontend no conecta con Backend

Verificar CORS en el backend. El archivo `main.py` debe tener:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Siguientes Pasos

1. Personalizar la UI del frontend
2. Agregar autenticación
3. Implementar streaming bidireccional con gRPC-Web
4. Agregar persistencia de transcripciones
5. Configurar workers de RabbitMQ para procesar transcripciones

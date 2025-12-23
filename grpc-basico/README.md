# gRPC Básico - Tutorial de Aprendizaje

Proyecto simple y educativo para aprender gRPC con Node.js y TypeScript.

## Descripción

Este proyecto proporciona una introducción práctica a gRPC mediante ejemplos simples y progresivos. Está diseñado para ser tu primer contacto con gRPC antes de abordar proyectos más complejos como `grpc-voice`.

## Características

- **Ejemplos progresivos**: Desde conceptos básicos hasta streaming bidireccional
- **Dos servicios completos**:
  - **Greeter**: Servicio de saludo con soporte multiidioma
  - **Calculator**: Calculadora con operaciones matemáticas
- **Todos los tipos de RPC**:
  - Unary RPC (petición-respuesta simple)
  - Server Streaming (un request, múltiples responses)
  - Client Streaming (múltiples requests, una response)
  - Bidirectional Streaming (comunicación en ambas direcciones)
- **Cliente interactivo**: Menú de terminal para probar todos los ejemplos
- **Documentación completa**: Guía de aprendizaje y taller práctico

## Estructura del Proyecto

```
grpc-basico/
├── proto/                      # Definiciones Protocol Buffers
│   ├── greeter.proto          # Servicio de saludo
│   └── calculator.proto       # Servicio de calculadora
├── server/                     # Implementación del servidor
│   ├── index.ts               # Punto de entrada
│   └── services/
│       ├── greeterService.ts
│       └── calculatorService.ts
├── client/                     # Cliente interactivo
│   └── index.ts
├── package.json
├── tsconfig.json
├── Dockerfile                  # Imagen Docker
├── docker-compose.yml          # Orquestación (producción)
├── docker-compose.dev.yml      # Desarrollo con hot-reload
├── docker-compose.test.yml     # Tests automáticos
├── .dockerignore
├── README.md                   # Este archivo
├── GUIA_APRENDIZAJE.md        # Guía completa de gRPC
├── TALLER.md                   # Ejercicios prácticos
└── DOCKER_GUIDE.md             # Guía de Docker
```

## Requisitos Previos

### Opción 1: Ejecución Local
- Node.js 18 o superior
- npm 8 o superior
- Conocimientos básicos de TypeScript

### Opción 2: Docker (Recomendado)
- Docker 20.10 o superior
- Docker Compose 2.0 o superior

## Instalación

### Opción A: Setup Local

```bash
cd grpc-basico
npm install
```

### Opción B: Docker (Recomendado)

```bash
cd grpc-basico
docker-compose build
```

## Inicio Rápido

Tienes dos formas de ejecutar el proyecto:

### 🐳 Con Docker (Más fácil)

```bash
# Iniciar servidor y cliente con un solo comando
docker-compose up

# El cliente mostrará el menú interactivo
# Selecciona opciones 1-6 para probar

# Para detener: Ctrl+C o
docker-compose down
```

**Ventajas:**
- No necesitas instalar Node.js
- Todo funciona en un ambiente aislado
- Fácil de limpiar después

Ver [DOCKER_GUIDE.md](./DOCKER_GUIDE.md) para más detalles.

---

### 💻 Sin Docker (Setup manual)

### 1. Iniciar el Servidor

Terminal 1:
```bash
npm run server
```

Deberías ver:
```
🚀 Servidor gRPC ejecutándose en 0.0.0.0:50051

📋 Servicios disponibles:
  - Greeter Service (greeter.proto)
  - Calculator Service (calculator.proto)

✅ El servidor está listo para recibir peticiones
```

### 2. Iniciar el Cliente

Terminal 2:
```bash
npm run client
```

Deberías ver un menú interactivo:
```
=== Cliente gRPC - Menú de Pruebas ===
1. SayHello (Unary RPC)
2. SayHelloStream (Server Streaming)
3. SayHelloChat (Bidirectional Streaming)
4. Calculator (Operaciones básicas)
5. SumStream (Client Streaming)
6. Ejecutar todos los tests
0. Salir

Conectado a: localhost:50051

Selecciona una opción:
```

### 3. Probar los Ejemplos

Selecciona las opciones 1-6 para probar diferentes tipos de RPC.

**Recomendación:** Empieza con la opción 1 (más simple) y avanza progresivamente.

## Ejemplos Incluidos

### 1. Unary RPC - SayHello

El tipo más simple de RPC: una petición, una respuesta.

```bash
# En el menú del cliente, selecciona: 1
```

**Qué hace:**
- Cliente envía nombre e idioma
- Servidor responde con saludo en el idioma especificado

**Código relevante:**
- Proto: `proto/greeter.proto:7`
- Servidor: `server/services/greeterService.ts:14`
- Cliente: `client/index.ts:45`

### 2. Server Streaming - SayHelloStream

Un request, múltiples responses en streaming.

```bash
# En el menú del cliente, selecciona: 2
```

**Qué hace:**
- Cliente envía nombre una vez
- Servidor responde con 5 saludos en secuencia (uno por segundo)

**Uso típico:** Descargas, logs en tiempo real, notificaciones

### 3. Client Streaming - SumStream

Múltiples requests en streaming, una response.

```bash
# En el menú del cliente, selecciona: 5
```

**Qué hace:**
- Cliente envía 5 números en secuencia
- Servidor suma todos los números
- Al finalizar, servidor responde con la suma total

**Uso típico:** Upload de archivos, envío de métricas, batch processing

### 4. Bidirectional Streaming - SayHelloChat

Comunicación en ambas direcciones simultáneamente.

```bash
# En el menú del cliente, selecciona: 3
```

**Qué hace:**
- Cliente y servidor mantienen un canal abierto
- Cliente envía mensajes en diferentes idiomas
- Servidor responde a cada mensaje inmediatamente

**Uso típico:** Chat, colaboración en tiempo real, juegos multiplayer

### 5. Calculator - Operaciones Matemáticas

Ejemplo de servicio con múltiples métodos unary.

```bash
# En el menú del cliente, selecciona: 4
```

**Qué hace:**
- Suma, resta, multiplicación, división
- Manejo de errores (división por cero)

## Scripts Disponibles

### Con npm (ejecución local)

```bash
# Ejecutar servidor
npm run server

# Ejecutar cliente
npm run client

# Desarrollo con auto-reload
npm run dev:server  # Reinicia al detectar cambios
npm run dev:client

# Compilar TypeScript
npm run build

# Generar archivos desde .proto (si modificas los .proto)
npm run proto
```

### Con Docker

```bash
# Producción: Iniciar servidor y cliente
docker-compose up

# Producción en background
docker-compose up -d

# Desarrollo con hot-reload
docker-compose -f docker-compose.dev.yml up

# Ejecutar tests automáticos
docker-compose -f docker-compose.test.yml up

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Ver más comandos en DOCKER_GUIDE.md
```

## Documentación

### Guía de Aprendizaje

Lee [GUIA_APRENDIZAJE.md](./GUIA_APRENDIZAJE.md) para:
- Entender qué es gRPC y cuándo usarlo
- Aprender Protocol Buffers
- Comprender los 4 tipos de RPC
- Ejemplos paso a paso
- Mejores prácticas

### Taller Práctico

Completa [TALLER.md](./TALLER.md) para:
- Ejercicios guiados (básico → avanzado)
- Modificar el código existente
- Crear nuevos servicios
- Implementar features avanzadas
- Proyectos desafío

## Flujo de Aprendizaje Recomendado

```
1. Leer README.md (este archivo) ✓
   └─> Entender qué hace el proyecto

2. Ejecutar el proyecto
   └─> npm install && npm run server (terminal 1)
   └─> npm run client (terminal 2)
   └─> Probar opciones 1-6 del menú

3. Leer GUIA_APRENDIZAJE.md
   └─> Conceptos de gRPC
   └─> Protocol Buffers
   └─> Tipos de RPC

4. Completar TALLER.md
   └─> Ejercicios básicos (1-3)
   └─> Ejercicios intermedios (4-5)
   └─> Ejercicios avanzados (6-8)

5. Explorar el código
   └─> proto/*.proto (definiciones)
   └─> server/services/*.ts (implementaciones)
   └─> client/index.ts (uso del cliente)

6. Proyecto avanzado: grpc-voice
   └─> Ver ../grpc-voice/GUIA_APRENDIZAJE_GRPC_VOICE.md
```

## Comparación: gRPC vs REST

| Aspecto | gRPC | REST |
|---------|------|------|
| **Protocolo** | HTTP/2 | HTTP/1.1 |
| **Formato** | Protocol Buffers (binario) | JSON (texto) |
| **Rendimiento** | ⚡ Muy rápido | Moderado |
| **Streaming** | ✅ Soporta todos los tipos | ❌ Limitado (SSE) |
| **Tipado** | ✅ Fuerte (generado) | ❌ Dinámico |
| **Legibilidad** | Binario (no legible) | JSON (legible) |
| **Uso típico** | Microservicios internos | APIs públicas |
| **Soporte navegador** | Limitado (requiere gRPC-Web) | ✅ Nativo |

## ¿Cuándo usar gRPC?

### ✅ Usar gRPC cuando:
- Comunicación entre microservicios
- Necesitas alto rendimiento
- Requieres streaming bidireccional
- Quieres contratos estrictos (tipado)
- Backend a backend

### ❌ No usar gRPC cuando:
- API pública para terceros
- Solo necesitas navegador (sin proxy)
- Prefieres JSON legible
- No necesitas alto rendimiento

## Troubleshooting

### Error: "Port 50051 already in use"

```bash
# Encontrar proceso usando el puerto
lsof -i :50051

# Matar el proceso
kill -9 <PID>

# O cambiar el puerto en server/index.ts
const PORT = '50052';  // Cambiar a otro puerto
```

### Error: "Cannot find module '@grpc/grpc-js'"

```bash
# Reinstalar dependencias
rm -rf node_modules package-lock.json
npm install
```

### Error al compilar TypeScript

```bash
# Limpiar y recompilar
rm -rf dist/
npm run build
```

## Proyecto Relacionado: grpc-voice

Una vez que te sientas cómodo con este proyecto, explora **grpc-voice** para ver:
- gRPC en un proyecto real de producción
- Streaming de audio con Whisper AI
- gRPC-Web (frontend React)
- Integración con RabbitMQ
- Docker y deploy a producción

**Guía:** `../grpc-voice/GUIA_APRENDIZAJE_GRPC_VOICE.md`

## Recursos Adicionales

### Documentación Oficial
- [gRPC.io](https://grpc.io/) - Documentación oficial
- [Protocol Buffers](https://protobuf.dev/) - Guía de proto3
- [gRPC Node.js](https://grpc.io/docs/languages/node/) - Guía específica de Node.js

### Tutoriales
- [gRPC Quick Start](https://grpc.io/docs/languages/node/quickstart/)
- [Protocol Buffers Tutorial](https://protobuf.dev/getting-started/typescripttutorial/)

### Comparaciones
- [gRPC vs REST](https://grpc.io/blog/grpc-vs-rest/)
- [When to use gRPC](https://grpc.io/docs/what-is-grpc/faq/)

## Contribuir

Este es un proyecto educativo. Si encuentras errores o tienes sugerencias:

1. Revisa el código
2. Propón mejoras
3. Comparte con otros estudiantes

## Licencia

MIT License - Uso libre para aprendizaje y proyectos personales.

---

**¡Feliz aprendizaje de gRPC!** 🚀

¿Tienes preguntas? Revisa:
1. [GUIA_APRENDIZAJE.md](./GUIA_APRENDIZAJE.md) - Conceptos teóricos
2. [TALLER.md](./TALLER.md) - Ejercicios prácticos
3. El código fuente con comentarios explicativos

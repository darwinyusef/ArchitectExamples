# Guía de Aprendizaje gRPC

## Índice
1. [Introducción a gRPC](#introducción-a-grpc)
2. [Conceptos Fundamentales](#conceptos-fundamentales)
3. [Protocol Buffers](#protocol-buffers)
4. [Tipos de RPC](#tipos-de-rpc)
5. [Instalación y Configuración](#instalación-y-configuración)
6. [Estructura del Proyecto](#estructura-del-proyecto)
7. [Paso a Paso](#paso-a-paso)
8. [Ejemplos Prácticos](#ejemplos-prácticos)

---

## Introducción a gRPC

### ¿Qué es gRPC?

gRPC (gRPC Remote Procedure Call) es un framework de comunicación RPC de código abierto desarrollado por Google. Permite que aplicaciones cliente y servidor se comuniquen de manera transparente y eficiente.

### Características principales:

- **Alto rendimiento**: Usa HTTP/2 y Protocol Buffers (binario)
- **Multiplataforma**: Funciona en múltiples lenguajes de programación
- **Streaming bidireccional**: Soporta comunicación en tiempo real
- **Tipado fuerte**: Definiciones estrictas de contratos con .proto
- **Generación de código**: Crea automáticamente clientes y servidores

### ¿Cuándo usar gRPC?

✅ **Ideal para:**
- Microservicios internos
- Comunicación entre servicios de backend
- Aplicaciones que requieren alto rendimiento
- Streaming en tiempo real
- APIs con contratos estrictos

❌ **No ideal para:**
- APIs públicas (REST es más común)
- Navegadores web (soporte limitado)
- Cuando necesitas legibilidad humana (usa REST/JSON)

---

## Conceptos Fundamentales

### 1. Protocol Buffers (.proto)

Los archivos `.proto` definen:
- Mensajes (estructuras de datos)
- Servicios (métodos RPC)
- Tipos de datos

Ejemplo básico:

```protobuf
syntax = "proto3";

message Persona {
  string nombre = 1;
  int32 edad = 2;
}

service PersonaService {
  rpc ObtenerPersona (PersonaRequest) returns (Persona) {}
}
```

### 2. Cliente y Servidor

- **Servidor**: Implementa los métodos definidos en el .proto
- **Cliente**: Llama a esos métodos como si fueran locales

### 3. Canales (Channels)

Los canales representan conexiones a un servidor gRPC y se usan para crear stubs de cliente.

---

## Protocol Buffers

### Sintaxis Básica

```protobuf
syntax = "proto3";  // Versión de Protocol Buffers

package mi_servicio;  // Namespace

// Definición de mensaje
message MiMensaje {
  string campo1 = 1;  // Número = tag (identificador único)
  int32 campo2 = 2;
  bool campo3 = 3;
}

// Definición de servicio
service MiServicio {
  rpc MiMetodo (MiRequest) returns (MiResponse) {}
}
```

### Tipos de Datos Comunes

| Proto Type | TypeScript | Descripción |
|------------|------------|-------------|
| `string` | `string` | Texto |
| `int32` | `number` | Entero de 32 bits |
| `int64` | `string` | Entero de 64 bits |
| `bool` | `boolean` | Booleano |
| `double` | `number` | Decimal de precisión doble |
| `float` | `number` | Decimal |
| `bytes` | `Uint8Array` | Datos binarios |

### Tags (Números de Campo)

```protobuf
message Ejemplo {
  string campo1 = 1;  // Tag 1
  int32 campo2 = 2;   // Tag 2
  bool campo3 = 3;    // Tag 3
}
```

**Importante:**
- Los tags deben ser únicos dentro de un mensaje
- Los tags 1-15 usan 1 byte (úsalos para campos frecuentes)
- Los tags 16-2047 usan 2 bytes
- Nunca cambies los tags de campos existentes

---

## Tipos de RPC

### 1. Unary RPC (Simple)

**Un request → Una response**

```protobuf
rpc SayHello (HelloRequest) returns (HelloReply) {}
```

```typescript
// Cliente
client.sayHello({ name: 'Juan' }, (error, response) => {
  console.log(response.message);
});

// Servidor
sayHello: (call, callback) => {
  callback(null, { message: `Hola, ${call.request.name}` });
}
```

**Uso:** Operaciones simples como consultas, creación de recursos.

---

### 2. Server Streaming RPC

**Un request → Múltiples responses (stream)**

```protobuf
rpc ListFiles (ListRequest) returns (stream File) {}
```

```typescript
// Cliente
const call = client.listFiles({ directory: '/home' });
call.on('data', (file) => console.log(file.name));
call.on('end', () => console.log('Terminado'));

// Servidor
listFiles: (call) => {
  files.forEach(file => {
    call.write(file);
  });
  call.end();
}
```

**Uso:** Descargar archivos grandes, logs en tiempo real, notificaciones.

---

### 3. Client Streaming RPC

**Múltiples requests (stream) → Una response**

```protobuf
rpc UploadFile (stream Chunk) returns (UploadResponse) {}
```

```typescript
// Cliente
const call = client.uploadFile((error, response) => {
  console.log('Upload completo:', response.size);
});
chunks.forEach(chunk => call.write(chunk));
call.end();

// Servidor
uploadFile: (call, callback) => {
  let totalSize = 0;
  call.on('data', (chunk) => totalSize += chunk.size);
  call.on('end', () => callback(null, { size: totalSize }));
}
```

**Uso:** Subir archivos grandes, enviar datos de sensores en batch.

---

### 4. Bidirectional Streaming RPC

**Múltiples requests (stream) ↔ Múltiples responses (stream)**

```protobuf
rpc Chat (stream ChatMessage) returns (stream ChatMessage) {}
```

```typescript
// Cliente
const call = client.chat();
call.on('data', (msg) => console.log('Recibido:', msg.text));
call.write({ text: 'Hola' });
call.write({ text: 'Cómo estás?' });

// Servidor
chat: (call) => {
  call.on('data', (msg) => {
    call.write({ text: `Echo: ${msg.text}` });
  });
  call.on('end', () => call.end());
}
```

**Uso:** Chat en tiempo real, colaboración en vivo, juegos multiplayer.

---

## Instalación y Configuración

### Paso 1: Requisitos Previos

```bash
node --version  # v18 o superior
npm --version   # v8 o superior
```

### Paso 2: Instalar Dependencias

```bash
cd grpc-basico
npm install
```

### Paso 3: Verificar Instalación

```bash
npm list @grpc/grpc-js @grpc/proto-loader
```

---

## Estructura del Proyecto

```
grpc-basico/
├── proto/                    # Definiciones Protocol Buffers
│   ├── greeter.proto        # Servicio de saludo
│   └── calculator.proto     # Servicio de calculadora
├── server/                   # Implementación del servidor
│   ├── index.ts             # Punto de entrada del servidor
│   └── services/
│       ├── greeterService.ts
│       └── calculatorService.ts
├── client/                   # Implementación del cliente
│   └── index.ts             # Cliente con menú interactivo
├── package.json             # Dependencias y scripts
├── tsconfig.json            # Configuración de TypeScript
├── GUIA_APRENDIZAJE.md      # Esta guía
└── TALLER.md                # Ejercicios prácticos
```

---

## Paso a Paso

### Paso 1: Definir el Servicio (.proto)

Crea `proto/greeter.proto`:

```protobuf
syntax = "proto3";
package greeter;

service Greeter {
  rpc SayHello (HelloRequest) returns (HelloReply) {}
}

message HelloRequest {
  string name = 1;
}

message HelloReply {
  string message = 1;
}
```

### Paso 2: Implementar el Servidor

Crea `server/index.ts`:

```typescript
import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';

const PROTO_PATH = './proto/greeter.proto';
const packageDef = protoLoader.loadSync(PROTO_PATH);
const greeterProto = grpc.loadPackageDefinition(packageDef) as any;

const server = new grpc.Server();

server.addService(greeterProto.greeter.Greeter.service, {
  sayHello: (call: any, callback: any) => {
    callback(null, {
      message: `Hola, ${call.request.name}!`
    });
  }
});

server.bindAsync(
  '0.0.0.0:50051',
  grpc.ServerCredentials.createInsecure(),
  () => console.log('Servidor iniciado en :50051')
);
```

### Paso 3: Crear el Cliente

Crea `client/index.ts`:

```typescript
import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';

const PROTO_PATH = './proto/greeter.proto';
const packageDef = protoLoader.loadSync(PROTO_PATH);
const greeterProto = grpc.loadPackageDefinition(packageDef) as any;

const client = new greeterProto.greeter.Greeter(
  'localhost:50051',
  grpc.credentials.createInsecure()
);

client.sayHello({ name: 'Juan' }, (error: any, response: any) => {
  if (error) {
    console.error(error);
    return;
  }
  console.log('Respuesta:', response.message);
});
```

### Paso 4: Ejecutar

Terminal 1 (Servidor):
```bash
npm run server
```

Terminal 2 (Cliente):
```bash
npm run client
```

---

## Ejemplos Prácticos

### Ejemplo 1: Greeter Service (Unary RPC)

Ver archivos:
- `proto/greeter.proto`
- `server/services/greeterService.ts`
- `client/index.ts` (opción 1)

### Ejemplo 2: Calculator Service

Ver archivos:
- `proto/calculator.proto`
- `server/services/calculatorService.ts`
- `client/index.ts` (opción 4)

### Ejemplo 3: Server Streaming

Ver `greeterService.ts` método `sayHelloStream`

### Ejemplo 4: Client Streaming

Ver `calculatorService.ts` método `sumStream`

### Ejemplo 5: Bidirectional Streaming

Ver `greeterService.ts` método `sayHelloChat`

---

## Comandos Útiles

```bash
# Instalar dependencias
npm install

# Ejecutar servidor
npm run server

# Ejecutar cliente
npm run client

# Desarrollo con auto-reload
npm run dev:server
npm run dev:client

# Compilar TypeScript
npm run build
```

---

## Próximos Pasos

1. Completa el [TALLER.md](./TALLER.md) con ejercicios prácticos
2. Explora el proyecto `grpc-voice` para un ejemplo más avanzado
3. Aprende sobre autenticación y seguridad en gRPC
4. Investiga sobre gRPC-Web para uso en navegadores
5. Estudia interceptores y middleware en gRPC

---

## Recursos Adicionales

- [Documentación oficial de gRPC](https://grpc.io/)
- [Protocol Buffers Guide](https://protobuf.dev/)
- [gRPC Node.js Quick Start](https://grpc.io/docs/languages/node/quickstart/)
- [Comparación gRPC vs REST](https://grpc.io/blog/grpc-vs-rest/)

---

## Glosario

- **RPC**: Remote Procedure Call (Llamada a Procedimiento Remoto)
- **Stub**: Código generado para cliente que representa el servidor
- **Protocol Buffers**: Formato de serialización binario de Google
- **HTTP/2**: Protocolo de transporte usado por gRPC
- **Streaming**: Envío continuo de datos entre cliente y servidor
- **Unary**: RPC de una sola petición y respuesta
- **Channel**: Conexión entre cliente y servidor gRPC

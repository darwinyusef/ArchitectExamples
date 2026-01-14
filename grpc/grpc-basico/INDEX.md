# Índice de Documentación - gRPC Básico

## 📚 Guías de Inicio

| Documento | Descripción | Tiempo | Audiencia |
|-----------|-------------|--------|-----------|
| **[QUICKSTART.md](./QUICKSTART.md)** | Ejecuta el proyecto en 5 minutos | 5 min | Todos |
| **[README.md](./README.md)** | Documentación completa del proyecto | 15 min | Todos |

## 🎓 Guías de Aprendizaje

| Documento | Descripción | Tiempo | Nivel |
|-----------|-------------|--------|-------|
| **[GUIA_APRENDIZAJE.md](./GUIA_APRENDIZAJE.md)** | Conceptos de gRPC, Protocol Buffers, tipos de RPC | 30-45 min | Básico |
| **[TALLER.md](./TALLER.md)** | Ejercicios prácticos progresivos | 2-4 horas | Básico a Avanzado |

## 🐳 Guías Técnicas

| Documento | Descripción | Tiempo | Audiencia |
|-----------|-------------|--------|-----------|
| **[DOCKER_GUIDE.md](./DOCKER_GUIDE.md)** | Guía completa de Docker y Docker Compose | 20 min | DevOps, Desarrolladores |

## 📁 Estructura de Archivos

### Código Fuente

```
proto/                    Definiciones Protocol Buffers
├── greeter.proto        Servicio de saludo
└── calculator.proto     Servicio de calculadora

server/                   Servidor gRPC
├── index.ts             Punto de entrada
└── services/
    ├── greeterService.ts
    └── calculatorService.ts

client/                   Cliente gRPC
└── index.ts             Cliente interactivo con menú
```

### Configuración

```
package.json              Dependencias npm
tsconfig.json            Configuración TypeScript
.gitignore               Archivos a ignorar en Git
```

### Docker

```
Dockerfile               Imagen Docker
docker-compose.yml       Producción
docker-compose.dev.yml   Desarrollo con hot-reload
docker-compose.test.yml  Tests automáticos
.dockerignore           Archivos a ignorar en Docker
```

### Documentación

```
README.md               Documentación principal
QUICKSTART.md          Inicio rápido
GUIA_APRENDIZAJE.md    Guía de conceptos
TALLER.md              Ejercicios prácticos
DOCKER_GUIDE.md        Guía de Docker
INDEX.md               Este archivo
```

---

## 🚀 Rutas de Aprendizaje

### Ruta 1: Usuario Nuevo (Total: ~3 horas)

```
1. QUICKSTART.md (5 min)
   └─> Ejecutar el proyecto con Docker

2. Probar ejemplos (15 min)
   └─> Opciones 1-6 del menú del cliente

3. README.md (15 min)
   └─> Entender la estructura del proyecto

4. GUIA_APRENDIZAJE.md (45 min)
   └─> Conceptos: gRPC, Protocol Buffers, RPC types

5. TALLER.md - Ejercicios Básicos (2 horas)
   └─> Ejercicios 1-3
```

**Resultado:** Entenderás gRPC y sabrás crear servicios básicos.

---

### Ruta 2: Desarrollador con Experiencia (Total: ~2 horas)

```
1. README.md (10 min)
   └─> Overview rápido

2. Código fuente (30 min)
   └─> Explorar proto/, server/, client/

3. GUIA_APRENDIZAJE.md (20 min)
   └─> Revisar secciones avanzadas

4. TALLER.md - Ejercicios Intermedios (1 hora)
   └─> Ejercicios 4-5
```

**Resultado:** Implementarás servicios gRPC complejos.

---

### Ruta 3: DevOps / Deployment (Total: ~1 hora)

```
1. QUICKSTART.md (5 min)
   └─> Ejecutar con Docker

2. DOCKER_GUIDE.md (30 min)
   └─> Todas las configuraciones Docker

3. Experimentar con Docker Compose (30 min)
   └─> Producción, desarrollo, tests
```

**Resultado:** Desplegarás servicios gRPC con Docker.

---

## 📖 Por Tema

### Conceptos Básicos de gRPC

- **¿Qué es gRPC?** → [GUIA_APRENDIZAJE.md#introduccion-a-grpc](./GUIA_APRENDIZAJE.md#introducción-a-grpc)
- **¿Cuándo usar gRPC?** → [GUIA_APRENDIZAJE.md#cuando-usar-grpc](./GUIA_APRENDIZAJE.md)
- **gRPC vs REST** → [README.md#comparacion-grpc-vs-rest](./README.md#comparación-grpc-vs-rest)

### Protocol Buffers

- **Sintaxis básica** → [GUIA_APRENDIZAJE.md#protocol-buffers](./GUIA_APRENDIZAJE.md#protocol-buffers)
- **Tipos de datos** → [GUIA_APRENDIZAJE.md#tipos-de-datos-comunes](./GUIA_APRENDIZAJE.md)
- **Tags y números de campo** → [GUIA_APRENDIZAJE.md#tags-numeros-de-campo](./GUIA_APRENDIZAJE.md)

### Tipos de RPC

- **Unary RPC** → [GUIA_APRENDIZAJE.md#unary-rpc-simple](./GUIA_APRENDIZAJE.md#1-unary-rpc-simple)
- **Server Streaming** → [GUIA_APRENDIZAJE.md#server-streaming-rpc](./GUIA_APRENDIZAJE.md#2-server-streaming-rpc)
- **Client Streaming** → [GUIA_APRENDIZAJE.md#client-streaming-rpc](./GUIA_APRENDIZAJE.md#3-client-streaming-rpc)
- **Bidirectional Streaming** → [GUIA_APRENDIZAJE.md#bidirectional-streaming-rpc](./GUIA_APRENDIZAJE.md#4-bidirectional-streaming-rpc)

### Ejemplos Prácticos

- **SayHello (Unary)** → [README.md#1-unary-rpc---sayhello](./README.md#1-unary-rpc---sayhello)
- **Calculator** → [README.md#5-calculator](./README.md#5-calculator---operaciones-matemáticas)
- **SayHelloStream (Server)** → [README.md#2-server-streaming](./README.md#2-server-streaming---sayhellostream)
- **SumStream (Client)** → [README.md#3-client-streaming](./README.md#3-client-streaming---sumstream)
- **Chat (Bidirectional)** → [README.md#4-bidirectional-streaming](./README.md#4-bidirectional-streaming---sayhellochat)

### Ejercicios

- **Nivel Básico** → [TALLER.md#ejercicios-nivel-basico](./TALLER.md#ejercicios-nivel-básico)
- **Nivel Intermedio** → [TALLER.md#ejercicios-nivel-intermedio](./TALLER.md#ejercicios-nivel-intermedio)
- **Nivel Avanzado** → [TALLER.md#ejercicios-nivel-avanzado](./TALLER.md#ejercicios-nivel-avanzado)
- **Desafíos** → [TALLER.md#ejercicios-desafio](./TALLER.md#ejercicios-desafío)

### Docker

- **Inicio rápido** → [DOCKER_GUIDE.md#inicio-rapido](./DOCKER_GUIDE.md#inicio-rápido)
- **Desarrollo con hot-reload** → [DOCKER_GUIDE.md#desarrollo-con-docker](./DOCKER_GUIDE.md#desarrollo-con-docker)
- **Troubleshooting** → [DOCKER_GUIDE.md#troubleshooting](./DOCKER_GUIDE.md#troubleshooting)
- **Comandos útiles** → [DOCKER_GUIDE.md#comandos-utiles](./DOCKER_GUIDE.md#comandos-útiles)

---

## 🎯 Por Objetivo

### "Quiero ejecutar el proyecto YA"

→ [QUICKSTART.md](./QUICKSTART.md)

### "Quiero entender qué es gRPC"

→ [GUIA_APRENDIZAJE.md](./GUIA_APRENDIZAJE.md)

### "Quiero practicar y hacer ejercicios"

→ [TALLER.md](./TALLER.md)

### "Quiero usar Docker"

→ [DOCKER_GUIDE.md](./DOCKER_GUIDE.md)

### "Quiero ver todos los detalles del proyecto"

→ [README.md](./README.md)

### "Tengo un problema/error"

→ [DOCKER_GUIDE.md#troubleshooting](./DOCKER_GUIDE.md#troubleshooting) o [README.md#troubleshooting](./README.md#troubleshooting)

---

## 🔗 Recursos Externos

### Documentación Oficial

- [gRPC.io](https://grpc.io/) - Sitio oficial
- [Protocol Buffers](https://protobuf.dev/) - Documentación proto3
- [gRPC Node.js](https://grpc.io/docs/languages/node/) - Guía específica

### Tutoriales

- [gRPC Quick Start](https://grpc.io/docs/languages/node/quickstart/)
- [Protocol Buffers Tutorial](https://protobuf.dev/getting-started/typescripttutorial/)

### Comparaciones

- [gRPC vs REST](https://grpc.io/blog/grpc-vs-rest/)
- [When to use gRPC](https://grpc.io/docs/what-is-grpc/faq/)

---

## 📊 Resumen del Contenido

| Categoría | Archivos | Líneas aprox. |
|-----------|----------|---------------|
| Código fuente | 6 archivos | ~800 líneas |
| Definiciones .proto | 2 archivos | ~60 líneas |
| Documentación | 6 archivos | ~1500 líneas |
| Configuración | 7 archivos | ~100 líneas |
| **Total** | **21 archivos** | **~2500 líneas** |

---

## 🤝 Contribuir

Este proyecto es educativo y open source. Si quieres contribuir:

1. Reporta errores
2. Sugiere mejoras
3. Comparte con otros estudiantes

---

## 📝 Licencia

MIT License - Uso libre para aprendizaje y proyectos personales.

---

## 🚀 Proyecto Avanzado: grpc-voice

Una vez domines este proyecto, explora:

**Ubicación:** `../grpc-voice/`

**Incluye:**
- gRPC en producción real
- Streaming de audio con Whisper AI
- gRPC-Web (React frontend)
- RabbitMQ integration
- Docker completo con Nginx, Envoy, SSL

**Guía:** [../grpc-voice/GUIA_APRENDIZAJE_GRPC_VOICE.md](../grpc-voice/GUIA_APRENDIZAJE_GRPC_VOICE.md)

---

**Última actualización:** Diciembre 2024

**Versión:** 1.0

**Mantenedor:** Tutorial educativo de gRPC

---

¿Por dónde empezar? → [QUICKSTART.md](./QUICKSTART.md) 🚀

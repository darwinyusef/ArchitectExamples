# Inicio Rápido - gRPC Básico

Guía rápida para ejecutar el proyecto en menos de 5 minutos.

## Opción 1: Docker (Recomendado) 🐳

**Prerrequisito:** Docker instalado

```bash
# 1. Navegar al proyecto
cd grpc-basico

# 2. Construir y ejecutar
docker-compose up

# 3. Interactuar con el menú del cliente
# Selecciona opciones 1-6

# 4. Detener (Ctrl+C)
```

**¡Listo!** No necesitas instalar nada más.

---

## Opción 2: Sin Docker 💻

**Prerrequisitos:** Node.js 18+ y npm 8+

```bash
# 1. Navegar al proyecto
cd grpc-basico

# 2. Instalar dependencias
npm install

# 3. Terminal 1 - Servidor
npm run server

# 4. Terminal 2 - Cliente
npm run client

# 5. Interactuar con el menú del cliente
# Selecciona opciones 1-6
```

---

## ¿Qué probar primero?

Una vez que el cliente esté corriendo, prueba en este orden:

### 1️⃣ Opción 1: SayHello (Unary RPC)
El ejemplo más simple. Envía un nombre y recibe un saludo.

### 2️⃣ Opción 4: Calculator
Prueba operaciones matemáticas básicas.

### 3️⃣ Opción 2: SayHelloStream
Ve cómo el servidor envía múltiples mensajes en streaming.

### 4️⃣ Opción 6: Ejecutar todos los tests
Ve todos los ejemplos en acción automáticamente.

---

## Próximos Pasos

### 📖 Aprender conceptos
Lee [GUIA_APRENDIZAJE.md](./GUIA_APRENDIZAJE.md) para entender:
- ¿Qué es gRPC?
- Protocol Buffers
- Tipos de RPC (Unary, Streaming, etc.)

### 🛠️ Practicar
Completa [TALLER.md](./TALLER.md) con:
- Ejercicios guiados
- Modificaciones al código
- Proyectos desafío

### 🐳 Profundizar en Docker
Lee [DOCKER_GUIDE.md](./DOCKER_GUIDE.md) para:
- Desarrollo con hot-reload
- Tests automáticos
- Debugging con Docker

### 🚀 Proyecto Avanzado
Explora `../grpc-voice/` para ver:
- gRPC en producción
- Streaming de audio con Whisper AI
- gRPC-Web (frontend React)
- RabbitMQ integration

---

## Comandos Útiles

### Docker

```bash
# Iniciar
docker-compose up

# Detener
docker-compose down

# Ver logs
docker-compose logs -f

# Desarrollo con hot-reload
docker-compose -f docker-compose.dev.yml up

# Tests automáticos
docker-compose -f docker-compose.test.yml up
```

### Sin Docker

```bash
# Servidor
npm run server

# Cliente
npm run client

# Desarrollo con auto-reload
npm run dev:server
npm run dev:client
```

---

## Troubleshooting Rápido

### Error: Puerto 50051 ocupado

```bash
# Encontrar y matar proceso
lsof -i :50051
kill -9 <PID>

# O con Docker
docker-compose down
```

### Error: Cannot connect to server

```bash
# Verificar que el servidor esté corriendo
docker-compose ps

# Reiniciar
docker-compose restart
```

### Cliente no responde

```bash
# Adjuntar al cliente
docker attach grpc-basico-client

# O ejecutar de nuevo
docker-compose exec client npm run client
```

---

## Estructura de Archivos Clave

```
grpc-basico/
├── proto/
│   ├── greeter.proto       ← Definición del servicio de saludo
│   └── calculator.proto    ← Definición del servicio de calculadora
├── server/
│   └── services/
│       ├── greeterService.ts    ← Implementación servidor
│       └── calculatorService.ts
└── client/
    └── index.ts            ← Cliente con menú interactivo
```

---

## FAQ

**P: ¿Necesito conocimientos previos de gRPC?**
R: No, este proyecto está diseñado para principiantes.

**P: ¿Cuánto tiempo toma completar el tutorial?**
R:
- Ejecutar ejemplos: 10-15 minutos
- Leer guía: 30-45 minutos
- Completar taller: 2-4 horas

**P: ¿Puedo usar esto en producción?**
R: Este proyecto es educativo. Para producción, ve `grpc-voice` como referencia.

**P: ¿Funciona en Windows/Mac/Linux?**
R: Sí, especialmente con Docker que garantiza consistencia.

**P: ¿Qué hacer si tengo errores?**
R:
1. Revisa [DOCKER_GUIDE.md](./DOCKER_GUIDE.md) sección Troubleshooting
2. Verifica logs con `docker-compose logs -f`
3. Intenta reconstruir: `docker-compose build --no-cache`

---

## Flujo de Aprendizaje Completo

```
1. QUICKSTART.md (5 min)
   └─> Ejecutar proyecto

2. Probar ejemplos (10 min)
   └─> Opciones 1-6 del menú

3. GUIA_APRENDIZAJE.md (30 min)
   └─> Entender conceptos

4. Explorar código (20 min)
   └─> Ver implementaciones

5. TALLER.md (2-4 horas)
   └─> Ejercicios prácticos

6. grpc-voice (proyecto avanzado)
   └─> Aplicación real
```

---

## Recursos

- [README.md](./README.md) - Documentación completa
- [GUIA_APRENDIZAJE.md](./GUIA_APRENDIZAJE.md) - Conceptos y teoría
- [TALLER.md](./TALLER.md) - Ejercicios prácticos
- [DOCKER_GUIDE.md](./DOCKER_GUIDE.md) - Guía de Docker
- [gRPC Official Docs](https://grpc.io/docs/) - Documentación oficial

---

**¡Comienza ahora!** Ejecuta `docker-compose up` y empieza a aprender gRPC 🚀

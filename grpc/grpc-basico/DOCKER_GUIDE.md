# Guía de Docker - gRPC Básico

Esta guía explica cómo ejecutar el proyecto gRPC Básico usando Docker y Docker Compose.

## Índice
1. [Requisitos](#requisitos)
2. [Configuraciones Disponibles](#configuraciones-disponibles)
3. [Inicio Rápido](#inicio-rápido)
4. [Comandos Útiles](#comandos-útiles)
5. [Desarrollo con Docker](#desarrollo-con-docker)
6. [Troubleshooting](#troubleshooting)

---

## Requisitos

- Docker 20.10 o superior
- Docker Compose 2.0 o superior

**Verificar instalación:**

```bash
docker --version
docker-compose --version
```

---

## Configuraciones Disponibles

Tenemos 3 configuraciones de Docker Compose según tus necesidades:

### 1. Producción (docker-compose.yml) ⭐

**Uso recomendado:** Ejecutar el proyecto completo

```bash
docker-compose up
```

**Incluye:**
- Servidor gRPC en puerto 50051
- Cliente interactivo con menú
- Networking entre contenedores
- Health checks

**Cuándo usar:** Primera vez, demos, testing

---

### 2. Desarrollo (docker-compose.dev.yml)

**Uso recomendado:** Desarrollo con hot-reload

```bash
docker-compose -f docker-compose.dev.yml up
```

**Incluye:**
- Auto-reload al detectar cambios
- Volúmenes montados para edición en vivo
- Logs detallados
- Variables de entorno de desarrollo

**Cuándo usar:** Cuando estás modificando el código

---

### 3. Testing (docker-compose.test.yml)

**Uso recomendado:** Ejecutar tests automáticos

```bash
docker-compose -f docker-compose.test.yml up
```

**Incluye:**
- Ejecuta todos los tests automáticamente (opción 6)
- Se detiene después de completar
- Health checks optimizados

**Cuándo usar:** CI/CD, verificación rápida

---

## Inicio Rápido

### Opción 1: Producción (Recomendado para empezar)

```bash
# 1. Construir imágenes
docker-compose build

# 2. Iniciar servicios
docker-compose up

# El cliente mostrará el menú interactivo
# Selecciona opciones 1-6 para probar
```

**Para detener:**
```bash
# Ctrl+C o en otra terminal:
docker-compose down
```

---

### Opción 2: Desarrollo con Hot-Reload

```bash
# Iniciar en modo desarrollo
docker-compose -f docker-compose.dev.yml up

# Ahora puedes editar archivos en server/ o client/
# Los cambios se recargarán automáticamente
```

**Editar código:**
```bash
# En otra terminal, edita archivos:
code server/services/greeterService.ts

# Los cambios se aplicarán automáticamente
```

---

### Opción 3: Ejecutar Tests Automáticos

```bash
# Ejecutar todos los tests
docker-compose -f docker-compose.test.yml up

# Ver resultados en la salida
```

---

## Comandos Útiles

### Construcción

```bash
# Construir imágenes
docker-compose build

# Reconstruir sin caché
docker-compose build --no-cache

# Construir solo el servidor
docker-compose build server
```

### Ejecución

```bash
# Iniciar en foreground (ver logs)
docker-compose up

# Iniciar en background
docker-compose up -d

# Iniciar solo el servidor
docker-compose up server

# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f server
docker-compose logs -f client
```

### Interacción

```bash
# Adjuntar al cliente interactivo
docker attach grpc-basico-client

# Ejecutar comando en contenedor
docker-compose exec server sh
docker-compose exec client sh

# Ejecutar cliente manualmente
docker-compose exec client npm run client
```

### Limpieza

```bash
# Detener servicios
docker-compose stop

# Detener y eliminar contenedores
docker-compose down

# Eliminar contenedores, volúmenes y redes
docker-compose down -v

# Eliminar también imágenes
docker-compose down --rmi all
```

### Inspección

```bash
# Ver estado de servicios
docker-compose ps

# Ver uso de recursos
docker stats grpc-basico-server grpc-basico-client

# Ver logs
docker-compose logs

# Ver redes
docker network ls | grep grpc

# Inspeccionar red
docker network inspect grpc-basico_grpc-network
```

---

## Desarrollo con Docker

### Modificar código con Hot-Reload

1. Inicia el proyecto en modo desarrollo:

```bash
docker-compose -f docker-compose.dev.yml up
```

2. Edita archivos en tu editor local:

```bash
# Los archivos están montados como volúmenes
# Cualquier cambio se reflejará automáticamente
code server/services/greeterService.ts
```

3. El servidor/cliente se reiniciará automáticamente con tus cambios.

### Agregar nuevas dependencias

Si agregas dependencias en `package.json`:

```bash
# 1. Detener contenedores
docker-compose down

# 2. Reconstruir imágenes
docker-compose build

# 3. Reiniciar
docker-compose up
```

### Debuggear con Docker

**Ver logs detallados:**

```bash
# Servidor
docker-compose logs -f server

# Cliente
docker-compose logs -f client
```

**Acceder a shell del contenedor:**

```bash
# Acceder al servidor
docker-compose exec server sh

# Ver archivos
ls -la

# Verificar proceso
ps aux | grep node

# Verificar puerto
netstat -tlnp | grep 50051
```

---

## Configuraciones de Red

### Red por defecto: grpc-network

Todos los servicios están en la misma red bridge:

```yaml
networks:
  grpc-network:
    driver: bridge
```

**Beneficios:**
- Contenedores pueden comunicarse por nombre (server, client)
- Aislamiento del host
- DNS automático entre contenedores

**Conectividad:**
- Cliente → Servidor: `server:50051`
- Host → Servidor: `localhost:50051`

### Exponer puertos

```yaml
ports:
  - "50051:50051"  # host:container
```

Esto permite acceder al servidor desde:
- Dentro de Docker: `server:50051`
- Desde el host: `localhost:50051`

---

## Variables de Entorno

### Configurar URL del servidor

Por defecto, el cliente se conecta a `server:50051` (nombre DNS de Docker).

Para cambiar:

```bash
# En docker-compose.yml
environment:
  - SERVER_URL=otro-servidor:50051
```

O al ejecutar:

```bash
docker-compose run -e SERVER_URL=localhost:50051 client
```

### Otras variables

```yaml
environment:
  - NODE_ENV=production
  - DEBUG=grpc:*
  - LOG_LEVEL=info
```

---

## Troubleshooting

### Error: "Cannot connect to Docker daemon"

**Causa:** Docker no está corriendo

**Solución:**
```bash
# macOS/Windows: Iniciar Docker Desktop
# Linux:
sudo systemctl start docker
```

---

### Error: "Port 50051 is already allocated"

**Causa:** Otro servicio usando el puerto

**Solución 1:** Detener el servicio que usa el puerto
```bash
# Encontrar proceso
lsof -i :50051

# Matar proceso
kill -9 <PID>
```

**Solución 2:** Cambiar puerto en docker-compose.yml
```yaml
ports:
  - "50052:50051"  # Mapear a puerto diferente en host
```

---

### Error: "Client cannot connect to server"

**Causa:** Servidor no está listo o red mal configurada

**Solución:**
```bash
# Verificar que el servidor esté corriendo
docker-compose ps

# Ver logs del servidor
docker-compose logs server

# Verificar conectividad
docker-compose exec client ping server

# Reiniciar servicios
docker-compose restart
```

---

### Error: "No such file or directory" al construir

**Causa:** Archivos necesarios no copiados

**Solución:**
```bash
# Verificar que existan todos los archivos
ls -la proto/ server/ client/

# Reconstruir sin caché
docker-compose build --no-cache
```

---

### Logs no se muestran

**Causa:** Servicios corriendo en background

**Solución:**
```bash
# Ver logs en tiempo real
docker-compose logs -f

# O iniciar en foreground
docker-compose up
```

---

### Hot-reload no funciona

**Causa:** Volúmenes no montados correctamente

**Solución:**
```bash
# Verificar que estés usando docker-compose.dev.yml
docker-compose -f docker-compose.dev.yml up

# Verificar volúmenes montados
docker-compose -f docker-compose.dev.yml config | grep volumes
```

---

### Cliente interactivo no responde

**Causa:** Stdin/TTY no habilitados

**Solución:**
```bash
# Verificar que docker-compose.yml tenga:
stdin_open: true
tty: true

# Adjuntar manualmente
docker attach grpc-basico-client

# O ejecutar de nuevo
docker-compose exec client npm run client
```

---

## Workflows Comunes

### Workflow 1: Primera vez usando el proyecto

```bash
# 1. Clonar/navegar al proyecto
cd grpc-basico

# 2. Construir imágenes
docker-compose build

# 3. Iniciar servicios
docker-compose up

# 4. Interactuar con el cliente (menú interactivo)

# 5. Detener (Ctrl+C)
```

---

### Workflow 2: Desarrollo iterativo

```bash
# 1. Iniciar en modo desarrollo
docker-compose -f docker-compose.dev.yml up -d

# 2. Ver logs
docker-compose -f docker-compose.dev.yml logs -f

# 3. Editar código en tu editor local

# 4. Los cambios se aplican automáticamente

# 5. Cuando termines
docker-compose -f docker-compose.dev.yml down
```

---

### Workflow 3: Ejecutar tests rápidos

```bash
# Ejecutar tests y ver resultados
docker-compose -f docker-compose.test.yml up

# Limpiar
docker-compose -f docker-compose.test.yml down
```

---

### Workflow 4: Depuración de problemas

```bash
# 1. Ver estado de servicios
docker-compose ps

# 2. Ver logs
docker-compose logs

# 3. Acceder a contenedor
docker-compose exec server sh

# 4. Verificar conectividad
docker-compose exec client ping server

# 5. Reiniciar servicio problemático
docker-compose restart server

# 6. Si es necesario, reconstruir
docker-compose down
docker-compose build --no-cache
docker-compose up
```

---

## Comparación: Docker vs Local

| Aspecto | Docker | Local (npm) |
|---------|--------|-------------|
| **Setup** | Solo Docker | Node.js + dependencias |
| **Aislamiento** | ✅ Completo | ❌ Comparte con sistema |
| **Portabilidad** | ✅ Funciona igual en todos los OS | ⚠️ Puede variar |
| **Rendimiento** | Ligeramente más lento | Más rápido |
| **Limpieza** | Fácil (down) | Manual |
| **Networking** | DNS automático | Configuración manual |
| **Mejor para** | Demos, CI/CD, consistencia | Desarrollo rápido |

---

## Próximos Pasos

1. Ejecuta el proyecto con Docker
2. Prueba todas las configuraciones (producción, dev, test)
3. Modifica el código en modo desarrollo
4. Explora los logs y debugging
5. Compara con ejecución local (npm)

---

## Recursos Adicionales

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Node.js Docker Best Practices](https://github.com/nodejs/docker-node/blob/main/docs/BestPractices.md)

---

¡Listo para usar Docker con gRPC! 🐳

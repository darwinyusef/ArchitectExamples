# 🐳 Guía de Deploy con Docker - gRTC

Guía completa para desplegar el proyecto gRTC con Docker y simular múltiples clientes.

---

## 🎯 Arquitectura con Docker

```
┌─────────────────────────────────────────────────────────┐
│                    DOCKER HOST                          │
│                                                         │
│  ┌────────────────────────────────────────────────────┐│
│  │              Nginx (Puerto 80)                     ││
│  │         (Reverse Proxy - Opcional)                 ││
│  └───────────────────┬────────────────────────────────┘│
│                      │                                  │
│  ┌───────────────────▼────────────────────────────────┐│
│  │         FastAPI Backend (Puerto 8001)              ││
│  │                                                    ││
│  │  ┌──────────────┐  ┌──────────────┐              ││
│  │  │   REST API   │  │  WebSocket   │              ││
│  │  │   (CRUD)     │  │  Server      │              ││
│  │  └──────────────┘  └──────────────┘              ││
│  │           │              │                        ││
│  │  ┌────────▼──────────────▼────────┐              ││
│  │  │      SQLite Database           │              ││
│  │  │      (/app/data/items.db)      │              ││
│  │  └────────────────────────────────┘              ││
│  └───────────────────────────────────────────────────┘│
│                                                         │
│  ┌──────────────────┐    ┌──────────────────┐         │
│  │  Cliente A       │    │  Cliente B       │         │
│  │  (Selenium)      │    │  (Selenium)      │         │
│  │  Chrome          │    │  Chrome          │         │
│  │  Puerto 7900     │    │  Puerto 7901     │         │
│  └─────────┬────────┘    └─────────┬────────┘         │
│            │                       │                   │
└────────────┼───────────────────────┼───────────────────┘
             │                       │
             │   WebSocket + HTTP    │
             │                       │
             ▼                       ▼
        ┌─────────────────────────────────┐
        │  FastAPI Backend                │
        │  (Señalización WebRTC)          │
        └─────────────────────────────────┘
                      │
             ┌────────┴────────┐
             │                 │
    Cliente A ◄═══════════════► Cliente B
             WebRTC P2P Directo
          (Audio/Video/Datos)
```

---

## 🚀 Opciones de Deploy

### Opción 1: Solo Backend (Básico)

```bash
docker-compose up -d
```

**Incluye:**
- ✅ FastAPI backend con WebSocket
- ✅ SQLite database

**Acceso:**
- Backend: http://localhost:8001
- Abrir manualmente en múltiples pestañas del navegador

### Opción 2: Con Nginx (Recomendado)

```bash
docker-compose --profile with-nginx up -d
```

**Incluye:**
- ✅ Nginx reverse proxy
- ✅ FastAPI backend
- ✅ SQLite database

**Acceso:**
- A través de Nginx: http://localhost
- Backend directo: http://localhost:8001

### Opción 3: Con Clientes Simulados (Testing)

```bash
docker-compose --profile with-clients up -d
```

**Incluye:**
- ✅ FastAPI backend
- ✅ Clientes Selenium (Chrome automatizado)
  - Cliente A: VNC en puerto 7900
  - Cliente B: VNC en puerto 7901

**Acceso:**
- Backend: http://localhost:8001
- VNC Cliente A: http://localhost:7900 (ver navegador de Cliente A)
- VNC Cliente B: http://localhost:7901 (ver navegador de Cliente B)

### Opción 4: Deploy Completo

```bash
docker-compose --profile with-nginx --profile with-clients up -d
```

**Incluye TODO.**

---

## 📋 Paso a Paso: Deploy Completo

### 1. Preparar Proyecto

```bash
cd /Users/yusefgonzalez/proyectos/grtc

# Verificar estructura
ls -la
# Debe contener:
# - Dockerfile
# - docker-compose.yml
# - nginx.conf
# - requirements.txt
# - main.py
# - app/
# - static/
# - templates/
```

### 2. Construir e Iniciar

```bash
# Build de imágenes
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f backend
```

### 3. Verificar Estado

```bash
# Ver contenedores
docker-compose ps

# Debe mostrar:
# grtc-backend    running    0.0.0.0:8001->8001/tcp

# Health check
curl http://localhost:8001/health
```

### 4. Probar en Navegador

Abrir 2-3 pestañas en:
```
http://localhost:8001
```

En cada pestaña:
1. Conectar al mismo Room ID (ej: "room1")
2. Ver que se detectan los peers
3. Enviar mensajes entre ellos

---

## 🎮 Usar Clientes Simulados (Selenium)

### Iniciar con Clientes

```bash
docker-compose --profile with-clients up -d
```

### Acceder a VNC

**Cliente A:**
```
http://localhost:7900
```

**Cliente B:**
```
http://localhost:7901
```

**Password VNC:** `secret` (por defecto)

### Dentro del VNC:

1. Abrir Chrome (ya está iniciado)
2. Navegar a: `http://backend:8001`
3. Conectar a un room
4. Repetir en el otro cliente
5. ¡Ver comunicación WebRTC en acción!

---

## 🔄 Interacción: Cómo Funciona

### Flujo Completo con Docker

```
┌─────────────────────────────────────────────────────────┐
│  1. USUARIO ABRE NAVEGADOR                              │
└─────────────────────────────────────────────────────────┘
         │
         ▼
    Navegador A                    Navegador B
         │                              │
         │ HTTP GET /                   │
         ▼                              ▼
┌──────────────────────────────────────────────────────┐
│  Nginx (Puerto 80) - OPCIONAL                        │
│  Proxy Pass → backend:8001                           │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│  FastAPI Backend (Container: grtc-backend)           │
│                                                      │
│  1. Servir index.html + static files                │
│  2. Usuario ve interfaz web                         │
└──────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  2. USUARIO CONECTA A ROOM                              │
└─────────────────────────────────────────────────────────┘
         │
    Navegador A                    Navegador B
         │                              │
         │ WebSocket                    │ WebSocket
         │ ws://localhost:8001/ws/room1 │
         ▼                              ▼
┌──────────────────────────────────────────────────────┐
│  FastAPI WebSocket Endpoint                          │
│                                                      │
│  manager.connect(websocket, room_id, peer_id)       │
│                                                      │
│  Estado en memoria:                                 │
│  {                                                  │
│    "room1": {                                       │
│      "peer-a": WebSocket(A),                        │
│      "peer-b": WebSocket(B)                         │
│    }                                                │
│  }                                                  │
└──────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  3. NEGOCIACIÓN WEBRTC (via WebSocket)                  │
└─────────────────────────────────────────────────────────┘

Peer A                    FastAPI               Peer B
  │                          │                      │
  │─── offer ───────────────►│                      │
  │                          │─── offer ───────────►│
  │                          │                      │
  │                          │◄─── answer ──────────│
  │◄─── answer ──────────────│                      │
  │                          │                      │
  │─── ICE candidate ───────►│─── ICE ────────────►│
  │                          │                      │

┌─────────────────────────────────────────────────────────┐
│  4. CONEXIÓN P2P ESTABLECIDA                            │
└─────────────────────────────────────────────────────────┘

Peer A ◄═════════════════════════════════════════► Peer B
      Conexión Directa (ya no usa servidor!)
         - Audio/Video
         - Data Channels
         - Archivos

┌─────────────────────────────────────────────────────────┐
│  5. OPERACIONES CRUD (Paralelo a WebRTC)                │
└─────────────────────────────────────────────────────────┘

Navegador                FastAPI               SQLite
    │                       │                      │
    │─── POST /api/items ──►│                      │
    │                       │─── INSERT ──────────►│
    │                       │◄─── Result ──────────│
    │◄─── Item creado ──────│                      │
    │                       │                      │
```

---

## 🔧 Configuración y Variables

### Variables de Entorno

Editar `docker-compose.yml`:

```yaml
backend:
  environment:
    - ENVIRONMENT=production    # development o production
    - LOG_LEVEL=info           # debug, info, warning, error
    - DATABASE_PATH=/app/data/items.db
```

### Volúmenes

```yaml
volumes:
  - ./data:/app/data         # Persistir base de datos
  - ./app:/app/app:ro        # Hot-reload (dev)
```

**Nota:** `:ro` = read-only (más seguro en producción)

---

## 📊 Monitoreo

### Ver Logs en Tiempo Real

```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo Nginx
docker-compose logs -f nginx

# Últimas 100 líneas
docker-compose logs --tail=100 backend
```

### Estado de Contenedores

```bash
# Ver contenedores activos
docker-compose ps

# Estadísticas de recursos
docker stats
```

### Inspeccionar Red

```bash
# Ver red de Docker
docker network ls

# Inspeccionar red del proyecto
docker network inspect grtc_grtc-network

# Ver IPs de contenedores
docker-compose exec backend hostname -i
```

---

## 🧪 Testing

### Test Automatizado con Selenium

Crear script `test_webrtc.py`:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Configurar drivers
options_a = webdriver.ChromeOptions()
options_a.add_argument('--use-fake-ui-for-media-stream')
options_a.add_argument('--use-fake-device-for-media-stream')

# Cliente A
driver_a = webdriver.Remote(
    command_executor='http://localhost:4444/wd/hub',
    options=options_a
)

# Cliente B
driver_b = webdriver.Remote(
    command_executor='http://localhost:4445/wd/hub',
    options=options_a
)

# Abrir aplicación
driver_a.get('http://backend:8001')
driver_b.get('http://backend:8001')

# Conectar a room
room_input_a = driver_a.find_element(By.ID, 'roomId')
room_input_a.send_keys('test-room')
driver_a.find_element(By.ID, 'connectBtn').click()

room_input_b = driver_b.find_element(By.ID, 'roomId')
room_input_b.send_keys('test-room')
driver_b.find_element(By.ID, 'connectBtn').click()

# Esperar conexión
time.sleep(3)

# Enviar mensaje
msg_input_a = driver_a.find_element(By.ID, 'messageInput')
msg_input_a.send_keys('Hola desde Cliente A!')
driver_a.find_element(By.ID, 'sendBtn').click()

# Verificar que B recibió el mensaje
time.sleep(2)
messages_b = driver_b.find_element(By.ID, 'messages').text

assert 'Hola desde Cliente A!' in messages_b

print("✅ Test passed!")

driver_a.quit()
driver_b.quit()
```

Ejecutar:
```bash
docker-compose --profile with-clients up -d
python test_webrtc.py
```

---

## 🛠️ Comandos Útiles

### Gestión de Contenedores

```bash
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Reiniciar un servicio
docker-compose restart backend

# Reconstruir imagen
docker-compose up -d --build backend

# Eliminar todo (incluye volúmenes)
docker-compose down -v

# Ver procesos dentro del contenedor
docker-compose exec backend ps aux
```

### Debugging

```bash
# Shell en contenedor
docker-compose exec backend bash

# Dentro del contenedor:
ls -la
cat /app/data/items.db
python -c "import sqlite3; print(sqlite3.connect('/app/data/items.db').execute('SELECT * FROM items').fetchall())"

# Ver configuración
docker-compose exec backend env

# Test de conectividad
docker-compose exec backend curl http://localhost:8001/health
```

### Base de Datos

```bash
# Backup de base de datos
docker-compose exec backend cat /app/data/items.db > backup.db

# Restaurar
cat backup.db | docker-compose exec -T backend sh -c 'cat > /app/data/items.db'

# Ver registros
docker-compose exec backend sqlite3 /app/data/items.db "SELECT * FROM items;"
```

---

## 🌐 Deploy en Producción

### Con Dominio y HTTPS

1. **Actualizar nginx.conf:**

```nginx
server {
    listen 80;
    server_name grtc.tudominio.com;

    # Redirigir a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name grtc.tudominio.com;

    ssl_certificate /etc/ssl/certs/fullchain.pem;
    ssl_certificate_key /etc/ssl/certs/privkey.pem;

    # ... resto de configuración
}
```

2. **Agregar certificados a docker-compose:**

```yaml
nginx:
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf:ro
    - /etc/letsencrypt:/etc/ssl/certs:ro
```

3. **Iniciar:**

```bash
docker-compose --profile with-nginx up -d
```

---

## 📈 Escalabilidad

### Múltiples Instancias del Backend

```yaml
backend:
  deploy:
    replicas: 3  # 3 instancias
```

**Problema:** WebSocket sticky sessions

**Solución:** Usar Redis para compartir estado

```yaml
services:
  redis:
    image: redis:alpine

  backend:
    environment:
      - REDIS_URL=redis://redis:6379
```

---

## ⚠️ Troubleshooting

### Backend no inicia

```bash
# Ver logs
docker-compose logs backend

# Verificar errores de Python
docker-compose exec backend python -c "import fastapi; print('OK')"
```

### WebSocket no conecta

```bash
# Verificar que el puerto esté expuesto
docker-compose ps

# Test de WebSocket
wscat -c ws://localhost:8001/ws/test-room?peer_id=test
```

### Base de datos corrupta

```bash
# Eliminar y recrear
docker-compose down -v
docker-compose up -d
```

### Clientes Selenium no accesibles

```bash
# Verificar que están corriendo
docker-compose --profile with-clients ps

# Ver logs
docker-compose logs client-a
```

---

## 📚 Resumen de Comandos

```bash
# Deploy básico
docker-compose up -d

# Deploy completo
docker-compose --profile with-nginx --profile with-clients up -d

# Ver logs
docker-compose logs -f backend

# Estado
docker-compose ps

# Detener
docker-compose down

# Limpiar todo
docker-compose down -v --rmi all

# Rebuild
docker-compose up -d --build

# Shell en contenedor
docker-compose exec backend bash

# Ver VNC
# http://localhost:7900  (Cliente A)
# http://localhost:7901  (Cliente B)
```

---

**¡Tu aplicación WebRTC está lista para desplegar con Docker!** 🐳🚀

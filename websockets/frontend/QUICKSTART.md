# Inicio Rápido - WebSockets

Ejecuta los ejemplos en menos de 5 minutos.

## Instalación

```bash
cd websockets
npm install
```

## Opción 1: Chat en Tiempo Real 💬

```bash
npm run chat
```

Abre http://localhost:3001 en **2+ pestañas** del navegador:
1. Ingresa diferentes nombres de usuario
2. Usa la misma sala (ej: "general")
3. ¡Chatea entre las pestañas!

**Prueba:**
- Enviar mensajes
- Ver indicador de "escribiendo..."
- Lista de usuarios conectados

---

## Opción 2: Dashboard en Tiempo Real 📊

```bash
npm run dashboard
```

Abre http://localhost:3002

**Observa:**
- Métricas actualizándose cada segundo
- Gráficos en vivo
- Nuevas órdenes apareciendo
- Alertas aleatorias

**Tip:** Abre en múltiples pestañas, verás que están sincronizadas.

---

## Opción 3: Notificaciones Push 🔔

```bash
npm run notifications
```

Abre http://localhost:3003

**Registra un usuario:**
- UserID: `user123`
- Username: `Tu Nombre`

**Enviar notificación por API:**

```bash
curl -X POST http://localhost:3003/api/notify \
  -H "Content-Type: application/json" \
  -d '{
    "userId":"user123",
    "title":"Prueba",
    "message":"¡Hola desde la API!",
    "type":"success"
  }'
```

También recibirás notificaciones automáticas cada 10 segundos.

---

## Próximos Pasos

### 1. Lee la guía completa
```bash
cat GUIA.md
```

Aprende:
- Conceptos de WebSockets
- Cómo funciona Socket.io
- Patrones comunes
- Best practices

### 2. Completa el taller
```bash
cat TALLER.md
```

Ejercicios:
- Modificar ejemplos existentes
- Agregar nuevas características
- Proyectos desafío

### 3. Explora el código

```bash
# Chat
cat examples/chat/server.js
cat examples/chat/public/chat.js

# Dashboard
cat examples/dashboard/server.js
cat examples/dashboard/public/dashboard.js
```

---

## Ejecutar Múltiples Ejemplos

Terminal 1:
```bash
npm run chat
```

Terminal 2:
```bash
npm run dashboard
```

Terminal 3:
```bash
npm run notifications
```

Ahora tienes 3 servidores corriendo simultáneamente:
- Chat: http://localhost:3001
- Dashboard: http://localhost:3002
- Notificaciones: http://localhost:3003

---

## Troubleshooting

### Puerto ocupado
```bash
# Cambiar puerto en el archivo server.js correspondiente
const PORT = 3005; // Cambiar número
```

### No se conecta
1. Verifica que el servidor esté corriendo
2. Abre consola del navegador (F12)
3. Busca errores en rojo
4. Verifica la URL es correcta

### Reinstalar dependencias
```bash
rm -rf node_modules
npm install
```

---

## Estructura Rápida

```
websockets/
├── examples/
│   ├── chat/          Puerto 3001
│   ├── dashboard/     Puerto 3002
│   └── notifications/ Puerto 3003
├── GUIA.md           Guía completa
├── TALLER.md         Ejercicios
└── README.md         Documentación
```

---

¡Listo para aprender WebSockets! 🚀

**Siguiente:** Lee `GUIA.md` para entender los conceptos.

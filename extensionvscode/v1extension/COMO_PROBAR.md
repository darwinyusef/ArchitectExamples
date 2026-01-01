# Cómo Probar la Extensión AI Goals Tracker

## ⚡ Inicio Rápido (5 pasos)

### Paso 1: Levantar el Backend

```bash
# Ir al backend
cd ../v2extension

# Verificar que existe .env con OPENAI_API_KEY
cat .env

# Si no existe, crear:
cat > .env << 'EOF'
OPENAI_API_KEY=sk-tu-key-aqui
SECRET_KEY=$(openssl rand -hex 32)
REDIS_URL=redis://64.23.150.221:6379/0
EOF

# Levantar servicios
docker-compose up -d

# Esperar ~10 segundos y verificar
curl http://localhost:8000/health
# Debe responder: {"status":"healthy","version":"2.0.0"}
```

### Paso 2: Compilar la Extensión

```bash
# Volver a la extensión
cd ../v1extension

# Instalar dependencias (si no lo hiciste)
npm install

# Compilar
npm run compile
# Debe compilar sin errores
```

### Paso 3: Abrir en VSCode

```bash
# Abrir esta carpeta en VSCode
code .
```

### Paso 4: Ejecutar la Extensión

En VSCode:

1. **Presiona F5** (o Run → Start Debugging)
2. Se abrirá una **nueva ventana** de VSCode con la extensión cargada
3. En esa nueva ventana, busca el ícono de "AI Goals Tracker" en la barra lateral izquierda

### Paso 5: Probar la Extensión

En la nueva ventana de VSCode:

1. **Click en "AI Goals Tracker"** en la Activity Bar (barra lateral izquierda)

2. **Deberías ver:**
   ```
   ✅ AI Goals Tracker: Connected to backend at http://localhost:8000
   ```

3. **Ver los logs:**
   - View → Output
   - Selecciona "AI Goals Tracker - Backend" del dropdown
   - Deberías ver logs de conexión

4. **Crear un goal:**
   - Click en el botón `+` (Add New Goal)
   - Ingresa título: "Mi primer goal"
   - Ingresa descripción: "Probando la integración"
   - Selecciona prioridad: High
   - Click OK

5. **Verificar que se creó en el backend:**
   ```bash
   curl "http://localhost:8000/api/v1/goals?user_id=vscode-user"
   # Deberías ver tu goal en la respuesta
   ```

## 🎯 Funcionalidades para Probar

### ✅ Crear Goal desde Extensión

1. Click en `+` (Add New Goal)
2. Ingresa datos
3. Ver que aparece en el TreeView
4. Verificar en backend:
   ```bash
   curl "http://localhost:8000/api/v1/goals?user_id=$(grep userId ~/.vscode/settings.json | cut -d'"' -f4)"
   ```

### ✅ Crear Goal desde Backend

```bash
# Crear goal desde API
curl -X POST http://localhost:8000/api/v1/goals \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Goal desde API",
    "description": "Este goal se creó desde el backend",
    "user_id": "vscode-user-123",
    "priority": "high"
  }'

# Espera 30 segundos (auto-sync) o click en Refresh
# El goal debe aparecer en la extensión
```

### ✅ WebSocket Real-time

1. Deja la extensión abierta con Output panel visible
2. Desde terminal, crea un goal:
   ```bash
   curl -X POST http://localhost:8000/api/v1/goals \
     -H "Content-Type: application/json" \
     -d '{"title":"WebSocket Test","user_id":"vscode-user","priority":"medium"}'
   ```
3. En el Output panel deberías ver logs de WebSocket
4. El goal debe aparecer automáticamente (después del sync)

### ✅ Rate Limits

1. En la extensión, abre Command Palette (Cmd+Shift+P)
2. Busca: "AI Goals Tracker: Show Rate Limits"
3. Verás el estado de tus rate limits

### ✅ Refresh Manual

1. Click en el botón de refresh (🔄) en el TreeView
2. Los goals se sincronizan inmediatamente

### ✅ Eliminar Goal

1. Click derecho en un goal
2. Selecciona "Delete Goal"
3. Confirma
4. El goal desaparece

## 🔧 Configuración

### Ver/Editar Settings

1. En VSCode: Cmd+, (o Ctrl+,)
2. Busca "AI Goals Tracker"
3. Settings disponibles:
   - **Backend API URL:** http://localhost:8000
   - **WebSocket URL:** ws://localhost:8000/api/v1/ws
   - **Enable Backend:** true
   - **Enable WebSocket:** true
   - **Sync Interval:** 30 segundos

### Cambiar User ID

Por defecto se genera automáticamente. Para cambiarlo:

```json
{
  "aiGoalsTracker.userId": "mi-usuario-personalizado"
}
```

## 🐛 Troubleshooting

### No conecta al backend

**Error:** "Backend is not reachable"

**Solución:**
```bash
# Verificar que el backend está corriendo
curl http://localhost:8000/health

# Si no responde, reiniciar:
cd v2extension
docker-compose restart backend
docker-compose logs -f backend
```

### No aparecen los goals

**Solución:**
1. Click en Refresh (🔄)
2. Verificar User ID en settings
3. Ver Output panel para errores

### WebSocket no conecta

**Solución:**
1. Verificar en Output panel: "AI Goals Tracker - Backend"
2. Buscar errores de WebSocket
3. Verificar que enableWebSocket esté en true
4. Reiniciar la extensión (F5 de nuevo)

### Extension no carga

**Solución:**
1. Help → Toggle Developer Tools
2. Ver consola para errores
3. Recompilar:
   ```bash
   npm run compile
   ```
4. Reiniciar debug (F5)

## 📊 Verificar Todo Funciona

### Checklist

- [ ] Backend responde en http://localhost:8000/health
- [ ] Extension carga (F5 abre nueva ventana)
- [ ] Ves mensaje "Connected to backend"
- [ ] Puedes crear un goal desde extensión
- [ ] El goal aparece en TreeView
- [ ] Puedes refrescar goals
- [ ] WebSocket logs aparecen en Output
- [ ] Rate limits funcionan
- [ ] Puedes eliminar goals

## 🎉 Siguiente Nivel

Una vez que todo funciona:

1. **Explora los endpoints del backend:**
   - http://localhost:8000/docs (Swagger UI)
   - Prueba crear tasks
   - Prueba completar tasks

2. **Mira las métricas:**
   ```bash
   curl http://localhost:8000/api/v1/admin/rate-limits/users/vscode-user/status
   ```

3. **Ve el dashboard:**
   - RabbitMQ: http://localhost:15672
   - MinIO: http://localhost:9001

---

**¿Problemas?** Revisa INTEGRATION_GUIDE.md para más detalles.

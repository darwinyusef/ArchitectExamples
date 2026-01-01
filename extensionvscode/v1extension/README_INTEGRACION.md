# 🎯 Integración Completa - AI Goals Tracker V2

## 📋 Resumen de la Integración

Esta integración conecta la extensión de VSCode (`v1extension`) con el backend FastAPI (`v2extension`) para crear un sistema completo de gestión de objetivos con IA.

### ✅ Estado Actual

- ✅ **Backend completado** (v2extension)
  - FastAPI con LangGraph
  - PostgreSQL + pgvector
  - 8 migraciones de base de datos
  - Rate limiting con OpenAI tokens
  - 32 tests unitarios
  - WebSocket real-time

- ✅ **Extensión integrada** (v1extension)
  - BackendService con REST API
  - WebSocket client
  - Auto-sync cada 30s
  - Event handlers
  - Compilación exitosa

- ⏳ **Pendiente verificar**
  - Migraciones ejecutadas en PostgreSQL
  - Pruebas end-to-end
  - Servicios levantados

## 🏗️ Arquitectura de la Integración

```
┌─────────────────────────────────────────────────────────────────┐
│                         VSCode Extension (v1extension)           │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ extensionV2  │→ │BackendService│→ │ REST API (axios)   │   │
│  │   (UI)       │  │              │  │ WS Client (ws lib) │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
│         ↓                                      ↓                │
│  ┌──────────────┐                     ┌────────────────────┐   │
│  │ TreeView     │                     │  Config Manager    │   │
│  │ Commands     │                     │  Event Handlers    │   │
│  └──────────────┘                     └────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↕ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend (v2extension)                │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ FastAPI      │→ │  LangGraph   │→ │  PostgreSQL+vector │   │
│  │ REST + WS    │  │  RAG Agents  │  │  8 Tablas          │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
│         ↓                 ↓                     ↓               │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ Rate Limiter │  │ OpenAI API   │  │  Redis Cache       │   │
│  │ (Token Bucket│  │ (GPT-4)      │  │  RabbitMQ Queue    │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Estructura de Archivos

```
extensionvscode/
│
├── v2extension/                    # Backend FastAPI
│   ├── backend/
│   │   ├── api/                   # Endpoints REST
│   │   ├── core/                  # Configuración
│   │   ├── db/                    # Database models
│   │   ├── services/              # Business logic
│   │   ├── utils/                 # Utilities
│   │   └── tests/                 # 32 unit tests
│   ├── alembic/                   # Database migrations
│   │   └── versions/              # 8 migration files
│   ├── docker-compose.yml         # Services orchestration
│   ├── .env                       # Environment variables
│   ├── check_migrations.sh        # ✅ Script verificación
│   └── README.md
│
├── v1extension/                   # VSCode Extension
│   ├── src/
│   │   ├── extension.ts           # Entry point original
│   │   ├── extensionV2.ts         # ✅ Entry point integrado
│   │   ├── backendService.ts      # ✅ REST + WebSocket client
│   │   ├── config.ts              # ✅ Configuration manager
│   │   ├── goalsTreeProvider.ts   # TreeView provider
│   │   ├── types.ts               # Type definitions
│   │   └── aiService.ts           # AI validation
│   ├── package.json               # ✅ Updated with backend config
│   ├── INTEGRATION_GUIDE.md       # ✅ Guía completa integración
│   ├── COMO_PROBAR.md             # ✅ Guía rápida testing
│   └── README_INTEGRACION.md      # ✅ Este documento
│
└── SETUP_COMPLETE.sh              # ✅ Script setup automático
```

## 🔧 Archivos Clave de la Integración

### 1. backendService.ts (400 líneas)
**Propósito**: Servicio que conecta la extensión con el backend.

**Funcionalidades**:
- ✅ Cliente HTTP con axios
- ✅ Cliente WebSocket con ws
- ✅ Auto-reconnection
- ✅ Event handlers
- ✅ Logging en Output Channel
- ✅ Rate limit status

**Endpoints implementados**:
```typescript
// Goals
getGoals()                           // GET /api/v1/goals
getGoal(goalId)                      // GET /api/v1/goals/{id}
createGoal(data)                     // POST /api/v1/goals
updateGoal(goalId, updates)          // PATCH /api/v1/goals/{id}
deleteGoal(goalId)                   // DELETE /api/v1/goals/{id}

// Tasks
getTasks(goalId)                     // GET /api/v1/tasks
createTask(data)                     // POST /api/v1/tasks
updateTask(taskId, updates)          // PATCH /api/v1/tasks/{id}
completeTask(taskId)                 // POST /api/v1/tasks/{id}/complete

// Rate Limits
getRateLimitStatus()                 // GET /api/v1/admin/rate-limits/users/{userId}/status

// WebSocket
connectWebSocket()                   // Connect to ws://localhost:8000/api/v1/ws/{userId}
on(eventType, handler)               // Subscribe to events
```

**WebSocket Events**:
- `goal_created` - Nuevo goal creado
- `goal_updated` - Goal actualizado
- `task_completed` - Task completada
- `code_validated` - Código validado por IA

### 2. config.ts (80 líneas)
**Propósito**: Gestión centralizada de configuración.

**Settings disponibles**:
```typescript
aiGoalsTracker.backendApiUrl        // Default: http://localhost:8000
aiGoalsTracker.backendWsUrl         // Default: ws://localhost:8000/api/v1/ws
aiGoalsTracker.userId               // Auto-generated
aiGoalsTracker.courseId             // Optional
aiGoalsTracker.enableBackend        // Default: true
aiGoalsTracker.enableWebSocket      // Default: true
aiGoalsTracker.syncInterval         // Default: 30 seconds
```

### 3. extensionV2.ts (400 líneas)
**Propósito**: Punto de entrada integrado con backend.

**Características**:
- ✅ Inicializa BackendService
- ✅ Conecta WebSocket
- ✅ Auto-sync periódico
- ✅ Event handlers para notificaciones
- ✅ Commands integrados
- ✅ TreeView actualizado en tiempo real

## 🚀 Cómo Probar la Integración

### Paso 1: Verificar Migraciones

```bash
cd v2extension
bash check_migrations.sh
```

**Si las migraciones NO están ejecutadas**, verás:
```
⚠️  MIGRACIONES NO EJECUTADAS

Para ejecutar las migraciones:
  docker-compose exec backend alembic upgrade head
```

**Si las migraciones SÍ están ejecutadas**, verás:
```
✅ TODAS LAS MIGRACIONES EJECUTADAS

Las 8 tablas esperadas están presentes:
  ✓ users
  ✓ courses
  ✓ goals
  ✓ tasks
  ✓ code_snapshots
  ✓ events
  ✓ embeddings
  ✓ rate_limit_audits
```

### Paso 2: Levantar el Backend

```bash
cd v2extension

# Verificar .env tiene OPENAI_API_KEY
cat .env

# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Verificar salud
curl http://localhost:8000/health
# Debe responder: {"status":"healthy","version":"2.0.0"}
```

### Paso 3: Compilar la Extensión

```bash
cd ../v1extension

# Instalar dependencias
npm install

# Compilar
npm run compile
# ✅ Debe compilar sin errores
```

### Paso 4: Ejecutar la Extensión

```bash
# En v1extension/
code .

# Luego en VSCode:
# 1. Presiona F5 (Start Debugging)
# 2. Se abre nueva ventana con extensión cargada
# 3. Click en "AI Goals Tracker" en Activity Bar
```

### Paso 5: Verificar Conexión

En la nueva ventana de VSCode:

1. **Ver Output Panel**:
   - View → Output
   - Selecciona "AI Goals Tracker - Backend"
   - Deberías ver:
     ```
     ✓ Backend Service initialized
     ✓ WebSocket connected
     ```

2. **Crear un Goal**:
   - Click en `+` (Add New Goal)
   - Título: "Test Integration"
   - Descripción: "Testing backend connection"
   - Priority: High
   - Click OK

3. **Verificar en Backend**:
   ```bash
   curl "http://localhost:8000/api/v1/goals?user_id=vscode-user"
   # Debes ver tu goal en la respuesta JSON
   ```

4. **Probar WebSocket Real-time**:
   ```bash
   # Crear goal desde API
   curl -X POST http://localhost:8000/api/v1/goals \
     -H "Content-Type: application/json" \
     -d '{
       "title": "WebSocket Test",
       "description": "Should appear in real-time",
       "user_id": "vscode-user",
       "priority": "high"
     }'

   # En la extensión deberías ver notificación:
   # "📌 New goal created: WebSocket Test"
   ```

## 🔍 Verificación de Funcionalidades

### ✅ Checklist de Testing

- [ ] Backend responde en http://localhost:8000/health
- [ ] PostgreSQL tiene las 8 tablas
- [ ] pgvector extension instalado
- [ ] Extension compila sin errores
- [ ] Extension carga (F5 abre nueva ventana)
- [ ] Mensaje "✓ WebSocket connected" en Output
- [ ] Crear goal desde extensión funciona
- [ ] Goal aparece en TreeView
- [ ] Crear goal desde API aparece en extensión (real-time)
- [ ] Refresh manual funciona
- [ ] Rate limits se pueden consultar
- [ ] Eliminar goal funciona

### 📊 Pruebas de Integración

**1. CRUD de Goals**:
```bash
# Crear
curl -X POST http://localhost:8000/api/v1/goals \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn FastAPI",
    "description": "Master FastAPI framework",
    "user_id": "test-user",
    "priority": "high"
  }'

# Listar
curl "http://localhost:8000/api/v1/goals?user_id=test-user"

# Actualizar
curl -X PATCH http://localhost:8000/api/v1/goals/{goal_id} \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'

# Eliminar
curl -X DELETE http://localhost:8000/api/v1/goals/{goal_id}
```

**2. CRUD de Tasks**:
```bash
# Crear task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Setup FastAPI project",
    "description": "Initialize project structure",
    "goal_id": "{goal_id}",
    "user_id": "test-user",
    "task_type": "coding"
  }'

# Completar task
curl -X POST http://localhost:8000/api/v1/tasks/{task_id}/complete
```

**3. Rate Limits**:
```bash
curl http://localhost:8000/api/v1/admin/rate-limits/users/test-user/status
```

## 🐛 Troubleshooting

### Backend no conecta

**Síntoma**: Extension muestra "Backend is not reachable"

**Solución**:
```bash
cd v2extension

# Ver estado de servicios
docker-compose ps

# Ver logs
docker-compose logs backend

# Reiniciar si es necesario
docker-compose restart backend
```

### WebSocket no conecta

**Síntoma**: No aparecen logs de WebSocket en Output

**Solución**:
1. Verificar en settings: `aiGoalsTracker.enableWebSocket` = true
2. Verificar URL: `aiGoalsTracker.backendWsUrl` = ws://localhost:8000/api/v1/ws
3. Reiniciar extensión (F5)

### PostgreSQL sin migraciones

**Síntoma**: `check_migrations.sh` muestra "⚠️ NO HAY TABLAS"

**Solución**:
```bash
cd v2extension

# Ejecutar migraciones
docker-compose exec backend alembic upgrade head

# Verificar
bash check_migrations.sh
```

### Extension no compila

**Síntoma**: Errores de TypeScript

**Solución**:
```bash
cd v1extension

# Limpiar
rm -rf node_modules out

# Reinstalar
npm install

# Compilar
npm run compile
```

## 📖 Documentación Relacionada

- **INTEGRATION_GUIDE.md** - Guía técnica completa de integración
- **COMO_PROBAR.md** - Guía rápida de 5 pasos para probar
- **v2extension/README.md** - Documentación del backend
- **v2extension/RATE_LIMITING.md** - Documentación de rate limiting
- **v2extension/DOCKER_SETUP.md** - Setup de Docker y PostgreSQL

## 🎯 Próximos Pasos

1. **Verificar migraciones**: `cd v2extension && bash check_migrations.sh`
2. **Levantar servicios**: `docker-compose up -d`
3. **Probar extensión**: `cd ../v1extension && code . && F5`
4. **Crear datos de prueba**: Usar curls o extensión
5. **Publicar extensión**: Crear .vsix file

## 🔗 URLs Importantes

- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- RabbitMQ: http://localhost:15672 (guest/guest)
- MinIO: http://localhost:9001 (minioadmin/minioadmin)

## ✅ Resumen de Cambios

### Archivos Creados
1. `v1extension/src/backendService.ts` - Cliente REST + WebSocket
2. `v1extension/src/config.ts` - Gestión de configuración
3. `v1extension/src/extensionV2.ts` - Entry point integrado
4. `v1extension/INTEGRATION_GUIDE.md` - Guía técnica
5. `v1extension/COMO_PROBAR.md` - Guía rápida
6. `v2extension/check_migrations.sh` - Script verificación
7. `SETUP_COMPLETE.sh` - Setup automático
8. `v1extension/README_INTEGRACION.md` - Este documento

### Archivos Modificados
1. `v1extension/package.json` - Settings y dependencias
   - Added: axios, ws
   - Added: @types/ws (dev)
   - Added: 7 new configuration settings

### Dependencias Agregadas
- `axios@^1.4.0` - HTTP client
- `ws@^8.14.2` - WebSocket client
- `@types/ws@^8.18.1` - TypeScript types

---

**Estado**: ✅ Integración completa y lista para probar

**Última actualización**: 2026-01-01

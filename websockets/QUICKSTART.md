# Quick Start Guide

Guía rápida para poner en marcha la aplicación en menos de 5 minutos.

## Opción 1: Inicio Rápido (Recomendado)

### Terminal 1 - Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Terminal 2 - Frontend

```bash
cd frontend
npm install
npm run dev
```

### Acceder a la aplicación

Abre tu navegador en: **http://localhost:5173**

---

## Opción 2: Usando Docker

```bash
docker-compose up --build
```

Accede a: **http://localhost:5173**

---

## Opción 3: Scripts de Inicio

### macOS/Linux

**Backend:**
```bash
#!/bin/bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
```bash
#!/bin/bash
cd frontend
npm install
npm run dev
```

### Windows

**Backend (start-backend.bat):**
```batch
@echo off
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**Frontend (start-frontend.bat):**
```batch
@echo off
cd frontend
npm install
npm run dev
```

---

## Verificación Rápida

### 1. Verificar Backend
```bash
curl http://localhost:8000/health
```

Deberías ver:
```json
{
  "status": "healthy",
  "active_connections": 0,
  "users": []
}
```

### 2. Verificar Frontend

Abre http://localhost:5173 en tu navegador

### 3. Probar WebSocket

Abre dos ventanas del navegador y conecta con diferentes usuarios para ver el chat en tiempo real.

---

## Comandos Útiles

### Backend
```bash
# Iniciar servidor
python main.py

# Iniciar con uvicorn directamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Ver logs
python main.py --log-level debug
```

### Frontend
```bash
# Iniciar desarrollo
npm run dev

# Build para producción
npm run build

# Preview del build
npm run preview
```

---

## Solución Rápida de Problemas

### Backend no inicia
```bash
# Reinstalar dependencias
pip install --upgrade -r requirements.txt

# Cambiar puerto si está ocupado
uvicorn main:app --reload --port 8001
```

### Frontend no conecta
```bash
# Limpiar cache y reinstalar
rm -rf node_modules package-lock.json
npm install
```

### WebSocket no conecta
1. Verifica que el backend esté corriendo en http://localhost:8000
2. Revisa la consola del navegador para errores
3. Verifica que el puerto 8000 no esté bloqueado por firewall

---

## Siguiente Paso

Lee el [README.md](./README.md) completo para más detalles y la [GUIA_WEBSOCKETS.md](./GUIA_WEBSOCKETS.md) para aprender en profundidad.

¡Feliz coding! 🚀

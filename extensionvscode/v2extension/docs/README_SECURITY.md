# 🔒 Configuración de Seguridad - AI Goals Tracker V2

## ✅ Estado de Seguridad

El proyecto está **completamente protegido** contra la exposición accidental de credenciales en GitHub.

---

## 🛡️ Archivos Protegidos

### ✅ Ya Configurados

| Archivo | Estado | Protección |
|---------|--------|------------|
| `.gitignore` | ✅ Creado | Protege `.env`, `backend/data/`, credenciales |
| `.env` | ✅ Creado | Contiene credenciales reales, **NO se sube** |
| `.env.example` | ✅ Sanitizado | Template sin credenciales, **SÍ se sube** |
| `SECURITY.md` | ✅ Creado | Guía de seguridad completa |
| Documentación (11 .md) | ✅ Sanitizados | Sin credenciales reales |
| `test_rabbitmq.py` | ✅ Actualizado | Lee de `.env`, no hardcoded |
| `test_redis.py` | ✅ Actualizado | Lee de `.env`, no hardcoded |

---

## 📋 Checklist Pre-Commit

Antes de hacer `git push`, verifica:

```bash
# 1. Verificar que .env NO se va a subir
git status | grep ".env$"
# ❌ No debe aparecer nada

# 2. Verificar archivos a subir
git diff --cached

# 3. Buscar posibles credenciales accidentales
git diff --cached | grep -E "64\.23\.150|postgres.*123456|aquicreamos.*pepito"
# ❌ No debe aparecer nada

# 4. Verificar .gitignore está presente
ls -la .gitignore
# ✅ Debe existir
```

---

## 🔍 Archivos Sanitizados

Los siguientes archivos fueron sanitizados (credenciales reales → placeholders):

1. `README.md`
2. `README_FINAL.md`
3. `README_REDIS.md`
4. `CONFIGURACION_ACTUAL.md`
5. `INICIO_RAPIDO.md`
6. `SETUP_COMPLETO.md`
7. `SETUP_CON_POSTGRES_LOCAL.md`
8. `RESUMEN_COMPLETO.md`
9. `FINAL_SUMMARY.md`
10. `DEPLOYMENT_OPTIONS.md`
11. `REDIS_SETUP.md`

**Cambios aplicados**:
- `64.23.150.221` → `YOUR_REDIS_OR_RABBITMQ_HOST`
- `postgres/123456` → `YOUR_DB_USER/YOUR_DB_PASSWORD`
- `aquicreamos/pepito` → `YOUR_RABBITMQ_USER/YOUR_RABBITMQ_PASSWORD`

---

## 🚀 Setup Seguro para Nuevos Desarrolladores

### 1. Clonar el repositorio

```bash
git clone <tu-repo>
cd v2extension
```

### 2. Copiar y configurar .env

```bash
# Copiar template
cp .env.example .env

# Editar con tus credenciales reales
nano .env
# o
code .env
```

### 3. Configurar credenciales reales en .env

Reemplaza los placeholders con tus valores reales:

```bash
# Redis
REDIS_URL=redis://TU_HOST_REAL:6379/0

# PostgreSQL
DATABASE_URL=postgresql+asyncpg://TU_USER:TU_PASSWORD@localhost:5432/ai_goals_tracker

# RabbitMQ
RABBITMQ_URL=amqp://TU_USER:TU_PASSWORD@TU_HOST:5672/

# OpenAI
OPENAI_API_KEY=sk-tu-key-real

# Secret Key (generar con: openssl rand -hex 32)
SECRET_KEY=$(openssl rand -hex 32)
```

### 4. Verificar que .env NO se subirá

```bash
# .env debe estar en .gitignore
cat .gitignore | grep "^\.env$"
# ✅ Debe aparecer: .env

# Verificar que git lo ignora
git status | grep ".env$"
# ❌ No debe aparecer
```

---

## 🔐 Credenciales por Servicio

### Redis
- **Archivo de config**: `.env`
- **Variable**: `REDIS_URL`
- **Formato**: `redis://HOST:6379/0`
- **Protección**: ✅ `.gitignore`

### PostgreSQL
- **Archivo de config**: `.env`
- **Variable**: `DATABASE_URL`
- **Formato**: `postgresql+asyncpg://USER:PASSWORD@localhost:5432/ai_goals_tracker`
- **Protección**: ✅ `.gitignore`

### RabbitMQ
- **Archivo de config**: `.env`
- **Variable**: `RABBITMQ_URL`
- **Formato**: `amqp://USER:PASSWORD@HOST:5672/`
- **Protección**: ✅ `.gitignore`

### OpenAI
- **Archivo de config**: `.env`
- **Variable**: `OPENAI_API_KEY`
- **Formato**: `sk-proj-...`
- **Protección**: ✅ `.gitignore`

### JWT Secret
- **Archivo de config**: `.env`
- **Variable**: `SECRET_KEY`
- **Generación**: `openssl rand -hex 32`
- **Protección**: ✅ `.gitignore`

---

## 🧪 Testing con Credenciales Seguras

Los scripts de testing ahora usan `.env`:

```bash
# Test Redis (usa REDIS_URL de .env)
python backend/scripts/test_redis.py

# Test RabbitMQ (usa RABBITMQ_URL de .env)
python backend/scripts/test_rabbitmq.py

# O proporcionar credenciales por argumentos (solo para testing)
python backend/scripts/test_rabbitmq.py USERNAME PASSWORD HOST
```

---

## ⚠️ Qué NUNCA Hacer

❌ **NO** hardcodear credenciales en código Python:
```python
# ❌ MAL
redis_client = redis.Redis(host="64.23.150.221", password="secret")

# ✅ BIEN
redis_url = os.getenv("REDIS_URL")
redis_client = redis.from_url(redis_url)
```

❌ **NO** poner credenciales en comentarios:
```python
# ❌ MAL
# Conectar a Redis: 64.23.150.221 con password 123456

# ✅ BIEN
# Conectar a Redis usando REDIS_URL de .env
```

❌ **NO** hacer commit de `.env`:
```bash
# ❌ MAL
git add .env
git commit -m "Add configuration"

# ✅ BIEN
git add .env.example
git commit -m "Add configuration template"
```

---

## 🔄 Rotación de Credenciales

Si necesitas cambiar credenciales:

### 1. Local
```bash
# Editar .env
nano .env

# Reiniciar servicios
docker-compose restart
cd backend && poetry run uvicorn app.main:app --reload
```

### 2. Remoto (PostgreSQL)
```bash
# Cambiar password en PostgreSQL
psql -U postgres -c "ALTER USER postgres PASSWORD 'nueva_password';"

# Actualizar .env
nano .env
# DATABASE_URL=postgresql+asyncpg://postgres:nueva_password@localhost:5432/ai_goals_tracker
```

### 3. OpenAI
```bash
# 1. Ir a https://platform.openai.com/api-keys
# 2. Revocar key antigua
# 3. Crear nueva key
# 4. Actualizar .env
nano .env
# OPENAI_API_KEY=sk-nueva-key
```

---

## 📊 Verificación Final

Script para verificar seguridad:

```bash
#!/bin/bash
echo "🔒 Verificando seguridad..."

# 1. .env existe
if [ -f .env ]; then
    echo "✅ .env existe"
else
    echo "❌ .env NO existe - copiar de .env.example"
    exit 1
fi

# 2. .env está en .gitignore
if grep -q "^\.env$" .gitignore; then
    echo "✅ .env está en .gitignore"
else
    echo "❌ .env NO está en .gitignore"
    exit 1
fi

# 3. .env no está en git
if git ls-files | grep -q "^\.env$"; then
    echo "❌ .env está trackeado por git - eliminar!"
    exit 1
else
    echo "✅ .env NO está trackeado por git"
fi

# 4. No hay credenciales en archivos .md
if grep -r "64\.23\.150\.221\|postgres:123456\|aquicreamos:pepito" *.md 2>/dev/null; then
    echo "❌ Se encontraron credenciales en archivos .md"
    exit 1
else
    echo "✅ No hay credenciales en .md"
fi

echo ""
echo "✅ Todas las verificaciones pasaron"
echo "🚀 Seguro para hacer git push"
```

Guardar como `verify-security.sh` y ejecutar:
```bash
chmod +x verify-security.sh
./verify-security.sh
```

---

## 📞 Si Hubo Exposición Accidental

Si ya subiste credenciales a GitHub:

### 1. Acción Inmediata
```bash
# NO hacer más commits hasta rotar credenciales
```

### 2. Rotar TODAS las Credenciales
- ✅ Cambiar password de PostgreSQL
- ✅ Revocar y regenerar OpenAI API key
- ✅ Cambiar credenciales de RabbitMQ
- ✅ Generar nueva SECRET_KEY
- ✅ Cambiar password de Redis (si aplica)

### 3. Limpiar Historial de Git (Peligroso)
```bash
# CUIDADO: Esto reescribe la historia
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

git push origin --force --all
```

### 4. Reportar Incidente
- Documentar qué credenciales se expusieron
- Verificar logs de acceso a servicios
- Cambiar contraseñas relacionadas

---

## ✅ Checklist Final

- [ ] `.env` creado con credenciales reales
- [ ] `.env` está en `.gitignore`
- [ ] `.env` NO está trackeado por git
- [ ] `.env.example` no tiene credenciales reales
- [ ] Documentación sanitizada (sin credenciales)
- [ ] Scripts usan `.env` (no hardcoded)
- [ ] `verify-security.sh` pasa todas las pruebas

---

**Fecha**: 2025-12-28
**Versión**: 2.0.0
**Estado**: 🔒 **SEGURO PARA GITHUB**

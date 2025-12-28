# 🔒 Seguridad y Gestión de Credenciales

## ⚠️ IMPORTANTE: Protección de Credenciales

Este proyecto utiliza varios servicios que requieren credenciales sensibles. **NUNCA** subas credenciales reales a GitHub.

---

## 📋 Archivos Protegidos

Los siguientes archivos están incluidos en `.gitignore` y **NO** se subirán a GitHub:

### Archivos de Configuración
- `.env` - Contiene TODAS las credenciales reales
- `.vscode/settings.json` - Puede contener API keys locales
- `backend/data/` - Datos locales y eventos

### Credenciales Protegidas
- ❌ Contraseñas de PostgreSQL local
- ❌ API Keys de OpenAI
- ❌ SECRET_KEY de JWT
- ❌ Credenciales de RabbitMQ
- ❌ Credenciales de Redis

---

## ✅ Configuración Segura

### Paso 1: Copiar .env.example
```bash
cp .env.example .env
```

### Paso 2: Editar .env con tus credenciales
```bash
# Usar tu editor preferido
nano .env
# o
code .env
```

### Paso 3: Reemplazar los placeholders

En el archivo `.env`, reemplaza:
- `YOUR_REDIS_HOST` → Tu servidor Redis
- `YOUR_DB_USER` / `YOUR_DB_PASSWORD` → Tus credenciales PostgreSQL
- `YOUR_RABBITMQ_USER` / `YOUR_RABBITMQ_PASSWORD` → Tus credenciales RabbitMQ
- `sk-your-openai-api-key-here` → Tu API key de OpenAI
- `your-secret-key-here` → Genera una con `openssl rand -hex 32`

---

## 🔐 Generación de SECRET_KEY

La `SECRET_KEY` se usa para firmar tokens JWT. **NUNCA** uses la misma key en producción y desarrollo.

### Generar SECRET_KEY
```bash
# Método 1: OpenSSL
openssl rand -hex 32

# Método 2: Python
python3 -c "import secrets; print(secrets.token_hex(32))"

# Método 3: Usar el script automático
./migrate-api-key.sh
```

---

## 📁 Estructura de Archivos de Configuración

```
v2extension/
├── .env                    # ❌ NUNCA SUBIR - Credenciales reales
├── .env.example            # ✅ OK SUBIR - Template sin credenciales
├── .gitignore              # ✅ Protege archivos sensibles
├── SECURITY.md             # ✅ Este archivo
└── backend/
    ├── data/               # ❌ NUNCA SUBIR - Datos locales
    └── storage/            # ❌ NUNCA SUBIR - Archivos de usuarios
```

---

## 🚨 Verificación Pre-Commit

Antes de hacer commit, verifica que NO estás subiendo credenciales:

```bash
# Verificar archivos a subir
git status

# Verificar que .env NO aparece
git ls-files | grep -E "\.env$|credentials|secrets"

# Debe retornar vacío. Si aparece algo, revisa tu .gitignore
```

---

## 🔍 Credenciales Comprometidas

Si accidentalmente subiste credenciales a GitHub:

### 1. Rotar INMEDIATAMENTE
- ✅ Cambiar contraseña de PostgreSQL
- ✅ Regenerar OpenAI API key
- ✅ Cambiar credenciales de RabbitMQ
- ✅ Generar nueva SECRET_KEY

### 2. Limpiar historial de Git
```bash
# Eliminar archivo del historial (CUIDADO)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (solo si es tu repo personal)
git push origin --force --all
```

### 3. Invalidar credenciales antiguas
- OpenAI: https://platform.openai.com/api-keys → Revoke key
- PostgreSQL: `ALTER USER postgres PASSWORD 'nueva_contraseña';`
- RabbitMQ: Cambiar password en panel de administración

---

## 📚 Buenas Prácticas

### ✅ DO (Hacer)
- Usar `.env` para todas las credenciales
- Verificar `.gitignore` antes del primer commit
- Rotar credenciales periódicamente
- Usar credenciales diferentes en dev/staging/prod
- Documentar variables de entorno en `.env.example`

### ❌ DON'T (No Hacer)
- Hardcodear credenciales en código
- Subir `.env` a GitHub
- Compartir credenciales por Slack/Email
- Usar misma contraseña en múltiples servicios
- Commitear archivos con credenciales temporales

---

## 🎯 Checklist de Seguridad

Antes de subir a GitHub:

- [ ] `.env` está en `.gitignore`
- [ ] `.env.example` NO tiene credenciales reales
- [ ] `backend/data/` está en `.gitignore`
- [ ] No hay API keys hardcodeadas en código
- [ ] `SECRET_KEY` es única y generada aleatoriamente
- [ ] Contraseñas locales NO están en archivos versionados
- [ ] `git status` no muestra archivos sensibles

---

## 📞 Contacto

Si detectas una vulnerabilidad de seguridad:
1. NO abrir issue público en GitHub
2. Contactar directamente al maintainer
3. Reportar con detalles del problema
4. Esperar confirmación antes de disclosure público

---

**Última actualización**: 2025-12-28
**Versión**: 2.0.0

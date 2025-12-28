# 🔧 Guía de Configuración Rápida

## ✅ Problema Resuelto

Ahora la configuración `aiGoalsTracker.openaiApiKey` aparecerá correctamente en VS Code Settings.

## 🚀 Configuración en 3 Pasos

### 1. Obtener API Key de OpenAI

1. Ve a https://platform.openai.com/api-keys
2. Inicia sesión o crea una cuenta
3. Click en "Create new secret key"
4. Copia la clave (empieza con `sk-proj-...`)

### 2. Configurar en VS Code

#### Opción A: Desde la UI de Settings

1. Abre VS Code
2. Presiona `Cmd/Ctrl + ,` para abrir Settings
3. Busca: `aiGoalsTracker`
4. Verás tres opciones:
   - **OpenAI API Key** - Pega tu clave aquí
   - **Model** - Dejalo en `gpt-4o-mini`
   - **Auto Save** - Dejalo en `true`

#### Opción B: Editar settings.json directamente

```json
{
  "aiGoalsTracker.openaiApiKey": "sk-proj-TU_CLAVE_AQUI",
  "aiGoalsTracker.model": "gpt-4o-mini",
  "aiGoalsTracker.autoSave": true
}
```

Para abrir settings.json:
- `Cmd/Ctrl + Shift + P`
- Escribe: "Preferences: Open User Settings (JSON)"

### 3. Verificar Configuración

1. Abre la paleta de comandos: `Cmd/Ctrl + Shift + P`
2. Escribe: "AI Goals"
3. Deberías ver los comandos de la extensión

## 📍 Dónde Configurar

### Configuración Global (Recomendado)

Se aplicará a todos tus proyectos:

**Ubicación**: Settings de Usuario
**Cómo**: `File > Preferences > Settings` (o `Cmd/Ctrl + ,`)

### Configuración por Proyecto

Solo para el workspace actual:

**Ubicación**: `.vscode/settings.json` en tu proyecto
**Cómo**:
1. Crea archivo `.vscode/settings.json`
2. Agrega la configuración

```json
{
  "aiGoalsTracker.openaiApiKey": "sk-proj-...",
  "aiGoalsTracker.model": "gpt-4o-mini"
}
```

## 🔐 Seguridad de la API Key

### ✅ Hacer

- Usar variables de entorno para proyectos en Git
- Agregar `.vscode/settings.json` a `.gitignore` si contiene la clave
- Configurar en Settings de Usuario (no se commitea)

### ❌ No Hacer

- Commitear la API key a repositorios públicos
- Compartir la API key en código
- Usar la misma clave en múltiples equipos

### Configuración Segura con Variables de Entorno

Si necesitas compartir el proyecto sin exponer la clave:

1. Crea un archivo `.env`:
```bash
OPENAI_API_KEY=sk-proj-tu-clave-aqui
```

2. Agrega `.env` a `.gitignore`:
```
.env
.vscode/settings.json
```

3. En settings.json usa:
```json
{
  "aiGoalsTracker.openaiApiKey": "${env:OPENAI_API_KEY}"
}
```

## 🎯 Configuraciones Disponibles

### aiGoalsTracker.openaiApiKey

- **Tipo**: String
- **Requerido**: Sí
- **Descripción**: Tu API Key de OpenAI
- **Dónde obtener**: https://platform.openai.com/api-keys

### aiGoalsTracker.model

- **Tipo**: String
- **Default**: `gpt-4o-mini`
- **Opciones**: Solo `gpt-4o-mini`
- **Descripción**: Modelo de OpenAI a usar

### aiGoalsTracker.autoSave

- **Tipo**: Boolean
- **Default**: `true`
- **Descripción**: Auto-guardar cambios en goals.json

## 🧪 Verificar que Funciona

### Test 1: Verificar API Key

1. Abre cualquier archivo en VS Code
2. Abre el panel "AI Goals Tracker"
3. Click en un goal y luego en ▶ Start Goal
4. Si no hay error, la clave está configurada correctamente

### Test 2: Validar Código

1. Inicia un goal
2. Escribe código simple:
```javascript
function suma(a, b) {
  return a + b;
}
```
3. Click en ✓ Validate Task
4. Deberías recibir respuesta de la IA

## ❗ Solución de Problemas

### "OpenAI API Key not configured"

**Causa**: La clave no está configurada o está mal escrita

**Solución**:
1. Ve a Settings (`Cmd/Ctrl + ,`)
2. Busca `aiGoalsTracker.openaiApiKey`
3. Verifica que la clave esté correcta
4. Recarga VS Code (`Cmd/Ctrl + R` en ventana de desarrollo)

### "Settings not found"

**Causa**: La extensión no está compilada o instalada correctamente

**Solución**:
```bash
cd v1extension
npm run compile
# Presiona F5 para recargar
```

### "Error validating code: 401"

**Causa**: API Key inválida o sin créditos

**Solución**:
1. Verifica la clave en https://platform.openai.com/api-keys
2. Verifica que tengas créditos en tu cuenta
3. Regenera la clave si es necesario

### "Error validating code: Network error"

**Causa**: Sin conexión a internet o firewall

**Solución**:
1. Verifica tu conexión a internet
2. Verifica que no haya firewall bloqueando api.openai.com
3. Prueba con VPN si estás en una red restringida

## 📝 Ejemplo Completo de Configuración

### settings.json (Usuario)

```json
{
  "// AI Goals Tracker Configuration": "",
  "aiGoalsTracker.openaiApiKey": "sk-proj-abc123...",
  "aiGoalsTracker.model": "gpt-4o-mini",
  "aiGoalsTracker.autoSave": true,

  "// Optional VS Code customizations": "",
  "workbench.colorCustomizations": {
    "statusBar.background": "#007ACC"
  },
  "editor.formatOnSave": true
}
```

### .gitignore (Proyecto)

```gitignore
# VS Code settings with sensitive data
.vscode/settings.json

# Environment variables
.env
.env.local

# Node modules
node_modules/

# Build output
out/
dist/
```

## 🎓 Mejores Prácticas

1. **Usa Settings de Usuario** para la API key
2. **Usa Settings de Workspace** para configuraciones específicas del proyecto
3. **Nunca commitees** API keys al repositorio
4. **Rota las claves** periódicamente por seguridad
5. **Monitorea el uso** en OpenAI dashboard

## 📚 Recursos

- [OpenAI API Keys](https://platform.openai.com/api-keys)
- [OpenAI Pricing](https://openai.com/pricing)
- [VS Code Settings](https://code.visualstudio.com/docs/getstarted/settings)
- [Environment Variables en VS Code](https://code.visualstudio.com/docs/editor/variables-reference)

## 🎉 Listo!

Una vez configurado, ve a [QUICKSTART.md](./QUICKSTART.md) para empezar a usar la extensión.

---

**Configuración completada** ✅
Ahora puedes usar AI Goals Tracker con validación de código por IA!

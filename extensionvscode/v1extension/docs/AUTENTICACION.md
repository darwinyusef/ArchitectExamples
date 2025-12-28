# 🔐 Guía de Autenticación - AI Goals Tracker

## Resumen

La extensión ahora requiere autenticación de usuario para validar tareas. Las credenciales se validan contra un mock en GitHub.

## 🔑 Credenciales de Acceso

### Credenciales del Mock

```json
{
  "user": "admin",
  "pass": "admin"
}
```

**URL del Mock**: https://raw.githubusercontent.com/darwinyusef/darwinyusef/refs/heads/master/information/loggin_mock.json

## 📝 Configuración

### Opción 1: Desde VS Code Settings

1. Abre Settings: `Cmd/Ctrl + ,`
2. Busca: `aiGoalsTracker`
3. Configura:
   - **Username**: admin
   - **Password**: admin
   - **OpenAI API Key**: tu-clave-aqui

### Opción 2: Editar settings.json

```json
{
  "aiGoalsTracker.username": "admin",
  "aiGoalsTracker.password": "admin",
  "aiGoalsTracker.openaiApiKey": "sk-proj-...",
  "aiGoalsTracker.model": "gpt-4o-mini",
  "aiGoalsTracker.autoSave": true
}
```

### Opción 3: Prompt Interactivo

La primera vez que intentes validar una tarea sin credenciales configuradas:

1. Aparecerá un mensaje: "Authentication required. Would you like to enter your credentials?"
2. Click en "Yes"
3. Ingresa username: `admin`
4. Ingresa password: `admin`
5. Las credenciales se guardarán automáticamente

## 🚀 Flujo de Autenticación

### Al Iniciar la Extensión

```
1. Extension se activa
   ↓
2. Verifica si hay username/password configurados
   ↓
3a. Si están configurados:
    - Valida contra el mock en GitHub
    - Muestra "✅ Authenticated successfully!" si es correcto
    - Muestra error si las credenciales son incorrectas
    ↓
3b. Si NO están configurados:
    - La extensión se activa normalmente
    - Pedirá autenticación al validar la primera tarea
```

### Al Validar una Tarea

```
1. Usuario click en ✓ Validate Task
   ↓
2. Verifica autenticación
   ↓
3a. Si está autenticado (cache válido por 5 min):
    - Procede con la validación
    ↓
3b. Si NO está autenticado:
    - Muestra prompt para ingresar credenciales
    - Valida contra GitHub
    - Si es correcto, procede con la validación
    - Si falla, muestra error y cancela
```

## 🔒 Seguridad

### Caché de Autenticación

- Las credenciales se validan contra GitHub
- Se mantiene un caché de autenticación por **5 minutos**
- Después de 5 minutos, se re-valida automáticamente

### Almacenamiento

- Las credenciales se guardan en la configuración de VS Code
- **Importante**: Las credenciales se almacenan en texto plano
- Asegúrate de no compartir tu `settings.json` si contiene credenciales

### Mejores Prácticas

1. **Usa Settings de Workspace** para proyectos compartidos
2. **Usa Settings de Usuario** para uso personal
3. **Agrega a .gitignore**: `.vscode/settings.json`

## 🔄 Cambiar Credenciales

### Método 1: Settings

1. Ve a Settings: `Cmd/Ctrl + ,`
2. Busca: `aiGoalsTracker.username`
3. Actualiza los valores

### Método 2: Borrar y Re-ingresar

1. Borra las credenciales en Settings
2. Intenta validar una tarea
3. Ingresa las nuevas credenciales en el prompt

## ❌ Cerrar Sesión

Actualmente no hay comando de logout. Para "cerrar sesión":

1. Borra las credenciales de Settings
2. O recarga VS Code: `Cmd/Ctrl + R`

## 🐛 Troubleshooting

### Error: "Authentication failed: Invalid username or password"

**Causa**: Credenciales incorrectas

**Solución**:
```
Credenciales correctas:
- Username: admin
- Password: admin
```

### Error: "Error validating credentials"

**Causa**: No se pudo conectar al mock en GitHub

**Solución**:
1. Verifica tu conexión a internet
2. Verifica que la URL sea accesible:
   https://raw.githubusercontent.com/darwinyusef/darwinyusef/refs/heads/master/information/loggin_mock.json
3. Verifica que no haya firewall bloqueando GitHub

### No aparece prompt de autenticación

**Causa**: Ya tienes credenciales configuradas (aunque incorrectas)

**Solución**:
1. Ve a Settings
2. Verifica `aiGoalsTracker.username` y `aiGoalsTracker.password`
3. Actualízalos a `admin` / `admin`

### "Authentication required to validate tasks"

**Causa**: No estás autenticado

**Solución**:
1. Configura username y password en Settings
2. O responde "Yes" al prompt interactivo

## 📊 Arquitectura de Autenticación

### AuthService

```typescript
class AuthService {
  // Valida credenciales contra GitHub mock
  async validateCredentials(): Promise<boolean>

  // Muestra prompt para ingresar credenciales
  async promptForCredentials(): Promise<boolean>

  // Asegura que el usuario esté autenticado
  async ensureAuthenticated(): Promise<boolean>

  // Verifica si está autenticado (caché)
  isUserAuthenticated(): boolean

  // Cierra sesión
  logout(): void
}
```

### Flujo de Validación

```typescript
// En extension.ts - comando validateTask
const isAuthenticated = await authService.ensureAuthenticated();
if (!isAuthenticated) {
  vscode.window.showErrorMessage('❌ Authentication required');
  return;
}
// Continúa con la validación...
```

## 🔐 Ejemplo de Configuración Completa

```json
{
  "// === AUTENTICACIÓN ===": "",
  "aiGoalsTracker.username": "admin",
  "aiGoalsTracker.password": "admin",

  "// === OPENAI ===": "",
  "aiGoalsTracker.openaiApiKey": "sk-proj-abc123...",
  "aiGoalsTracker.model": "gpt-4o-mini",

  "// === OTRAS OPCIONES ===": "",
  "aiGoalsTracker.autoSave": true
}
```

## 📝 Notas Importantes

1. **Las credenciales del mock son públicas** (`admin`/`admin`)
2. **Esto es solo un ejemplo** - en producción se usaría un sistema real
3. **La validación se hace en cada inicio** de la extensión
4. **Cache de 5 minutos** para no hacer requests constantes
5. **Se requiere internet** para validar contra GitHub

## 🎯 Próximos Pasos

1. Configura tus credenciales (`admin`/`admin`)
2. Configura tu API key de OpenAI
3. Recarga VS Code o presiona F5
4. Deberías ver "✅ Authenticated successfully!"
5. Ya puedes validar tareas

---

**Autenticación configurada** ✅
Ahora estás listo para usar AI Goals Tracker de forma segura!

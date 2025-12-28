# Guía de Instalación - AI Goals Tracker

## Requisitos Previos

- **Node.js**: v16 o superior
- **VS Code**: v1.75.0 o superior
- **npm**: v7 o superior
- **API Key de OpenAI**: [Obtener aquí](https://platform.openai.com/api-keys)

## Instalación para Desarrollo

### 1. Clonar/Descargar el proyecto

```bash
cd /ruta/a/tu/proyecto
cd v1extension
```

### 2. Instalar dependencias

```bash
npm install
```

Esto instalará:
- TypeScript
- VS Code Extension API types
- ESLint
- axios (para llamadas a OpenAI)

### 3. Compilar el proyecto

```bash
npm run compile
```

O para compilación continua durante desarrollo:

```bash
npm run watch
```

### 4. Ejecutar la extensión

**Método 1: Desde VS Code**
1. Abre la carpeta `v1extension` en VS Code
2. Presiona `F5`
3. Selecciona "VS Code Extension Development" si pregunta
4. Se abrirá una nueva ventana de VS Code con la extensión cargada

**Método 2: Desde el menú**
1. Ve a **Run > Start Debugging**
2. O usa **Run > Run Without Debugging** (`Ctrl+F5`)

### 5. Configurar API Key

En la ventana de desarrollo que se abrió:

1. `Cmd/Ctrl + Shift + P`
2. Busca: "Preferences: Open Settings (UI)"
3. Busca: `aiGoalsTracker.openaiApiKey`
4. Ingresa tu API key

O edita directamente `.vscode/settings.json` del workspace:

```json
{
  "aiGoalsTracker.openaiApiKey": "sk-proj-..."
}
```

## Instalación para Producción

### Opción 1: Instalar desde VSIX

#### Empaquetar la extensión

```bash
# Instalar vsce globalmente
npm install -g @vscode/vsce

# Empaquetar
vsce package
```

Esto generará `ai-goals-tracker-0.0.1.vsix`

#### Instalar el VSIX

**Desde VS Code:**
1. Ve a Extensions (`Cmd/Ctrl + Shift + X`)
2. Click en `...` (más opciones)
3. Selecciona "Install from VSIX..."
4. Selecciona el archivo `.vsix`

**Desde línea de comandos:**

```bash
code --install-extension ai-goals-tracker-0.0.1.vsix
```

### Opción 2: Desarrollo Local

Crear un symlink a la extensión:

```bash
# macOS/Linux
ln -s /ruta/completa/a/v1extension ~/.vscode/extensions/ai-goals-tracker

# Windows (como administrador)
mklink /D "%USERPROFILE%\.vscode\extensions\ai-goals-tracker" "C:\ruta\completa\a\v1extension"
```

Luego compila y recarga VS Code.

## Verificar Instalación

### 1. Verificar que la extensión está activa

1. Abre la paleta de comandos (`Cmd/Ctrl + Shift + P`)
2. Escribe "AI Goals"
3. Deberías ver comandos como:
   - `AI Goals Tracker: Refresh Goals`
   - `AI Goals Tracker: Add New Goal`

### 2. Verificar el panel lateral

1. Busca el ícono de "AI Goals Tracker" en la barra de actividades (izquierda)
2. Click en el ícono
3. Deberías ver tres paneles:
   - Goals & Tasks
   - Current Goal Documentation
   - Upcoming Goals Documentation

### 3. Verificar que carga goals

1. Abre cualquier carpeta de proyecto
2. La extensión debería crear `.vscode/goals.json` automáticamente
3. Deberías ver goals de ejemplo en el panel

## Configuración Adicional

### Settings Recomendados

Agrega esto a tu `settings.json` para mejor experiencia:

```json
{
  "aiGoalsTracker.openaiApiKey": "tu-api-key",
  "workbench.colorCustomizations": {
    "aiGoalsContainer.foreground": "#007ACC"
  }
}
```

### Keyboard Shortcuts Personalizados

Agrega a `keybindings.json`:

```json
[
  {
    "key": "ctrl+shift+g",
    "command": "aiGoalsTracker.refreshGoals"
  },
  {
    "key": "ctrl+shift+v",
    "command": "aiGoalsTracker.validateTask"
  }
]
```

## Solución de Problemas

### La extensión no aparece

**Problema**: No veo el ícono en la barra de actividades

**Solución**:
```bash
# Recompilar
npm run compile

# Verificar que no hay errores
npm run lint

# Recargar VS Code
Cmd/Ctrl + R (en la ventana de desarrollo)
```

### Error de compilación

**Problema**: `npm run compile` falla

**Solución**:
```bash
# Limpiar y reinstalar
rm -rf node_modules package-lock.json
npm install
npm run compile
```

### La IA no responde

**Problema**: Las validaciones fallan o timeout

**Solución**:
1. Verifica tu API key en settings
2. Verifica que tienes créditos en OpenAI
3. Verifica tu conexión a internet
4. Revisa la consola de desarrollo:
   - `Help > Toggle Developer Tools`
   - Pestaña "Console"

### Goals no se cargan

**Problema**: El panel está vacío

**Solución**:
1. Asegúrate de tener un workspace abierto (no solo archivos)
2. Verifica que `.vscode/goals.json` existe
3. Valida el JSON en https://jsonlint.com
4. Ejecuta "Refresh Goals"

### Error: "Cannot find module"

**Problema**: Error al activar la extensión

**Solución**:
```bash
# Reinstalar dependencias
npm install

# Recompilar
npm run compile

# Si persiste, verifica tsconfig.json
cat tsconfig.json
```

## Actualizar la Extensión

### Desde desarrollo

```bash
git pull  # o descarga nueva versión
npm install
npm run compile
```

Luego recarga VS Code (`Cmd/Ctrl + R` en ventana de desarrollo)

### Desde VSIX

1. Desinstala la versión anterior
2. Instala el nuevo VSIX
3. Recarga VS Code

## Desinstalar

### Desde VS Code

1. Ve a Extensions (`Cmd/Ctrl + Shift + X`)
2. Busca "AI Goals Tracker"
3. Click en el ícono de engranaje
4. Selecciona "Uninstall"

### Desde línea de comandos

```bash
code --uninstall-extension ai-goals-tracker
```

### Limpiar datos

```bash
# Eliminar configuración
rm ~/.config/Code/User/settings.json  # Editar y quitar la API key

# Eliminar goals de proyectos
find ~/proyectos -name "goals.json" -path "*/.vscode/*" -delete
```

## Debugging

### Ver logs de la extensión

1. En la ventana de desarrollo
2. `Help > Toggle Developer Tools`
3. Pestaña "Console"
4. Filtrar por "AI Goals"

### Breakpoints

1. Abre `src/extension.ts` en VS Code
2. Agrega breakpoints (click en el margen izquierdo)
3. Presiona `F5`
4. El debugger se detendrá en los breakpoints

### Inspeccionar estado

Agrega console.logs temporales:

```typescript
console.log('Goals loaded:', goals);
console.log('Validation result:', validationResult);
```

## Scripts Disponibles

```bash
# Compilar una vez
npm run compile

# Compilar en modo watch
npm run watch

# Linter
npm run lint

# Tests (si se implementan)
npm test

# Empaquetar para distribución
vsce package

# Publicar a marketplace (requiere cuenta)
vsce publish
```

## Recursos Adicionales

- [README.md](./README.md) - Documentación general
- [QUICKSTART.md](./QUICKSTART.md) - Tutorial de inicio rápido
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Arquitectura del proyecto
- [examples/goals.json](./examples/goals.json) - Ejemplos de goals

## Soporte

Si encuentras problemas:

1. Revisa esta guía de instalación
2. Revisa QUICKSTART.md para troubleshooting
3. Revisa los logs de la consola
4. Crea un issue con:
   - Versión de VS Code
   - Versión de Node.js
   - Sistema operativo
   - Logs de error
   - Pasos para reproducir

## Siguiente Paso

Una vez instalado correctamente, ve a [QUICKSTART.md](./QUICKSTART.md) para un tutorial interactivo.

¡Feliz desarrollo con AI Goals Tracker! 🚀

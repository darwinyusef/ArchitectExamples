# Guía de Inicio Rápido - AI Goals Tracker

## Instalación y Setup (5 minutos)

### Paso 1: Instalar dependencias

```bash
cd v1extension
npm install
```

### Paso 2: Compilar la extensión

```bash
npm run compile
```

### Paso 3: Ejecutar en modo desarrollo

Presiona `F5` en VS Code o ejecuta:
- **View > Run**
- Selecciona "Run Extension"

Esto abrirá una nueva ventana de VS Code con la extensión cargada.

## Configuración Inicial

### 1. Configurar OpenAI API Key

En la ventana de extensión que se abrió:

1. Abre Settings: `Cmd/Ctrl + ,`
2. Busca: `aiGoalsTracker.openaiApiKey`
3. Ingresa tu API key de OpenAI

O edita directamente `settings.json`:

```json
{
  "aiGoalsTracker.openaiApiKey": "sk-..."
}
```

### 2. Abrir un proyecto

Abre cualquier carpeta de proyecto en VS Code (la extensión necesita un workspace).

## Primer Goal - Tutorial Interactivo

### Paso 1: Ver el panel lateral

Click en el ícono de "AI Goals Tracker" en la barra de actividades (izquierda).

Verás tres paneles:
- **Goals & Tasks** - Lista de objetivos
- **Current Goal Documentation** - Documentación del goal activo
- **Upcoming Goals Documentation** - Próximos goals

### Paso 2: Iniciar un goal

1. En el panel "Goals & Tasks", verás goals de ejemplo
2. Click en el ícono de play (▶) junto a "Setup Project Structure"
3. El goal se marcará como "in progress"

### Paso 3: Completar la primera tarea

La primera tarea es: "Create src, tests, and config folders"

1. Abre el terminal integrado (`Ctrl + ñ` o `Cmd + J`)
2. Ejecuta:
   ```bash
   mkdir src tests config
   ```
3. Crea un archivo en `src/index.js`:
   ```javascript
   // Main entry point
   console.log('Project initialized');
   ```
4. Abre `src/index.js` en el editor
5. Click en el ícono de check (✓) junto a la tarea
6. La IA validará tu código

### Paso 4: Continuar con las siguientes tareas

Si la validación es exitosa:
- La tarea se marca como completada (✓)
- Automáticamente pasa a la siguiente tarea
- Puedes ver el progreso en la barra de progreso

Si falla:
- Recibirás sugerencias de mejora
- Puedes corregir y volver a validar

## Crear tus Propios Goals

### Opción 1: Usar el archivo de ejemplo

```bash
cp examples/goals.json .vscode/goals.json
```

Luego edita `.vscode/goals.json` con tus propios goals.

### Opción 2: Crear desde cero

Crea `.vscode/goals.json`:

```json
{
  "goals": [
    {
      "id": "mi-goal-1",
      "title": "Mi Primer Goal",
      "description": "Aprender a usar la extensión",
      "documentation": "# Mi Goal\n\nAquí va la documentación en Markdown",
      "tasks": [
        {
          "id": "tarea-1",
          "description": "Primera tarea a completar",
          "code": "",
          "status": "pending"
        }
      ],
      "status": "pending",
      "currentTaskIndex": 0
    }
  ]
}
```

### Opción 3: Usar el comando "Add Goal"

1. Click en el ícono "+" en el panel de Goals & Tasks
2. Ingresa el título del goal
3. Ingresa la descripción
4. Edita `.vscode/goals.json` para agregar tareas

## Comandos Disponibles

### Desde el panel Goals & Tasks:

- **▶ Start Goal**: Inicia un goal
- **✓ Validate Task**: Valida la tarea actual con IA
- **🔄 Refresh Goals**: Recarga el archivo goals.json
- **+ Add Goal**: Agrega un nuevo goal

### Desde la paleta de comandos (`Cmd/Ctrl + Shift + P`):

- `AI Goals Tracker: Refresh Goals`
- `AI Goals Tracker: Add New Goal`

## Tips y Mejores Prácticas

### 1. Estructura de Goals

- Divide goals grandes en goals más pequeños
- Cada task debe ser específica y medible
- Usa documentación Markdown para explicar el contexto

### 2. Validación de Código

- Asegúrate de tener el archivo relevante abierto en el editor
- La IA valida TODO el contenido del archivo activo
- Sé específico en la descripción de las tareas

### 3. Documentación

- Usa headers Markdown (# ## ###)
- Incluye ejemplos de código
- Agrega enlaces a recursos externos

### 4. Workflow Eficiente

```
1. Lee la documentación del goal
2. Lee la descripción de la tarea actual
3. Escribe el código
4. Valida con IA
5. Si pasa → siguiente tarea
6. Si falla → lee sugerencias → corrige → revalida
```

## Ejemplo de Goal Completo

```json
{
  "id": "auth-system",
  "title": "Sistema de Autenticación",
  "description": "Implementar login y registro de usuarios",
  "documentation": "# Sistema de Autenticación\n\n## Objetivo\nCrear un sistema seguro de autenticación.\n\n## Tecnologías\n- JWT para tokens\n- bcrypt para passwords\n- Express.js\n\n## Seguridad\n- Hash de passwords\n- Validación de inputs\n- Rate limiting",
  "tasks": [
    {
      "id": "auth-1",
      "description": "Crear modelo User con campos email y hashedPassword",
      "code": "",
      "status": "pending"
    },
    {
      "id": "auth-2",
      "description": "Implementar función hashPassword usando bcrypt",
      "code": "",
      "status": "pending"
    },
    {
      "id": "auth-3",
      "description": "Crear endpoint POST /register que valide email y hashee password",
      "code": "",
      "status": "pending"
    },
    {
      "id": "auth-4",
      "description": "Crear endpoint POST /login que genere JWT token",
      "code": "",
      "status": "pending"
    },
    {
      "id": "auth-5",
      "description": "Implementar middleware de autenticación que verifique JWT",
      "code": "",
      "status": "pending"
    }
  ],
  "status": "pending",
  "currentTaskIndex": 0
}
```

## Troubleshooting

### La extensión no aparece

1. Verifica que compiló correctamente: `npm run compile`
2. Recarga la ventana: `Cmd/Ctrl + R`
3. Revisa la consola: `Help > Toggle Developer Tools`

### La validación falla siempre

1. Verifica tu API key
2. Verifica que tienes créditos en OpenAI
3. Revisa que el archivo correcto esté abierto en el editor

### No se cargan los goals

1. Verifica que `.vscode/goals.json` exista
2. Valida el JSON en un validador online
3. Usa el comando "Refresh Goals"

## Próximos Pasos

1. Crea un goal para tu proyecto actual
2. Experimenta con diferentes tipos de tareas
3. Personaliza la documentación con Markdown
4. Comparte tus goals con tu equipo

## Recursos

- [Documentación de OpenAI API](https://platform.openai.com/docs)
- [Markdown Guide](https://www.markdownguide.org/)
- [VS Code Extension API](https://code.visualstudio.com/api)

¡Feliz codificación con asistencia de IA! 🚀

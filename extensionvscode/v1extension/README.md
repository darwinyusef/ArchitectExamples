# AI Goals Tracker - VS Code Extension

Una extensión de Visual Studio Code que te permite gestionar y validar objetivos de código con asistencia de inteligencia artificial (ChatGPT).

## Características

- **Panel lateral de Goals y Tasks**: Visualiza y gestiona tus objetivos de desarrollo en un árbol jerárquico
- **Validación automática con IA**: Valida tu código usando ChatGPT para verificar si cumple con los requisitos de cada tarea
- **Documentación integrada**: Visualiza la documentación del goal actual y los próximos goals directamente en VS Code
- **Seguimiento de progreso**: Rastrea el progreso de cada tarea y goal con estados visuales
- **Ejecución secuencial**: Las tareas se ejecutan una por una, asegurando un flujo de trabajo organizado

## Instalación

### Desde el código fuente:

1. Clona o descarga este repositorio
2. Abre la carpeta en VS Code
3. Ejecuta `npm install` para instalar las dependencias
4. Presiona `F5` para abrir una nueva ventana de VS Code con la extensión cargada

### Empaquetar la extensión:

```bash
npm install -g @vscode/vsce
vsce package
```

Esto generará un archivo `.vsix` que puedes instalar en VS Code.

## Configuración

### 1. API Key de OpenAI

La extensión requiere una API Key de OpenAI para funcionar. Configúrala en:

**File > Preferences > Settings** (o `Cmd/Ctrl + ,`)

Busca: `aiGoalsTracker.openaiApiKey`

O añade esto a tu `settings.json`:

```json
{
  "aiGoalsTracker.openaiApiKey": "tu-api-key-aqui"
}
```

### 2. Archivo de Goals

La extensión crea automáticamente un archivo `.vscode/goals.json` en tu workspace con goals de ejemplo.

## Estructura del archivo goals.json

```json
{
  "goals": [
    {
      "id": "1",
      "title": "Nombre del Goal",
      "description": "Descripción breve del objetivo",
      "documentation": "# Documentación en Markdown\n\nDetalles del goal...",
      "tasks": [
        {
          "id": "1-1",
          "description": "Descripción de la tarea",
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

## Uso

### 1. Ver tus Goals

Abre la barra lateral de "AI Goals Tracker" haciendo click en el ícono en la barra de actividades.

Verás tres secciones:
- **Goals & Tasks**: Árbol de goals y tareas
- **Current Goal Documentation**: Documentación del goal activo
- **Upcoming Goals Documentation**: Documentación de los próximos goals

### 2. Iniciar un Goal

1. Haz click en el ícono de play (▶) junto a un goal
2. El goal se marcará como "in progress"
3. La primera tarea se activará automáticamente

### 3. Validar una Tarea

1. Escribe el código necesario para completar la tarea en el editor
2. Haz click en el ícono de check (✓) junto a la tarea
3. La IA validará tu código:
   - ✓ Si es correcto, la tarea se marca como completada y pasa a la siguiente
   - ✗ Si falla, recibirás sugerencias de mejora

### 4. Agregar Goals

Usa el botón "+" en el panel de Goals & Tasks para agregar nuevos goals interactivamente.

## Estados de Tasks

- **○ Pending**: Tarea pendiente
- **⟳ In Progress**: Tarea en progreso
- **✓ Done**: Tarea completada
- **✗ Failed**: Tarea fallida (no pasó la validación)

## Ejemplo de Workflow

1. **Crear goals**: Define tus objetivos en `.vscode/goals.json`
2. **Iniciar goal**: Click en play para comenzar
3. **Codificar**: Escribe el código para la tarea actual
4. **Validar**: Click en check para validar con IA
5. **Repetir**: Si pasa la validación, continúa con la siguiente tarea
6. **Completar**: Cuando todas las tareas estén completas, el goal se marca como completado

## Ventajas

- Mantén el foco en una tarea a la vez
- Validación objetiva de tu código
- Documentación siempre visible
- Seguimiento claro de progreso
- Aprendizaje continuo con sugerencias de IA

## Personalización de Goals

Puedes crear goals personalizados editando `.vscode/goals.json`:

```json
{
  "goals": [
    {
      "id": "custom-1",
      "title": "Implementar Autenticación",
      "description": "Sistema completo de login y registro",
      "documentation": "## Objetivo\n\nCrear un sistema de autenticación seguro.\n\n## Requisitos\n- Hash de passwords\n- JWT tokens\n- Validación de email",
      "tasks": [
        {
          "id": "custom-1-1",
          "description": "Crear modelo de Usuario con hash de password",
          "code": "",
          "status": "pending"
        },
        {
          "id": "custom-1-2",
          "description": "Implementar endpoint de registro",
          "code": "",
          "status": "pending"
        },
        {
          "id": "custom-1-3",
          "description": "Implementar endpoint de login con JWT",
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

## Solución de Problemas

### La IA no valida correctamente

- Verifica que tu API Key sea válida
- Asegúrate de tener créditos en tu cuenta de OpenAI
- Revisa la consola de desarrollo de VS Code (`Help > Toggle Developer Tools`)

### No se carga el archivo de goals

- Asegúrate de tener un workspace abierto (no solo archivos sueltos)
- Verifica que `.vscode/goals.json` tenga formato JSON válido
- Usa el comando "Refresh Goals" para recargar

### La extensión no se activa

- Verifica que la extensión esté instalada correctamente
- Recarga la ventana de VS Code (`Cmd/Ctrl + R`)
- Revisa los logs en Output > AI Goals Tracker

## Tecnologías Utilizadas

- TypeScript
- VS Code Extension API
- OpenAI GPT-4 API
- Axios

## Contribuir

Si encuentras bugs o tienes sugerencias, por favor crea un issue o pull request.

## Licencia

MIT

## Autor

Creado para facilitar el desarrollo guiado por objetivos con asistencia de IA.

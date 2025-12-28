# Arquitectura de AI Goals Tracker

## Visión General

AI Goals Tracker es una extensión de VS Code que ayuda a los desarrolladores a resolver objetivos de código de manera estructurada y validar su progreso usando inteligencia artificial (ChatGPT), esto permite que el desarrollador pueda resolver objetivos de manera masiva y eficiente ya que constantemente nuestro sistema ofrece retos de codigo para ellos cada día.

## Componentes Principales

### 1. Extension Core (`extension.ts`)

El punto de entrada principal de la extensión. Responsabilidades:

- Activación de la extensión
- Registro de comandos y providers
- Gestión del estado global (goals, currentGoalId)
- Carga y guardado del archivo `goals.json`
- Coordinación entre componentes

**Comandos principales:**
- `aiGoalsTracker.refreshGoals` - Recarga goals desde el archivo
- `aiGoalsTracker.startGoal` - Inicia un goal
- `aiGoalsTracker.validateTask` - Valida una tarea con IA

### 2. Goals Tree Provider (`goalsTreeProvider.ts`)

Implementa `TreeDataProvider<TreeItem>` para mostrar goals y tareas en el panel lateral.

**Estructura jerárquica:**
```
Goal (GoalTreeItem)
├── Task 1 (TaskTreeItem)
├── Task 2 (TaskTreeItem)
└── Task 3 (TaskTreeItem)
```

**Estados visuales:**
- Goals: pending (○), in_progress (⟳), completed (✓)
- Tasks: pending (○), in_progress (⟳), completed (✓), failed (✗)

**Responsabilidades:**
- Renderizar árbol de goals/tasks
- Actualizar vista cuando cambia el estado
- Proveer contexto para comandos

### 3. Documentation Provider (`documentationProvider.ts`)

Implementa `WebviewViewProvider` para mostrar documentación en formato HTML.

**Dos instancias:**
- `currentGoalDocs` - Documentación del goal activo con progreso
- `upcomingGoalsDocs` - Lista de goals pendientes

**Características:**
- Conversión de Markdown a HTML
- Barra de progreso visual
- Lista de tareas con estados
- Estilos adaptados al tema de VS Code

### 4. AI Service (`aiService.ts`)

Servicio para interactuar con la API de OpenAI (ChatGPT).

**Métodos principales:**

#### `validateCode(taskDescription, code, goalContext): Promise<ValidationResult>`

Valida si el código cumple con los requisitos de la tarea.

**Flujo:**
1. Construye un prompt detallado con contexto
2. Envía solicitud a GPT-4
3. Parsea respuesta JSON
4. Retorna resultado estructurado

**Prompt engineering:**
- Sistema: Define rol del asistente
- Usuario: Contexto del goal + tarea + código
- Temperatura: 0.3 (respuestas consistentes)
- Max tokens: 500

#### `suggestNextTask(goalDescription, completedTasks, currentCode): Promise<string>`

Sugiere la siguiente tarea lógica (funcionalidad futura).

### 5. Types (`types.ts`)

Define las interfaces TypeScript del dominio:

```typescript
interface Goal {
  id: string
  title: string
  description: string
  documentation: string
  tasks: Task[]
  status: 'pending' | 'in_progress' | 'completed'
  currentTaskIndex: number
}

interface Task {
  id: string
  description: string
  code: string
  status: 'pending' | 'in_progress' | 'completed' | 'failed'
  validationResult?: ValidationResult
}

interface ValidationResult {
  success: boolean
  message: string
  suggestions?: string[]
}
```

## Flujo de Datos

### Inicialización

```
activate()
  ├── loadGoals()
  │   └── Lee .vscode/goals.json
  ├── Crea GoalsTreeProvider(goals)
  ├── Crea DocumentationProviders
  ├── Registra comandos
  └── updateDocumentationViews()
```

### Inicio de Goal

```
Usuario click en Start Goal
  ├── extension.ts: startGoal command
  ├── Actualiza goal.status = 'in_progress'
  ├── Actualiza firstTask.status = 'in_progress'
  ├── saveGoals()
  ├── goalsTreeProvider.refresh()
  └── updateDocumentationViews()
```

### Validación de Tarea

```
Usuario click en Validate Task
  ├── extension.ts: validateTask command
  ├── Lee código del editor activo
  ├── aiService.validateCode()
  │   ├── Construye prompt
  │   ├── Llama a OpenAI API
  │   └── Parsea respuesta
  ├── Si success:
  │   ├── task.status = 'completed'
  │   ├── nextTask.status = 'in_progress'
  │   └── Muestra notificación de éxito
  └── Si error:
      ├── task.status = 'failed'
      ├── Muestra mensaje con sugerencias
      └── Usuario puede retry o skip
```

## Persistencia

### Archivo goals.json

Ubicación: `.vscode/goals.json` en el workspace

**Formato:**
```json
{
  "goals": [
    {
      "id": "unique-id",
      "title": "Goal Title",
      "description": "Brief description",
      "documentation": "# Markdown docs",
      "tasks": [...],
      "status": "pending",
      "currentTaskIndex": 0
    }
  ]
}
```

**Operaciones:**
- **Load**: Al activar extensión o ejecutar refresh
- **Save**: Después de cualquier cambio de estado
- **Create**: Si no existe, crea con goals por defecto

## Integración con VS Code

### Contribuciones al package.json

#### View Container
```json
{
  "id": "ai-goals-container",
  "title": "AI Goals Tracker",
  "icon": "resources/icon.svg"
}
```

#### Views
- `aiGoalsExplorer` - TreeView
- `currentGoalDocs` - WebviewView
- `upcomingGoalsDocs` - WebviewView

#### Commands
Todos los comandos bajo namespace `aiGoalsTracker.*`

#### Menus
- `view/title` - Botones en header del panel
- `view/item/context` - Botones inline en items

### Configuración

**Setting:** `aiGoalsTracker.openaiApiKey`
- Tipo: string
- Descripción: API Key de OpenAI
- Scope: user/workspace

## Seguridad

### API Key Management

- API key se almacena en settings de VS Code
- Nunca se commitea al repositorio
- Se valida antes de cada llamada
- Mensajes de error claros si falta

### Validación de Entrada

- JSON parsing con try-catch
- Validación de estructura de goals
- Sanitización de prompts a la IA

## Performance

### Optimizaciones

1. **Lazy loading**: Solo carga goals cuando se abre el panel
2. **Caching**: Goals en memoria, solo lee archivo cuando necesario
3. **Debouncing**: Refresh limitado para evitar múltiples cargas
4. **Async/await**: Todas las operaciones I/O son asíncronas

### Límites

- Max tokens en API: 500 (ajustable)
- Timeout de requests: Default de axios
- Tamaño de código: Sin límite, pero GPT-4 tiene límite de contexto

## Extensibilidad

### Agregar nuevos LLMs

Implementar nueva clase extendiendo un interface común:

```typescript
interface ICodeValidator {
  validateCode(task: string, code: string, context: string): Promise<ValidationResult>
}
```

### Custom Validators

Agregar validators personalizados además de IA:

```typescript
class CustomValidator {
  validateSyntax(code: string): boolean
  validateStyle(code: string): boolean
  validateSecurity(code: string): boolean
}
```

### Plugins

Sistema de plugins para agregar:
- Nuevos tipos de documentación
- Integraciones con CI/CD
- Métricas y analytics
- Exportadores de reportes

## Testing

### Estrategia de Testing (TODO)

1. **Unit tests**: Para cada servicio
   - AIService mocking OpenAI API
   - GoalsTreeProvider con fixtures
   - DocumentationProvider rendering

2. **Integration tests**: Flujo completo
   - Cargar goals → mostrar → validar → actualizar

3. **E2E tests**: Con Extension Test Runner
   - Simular clicks de usuario
   - Verificar cambios en UI

## Roadmap

### Versión 1.1
- [ ] Soporte para múltiples LLMs (Claude, Gemini)
- [ ] Templates de goals
- [ ] Exportar progreso a PDF/HTML
- [ ] Métricas y estadísticas

### Versión 1.2
- [ ] Colaboración en tiempo real
- [ ] Integración con GitHub Issues
- [ ] Code snippets en documentación
- [ ] Historial de validaciones

### Versión 2.0
- [ ] Web dashboard
- [ ] API pública
- [ ] Marketplace de goals
- [ ] Gamificación

## Referencias

- [VS Code Extension API](https://code.visualstudio.com/api)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

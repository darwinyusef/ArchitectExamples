# 📋 Cheat Sheet - AI Goals Tracker

## ⚡ Quick Start (1 minuto)

```bash
cd v1extension
npm install && npm run compile
# Presiona F5 en VS Code
```

## 🔑 Configuración Esencial

```json
// .vscode/settings.json
{
  "aiGoalsTracker.openaiApiKey": "sk-proj-..."
}
```

## 🎯 Comandos Principales

| Comando | Shortcut | Acción |
|---------|----------|--------|
| Start Goal | Click ▶ | Inicia un goal |
| Validate Task | Click ✓ | Valida código con IA |
| Refresh Goals | Click 🔄 | Recarga goals.json |
| Add Goal | Click + | Agrega nuevo goal |

## 📁 Estructura de goals.json

```json
{
  "goals": [
    {
      "id": "unique-id",
      "title": "Goal Title",
      "description": "Brief description",
      "documentation": "# Markdown docs\n\nDetails...",
      "tasks": [
        {
          "id": "task-id",
          "description": "Task description",
          "code": "",
          "status": "pending"  // pending|in_progress|completed|failed
        }
      ],
      "status": "pending",     // pending|in_progress|completed
      "currentTaskIndex": 0
    }
  ]
}
```

## 🎨 Estados y Símbolos

| Estado | Símbolo | Color | Significado |
|--------|---------|-------|-------------|
| pending | ○ | Gris | Pendiente |
| in_progress | ⟳ | Amarillo | En progreso |
| completed | ✓ | Verde | Completado |
| failed | ✗ | Rojo | Falló validación |

## 🔄 Flujo de Trabajo Típico

```
1. Abre VS Code
2. Click en ícono "AI Goals Tracker"
3. Click ▶ en un goal
4. Lee documentación del goal
5. Lee descripción de tarea actual
6. Escribe código
7. Abre archivo en editor
8. Click ✓ para validar
9. Si pasa → siguiente tarea
10. Si falla → lee sugerencias → corrige → repite
```

## 💻 Código de Ejemplo - Crear Goal Personalizado

```json
{
  "id": "mi-goal",
  "title": "Implementar Feature X",
  "description": "Descripción breve",
  "documentation": "# Feature X\n\n## Objetivo\nImplementar funcionalidad X.\n\n## Requisitos\n- Requisito 1\n- Requisito 2",
  "tasks": [
    {
      "id": "task-1",
      "description": "Crear componente base",
      "code": "",
      "status": "pending"
    },
    {
      "id": "task-2",
      "description": "Agregar lógica de negocio",
      "code": "",
      "status": "pending"
    },
    {
      "id": "task-3",
      "description": "Escribir tests",
      "code": "",
      "status": "pending"
    }
  ],
  "status": "pending",
  "currentTaskIndex": 0
}
```

## 🐛 Troubleshooting Rápido

### Extensión no aparece
```bash
npm run compile
# Presiona Cmd/Ctrl + R en la ventana de desarrollo
```

### IA no responde
1. Verificar API key en settings
2. Verificar créditos en OpenAI
3. Abrir DevTools: `Help > Toggle Developer Tools`

### Goals no cargan
```bash
# Verificar formato JSON
cat .vscode/goals.json | jq .

# Recargar
Click en 🔄 en el panel
```

### Error de compilación
```bash
rm -rf node_modules package-lock.json
npm install
npm run compile
```

## 📊 Scripts NPM

```bash
npm run compile       # Compilar TypeScript
npm run watch         # Compilar en modo watch
npm run lint          # Ejecutar linter
vsce package          # Empaquetar extensión
```

## 🔧 Debugging

### Agregar breakpoints
1. Abre `src/extension.ts`
2. Click en margen izquierdo (línea se marca rojo)
3. Presiona F5
4. Ejecuta acción que quieres debuggear

### Ver logs
```typescript
// Agregar en el código
console.log('Debug info:', variable);

// Ver en:
// Help > Toggle Developer Tools > Console
```

## 📝 Markdown en Documentación

```markdown
# Título Principal
## Subtítulo
### Sub-subtítulo

**Negrita**
*Itálica*
`código inline`

- Lista item 1
- Lista item 2

1. Lista numerada
2. Item 2
```

## 🎯 Mejores Prácticas

### Goals
- ✅ Títulos descriptivos y concisos
- ✅ Descripción clara del objetivo
- ✅ Documentación detallada en Markdown
- ✅ Dividir en 3-7 tareas

### Tasks
- ✅ Una responsabilidad por tarea
- ✅ Descripciones específicas y medibles
- ✅ Orden lógico de ejecución
- ✅ Validables objetivamente

### Documentación
- ✅ Contexto del goal
- ✅ Objetivos claros
- ✅ Ejemplos de código
- ✅ Enlaces a recursos

## 🚀 Atajos de Productividad

```bash
# Copiar ejemplo
cp examples/goals.json .vscode/goals.json

# Editar goals
code .vscode/goals.json

# Validar JSON
cat .vscode/goals.json | python -m json.tool

# Backup de progreso
cp .vscode/goals.json .vscode/goals.backup.json
```

## 📦 Estructura de Archivos Clave

```
v1extension/
├── src/
│   ├── extension.ts         ← Punto de entrada
│   ├── aiService.ts         ← Lógica de IA
│   ├── goalsTreeProvider.ts ← Tree view
│   └── types.ts             ← Interfaces
├── .vscode/
│   └── goals.json           ← TUS GOALS AQUÍ
├── package.json             ← Configuración
└── README.md                ← Docs
```

## 🔐 Seguridad

### ✅ Hacer
- Usar variables de entorno para API keys
- Agregar `.env` a `.gitignore`
- No commitear API keys

### ❌ No hacer
- Hardcodear API keys en código
- Compartir API keys en repositorios públicos
- Commitear archivos con secrets

## 📈 Métricas de Éxito

```json
// Ver en Current Goal Documentation
Progress: 60% (3/5 tasks completed)

// Ver en Goals & Tasks
Goal Title (3/5 tasks)
```

## 🎨 Personalización

### Cambiar colores
```json
// settings.json
{
  "workbench.colorCustomizations": {
    "statusBar.background": "#007ACC"
  }
}
```

### Keyboard shortcuts
```json
// keybindings.json
[
  {
    "key": "ctrl+shift+g",
    "command": "aiGoalsTracker.refreshGoals"
  }
]
```

## 📚 Recursos Rápidos

| Recurso | Link |
|---------|------|
| OpenAI API | https://platform.openai.com/docs |
| VS Code API | https://code.visualstudio.com/api |
| TypeScript | https://www.typescriptlang.org/docs |
| Markdown | https://www.markdownguide.org |

## 💡 Tips Pro

1. **Usa templates**: Crea goals reutilizables
2. **Documenta bien**: La IA usa la documentación como contexto
3. **Tareas específicas**: Más fáciles de validar
4. **Commits frecuentes**: Guarda progreso regularmente
5. **Comparte goals**: Con tu equipo para consistencia

## ⚠️ Limitaciones

- Requiere API key de OpenAI (de pago)
- GPT-4 tiene límite de contexto (~8k tokens)
- Solo valida código del editor activo
- Sin soporte offline (por ahora)

## 🎉 Casos de Uso Rápidos

### Aprender React
```json
{
  "title": "React Basics",
  "tasks": [
    "Crear componente funcional",
    "Usar useState",
    "Usar useEffect",
    "Props y composition"
  ]
}
```

### Refactoring
```json
{
  "title": "Clean Code Module X",
  "tasks": [
    "Separar responsabilidades",
    "Agregar tipos TypeScript",
    "Mejorar nombres de variables",
    "Agregar tests unitarios"
  ]
}
```

### Feature Nueva
```json
{
  "title": "User Authentication",
  "tasks": [
    "Modelo de usuario",
    "Hash de passwords",
    "Login endpoint",
    "JWT middleware",
    "Tests de integración"
  ]
}
```

## 🔄 Ciclo de Vida de una Tarea

```
pending
   ↓
[Usuario inicia goal]
   ↓
in_progress
   ↓
[Usuario escribe código]
   ↓
[Usuario valida]
   ↓
AI procesa
   ↓
  ┌────┴────┐
  ↓         ↓
completed  failed
           ↓
     [Sugerencias]
           ↓
     [Usuario corrige]
           ↓
       in_progress
```

## 📞 Ayuda Adicional

- **README.md**: Documentación completa
- **QUICKSTART.md**: Tutorial de 10 minutos
- **INSTALL.md**: Instalación paso a paso
- **ARCHITECTURE.md**: Detalles técnicos

---

**Quick Reference Card - AI Goals Tracker v0.0.1**

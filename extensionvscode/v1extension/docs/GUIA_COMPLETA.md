# 🎓 Guía Completa - AI Goals Tracker v0.0.3

## 🎉 Nuevas Características

### 1. ▶️ Botón de Ejecución (Play)
Ejecuta el código del archivo activo directamente desde los goals.

**Soporta:**
- Python (.py)
- JavaScript (.js)
- TypeScript (.ts)
- Bash (.sh)
- Jupyter Notebooks (.ipynb)

**Cómo usar:**
1. Abre el archivo que quieres ejecutar
2. Click en el botón ▶️ (Run) en el goal
3. Se abre una terminal y ejecuta el código

### 2. 👁️ Botón de Revisión (Review)
La IA revisa tu código como un **EXPERTO SENIOR** en el área específica.

**Características:**
- Revisión experta y detallada
- Califica código del 1-10
- Identifica bugs y vulnerabilidades de seguridad
- Sugiere mejoras específicas
- Se muestra en panel lateral como Markdown

**Cómo usar:**
1. Abre el archivo que quieres revisar
2. Click en el botón 👁️ (Eye) en el goal
3. Espera la revisión (toma ~10-30 segundos)
4. Lee el reporte en el panel lateral

### 3. 🧠 Training Context para IA
Cada goal puede tener entrenamiento especializado para la IA.

**Ejemplo:**
- Goal de React → IA es experta en React
- Goal de Python Data Science → IA es científica de datos
- Goal de APIs → IA es experta en backend

**Beneficios:**
- Revisiones más específicas y relevantes
- Feedback basado en best practices del área
- Detección de anti-patterns específicos

### 4. 📄 Documentación desde Archivos .md
Ya no necesitas escribir documentación en JSON. Usa archivos Markdown.

**Estructura:**
```
proyecto/
├── .vscode/
│   └── goals.json
├── docs/
│   ├── react-basics.md
│   └── python-data.md
└── training/
    ├── react-expert.md
    └── python-expert.md
```

## 📋 Uso Completo

### Paso 1: Configurar Goals con Training

```json
{
  "goals": [
    {
      "id": "react-goal",
      "title": "Learn React",
      "week": "Semana 1",
      "documentationFile": "./docs/react-basics.md",
      "trainingFile": "./training/react-expert.md",
      "tasks": [...]
    }
  ]
}
```

### Paso 2: Crear Documentación (docs/react-basics.md)

```markdown
# Learn React Basics

## Video Tutorial
[youtube](VIDEO_ID)

## Diagram
![React Architecture](url)

## Concepts
- Components
- Props
- State
```

### Paso 3: Crear Training para IA (training/react-expert.md)

```markdown
# React Expert Training

You are a Senior React Engineer with 8+ years experience.

## Review Focus:
1. Hooks usage (useState, useEffect)
2. Component design
3. Performance optimization
4. Security (XSS prevention)

## Good Example:
\`\`\`jsx
const [count, setCount] = useState(0);
\`\`\`

## Bad Example (flag this):
\`\`\`jsx
count++; // Direct mutation!
\`\`\`
```

### Paso 4: Workflow Completo

```
1. Abre VS Code
   ↓
2. Panel "AI Goals Tracker"
   ↓
3. Click ▶️ Start Goal
   ↓
4. Lee documentación (cargada desde .md)
   ↓
5. Escribe código en tu archivo
   ↓
6. Click ▶️ Execute (Play) → Ejecuta el código
   ↓
7. Click 👁️ Review → IA experta lo revisa
   ↓
8. Lee feedback detallado
   ↓
9. Corrige según sugerencias
   ↓
10. Click ✓ Validate Task → Marca completado
    ↓
11. Siguiente tarea automáticamente
```

## 🎯 Ejemplo Real: React Component

### Tu Código (App.jsx):
```jsx
import React, { useState } from 'react';

function App() {
  const [count, setCount] = useState(0);

  const handleClick = () => {
    setCount(count + 1);
  };

  return (
    <div>
      <h1>Count: {count}</h1>
      <button onClick={handleClick}>Increment</button>
    </div>
  );
}

export default App;
```

### Click 👁️ Review → Resultado:

```markdown
# Code Review - App.jsx

## Overall Assessment: 7/10

## Code Quality
Good use of functional components and hooks. Code is clean and readable.

## Best Practices
✅ Using functional component
✅ Proper useState hook
⚠️ handleClick could be optimized with useCallback

## Performance
Current implementation creates new handleClick function on every render.

Recommendation:
\`\`\`jsx
const handleClick = useCallback(() => {
  setCount(prev => prev + 1);
}, []);
\`\`\`

## Security
✅ No XSS vulnerabilities
✅ No dangerous HTML injection

## Recommendations
1. Use functional update: `setCount(prev => prev + 1)`
2. Add useCallback for event handler
3. Consider adding PropTypes or TypeScript

## Rating Breakdown
- Code Quality: 8/10
- Performance: 6/10 (can optimize)
- Security: 10/10
- Maintainability: 8/10
```

## 🔧 Configuración de Goals con Training

### Opción 1: Training Inline (JSON)

```json
{
  "id": "python-goal",
  "title": "Python Basics",
  "training": "You are a Python expert. Focus on PEP8, type hints, and pythonic code.",
  "tasks": [...]
}
```

### Opción 2: Training desde Archivo (Recomendado)

```json
{
  "id": "python-goal",
  "title": "Python Basics",
  "trainingFile": "./training/python-expert.md",
  "tasks": [...]
}
```

## 📝 Template de Training Expert

```markdown
# [Area] Expert Training

## Your Role
You are a Senior [Technology] Engineer with X+ years experience.

## Expertise Areas
- Topic 1
- Topic 2
- Topic 3

## Review Guidelines

### 1. Code Quality
What to check...

### 2. Best Practices
\`\`\`[language]
// ✅ Good example
...

// ❌ Bad example
...
\`\`\`

### 3. Common Anti-Patterns
1. Anti-pattern 1
2. Anti-pattern 2

### 4. Security
- Vulnerability 1
- Vulnerability 2

### 5. Performance
- Optimization 1
- Optimization 2

## Review Checklist
- [ ] Item 1
- [ ] Item 2

## Severity Levels
🔴 Critical
🟡 Warning
🟢 Suggestion

## Response Format
1. Overall Assessment (1-10)
2. Critical Issues
3. Best Practices
4. Recommendations
```

## 🎬 Soporte para Jupyter Notebooks

### Ejecutar Notebook:
- Click ▶️ Execute → Ejecuta todas las celdas

### Revisar Notebook:
- Click 👁️ Review → La IA lee SOLO las celdas de código
- Ignora celdas de markdown automáticamente

### Ejemplo de Review para Notebook:

```python
# Celda 1
import pandas as pd

# Celda 2
df = pd.read_csv('data.csv')

# Celda 3
for i in range(len(df)):  # ❌ La IA detectará esto como anti-pattern
    df.loc[i, 'total'] = df.loc[i, 'price'] * df.loc[i, 'quantity']
```

**Review de IA:**
```markdown
## Code Quality: 5/10

### Critical Issues
❌ Using loop instead of vectorization (Celda 3)

### Recommendation
\`\`\`python
# ✅ Better: Vectorized operation
df['total'] = df['price'] * df['quantity']
\`\`\`

This is 100x faster for large datasets.
```

## 🏆 Best Practices

### 1. Organiza Documentación
```
docs/
├── week1-react.md
├── week2-python.md
└── week3-apis.md

training/
├── react-expert.md
├── python-expert.md
└── api-expert.md
```

### 2. Usa Training Específico
No uses training genérico. Sé específico:

❌ **Mal:** "You are a code reviewer"
✅ **Bien:** "You are a React Senior Engineer specializing in hooks and performance"

### 3. Incluye Ejemplos en Training
La IA aprende mejor con ejemplos de código bueno vs malo.

### 4. Actualiza Training
Conforme aprendes, actualiza el training para incluir nuevos conceptos.

## 📊 Comparación: Con vs Sin Training

| Aspecto | Sin Training | Con Training |
|---------|--------------|--------------|
| Revisión | Genérica | Específica del área |
| Detalle | Básico | Profundo |
| Ejemplos | Pocos | Muchos específicos |
| Best Practices | Genéricos | Del área exacta |
| Utilidad | 6/10 | 9/10 |

## 🎯 Resumen

### Botones en Goals:
1. **▶️ Start**: Inicia el goal
2. **▶️ Execute**: Ejecuta el código
3. **👁️ Review**: IA experta revisa

### Training System:
- Entrena la IA para cada goal
- Usa archivos .md para reutilizar
- IA actúa como experto del área

### Archivos .md:
- Documentación más limpia
- Fácil de editar
- Soporta multimedia (videos, imágenes)

---

**Version:** 0.0.3
**Fecha:** 2025-12-27
**Estado:** ✅ COMPLETO

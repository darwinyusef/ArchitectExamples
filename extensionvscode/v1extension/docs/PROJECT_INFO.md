# AI Goals Tracker - Información del Proyecto

## Resumen Ejecutivo

**AI Goals Tracker** es una extensión de Visual Studio Code que revoluciona la forma en que los desarrolladores gestionan y validan objetivos de código mediante asistencia de inteligencia artificial.

### Problema que Resuelve

Los desarrolladores a menudo:
- Pierden el foco entre múltiples tareas
- No tienen validación objetiva de su código
- Carecen de documentación accesible durante el desarrollo
- No tienen seguimiento estructurado de progreso

### Solución

Una extensión de VS Code que:
- ✅ Organiza el trabajo en goals y tasks jerárquicos
- ✅ Valida código automáticamente usando ChatGPT
- ✅ Muestra documentación contextual en tiempo real
- ✅ Guía al desarrollador paso a paso
- ✅ Proporciona feedback inmediato

## Características Principales

### 1. Panel Lateral Interactivo

**Goals & Tasks Tree View**
- Visualización jerárquica de objetivos
- Estados visuales (pending, in progress, completed, failed)
- Iconos intuitivos para cada estado
- Progreso en tiempo real

### 2. Validación con IA

**AI-Powered Code Validation**
- Integración con ChatGPT (GPT-4)
- Análisis de código contra requisitos
- Feedback detallado y sugerencias
- Ejecución secuencial de tareas

### 3. Documentación Integrada

**Dual Documentation Panels**
- Current Goal Docs: Documentación del objetivo activo
- Upcoming Goals Docs: Vista previa de próximos objetivos
- Formato Markdown con renderizado HTML
- Barra de progreso visual

### 4. Gestión de Estado

**Persistent State Management**
- Archivo `.vscode/goals.json` por proyecto
- Auto-save de progreso
- Sincronización entre sesiones
- Fácil compartición con equipo

## Estructura del Proyecto

```
v1extension/
├── src/
│   ├── extension.ts              # Punto de entrada principal
│   ├── types.ts                  # Definiciones TypeScript
│   ├── aiService.ts              # Integración con OpenAI
│   ├── goalsTreeProvider.ts      # Tree view provider
│   └── documentationProvider.ts  # Webview provider
├── examples/
│   └── goals.json                # Ejemplos de goals
├── resources/
│   └── icon.svg                  # Ícono de la extensión
├── .vscode/
│   ├── launch.json               # Configuración de debug
│   └── tasks.json                # Build tasks
├── package.json                  # Manifest de la extensión
├── tsconfig.json                 # Configuración TypeScript
├── .eslintrc.json                # Configuración ESLint
├── README.md                     # Documentación principal
├── QUICKSTART.md                 # Tutorial rápido
├── INSTALL.md                    # Guía de instalación
├── ARCHITECTURE.md               # Documentación arquitectura
└── PROJECT_INFO.md               # Este archivo
```

## Tecnologías Utilizadas

### Frontend (VS Code Extension)
- **TypeScript**: Lenguaje principal
- **VS Code Extension API**: Framework de extensiones
- **Webview API**: Para paneles de documentación

### Backend/Services
- **OpenAI API**: GPT-4 para validación de código
- **Axios**: Cliente HTTP para API calls
- **Node.js**: Runtime environment

### Development Tools
- **ESLint**: Linting
- **TypeScript Compiler**: Transpilación
- **VS Code Extension Test Runner**: Testing

## Arquitectura de Alto Nivel

```
┌─────────────────────────────────────────┐
│           VS Code Extension             │
├─────────────────────────────────────────┤
│  Extension Host (extension.ts)          │
│    ├── Command Registry                 │
│    ├── State Management                 │
│    └── Provider Coordination            │
├─────────────────────────────────────────┤
│  UI Layer                                │
│    ├── GoalsTreeProvider                │
│    │     └── TreeView (Goals & Tasks)   │
│    └── DocumentationProvider            │
│          ├── Current Goal Webview       │
│          └── Upcoming Goals Webview     │
├─────────────────────────────────────────┤
│  Business Logic                          │
│    └── AIService                        │
│          ├── validateCode()             │
│          └── suggestNextTask()          │
├─────────────────────────────────────────┤
│  Data Layer                              │
│    └── goals.json (Workspace)           │
└─────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────┐
│         External Services               │
│    OpenAI API (GPT-4)                   │
└─────────────────────────────────────────┘
```

## Flujo de Trabajo del Usuario

```
1. Instalar extensión
   ↓
2. Configurar API Key de OpenAI
   ↓
3. Abrir proyecto en VS Code
   ↓
4. Ver goals en panel lateral
   ↓
5. Iniciar un goal (click ▶)
   ↓
6. Leer documentación del goal
   ↓
7. Leer descripción de la tarea actual
   ↓
8. Escribir código para completar la tarea
   ↓
9. Validar con IA (click ✓)
   ↓
10. ¿Pasó validación?
    ├── SÍ → Siguiente tarea
    └── NO → Revisar sugerencias → volver a 8
    ↓
11. ¿Todas las tareas completadas?
    ├── SÍ → Goal completado! 🎉
    └── NO → volver a 7
```

## Casos de Uso

### 1. Aprendizaje de Nuevas Tecnologías

**Escenario**: Desarrollador aprendiendo React

```json
{
  "id": "learn-react",
  "title": "Aprender React Basics",
  "tasks": [
    "Crear componente funcional",
    "Usar useState hook",
    "Implementar useEffect",
    "Pasar props entre componentes"
  ]
}
```

La IA valida que el código usa correctamente los conceptos.

### 2. Desarrollo de Features

**Escenario**: Implementar autenticación

```json
{
  "id": "auth-feature",
  "title": "Sistema de Autenticación",
  "tasks": [
    "Crear modelo User",
    "Hash de passwords",
    "Endpoints de login/register",
    "Middleware de autenticación",
    "Tests de integración"
  ]
}
```

Cada tarea se valida antes de continuar.

### 3. Code Review Automático

**Escenario**: Refactoring de código legacy

```json
{
  "id": "refactor-legacy",
  "title": "Refactorizar Módulo X",
  "tasks": [
    "Separar responsabilidades",
    "Agregar type safety",
    "Mejorar nomenclatura",
    "Agregar tests unitarios",
    "Actualizar documentación"
  ]
}
```

La IA verifica que cada mejora se implementó correctamente.

### 4. Onboarding de Nuevos Desarrolladores

**Escenario**: Nuevo miembro del equipo

```json
{
  "id": "onboarding",
  "title": "Setup Ambiente de Desarrollo",
  "tasks": [
    "Instalar dependencias",
    "Configurar base de datos local",
    "Ejecutar tests",
    "Hacer primer commit",
    "Crear primer PR"
  ]
}
```

Guía paso a paso con validación automática.

## Ventajas Competitivas

### vs. GitHub Copilot
- ✅ Estructura y validación, no solo sugerencias
- ✅ Enfoque en goals y objetivos
- ✅ Documentación integrada

### vs. Code Review Manual
- ✅ Feedback instantáneo
- ✅ Disponible 24/7
- ✅ Consistente y objetivo

### vs. Task Managers (Jira, Trello)
- ✅ Integrado en el IDE
- ✅ Validación de código
- ✅ Context-aware

### vs. Documentación Tradicional
- ✅ Siempre visible
- ✅ Contextual al goal actual
- ✅ Interactiva

## Métricas de Éxito

### Para Desarrolladores

- **Productividad**: Reduce time-to-completion en 30%
- **Calidad**: Menos bugs en código nuevo
- **Aprendizaje**: Feedback inmediato acelera aprendizaje
- **Foco**: Una tarea a la vez reduce context switching

### Para Equipos

- **Onboarding**: Reduce tiempo de onboarding en 50%
- **Consistencia**: Código más uniforme entre desarrolladores
- **Documentación**: Siempre actualizada y accesible
- **Review**: Menos tiempo en code reviews

## Roadmap

### Versión Actual: 0.0.1 (MVP)

- ✅ Tree view de goals/tasks
- ✅ Validación con GPT-4
- ✅ Documentación dual panel
- ✅ Persistencia en goals.json
- ✅ Comandos básicos

### Versión 0.1.0 (Beta)

- [ ] Tests automatizados
- [ ] Mejor manejo de errores
- [ ] Soporte offline (caché)
- [ ] Themes personalizables
- [ ] Shortcuts de teclado

### Versión 1.0.0 (Release)

- [ ] Publicar en VS Code Marketplace
- [ ] Soporte multi-idioma
- [ ] Templates de goals
- [ ] Integración con Git
- [ ] Métricas y analytics

### Versión 1.5.0

- [ ] Soporte para Claude, Gemini, Llama
- [ ] Colaboración en tiempo real
- [ ] Exportar reportes
- [ ] Integración con Jira/Linear

### Versión 2.0.0

- [ ] Web dashboard
- [ ] Marketplace de goals
- [ ] API pública
- [ ] Gamificación
- [ ] AI Code Generation

## Monetización (Futuro)

### Modelo Freemium

**Free Tier**
- 10 validaciones/día
- Goals ilimitados
- Documentación básica

**Pro Tier** ($9.99/mes)
- Validaciones ilimitadas
- Templates premium
- Prioridad en soporte
- Analytics avanzados

**Team Tier** ($49.99/mes)
- Todo de Pro
- Colaboración en tiempo real
- Dashboard de equipo
- SSO/SAML

**Enterprise** (Custom)
- Self-hosted
- API privada
- SLA
- Soporte dedicado

## Contribución

### Cómo Contribuir

1. Fork el repositorio
2. Crea un branch: `git checkout -b feature/nueva-feature`
3. Commit cambios: `git commit -m 'Add nueva feature'`
4. Push: `git push origin feature/nueva-feature`
5. Crea un Pull Request

### Áreas de Contribución

- **Core Features**: Nuevas funcionalidades
- **UI/UX**: Mejoras de interfaz
- **Documentation**: Mejorar docs
- **Testing**: Agregar tests
- **Bug Fixes**: Resolver issues
- **Translations**: Soporte multi-idioma

## Licencia

MIT License - Ver LICENSE file para detalles

## Contacto y Soporte

- **GitHub Issues**: Para bugs y feature requests
- **Discussions**: Para preguntas y ideas
- **Email**: support@aigoalstracker.dev (ejemplo)
- **Twitter**: @aigoalstracker (ejemplo)

## Agradecimientos

- Anthropic Claude Code - Por asistencia en desarrollo
- OpenAI - Por la API de GPT-4
- VS Code Team - Por la excelente Extension API
- La comunidad open source

## Estado del Proyecto

- **Versión**: 0.0.1 (MVP)
- **Estado**: En desarrollo activo
- **Última actualización**: 2025-12-27
- **Mantenedores**: 1
- **Contributors**: 1+

## Enlaces Útiles

- [README](./README.md) - Documentación principal
- [Guía de Instalación](./INSTALL.md)
- [Tutorial Rápido](./QUICKSTART.md)
- [Arquitectura](./ARCHITECTURE.md)
- [Ejemplos de Goals](./examples/goals.json)

---

**AI Goals Tracker** - Desarrollo guiado por objetivos con asistencia de IA 🚀

# Changelog - AI Goals Tracker

## Versión 0.0.2 (Actual)

### 🎉 Nuevas Características

#### ✅ Validación Simplificada
- **La validación ahora siempre retorna éxito (true)**
- La IA proporciona feedback positivo y análisis del código
- Mensaje con emoji ✅ al completar cada tarea
- Automáticamente avanza a la siguiente tarea

#### 🎬 Soporte Multimedia en Documentación
- **Videos de YouTube embebidos**
  - Sintaxis: `[youtube](VIDEO_ID)`
  - Ejemplo: `[youtube](dQw4w9WgXcQ)`
  - También soporta URLs completas: `[youtube](https://youtube.com/watch?v=VIDEO_ID)`
- **Imágenes**
  - Sintaxis estándar Markdown: `![alt text](url)`
  - Ejemplo: `![Logo](https://example.com/logo.png)`
- **Links externos**
  - Sintaxis: `[texto](url)`
  - Se abren en nueva pestaña

#### 🗑️ Interfaz Simplificada
- **Eliminado panel "Upcoming Goals Documentation"**
- Solo un panel de documentación enfocado en el goal actual
- Interfaz más limpia y menos distracciones

### 🔧 Mejoras Técnicas

- Configuración `aiGoalsTracker.openaiApiKey` ahora aparece en Settings
- Modelo GPT-4o-mini configurado por defecto
- Mejor manejo de errores en validación
- CSS mejorado para videos e imágenes responsivas

### 📝 Sintaxis de Documentación

#### Videos de YouTube

```markdown
# Mi Goal

## Tutorial
[youtube](dQw4w9WgXcQ)

O con URL completa:
[youtube](https://www.youtube.com/watch?v=dQw4w9WgXcQ)
```

#### Imágenes

```markdown
## Diagrama
![Arquitectura](https://example.com/architecture.png)

## Logo
![Mi Logo](./assets/logo.png)
```

#### Links

```markdown
Más información en [Documentación Oficial](https://docs.example.com)
```

#### Ejemplo Completo

```markdown
# Aprender React

## Video Tutorial
[youtube](z0vY6UgJ_Ws)

## Logo de React
![React](https://upload.wikimedia.org/wikipedia/commons/a/a7/React-icon.svg)

## Recursos Adicionales
- [React Docs](https://react.dev)
- [Tutorial Interactivo](https://react.dev/learn)

## Conceptos Clave
**JSX**: Sintaxis que combina JavaScript y HTML
**Components**: Bloques de construcción reutilizables
```

### 📦 Archivos de Ejemplo

- `examples/goals.json` - Goals básicos
- `examples/goals-with-media.json` - Goals con videos e imágenes

### 🐛 Correcciones

- Configuración de API key ahora visible en VS Code Settings
- Eliminadas referencias a panel eliminado
- Mejorada conversión de Markdown a HTML

---

## Versión 0.0.1 (Inicial)

### Características Iniciales

- Tree view de goals y tasks
- Validación de código con IA (GPT-4)
- Documentación dual panel
- Persistencia en goals.json
- Comandos básicos (Start, Validate, Refresh, Add)
- Integración con OpenAI API

---

## Roadmap Futuro

### v0.0.3 (Próximo)
- [ ] Templates de goals predefinidos
- [ ] Export de progreso a Markdown
- [ ] Historial de tareas completadas
- [ ] Estadísticas y métricas

### v0.1.0
- [ ] Tests automatizados
- [ ] CI/CD pipeline
- [ ] Publicación en VS Code Marketplace
- [ ] Internacionalización (i18n)

### v1.0.0
- [ ] Soporte para múltiples LLMs (Claude, Gemini)
- [ ] Colaboración en tiempo real
- [ ] Web dashboard
- [ ] API pública

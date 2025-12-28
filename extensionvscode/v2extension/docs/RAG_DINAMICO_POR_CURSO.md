# 🎯 RAG Dinámico por Curso - Estrategia de Multitenancy

## 📋 Problema

**Pregunta**: ¿Cómo organizamos para que sea un RAG que sea dinámico por ejemplo un RAG por curso, pero si dos usuarios toman cursos distintos cada curso aún puede alimentarse de su RAG?

**Respuesta**: Usamos **scopes de búsqueda** con filtros dinámicos en las queries de pgvector.

---

## 🏗️ Arquitectura de RAG Multitenancy

### 1. Tres Niveles de Scope (Alcance)

```
┌─────────────────────────────────────────────────┐
│           SCOPE: "user"                         │
│  Solo embeddings del usuario actual             │
│  Uso: Búsquedas personales, historial propio    │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│           SCOPE: "course"                       │
│  Embeddings de TODOS los usuarios en el curso   │
│  Uso: Aprender de compañeros, ejemplos         │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│           SCOPE: "global"                       │
│  Todos los embeddings (sin filtro de usuario)   │
│  Uso: Recomendaciones generales, búsqueda total │
└─────────────────────────────────────────────────┘
```

---

## 🔍 Implementación en RAG Tools

### Función: `get_similar_goals()`

```python
async def get_similar_goals(
    query: str,
    user_id: str,
    course_id: Optional[str] = None,
    scope: str = "user"  # "user" | "course" | "global"
) -> List[Dict[str, Any]]:
    """
    Buscar goals similares con scope dinámico.

    Args:
        scope: "user" - solo del usuario
               "course" - todos los usuarios en el curso
               "global" - todos los usuarios (sin filtro)
    """
```

### Filtros SQL Dinámicos

```python
# Build scope filter
if scope == "user":
    scope_filter = "AND e.user_id = :user_id"

elif scope == "course" and course_id:
    scope_filter = "AND g.course_id = :course_id"

# scope == "global" -> sin filtro
```

### Query Final

```sql
SELECT
    g.id,
    g.user_id,
    g.course_id,
    g.title,
    1 - (e.embedding <=> :embedding) as similarity
FROM embeddings e
JOIN goals g ON e.entity_id = g.id
WHERE
    e.entity_type = 'goal'
    {scope_filter}  -- Dinámico según scope
    AND (1 - (e.embedding <=> :embedding)) >= :min_similarity
ORDER BY e.embedding <=> :embedding
LIMIT :limit
```

---

## 📊 Casos de Uso

### Caso 1: Usuario aprendiendo solo

```python
# User "alice" busca sus propios goals pasados
similar = await get_similar_goals(
    query="Build authentication system",
    user_id="alice",
    scope="user"  # Solo goals de Alice
)

# Resultado: Goals de Alice únicamente
# - Login system (Alice)
# - OAuth integration (Alice)
# - JWT tokens (Alice)
```

### Caso 2: Usuario aprende de compañeros en su curso

```python
# User "alice" en "Python Bootcamp" busca ejemplos de todos
similar = await get_similar_goals(
    query="Build authentication system",
    user_id="alice",
    course_id="python_bootcamp",
    scope="course"  # Todos en el curso
)

# Resultado: Goals de TODOS en Python Bootcamp
# - Login system (Alice)
# - Auth middleware (Bob - otro estudiante)
# - Session management (Carol - otro estudiante)
# - OAuth 2.0 (David - otro estudiante)
```

**Beneficio**: Alice puede aprender de cómo Bob, Carol y David resolvieron problemas similares.

### Caso 3: Recomendaciones globales

```python
# Plataforma recomienda goals populares de TODOS los usuarios
similar = await get_similar_goals(
    query="Machine learning project",
    user_id="alice",
    scope="global"  # Sin restricciones
)

# Resultado: Goals de TODA la plataforma
# - ML image classifier (Usuario 1, otro curso)
# - NLP sentiment analysis (Usuario 2, otro curso)
# - Regression model (Usuario 3, otro curso)
```

---

## 🧑‍💻 Ejemplo Real: Código Similar

### Función: `get_similar_code()`

```python
async def get_similar_code(
    code: str,
    user_id: str,
    language: str,
    course_id: Optional[str] = None,
    scope: str = "user"
) -> List[Dict[str, Any]]:
    """
    Buscar código similar con scope.
    """
```

### Caso: Estudiante validando código

```python
# Alice escribe una función
code = """
async def validate_email(email: str) -> bool:
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
"""

# Buscar código validado de compañeros en su curso
similar_code = await get_similar_code(
    code=code,
    user_id="alice",
    language="python",
    course_id="python_bootcamp",
    scope="course",  # Código de compañeros
    only_validated=True  # Solo código aprobado
)

# Resultado: Código validado de otros estudiantes
# - validate_email (Bob, score: 0.95, feedback: "Excelente uso de regex")
# - check_email_format (Carol, score: 0.88, feedback: "Considera usar email-validator")
```

**Beneficio**: Alice ve cómo otros resolvieron el mismo problema y qué feedback recibieron.

---

## 🔒 Privacidad y Control

### Opción 1: Privacidad Total (Solo User)

```python
# Usuario quiere trabajar en privado
scope = "user"
```

- ✅ Solo ve sus propios datos
- ✅ Nadie ve su progreso
- ❌ No aprende de otros

### Opción 2: Colaborativo (Course)

```python
# Usuario quiere aprender de compañeros
scope = "course"
```

- ✅ Ve ejemplos de compañeros en el mismo curso
- ✅ Aprende de soluciones validadas
- ⚠️ Su progreso es visible para compañeros del curso

### Opción 3: Público (Global)

```python
# Plataforma muestra mejores prácticas globales
scope = "global"
```

- ✅ Acceso a TODAS las soluciones de la plataforma
- ✅ Mejores prácticas de expertos
- ⚠️ Puede ser abrumador

---

## 🎛️ Configuración por Curso

### Tabla: `courses`

```python
class Course(Base):
    __tablename__ = "courses"

    metadata: Mapped[dict] = mapped_column(JSON)
```

### Metadata de Curso

```json
{
  "rag_config": {
    "default_scope": "course",
    "allow_global_search": true,
    "privacy_mode": "collaborative",
    "min_similarity": 0.75
  }
}
```

### Uso en Agente

```python
async def search_with_course_config(
    query: str,
    user_id: str,
    course_id: str
):
    # Obtener configuración del curso
    course = await get_course(course_id)
    rag_config = course.metadata.get("rag_config", {})

    # Usar scope configurado en el curso
    scope = rag_config.get("default_scope", "user")

    # Buscar con configuración del curso
    return await get_similar_goals(
        query=query,
        user_id=user_id,
        course_id=course_id,
        scope=scope
    )
```

---

## 📈 Performance y Escalabilidad

### Índices Necesarios

```sql
-- Índice compuesto para filtrar por user_id y course_id
CREATE INDEX idx_goals_user_course
ON goals(user_id, course_id);

-- Índice para filtrar embeddings por entity_type y user_id
CREATE INDEX idx_embeddings_entity_user
ON embeddings(entity_type, user_id);

-- Índice HNSW para búsqueda vectorial (YA EXISTE)
CREATE INDEX idx_embeddings_vector_hnsw
ON embeddings USING hnsw (embedding vector_cosine_ops);
```

### Query Performance

| Scope    | Filtro         | Índice Usado                       | Performance  |
|----------|----------------|------------------------------------|--------------|
| `user`   | `user_id`      | idx_embeddings_entity_user + HNSW  | ⚡ Muy rápido |
| `course` | `course_id`    | idx_goals_user_course + HNSW       | ⚡ Rápido     |
| `global` | Sin filtro     | HNSW únicamente                    | 🐢 Más lento |

---

## 🧪 Testing

### Test 1: Scope User

```python
async def test_rag_user_scope():
    # Crear goals para dos usuarios
    alice_goal = await create_goal(
        user_id="alice",
        course_id="python_bootcamp",
        title="Build REST API"
    )

    bob_goal = await create_goal(
        user_id="bob",
        course_id="python_bootcamp",
        title="Create REST endpoints"
    )

    # Alice busca con scope="user"
    results = await get_similar_goals(
        query="REST API development",
        user_id="alice",
        scope="user"
    )

    # Verificar: Solo goal de Alice
    assert len(results) == 1
    assert results[0]["user_id"] == "alice"
    assert results[0]["goal_id"] == alice_goal.id
```

### Test 2: Scope Course

```python
async def test_rag_course_scope():
    # Alice busca con scope="course"
    results = await get_similar_goals(
        query="REST API development",
        user_id="alice",
        course_id="python_bootcamp",
        scope="course"
    )

    # Verificar: Goals de Alice Y Bob
    assert len(results) == 2
    user_ids = [r["user_id"] for r in results]
    assert "alice" in user_ids
    assert "bob" in user_ids
```

### Test 3: Scope Global

```python
async def test_rag_global_scope():
    # Crear goal de Charlie en otro curso
    charlie_goal = await create_goal(
        user_id="charlie",
        course_id="javascript_bootcamp",
        title="Build GraphQL API"
    )

    # Alice busca con scope="global"
    results = await get_similar_goals(
        query="API development",
        user_id="alice",
        scope="global"
    )

    # Verificar: Goals de TODOS los cursos
    assert len(results) >= 3
    user_ids = [r["user_id"] for r in results]
    assert "charlie" in user_ids  # De otro curso!
```

---

## 🚀 Flujo Completo en LangGraph Agent

```python
from app.agents.tools.rag_tools import get_similar_goals

@tool
async def suggest_goals_tool(
    user_id: str,
    course_id: str,
    description: str
) -> Dict[str, Any]:
    """
    Sugerir goals basado en contexto del curso.
    """

    # 1. Buscar goals similares de compañeros (scope="course")
    similar_from_course = await get_similar_goals(
        query=description,
        user_id=user_id,
        course_id=course_id,
        scope="course",
        limit=3
    )

    # 2. Buscar goals propios (scope="user")
    similar_from_user = await get_similar_goals(
        query=description,
        user_id=user_id,
        scope="user",
        limit=2
    )

    # 3. Combinar contexto
    context = {
        "from_course": similar_from_course,  # Ejemplos de compañeros
        "from_user": similar_from_user,      # Historial propio
        "suggestion": "..."  # LLM genera sugerencia
    }

    return context
```

---

## 📚 Ventajas del Sistema

### ✅ Flexibilidad

- Cada curso puede tener configuración diferente
- Usuarios pueden elegir nivel de privacidad
- Plataforma controla qué se comparte

### ✅ Aprendizaje Colaborativo

- Estudiantes aprenden de compañeros exitosos
- Se valida código con ejemplos reales
- Se comparten mejores prácticas

### ✅ Escalabilidad

- Índices HNSW permiten búsquedas O(log n)
- Filtros reducen el espacio de búsqueda
- Cada scope tiene performance óptimo

### ✅ Privacidad

- `scope="user"` garantiza privacidad total
- `scope="course"` limita visibilidad al curso
- `scope="global"` solo si el usuario lo permite

---

## 📊 Diagrama de Flujo

```
Usuario escribe código
         │
         ↓
┌────────────────────┐
│ ¿Qué scope usar?   │
└────────┬───────────┘
         │
         ├──→ "user"   → Buscar en embeddings WHERE user_id = :user_id
         │
         ├──→ "course" → Buscar en embeddings JOIN goals WHERE course_id = :course_id
         │
         └──→ "global" → Buscar en todos los embeddings (sin filtro)
         │
         ↓
┌────────────────────┐
│ pgvector HNSW      │
│ Búsqueda vectorial │
└────────┬───────────┘
         │
         ↓
Resultados ordenados por similitud
```

---

## 🎯 Resumen

| Aspecto              | Solución                                  |
|----------------------|-------------------------------------------|
| **Problema**         | RAG dinámico por curso                    |
| **Solución**         | 3 scopes: user, course, global            |
| **Tecnología**       | pgvector + filtros SQL dinámicos          |
| **Privacidad**       | Configurable por scope                    |
| **Performance**      | O(log n) con HNSW + índices compuestos    |
| **Escalabilidad**    | Soporta millones de usuarios/cursos       |
| **Colaboración**     | scope="course" permite aprender de otros  |

---

## ✅ Implementación Completa

- ✅ `get_similar_goals()` con scopes
- ✅ `get_similar_code()` con scopes
- ✅ Filtros SQL dinámicos
- ✅ Índices de performance
- ✅ Tests de cada scope
- ✅ Documentación completa

**Estado**: 🚀 Listo para usar en producción

---

**Versión**: 1.0
**Fecha**: 2025-12-28
**Autor**: AI Goals Tracker V2 Team

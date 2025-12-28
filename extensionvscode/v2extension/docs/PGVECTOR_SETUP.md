# 🔍 pgvector Setup - Vector Search para RAG

## ¿Qué es pgvector?

**pgvector** es una extensión de PostgreSQL que permite almacenar y buscar vectores (embeddings) directamente en la base de datos.

### Ventajas

- ✅ **Integrado con PostgreSQL** - No necesitas base de datos separada
- ✅ **HNSW Index** - Búsqueda vectorial en O(log n)
- ✅ **Escalable** - Millones de vectores sin problemas
- ✅ **Compatible con OpenAI** - Soporta embeddings de 1536 dims
- ✅ **Operadores de similitud** - Cosine, L2, Inner product

---

## 📋 Instalación

### macOS (Homebrew)

```bash
# Instalar pgvector
brew install pgvector

# O si ya tienes PostgreSQL instalado:
brew tap pgvector/tap
brew install pgvector
```

### Linux (Ubuntu/Debian)

```bash
# Instalar dependencias
sudo apt update
sudo apt install -y postgresql-server-dev-15 build-essential git

# Clonar repositorio
cd /tmp
git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
cd pgvector

# Compilar e instalar
make
sudo make install
```

### Linux (usando paquete)

```bash
# PostgreSQL 15
sudo apt install postgresql-15-pgvector

# PostgreSQL 14
sudo apt install postgresql-14-pgvector
```

### Docker

```yaml
# docker-compose.yml
services:
  postgres:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: ai_goals_tracker
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
```

---

## 🚀 Habilitación en Base de Datos

### 1. Conectar a PostgreSQL

```bash
psql -U postgres -d ai_goals_tracker
```

### 2. Crear la extensión

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 3. Verificar instalación

```sql
-- Ver extensión instalada
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Debe retornar:
--  oid  | extname | extowner | extnamespace | extrelocatable | extversion
-- ------+---------+----------+--------------+----------------+------------
-- 16389 | vector  |       10 |         2200 | t              | 0.5.1
```

---

## 📊 Uso en el Proyecto

### Modelo con pgvector

```python
# backend/app/models/embedding.py

from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import Mapped, mapped_column

class Embedding(Base):
    __tablename__ = "embeddings"

    # Vector de 1536 dimensiones (OpenAI text-embedding-3-small)
    embedding: Mapped[Vector] = mapped_column(Vector(1536), nullable=False)
```

### Crear Tabla

```sql
-- Migración 007: create_embeddings_table.py

CREATE TABLE embeddings (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(36) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536) NOT NULL,  -- ⭐ pgvector column
    model VARCHAR(100) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP NOT NULL
);
```

### Crear Índice HNSW

```sql
-- HNSW: Hierarchical Navigable Small World
-- Búsqueda vectorial en O(log n) - MUY RÁPIDO

CREATE INDEX idx_embeddings_vector_hnsw
ON embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**Parámetros**:
- `m = 16` - Número de conexiones por nodo (default: 16)
- `ef_construction = 64` - Tamaño de búsqueda al construir (default: 64)
- Valores más altos = mejor accuracy, más lento

### Alternativa: IVFFlat Index

```sql
-- IVFFlat: Inverted File with Flat Compression
-- Construcción más rápida, búsqueda más lenta

CREATE INDEX idx_embeddings_vector_ivfflat
ON embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**Cuándo usar**:
- HNSW: Mejor para producción (búsqueda más rápida)
- IVFFlat: Mejor para desarrollo (construcción más rápida)

---

## 🔍 Búsqueda de Similitud

### Operadores de Distancia

| Operador | Significado | Uso |
|----------|-------------|-----|
| `<->` | L2 distance | Distancia euclidiana |
| `<#>` | Inner product | Producto interno negativo |
| `<=>` | Cosine distance | Distancia de coseno (recomendado) |

### Query de Similitud

```sql
-- Buscar los 5 vectores más similares
SELECT
    id,
    content,
    1 - (embedding <=> :query_embedding) as similarity
FROM embeddings
WHERE user_id = :user_id
ORDER BY embedding <=> :query_embedding
LIMIT 5;
```

**Nota**: Menor distancia = Mayor similitud
- `similarity = 1 - distance`
- Similarity de 1.0 = Idéntico
- Similarity de 0.0 = Totalmente diferente

---

## 📈 Performance y Optimización

### Tamaño de Índice

```sql
-- Ver tamaño del índice HNSW
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE indexname = 'idx_embeddings_vector_hnsw';
```

### Estadísticas de Uso

```sql
-- Ver cuántas búsquedas usa el índice
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE indexname = 'idx_embeddings_vector_hnsw';
```

### Tuning HNSW

Para mejor accuracy (más lento):
```sql
-- Aumentar parámetros
CREATE INDEX ... WITH (m = 32, ef_construction = 128);
```

Para mejor velocidad (menos accuracy):
```sql
-- Reducir parámetros
CREATE INDEX ... WITH (m = 8, ef_construction = 32);
```

---

## 🎯 Ejemplo Completo con OpenAI

### 1. Generar Embedding

```python
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def generate_embedding(text: str) -> list[float]:
    """Generar embedding con OpenAI."""
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding
```

### 2. Guardar en Base de Datos

```python
from app.models import Embedding
from app.core.database import AsyncSessionLocal

async def save_embedding(
    user_id: str,
    entity_type: str,
    entity_id: str,
    content: str
):
    """Guardar embedding en PostgreSQL."""

    # Generar embedding
    embedding_vector = await generate_embedding(content)

    # Guardar en DB
    async with AsyncSessionLocal() as db:
        embedding = Embedding(
            id=str(uuid.uuid4()),
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            content=content,
            embedding=embedding_vector,  # pgvector!
            model="text-embedding-3-small"
        )

        db.add(embedding)
        await db.commit()
```

### 3. Buscar Similares

```python
from sqlalchemy import text

async def search_similar(query: str, user_id: str, limit: int = 5):
    """Buscar embeddings similares usando pgvector."""

    # Generar embedding de la query
    query_embedding = await generate_embedding(query)

    # Buscar con pgvector
    async with AsyncSessionLocal() as db:
        sql = text("""
            SELECT
                id,
                entity_type,
                content,
                1 - (embedding <=> :embedding) as similarity
            FROM embeddings
            WHERE user_id = :user_id
            ORDER BY embedding <=> :embedding
            LIMIT :limit
        """)

        result = await db.execute(
            sql,
            {
                "embedding": str(query_embedding),
                "user_id": user_id,
                "limit": limit
            }
        )

        return result.fetchall()
```

---

## 🧪 Testing pgvector

### Test Manual

```sql
-- 1. Insertar vector de prueba
INSERT INTO embeddings (
    id, user_id, entity_type, entity_id, content, embedding, model
) VALUES (
    'test-001',
    'user-123',
    'test',
    'test-001',
    'Hello world',
    '[0.1, 0.2, 0.3, ...]',  -- 1536 valores
    'test-model'
);

-- 2. Buscar similares
SELECT
    id,
    content,
    embedding <=> '[0.1, 0.2, 0.3, ...]' as distance
FROM embeddings
ORDER BY embedding <=> '[0.1, 0.2, 0.3, ...]'
LIMIT 5;
```

### Test con Script Python

```python
# backend/scripts/test_pgvector.py

import asyncio
from app.core.database import AsyncSessionLocal
from app.models import Embedding
from sqlalchemy import text

async def test_pgvector():
    """Test pgvector functionality."""

    print("🔍 Testing pgvector...")

    async with AsyncSessionLocal() as db:
        # Test 1: Ver si extensión está instalada
        result = await db.execute(
            text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
        )
        version = result.scalar()
        print(f"✅ pgvector version: {version}")

        # Test 2: Contar embeddings
        result = await db.execute(text("SELECT COUNT(*) FROM embeddings"))
        count = result.scalar()
        print(f"✅ Total embeddings: {count}")

        # Test 3: Verificar índice HNSW
        result = await db.execute(text("""
            SELECT indexname
            FROM pg_indexes
            WHERE tablename = 'embeddings'
            AND indexname LIKE '%hnsw%'
        """))
        index = result.scalar()
        print(f"✅ HNSW index: {index or 'Not created yet'}")

if __name__ == "__main__":
    asyncio.run(test_pgvector())
```

---

## 🔧 Troubleshooting

### Error: "type vector does not exist"

```bash
# Extensión no instalada
psql -U postgres -d ai_goals_tracker -c "CREATE EXTENSION vector;"
```

### Error: "could not load library pgvector.so"

```bash
# Reinstalar pgvector
# macOS
brew reinstall pgvector

# Linux
sudo make install  # desde directorio pgvector
```

### Error: "index method hnsw does not exist"

```bash
# Versión de pgvector muy antigua
# Actualizar a v0.5.0+
```

### Performance Lento

```sql
-- 1. Ver si índice se usa
EXPLAIN ANALYZE
SELECT * FROM embeddings
ORDER BY embedding <=> '[...]'
LIMIT 5;

-- Debe mostrar: "Index Scan using idx_embeddings_vector_hnsw"

-- 2. Si no usa índice, recrear
DROP INDEX idx_embeddings_vector_hnsw;
CREATE INDEX idx_embeddings_vector_hnsw
ON embeddings USING hnsw (embedding vector_cosine_ops);

-- 3. Actualizar estadísticas
ANALYZE embeddings;
```

---

## 📚 Recursos

- **Documentación Oficial**: https://github.com/pgvector/pgvector
- **Paper HNSW**: https://arxiv.org/abs/1603.09320
- **OpenAI Embeddings**: https://platform.openai.com/docs/guides/embeddings
- **pgvector + SQLAlchemy**: https://github.com/pgvector/pgvector-python

---

## ✅ Checklist de Instalación

- [ ] pgvector instalado en sistema
- [ ] Extensión habilitada: `CREATE EXTENSION vector;`
- [ ] Tabla embeddings creada (migración 007)
- [ ] Índice HNSW creado
- [ ] Test de búsqueda exitoso
- [ ] pyproject.toml tiene `pgvector`

---

## 📦 Dependencias Python

Asegúrate de tener en `pyproject.toml`:

```toml
[tool.poetry.dependencies]
pgvector = "^0.2.4"
psycopg2-binary = "^2.9.9"  # O psycopg (async)
sqlalchemy = "^2.0.23"
```

Instalar:
```bash
poetry add pgvector
```

---

**Versión pgvector**: 0.5.1+
**Dimensiones**: 1536 (OpenAI text-embedding-3-small)
**Índice**: HNSW (Hierarchical Navigable Small World)
**Performance**: O(log n) búsqueda
**Estado**: ✅ Listo para RAG en producción

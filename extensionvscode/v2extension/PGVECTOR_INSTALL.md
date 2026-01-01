# 🔧 Guía de Instalación de pgvector para PostgreSQL 17

## ¿Qué es pgvector?

pgvector es una extensión de PostgreSQL que añade soporte para operaciones con vectores, esencial para:
- **RAG (Retrieval-Augmented Generation)**: Búsqueda semántica de documentación
- **Embeddings**: Almacenamiento de vectores de OpenAI para similarity search
- **AI Code Analysis**: Búsqueda de código similar usando embeddings

## ⚠️ Nota Importante

La extensión AI Goals Tracker puede funcionar **SIN pgvector** para la mayoría de funcionalidades:
- ✅ CRUD de Goals y Tasks
- ✅ Rate Limiting
- ✅ Code Snapshots
- ✅ Events
- ❌ **Solo embeddings** requiere pgvector (tabla `embeddings`)

## 📦 Instalación en macOS (Homebrew)

### Opción 1: Compilar desde fuente (Recomendado para PostgreSQL 17)

```bash
# 1. Instalar dependencias
brew install postgresql@17

# 2. Clonar repositorio pgvector
cd ~/Downloads
git clone --branch v0.7.0 https://github.com/pgvector/pgvector.git
cd pgvector

# 3. Compilar e instalar
make
make install

# 4. Verificar instalación
ls /opt/homebrew/share/postgresql@17/extension/vector*
# Debe mostrar: vector.control y vector--*.sql
```

### Opción 2: Usando Homebrew (puede no estar actualizado para PG 17)

```bash
# Instalar pgvector
brew install pgvector

# Si falla, usar la Opción 1
```

### Verificar Instalación

```bash
# Conectar a PostgreSQL
PGPASSWORD=123456 psql -U postgres -h localhost -d ai_goals_tracker

# Dentro de psql, ejecutar:
CREATE EXTENSION IF NOT EXISTS vector;

# Verificar
\dx
# Debe mostrar: vector | ... | vector data type and ivfflat and hnsw access methods

# Probar
SELECT '[1,2,3]'::vector;
# Debe retornar: [1,2,3]
```

## 🐳 Instalación con Docker (Alternativa)

Si prefieres usar Docker con pgvector pre-instalado:

```bash
# 1. Detener PostgreSQL local
brew services stop postgresql@17

# 2. Crear docker-compose.yml
cat > docker-compose-pg.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg17
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: 123456
      POSTGRES_DB: ai_goals_tracker
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
EOF

# 3. Levantar PostgreSQL con pgvector
docker-compose -f docker-compose-pg.yml up -d

# 4. Verificar
docker-compose -f docker-compose-pg.yml exec postgres psql -U postgres -d ai_goals_tracker -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## 🔧 Solución de Problemas

### Error: "extension vector is not available"

**Causa**: pgvector no está instalado en el sistema.

**Solución**:
1. Compilar desde fuente (Opción 1 arriba)
2. Verificar que los archivos estén en la ruta correcta:
   ```bash
   # Para Homebrew PostgreSQL
   ls /opt/homebrew/share/postgresql@17/extension/vector*

   # Para PostgreSQL instalado manualmente
   ls /Library/PostgreSQL/17/share/postgresql/extension/vector*
   ```

### Error: "make: pg_config: No such file or directory"

**Causa**: PostgreSQL dev headers no encontrados.

**Solución**:
```bash
# Instalar PostgreSQL con headers
brew install postgresql@17

# Agregar a PATH
export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"

# Verificar
pg_config --version
```

### Error: "permission denied" al hacer make install

**Solución**:
```bash
sudo make install
```

## 📋 Migración de la Tabla Embeddings

Una vez instalado pgvector, la migración creará automáticamente la tabla `embeddings`:

```sql
-- backend/db/migrations/versions/008_create_embeddings_table.py
CREATE TABLE embeddings (
    id UUID PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,  -- 'goal', 'task', 'code_snapshot', 'documentation'
    entity_id UUID NOT NULL,
    embedding vector(1536),  -- OpenAI ada-002 embeddings
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para búsqueda de similitud
CREATE INDEX embeddings_embedding_idx ON embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

## 🧪 Probar pgvector

```bash
# Conectar a la base de datos
PGPASSWORD=123456 psql -U postgres -h localhost -d ai_goals_tracker

# Crear tabla de prueba
CREATE TABLE items (
  id SERIAL PRIMARY KEY,
  embedding vector(3)
);

# Insertar datos
INSERT INTO items (embedding) VALUES
  ('[1,2,3]'),
  ('[4,5,6]'),
  ('[7,8,9]');

# Búsqueda por similitud coseno
SELECT id, embedding,
       1 - (embedding <=> '[3,4,5]') AS similarity
FROM items
ORDER BY embedding <=> '[3,4,5]'
LIMIT 3;

# Limpiar
DROP TABLE items;
```

## 🚀 Continuar con las Migraciones

Una vez instalado pgvector (o si decides continuar sin él):

```bash
# 1. Instalar dependencias Python
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Ejecutar migraciones
alembic upgrade head

# 3. Verificar tablas
PGPASSWORD=123456 psql -U postgres -h localhost -d ai_goals_tracker -c "\dt"
```

## 📚 Referencias

- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [pgvector Installation](https://github.com/pgvector/pgvector#installation)
- [PostgreSQL Extensions](https://www.postgresql.org/docs/17/contrib.html)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)

## ⏭️ Siguiente Paso

Si decides **NO instalar pgvector por ahora**:
1. La extensión funcionará sin RAG/embeddings
2. Puedes ejecutar las migraciones (se saltará la tabla embeddings)
3. Instalar pgvector más adelante cuando necesites RAG

Si decides **instalar pgvector ahora**:
1. Sigue la Opción 1 (compilar desde fuente)
2. Ejecuta las migraciones completas
3. Tendrás soporte completo de RAG

---

**Creado**: 2026-01-01
**PostgreSQL**: 17.4
**pgvector**: v0.7.0+

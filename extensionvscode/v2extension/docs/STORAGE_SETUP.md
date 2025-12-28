# Storage Setup - AI Goals Tracker V2

## 📁 Almacenamiento Actual: Local

Por ahora, el proyecto usa **almacenamiento local** en el filesystem. Cuando MinIO esté disponible online, migraremos automáticamente.

---

## 🎯 Configuración Actual

### Tipo de Storage
```bash
STORAGE_TYPE=local
STORAGE_LOCAL_PATH=./data/storage
```

### Estructura de Directorios

```
v2extension/backend/data/storage/
├── events/                    # Event sourcing events (Parquet)
│   └── 2025/
│       └── 12/
│           └── 28/
│               ├── events_001.parquet
│               └── events_002.parquet
│
└── snapshots/                 # Code snapshots
    └── user_id={uuid}/
        └── goal_id={uuid}/
            ├── snapshot_v1.py
            └── snapshot_v2.py
```

---

## 💾 Cómo se Usan los Archivos

### 1. Eventos (Event Sourcing)

Los eventos de RabbitMQ se procesan y guardan en formato Parquet:

```python
from app.core.storage import storage

# Guardar evento
event_data = {
    "event_type": "goal.created",
    "user_id": "uuid",
    "timestamp": "2025-12-28T00:00:00Z",
    "payload": {...}
}

# Convertir a Parquet y guardar
path = f"events/{year}/{month}/{day}/events_{batch_id}.parquet"
await storage.save_file(path, parquet_bytes)
```

### 2. Code Snapshots

Cuando un usuario valida código, guardamos un snapshot:

```python
# Guardar snapshot de código
code = "def hello(): return 'world'"
path = f"snapshots/user_id={user_id}/goal_id={goal_id}/snapshot_v{version}.py"

await storage.save_file(path, code.encode())
```

---

## 🔄 Migración a MinIO (Futuro)

Cuando MinIO esté disponible:

### Paso 1: Actualizar .env

```bash
# Cambiar de local a s3
STORAGE_TYPE=s3

# Configurar MinIO
MINIO_ENDPOINT=your-minio-server.com:9000
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
MINIO_SECURE=true  # HTTPS

# Buckets
MINIO_BUCKET_EVENTS=ai-goals-tracker-events
MINIO_BUCKET_SNAPSHOTS=ai-goals-tracker-snapshots
```

### Paso 2: Migrar Archivos Existentes

```bash
# Ejecutar script de migración (lo crearemos después)
python backend/scripts/migrate_to_minio.py
```

El script:
1. Lee todos los archivos de `./data/storage/`
2. Los sube a MinIO manteniendo la misma estructura
3. Opcionalmente elimina los archivos locales

### Paso 3: Reiniciar Backend

```bash
# El backend detectará automáticamente la nueva configuración
docker-compose restart backend
```

---

## 📊 Ventajas de Cada Opción

### Local (Actual)

✅ **Ventajas**:
- Sin configuración adicional
- Rápido (sin latencia de red)
- Fácil de debuggear
- No depende de servicios externos

❌ **Desventajas**:
- No compartido entre instancias
- No escalable
- Sin redundancia

### MinIO/S3 (Futuro)

✅ **Ventajas**:
- Compartido entre instancias
- Escalable
- Redundancia y backups
- Compatible con S3 (AWS, MinIO, etc.)

❌ **Desventajas**:
- Requiere configuración
- Latencia de red
- Costos (si es cloud)

---

## 🛠 API de Storage

El código usa una interfaz abstracta, así que funciona igual con local o MinIO:

```python
from app.core.storage import storage

# Guardar archivo
path = "events/2025/12/28/event.parquet"
await storage.save_file(path, data_bytes)

# Leer archivo
data = await storage.read_file(path)

# Listar archivos
files = await storage.list_files(prefix="events/2025/")

# Eliminar archivo
await storage.delete_file(path)
```

---

## 📁 Acceder a los Archivos Locales

```bash
# Ver estructura
tree backend/data/storage/

# Ver eventos guardados
ls -lh backend/data/storage/events/

# Ver snapshots de código
ls -lh backend/data/storage/snapshots/

# Leer un archivo Parquet
python -c "
import pandas as pd
df = pd.read_parquet('backend/data/storage/events/2025/12/28/events_001.parquet')
print(df.head())
"
```

---

## 🔍 Ejemplo Completo

### Guardar Evento

```python
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime
from app.core.storage import storage

# Crear evento
event = {
    "id": "evt_123",
    "type": "goal.created",
    "user_id": "user_456",
    "timestamp": datetime.now().isoformat(),
    "payload": {"goal_id": "goal_789", "title": "Learn Python"}
}

# Convertir a Parquet
table = pa.Table.from_pylist([event])
buf = pa.BufferOutputStream()
pq.write_table(table, buf)
parquet_bytes = buf.getvalue().to_pybytes()

# Guardar
now = datetime.now()
path = f"events/{now.year}/{now.month:02d}/{now.day:02d}/event_{event['id']}.parquet"
saved_path = await storage.save_file(path, parquet_bytes)

print(f"Event saved to: {saved_path}")
```

### Leer Evento

```python
# Leer de storage
path = "events/2025/12/28/event_evt_123.parquet"
data = await storage.read_file(path)

# Parsear Parquet
import io
table = pq.read_table(io.BytesIO(data))
df = table.to_pandas()

print(df)
```

---

## 🧹 Limpieza de Archivos

### Desarrollo

```bash
# Eliminar todos los archivos de prueba
rm -rf backend/data/storage/*

# O solo eventos
rm -rf backend/data/storage/events/*
```

### Producción (cuando uses MinIO)

```python
from app.core.storage import storage

# Eliminar eventos antiguos (más de 30 días)
from datetime import datetime, timedelta

cutoff_date = datetime.now() - timedelta(days=30)
old_files = await storage.list_files(prefix="events/")

for file in old_files:
    # Parse fecha del path
    # Si es más viejo que cutoff_date:
    await storage.delete_file(file)
```

---

## 📋 Checklist de Setup

### Configuración Actual (Local)

- ✅ `STORAGE_TYPE=local` en .env
- ✅ Directorio `backend/data/storage/` se crea automáticamente
- ✅ Permisos de escritura en el directorio
- ✅ `.gitignore` incluye `data/storage/` (no commitear datos)

### Para Migrar a MinIO (Futuro)

- [ ] MinIO server disponible online
- [ ] Obtener credenciales (access_key, secret_key)
- [ ] Crear buckets en MinIO
- [ ] Actualizar .env con configuración de MinIO
- [ ] Ejecutar script de migración
- [ ] Verificar que archivos se suben correctamente
- [ ] Eliminar archivos locales (opcional)

---

## 🎯 Próximos Pasos

### Por Ahora (Local Storage)

1. ✅ No hacer nada, ya está configurado
2. ✅ Los archivos se guardan en `backend/data/storage/`
3. ✅ Puedes verlos directamente en el filesystem

### Cuando MinIO Esté Disponible

1. Actualizar .env con credenciales de MinIO
2. Ejecutar script de migración
3. Verificar que funciona
4. Opcionalmente eliminar archivos locales

---

## 📊 Monitoreo de Storage

### Ver Tamaño de Almacenamiento Local

```bash
# Tamaño total
du -sh backend/data/storage/

# Por tipo
du -sh backend/data/storage/events/
du -sh backend/data/storage/snapshots/

# Archivos más grandes
find backend/data/storage/ -type f -exec ls -lh {} \; | sort -k5 -rh | head -10
```

### Ver Estadísticas

```bash
# Número de archivos
find backend/data/storage/ -type f | wc -l

# Por tipo
find backend/data/storage/events/ -type f | wc -l
find backend/data/storage/snapshots/ -type f | wc -l
```

---

**Storage Actual**: Local Filesystem (`./data/storage/`)
**Migración a MinIO**: Pendiente (cuando esté disponible)
**Estado**: ✅ FUNCIONANDO CON STORAGE LOCAL

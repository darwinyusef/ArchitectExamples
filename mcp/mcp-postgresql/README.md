# MCP PostgreSQL con Cliente LLM

Servidor MCP que permite interactuar con PostgreSQL mediante un LLM. Proporciona herramientas para ejecutar queries, obtener esquemas y realizar operaciones CRUD.

## Características

- ✅ Ejecutar queries SQL personalizadas
- ✅ Obtener esquema completo de la base de datos
- ✅ Listar todas las tablas con información
- ✅ Operaciones CRUD (Create, Read, Update, Delete)
- ✅ Soporte para parámetros preparados (prevención de SQL injection)
- ✅ Resources para acceso rápido al esquema

## Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar PostgreSQL con Docker

```bash
# Iniciar PostgreSQL con datos de ejemplo
docker-compose up -d

# Verificar que está corriendo
docker ps

# Ver logs
docker-compose logs -f
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env si es necesario
```

## Uso

### Iniciar el servidor MCP

```bash
python server.py
```

### Herramientas disponibles

#### 1. `execute_query`
Ejecuta cualquier query SQL:
```python
execute_query(
    query="SELECT * FROM users WHERE id = %s",
    params=[1]
)
```

#### 2. `get_database_schema`
Obtiene el esquema completo de la base de datos:
```python
get_database_schema()
```

#### 3. `list_tables`
Lista todas las tablas con información:
```python
list_tables()
```

#### 4. `get_table_info`
Información detallada de una tabla:
```python
get_table_info(table_name="users")
```

#### 5. `insert_data`
Insertar un nuevo registro:
```python
insert_data(
    table_name="users",
    data={"username": "nueva_usuaria", "email": "nueva@example.com"}
)
```

#### 6. `update_data`
Actualizar registros:
```python
update_data(
    table_name="users",
    data={"email": "nuevo@example.com"},
    condition="id = %s",
    condition_params=[1]
)
```

#### 7. `delete_data`
Eliminar registros:
```python
delete_data(
    table_name="users",
    condition="id = %s",
    condition_params=[1]
)
```

## Ejemplos de uso con LLM

El LLM puede interactuar naturalmente con la base de datos:

- "¿Cuáles son las tablas disponibles?"
- "Muéstrame el esquema de la tabla users"
- "Lista todos los productos con precio mayor a 100"
- "Inserta un nuevo usuario con username 'test' y email 'test@example.com'"
- "Actualiza el precio del producto con id 1 a 1499.99"
- "¿Cuántos pedidos están pendientes?"

## Seguridad

⚠️ **IMPORTANTE**: Este servidor está diseñado para desarrollo. Para producción:

- Usar roles de PostgreSQL con permisos limitados
- Validar todas las entradas
- Implementar rate limiting
- Usar SSL/TLS para conexiones
- No exponer credenciales en código
- Considerar queries permitidas en whitelist

## Estructura de la Base de Datos

El `init.sql` crea:

- **users**: Usuarios del sistema
- **products**: Catálogo de productos
- **orders**: Órdenes de compra
- **order_items**: Items de cada orden

## Detener el servicio

```bash
docker-compose down

# Para eliminar también los datos
docker-compose down -v
```

## Troubleshooting

### Error de conexión
```bash
# Verificar que PostgreSQL está corriendo
docker-compose ps

# Reiniciar el servicio
docker-compose restart
```

### Puerto ocupado
```bash
# Cambiar el puerto en docker-compose.yml
ports:
  - "5433:5432"  # Usar 5433 en lugar de 5432
```

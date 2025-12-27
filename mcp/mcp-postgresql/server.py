"""
MCP Server para PostgreSQL con capacidades LLM
Permite ejecutar queries, obtener esquemas y realizar operaciones CRUD
"""

from mcp.server.fastmcp import FastMCP
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
import json
import os
from contextlib import contextmanager

# Crear servidor MCP
mcp = FastMCP("PostgreSQL-LLM")

# Configuración de conexión (usar variables de entorno en producción)
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "database": os.getenv("POSTGRES_DB", "postgres"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres")
}

@contextmanager
def get_db_connection():
    """Context manager para manejar conexiones a la base de datos"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


@mcp.tool()
def execute_query(query: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
    """
    Ejecuta una query SQL en PostgreSQL y devuelve los resultados.

    Args:
        query: La query SQL a ejecutar
        params: Parámetros opcionales para la query (usar %s en la query)

    Returns:
        Diccionario con los resultados y metadatos
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or [])

                # Si es una query SELECT, obtener resultados
                if cur.description:
                    results = cur.fetchall()
                    return {
                        "success": True,
                        "rows": [dict(row) for row in results],
                        "row_count": len(results),
                        "columns": [desc[0] for desc in cur.description]
                    }
                else:
                    # Para INSERT, UPDATE, DELETE
                    return {
                        "success": True,
                        "rows_affected": cur.rowcount,
                        "message": f"Query ejecutada exitosamente. {cur.rowcount} filas afectadas."
                    }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


@mcp.tool()
def get_database_schema() -> Dict[str, Any]:
    """
    Obtiene el esquema completo de la base de datos incluyendo tablas, columnas y tipos.

    Returns:
        Diccionario con la estructura de todas las tablas
    """
    schema_query = """
    SELECT
        t.table_name,
        c.column_name,
        c.data_type,
        c.is_nullable,
        c.column_default,
        tc.constraint_type
    FROM information_schema.tables t
    LEFT JOIN information_schema.columns c
        ON t.table_name = c.table_name
    LEFT JOIN information_schema.constraint_column_usage ccu
        ON c.column_name = ccu.column_name AND c.table_name = ccu.table_name
    LEFT JOIN information_schema.table_constraints tc
        ON ccu.constraint_name = tc.constraint_name
    WHERE t.table_schema = 'public'
    ORDER BY t.table_name, c.ordinal_position;
    """

    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(schema_query)
                results = cur.fetchall()

                # Organizar por tablas
                schema = {}
                for row in results:
                    table = row['table_name']
                    if table not in schema:
                        schema[table] = {"columns": []}

                    schema[table]["columns"].append({
                        "name": row['column_name'],
                        "type": row['data_type'],
                        "nullable": row['is_nullable'] == 'YES',
                        "default": row['column_default'],
                        "constraint": row.get('constraint_type')
                    })

                return {
                    "success": True,
                    "schema": schema,
                    "table_count": len(schema)
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def get_table_info(table_name: str) -> Dict[str, Any]:
    """
    Obtiene información detallada de una tabla específica.

    Args:
        table_name: Nombre de la tabla

    Returns:
        Información completa de la tabla incluyendo índices y constraints
    """
    table_info_query = """
    SELECT
        c.column_name,
        c.data_type,
        c.character_maximum_length,
        c.is_nullable,
        c.column_default,
        pg_catalog.col_description(
            (quote_ident(c.table_schema)||'.'||quote_ident(c.table_name))::regclass::oid,
            c.ordinal_position
        ) as column_description
    FROM information_schema.columns c
    WHERE c.table_name = %s AND c.table_schema = 'public'
    ORDER BY c.ordinal_position;
    """

    constraints_query = """
    SELECT
        tc.constraint_name,
        tc.constraint_type,
        kcu.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
    WHERE tc.table_name = %s AND tc.table_schema = 'public';
    """

    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Obtener columnas
                cur.execute(table_info_query, [table_name])
                columns = [dict(row) for row in cur.fetchall()]

                # Obtener constraints
                cur.execute(constraints_query, [table_name])
                constraints = [dict(row) for row in cur.fetchall()]

                return {
                    "success": True,
                    "table_name": table_name,
                    "columns": columns,
                    "constraints": constraints
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def list_tables() -> Dict[str, Any]:
    """
    Lista todas las tablas disponibles en la base de datos.

    Returns:
        Lista de nombres de tablas con conteos de filas
    """
    query = """
    SELECT
        schemaname,
        tablename,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
    FROM pg_tables
    WHERE schemaname = 'public'
    ORDER BY tablename;
    """

    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                tables = [dict(row) for row in cur.fetchall()]

                # Obtener conteo de filas para cada tabla
                for table in tables:
                    count_query = f"SELECT COUNT(*) as count FROM {table['tablename']};"
                    cur.execute(count_query)
                    table['row_count'] = cur.fetchone()['count']

                return {
                    "success": True,
                    "tables": tables,
                    "total_tables": len(tables)
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def insert_data(table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inserta un registro en una tabla.

    Args:
        table_name: Nombre de la tabla
        data: Diccionario con los datos a insertar (columna: valor)

    Returns:
        Resultado de la inserción
    """
    try:
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        values = list(data.values())

        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING *;"

        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, values)
                result = dict(cur.fetchone())

                return {
                    "success": True,
                    "inserted_row": result,
                    "message": f"Registro insertado exitosamente en {table_name}"
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def update_data(table_name: str, data: Dict[str, Any], condition: str, condition_params: List[Any]) -> Dict[str, Any]:
    """
    Actualiza registros en una tabla.

    Args:
        table_name: Nombre de la tabla
        data: Diccionario con los datos a actualizar (columna: valor)
        condition: Condición WHERE (ej: "id = %s")
        condition_params: Parámetros para la condición

    Returns:
        Resultado de la actualización
    """
    try:
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        values = list(data.values()) + condition_params

        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition} RETURNING *;"

        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, values)
                results = [dict(row) for row in cur.fetchall()]

                return {
                    "success": True,
                    "updated_rows": results,
                    "rows_affected": len(results),
                    "message": f"{len(results)} registro(s) actualizado(s)"
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def delete_data(table_name: str, condition: str, condition_params: List[Any]) -> Dict[str, Any]:
    """
    Elimina registros de una tabla.

    Args:
        table_name: Nombre de la tabla
        condition: Condición WHERE (ej: "id = %s")
        condition_params: Parámetros para la condición

    Returns:
        Resultado de la eliminación
    """
    try:
        query = f"DELETE FROM {table_name} WHERE {condition} RETURNING *;"

        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, condition_params)
                results = [dict(row) for row in cur.fetchall()]

                return {
                    "success": True,
                    "deleted_rows": results,
                    "rows_affected": len(results),
                    "message": f"{len(results)} registro(s) eliminado(s)"
                }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.resource("database://schema")
def get_schema_resource() -> str:
    """Resource que provee el esquema de la base de datos"""
    result = get_database_schema()
    return json.dumps(result, indent=2)


@mcp.resource("database://tables")
def get_tables_resource() -> str:
    """Resource que provee la lista de tablas"""
    result = list_tables()
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    # Iniciar el servidor
    mcp.run()

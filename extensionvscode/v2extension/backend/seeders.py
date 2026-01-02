"""
Seeders para poblar la base de datos con datos básicos de prueba.
"""

import uuid
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import execute_values

# Conexión a la base de datos
DB_CONFIG = {
    'dbname': 'extension_db',
    'user': 'yusefgonzalez',
    'password': '123456',
    'host': 'localhost',
    'port': '5432'
}


def generate_uuid():
    """Genera un UUID como string."""
    return str(uuid.uuid4())


def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt."""
    # Usamos bcrypt directamente
    import bcrypt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def seed_users(cursor):
    """Crea usuarios de prueba."""
    print("Seeding users...")

    users = [
        {
            'id': generate_uuid(),
            'email': 'admin@test.com',
            'username': 'admin',
            'hashed_password': hash_password('admin123'),
            'full_name': 'Admin User',
            'is_active': True,
            'is_superuser': True,
            'metadata': '{"preferences": {"theme": "dark", "language": "es"}}',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'last_login_at': None
        },
        {
            'id': generate_uuid(),
            'email': 'user1@test.com',
            'username': 'user1',
            'hashed_password': hash_password('user123'),
            'full_name': 'Test User 1',
            'is_active': True,
            'is_superuser': False,
            'metadata': '{"preferences": {"theme": "light", "language": "en"}}',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'last_login_at': None
        },
        {
            'id': generate_uuid(),
            'email': 'user2@test.com',
            'username': 'user2',
            'hashed_password': hash_password('user123'),
            'full_name': 'Test User 2',
            'is_active': True,
            'is_superuser': False,
            'metadata': '{"preferences": {"theme": "dark", "language": "en"}}',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'last_login_at': None
        }
    ]

    query = """
        INSERT INTO users (id, email, username, hashed_password, full_name,
                          is_active, is_superuser, metadata, created_at, updated_at, last_login_at)
        VALUES (%(id)s, %(email)s, %(username)s, %(hashed_password)s, %(full_name)s,
                %(is_active)s, %(is_superuser)s, %(metadata)s, %(created_at)s, %(updated_at)s, %(last_login_at)s)
        RETURNING id, email, username
    """

    user_ids = []
    for user in users:
        cursor.execute(query, user)
        result = cursor.fetchone()
        user_ids.append(result[0])
        print(f"  ✓ Created user: {result[2]} ({result[1]})")

    return user_ids


def seed_courses(cursor, user_ids):
    """Crea cursos de prueba."""
    print("\nSeeding courses...")

    courses = [
        {
            'id': generate_uuid(),
            'user_id': user_ids[0],
            'title': 'Curso de Python Avanzado',
            'description': 'Aprende conceptos avanzados de Python incluyendo async/await, decoradores y metaclases',
            'status': 'active',
            'progress_percentage': 45.5,
            'metadata': '{"technologies": ["Python", "AsyncIO"], "difficulty": "advanced", "estimated_hours": 40}',
            'created_at': datetime.utcnow() - timedelta(days=30),
            'updated_at': datetime.utcnow(),
            'completed_at': None
        },
        {
            'id': generate_uuid(),
            'user_id': user_ids[1],
            'title': 'FastAPI & PostgreSQL',
            'description': 'Construcción de APIs RESTful con FastAPI y PostgreSQL',
            'status': 'active',
            'progress_percentage': 70.0,
            'metadata': '{"technologies": ["FastAPI", "PostgreSQL", "SQLAlchemy"], "difficulty": "intermediate", "estimated_hours": 30}',
            'created_at': datetime.utcnow() - timedelta(days=15),
            'updated_at': datetime.utcnow(),
            'completed_at': None
        },
        {
            'id': generate_uuid(),
            'user_id': user_ids[1],
            'title': 'React + TypeScript',
            'description': 'Desarrollo de aplicaciones web modernas con React y TypeScript',
            'status': 'completed',
            'progress_percentage': 100.0,
            'metadata': '{"technologies": ["React", "TypeScript", "Vite"], "difficulty": "intermediate", "estimated_hours": 35}',
            'created_at': datetime.utcnow() - timedelta(days=60),
            'updated_at': datetime.utcnow() - timedelta(days=5),
            'completed_at': datetime.utcnow() - timedelta(days=5)
        }
    ]

    query = """
        INSERT INTO courses (id, user_id, title, description, status, progress_percentage,
                           metadata, created_at, updated_at, completed_at)
        VALUES (%(id)s, %(user_id)s, %(title)s, %(description)s, %(status)s, %(progress_percentage)s,
                %(metadata)s::jsonb, %(created_at)s, %(updated_at)s, %(completed_at)s)
        RETURNING id, title
    """

    course_ids = []
    for course in courses:
        cursor.execute(query, course)
        result = cursor.fetchone()
        course_ids.append(result[0])
        print(f"  ✓ Created course: {result[1]}")

    return course_ids


def seed_goals(cursor, user_ids, course_ids):
    """Crea goals de prueba."""
    print("\nSeeding goals...")

    goals = [
        {
            'id': generate_uuid(),
            'user_id': user_ids[0],
            'course_id': course_ids[0],
            'title': 'Implementar sistema de autenticación JWT',
            'description': 'Crear un sistema completo de autenticación con JWT incluyendo refresh tokens',
            'status': 'in_progress',
            'priority': 'high',
            'progress_percentage': 60.0,
            'ai_generated': True,
            'validation_criteria': '{"criteria": ["Implementar login", "Implementar registro", "Implementar refresh token"]}',
            'metadata': '{"tags": ["backend", "security"], "estimated_hours": 8}',
            'created_at': datetime.utcnow() - timedelta(days=10),
            'updated_at': datetime.utcnow(),
            'started_at': datetime.utcnow() - timedelta(days=9),
            'completed_at': None,
            'due_date': datetime.utcnow() + timedelta(days=5)
        },
        {
            'id': generate_uuid(),
            'user_id': user_ids[1],
            'course_id': course_ids[1],
            'title': 'Crear endpoints CRUD para usuarios',
            'description': 'Implementar todos los endpoints necesarios para gestionar usuarios',
            'status': 'completed',
            'priority': 'medium',
            'progress_percentage': 100.0,
            'ai_generated': False,
            'validation_criteria': '{"criteria": ["GET /users", "POST /users", "PUT /users/:id", "DELETE /users/:id"]}',
            'metadata': '{"tags": ["backend", "api"], "estimated_hours": 6, "actual_hours": 5.5}',
            'created_at': datetime.utcnow() - timedelta(days=20),
            'updated_at': datetime.utcnow() - timedelta(days=3),
            'started_at': datetime.utcnow() - timedelta(days=19),
            'completed_at': datetime.utcnow() - timedelta(days=3),
            'due_date': None
        },
        {
            'id': generate_uuid(),
            'user_id': user_ids[1],
            'course_id': course_ids[1],
            'title': 'Implementar búsqueda con pgvector',
            'description': 'Agregar búsqueda semántica usando embeddings y pgvector',
            'status': 'pending',
            'priority': 'urgent',
            'progress_percentage': 0.0,
            'ai_generated': True,
            'validation_criteria': '{"criteria": ["Generar embeddings", "Crear índice HNSW", "Implementar búsqueda"]}',
            'metadata': '{"tags": ["backend", "ai", "rag"], "estimated_hours": 12}',
            'created_at': datetime.utcnow() - timedelta(days=2),
            'updated_at': datetime.utcnow() - timedelta(days=2),
            'started_at': None,
            'completed_at': None,
            'due_date': datetime.utcnow() + timedelta(days=7)
        }
    ]

    query = """
        INSERT INTO goals (id, user_id, course_id, title, description, status, priority,
                          progress_percentage, ai_generated, validation_criteria, metadata,
                          created_at, updated_at, started_at, completed_at, due_date)
        VALUES (%(id)s, %(user_id)s, %(course_id)s, %(title)s, %(description)s, %(status)s, %(priority)s,
                %(progress_percentage)s, %(ai_generated)s, %(validation_criteria)s::jsonb, %(metadata)s::jsonb,
                %(created_at)s, %(updated_at)s, %(started_at)s, %(completed_at)s, %(due_date)s)
        RETURNING id, title
    """

    goal_ids = []
    for goal in goals:
        cursor.execute(query, goal)
        result = cursor.fetchone()
        goal_ids.append(result[0])
        print(f"  ✓ Created goal: {result[1]}")

    return goal_ids


def seed_tasks(cursor, user_ids, goal_ids):
    """Crea tasks de prueba."""
    print("\nSeeding tasks...")

    tasks = [
        {
            'id': generate_uuid(),
            'goal_id': goal_ids[0],
            'user_id': user_ids[0],
            'title': 'Crear modelo User con SQLAlchemy',
            'description': 'Definir el modelo de usuario con todos los campos necesarios',
            'task_type': 'code',
            'status': 'completed',
            'priority': 1,
            'estimated_hours': 2.0,
            'actual_hours': 1.5,
            'validation_result': '{"passed": true, "score": 0.95}',
            'ai_feedback': 'Excelente implementación. El modelo está bien estructurado.',
            'metadata': '{"files": ["/app/models/user.py"]}',
            'created_at': datetime.utcnow() - timedelta(days=9),
            'updated_at': datetime.utcnow() - timedelta(days=7),
            'started_at': datetime.utcnow() - timedelta(days=9),
            'completed_at': datetime.utcnow() - timedelta(days=7)
        },
        {
            'id': generate_uuid(),
            'goal_id': goal_ids[0],
            'user_id': user_ids[0],
            'title': 'Implementar endpoints de autenticación',
            'description': 'Crear /login y /register endpoints',
            'task_type': 'code',
            'status': 'in_progress',
            'priority': 2,
            'estimated_hours': 4.0,
            'actual_hours': 2.5,
            'validation_result': None,
            'ai_feedback': None,
            'metadata': '{"files": ["/app/routes/auth.py"]}',
            'created_at': datetime.utcnow() - timedelta(days=7),
            'updated_at': datetime.utcnow(),
            'started_at': datetime.utcnow() - timedelta(days=6),
            'completed_at': None
        },
        {
            'id': generate_uuid(),
            'goal_id': goal_ids[1],
            'user_id': user_ids[1],
            'title': 'Documentar API con OpenAPI',
            'description': 'Agregar documentación completa de todos los endpoints',
            'task_type': 'documentation',
            'status': 'completed',
            'priority': 5,
            'estimated_hours': 3.0,
            'actual_hours': 3.5,
            'validation_result': '{"passed": true, "score": 0.88}',
            'ai_feedback': 'Buena documentación, considera agregar más ejemplos.',
            'metadata': '{"files": ["/docs/api.md"]}',
            'created_at': datetime.utcnow() - timedelta(days=5),
            'updated_at': datetime.utcnow() - timedelta(days=3),
            'started_at': datetime.utcnow() - timedelta(days=5),
            'completed_at': datetime.utcnow() - timedelta(days=3)
        },
        {
            'id': generate_uuid(),
            'goal_id': goal_ids[2],
            'user_id': user_ids[1],
            'title': 'Investigar mejores prácticas de pgvector',
            'description': 'Estudiar documentación y casos de uso de pgvector',
            'task_type': 'research',
            'status': 'todo',
            'priority': 1,
            'estimated_hours': 2.0,
            'actual_hours': None,
            'validation_result': None,
            'ai_feedback': None,
            'metadata': '{"resources": ["https://github.com/pgvector/pgvector"]}',
            'created_at': datetime.utcnow() - timedelta(days=1),
            'updated_at': datetime.utcnow() - timedelta(days=1),
            'started_at': None,
            'completed_at': None
        }
    ]

    query = """
        INSERT INTO tasks (id, goal_id, user_id, title, description, task_type, status,
                          priority, estimated_hours, actual_hours, validation_result, ai_feedback,
                          metadata, created_at, updated_at, started_at, completed_at)
        VALUES (%(id)s, %(goal_id)s, %(user_id)s, %(title)s, %(description)s, %(task_type)s, %(status)s,
                %(priority)s, %(estimated_hours)s, %(actual_hours)s, %(validation_result)s::jsonb, %(ai_feedback)s,
                %(metadata)s::jsonb, %(created_at)s, %(updated_at)s, %(started_at)s, %(completed_at)s)
        RETURNING id, title
    """

    task_ids = []
    for task in tasks:
        cursor.execute(query, task)
        result = cursor.fetchone()
        task_ids.append(result[0])
        print(f"  ✓ Created task: {result[1]}")

    return task_ids


def seed_events(cursor, user_ids):
    """Crea eventos de prueba."""
    print("\nSeeding events...")

    events = [
        {
            'id': generate_uuid(),
            'event_type': 'user.created',
            'user_id': user_ids[0],
            'entity_type': 'user',
            'entity_id': user_ids[0],
            'payload': '{"email": "admin@test.com", "username": "admin"}',
            'metadata': '{"ip_address": "127.0.0.1", "source": "api"}',
            'created_at': datetime.utcnow() - timedelta(days=30),
            'processed_at': datetime.utcnow() - timedelta(days=30),
            'parquet_path': None
        },
        {
            'id': generate_uuid(),
            'event_type': 'course.created',
            'user_id': user_ids[0],
            'entity_type': 'course',
            'entity_id': generate_uuid(),
            'payload': '{"title": "Curso de Python Avanzado"}',
            'metadata': '{"ip_address": "127.0.0.1", "source": "vscode_extension"}',
            'created_at': datetime.utcnow() - timedelta(days=30),
            'processed_at': datetime.utcnow() - timedelta(days=30),
            'parquet_path': None
        },
        {
            'id': generate_uuid(),
            'event_type': 'task.completed',
            'user_id': user_ids[0],
            'entity_type': 'task',
            'entity_id': generate_uuid(),
            'payload': '{"task_id": "xxx", "duration_hours": 1.5}',
            'metadata': '{"ip_address": "192.168.1.100", "source": "vscode_extension"}',
            'created_at': datetime.utcnow() - timedelta(days=7),
            'processed_at': datetime.utcnow() - timedelta(days=7),
            'parquet_path': None
        }
    ]

    query = """
        INSERT INTO events (id, event_type, user_id, entity_type, entity_id, payload,
                           metadata, created_at, processed_at, parquet_path)
        VALUES (%(id)s, %(event_type)s, %(user_id)s, %(entity_type)s, %(entity_id)s, %(payload)s::jsonb,
                %(metadata)s::jsonb, %(created_at)s, %(processed_at)s, %(parquet_path)s)
        RETURNING id, event_type
    """

    for event in events:
        cursor.execute(query, event)
        result = cursor.fetchone()
        print(f"  ✓ Created event: {result[1]}")


def main():
    """Ejecuta todos los seeders."""
    print("=" * 60)
    print("Iniciando seeders para extension_db")
    print("=" * 60)

    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Verificar si ya hay datos
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        if user_count > 0:
            print(f"\n⚠️  La base de datos ya tiene {user_count} usuarios.")
            response = input("¿Deseas limpiar y volver a crear los datos? (s/n): ")
            if response.lower() != 's':
                print("Operación cancelada.")
                return

            # Limpiar datos existentes
            print("\nLimpiando datos existentes...")
            cursor.execute("TRUNCATE users, courses, goals, tasks, events, code_snapshots, embeddings, rate_limit_audits CASCADE")
            print("  ✓ Datos limpiados")

        # Ejecutar seeders en orden
        user_ids = seed_users(cursor)
        course_ids = seed_courses(cursor, user_ids)
        goal_ids = seed_goals(cursor, user_ids, course_ids)
        task_ids = seed_tasks(cursor, user_ids, goal_ids)
        seed_events(cursor, user_ids)

        # Commit de los cambios
        conn.commit()

        print("\n" + "=" * 60)
        print("✓ Seeders completados exitosamente")
        print("=" * 60)
        print("\nResumen:")
        print(f"  - {len(user_ids)} usuarios creados")
        print(f"  - {len(course_ids)} cursos creados")
        print(f"  - {len(goal_ids)} goals creados")
        print(f"  - {len(task_ids)} tasks creadas")
        print(f"  - 3 eventos creados")
        print("\nCredenciales de prueba:")
        print("  Admin: admin@test.com / admin123")
        print("  User1: user1@test.com / user123")
        print("  User2: user2@test.com / user123")

    except Exception as e:
        print(f"\n❌ Error ejecutando seeders: {e}")
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()

"""
Parquet Schemas para Event Sourcing.

Los eventos se almacenan en formato Parquet para:
1. Análisis histórico eficiente
2. Queries analíticas rápidas
3. Menor consumo de espacio
4. Integración con herramientas de análisis (Pandas, Spark, DuckDB)

Estructura de directorios:
backend/data/storage/events/
├── 2024/
│   ├── 01/
│   │   ├── user_events_2024-01-15.parquet
│   │   ├── goal_events_2024-01-15.parquet
│   │   └── task_events_2024-01-15.parquet
│   └── 02/
│       └── ...
└── ...
"""

import pyarrow as pa
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum


# ==================== SCHEMAS PYARROW ====================

# Schema base para eventos
EVENT_SCHEMA = pa.schema([
    # IDs
    pa.field("event_id", pa.string(), nullable=False),
    pa.field("user_id", pa.string(), nullable=True),
    pa.field("entity_type", pa.string(), nullable=True),
    pa.field("entity_id", pa.string(), nullable=True),

    # Event info
    pa.field("event_type", pa.string(), nullable=False),

    # Payload (JSON as string para flexibilidad)
    pa.field("payload", pa.string(), nullable=False),

    # Metadata (JSON as string)
    pa.field("metadata", pa.string(), nullable=True),

    # Timestamps
    pa.field("created_at", pa.timestamp("us"), nullable=False),
    pa.field("processed_at", pa.timestamp("us"), nullable=True),

    # Partitioning fields
    pa.field("year", pa.int32(), nullable=False),
    pa.field("month", pa.int32(), nullable=False),
    pa.field("day", pa.int32(), nullable=False),
])


# Schema para user events
USER_EVENT_SCHEMA = pa.schema([
    pa.field("event_id", pa.string(), nullable=False),
    pa.field("user_id", pa.string(), nullable=False),
    pa.field("event_type", pa.string(), nullable=False),

    # User-specific fields
    pa.field("email", pa.string(), nullable=True),
    pa.field("username", pa.string(), nullable=True),
    pa.field("action", pa.string(), nullable=False),  # created, updated, login, logout

    # Metadata
    pa.field("ip_address", pa.string(), nullable=True),
    pa.field("user_agent", pa.string(), nullable=True),

    # Timestamps
    pa.field("created_at", pa.timestamp("us"), nullable=False),

    # Partitioning
    pa.field("year", pa.int32(), nullable=False),
    pa.field("month", pa.int32(), nullable=False),
    pa.field("day", pa.int32(), nullable=False),
])


# Schema para goal events
GOAL_EVENT_SCHEMA = pa.schema([
    pa.field("event_id", pa.string(), nullable=False),
    pa.field("user_id", pa.string(), nullable=False),
    pa.field("goal_id", pa.string(), nullable=False),
    pa.field("event_type", pa.string(), nullable=False),

    # Goal-specific fields
    pa.field("title", pa.string(), nullable=True),
    pa.field("status", pa.string(), nullable=True),
    pa.field("priority", pa.string(), nullable=True),
    pa.field("progress_percentage", pa.float64(), nullable=True),
    pa.field("ai_generated", pa.bool_(), nullable=True),

    # Course association
    pa.field("course_id", pa.string(), nullable=True),

    # Timestamps
    pa.field("created_at", pa.timestamp("us"), nullable=False),

    # Partitioning
    pa.field("year", pa.int32(), nullable=False),
    pa.field("month", pa.int32(), nullable=False),
    pa.field("day", pa.int32(), nullable=False),
])


# Schema para task events
TASK_EVENT_SCHEMA = pa.schema([
    pa.field("event_id", pa.string(), nullable=False),
    pa.field("user_id", pa.string(), nullable=False),
    pa.field("task_id", pa.string(), nullable=False),
    pa.field("goal_id", pa.string(), nullable=False),
    pa.field("event_type", pa.string(), nullable=False),

    # Task-specific fields
    pa.field("title", pa.string(), nullable=True),
    pa.field("task_type", pa.string(), nullable=True),
    pa.field("status", pa.string(), nullable=True),
    pa.field("validation_score", pa.float64(), nullable=True),
    pa.field("estimated_hours", pa.float64(), nullable=True),
    pa.field("actual_hours", pa.float64(), nullable=True),

    # Timestamps
    pa.field("created_at", pa.timestamp("us"), nullable=False),
    pa.field("started_at", pa.timestamp("us"), nullable=True),
    pa.field("completed_at", pa.timestamp("us"), nullable=True),

    # Partitioning
    pa.field("year", pa.int32(), nullable=False),
    pa.field("month", pa.int32(), nullable=False),
    pa.field("day", pa.int32(), nullable=False),
])


# Schema para code validation events
CODE_EVENT_SCHEMA = pa.schema([
    pa.field("event_id", pa.string(), nullable=False),
    pa.field("user_id", pa.string(), nullable=False),
    pa.field("code_snapshot_id", pa.string(), nullable=False),
    pa.field("task_id", pa.string(), nullable=True),
    pa.field("event_type", pa.string(), nullable=False),

    # Code-specific fields
    pa.field("file_path", pa.string(), nullable=True),
    pa.field("language", pa.string(), nullable=True),
    pa.field("lines_of_code", pa.int32(), nullable=True),
    pa.field("validation_passed", pa.bool_(), nullable=True),
    pa.field("validation_score", pa.float64(), nullable=True),
    pa.field("issues_count", pa.int32(), nullable=True),

    # Timestamps
    pa.field("created_at", pa.timestamp("us"), nullable=False),

    # Partitioning
    pa.field("year", pa.int32(), nullable=False),
    pa.field("month", pa.int32(), nullable=False),
    pa.field("day", pa.int32(), nullable=False),
])


# Schema para AI feedback events
AI_EVENT_SCHEMA = pa.schema([
    pa.field("event_id", pa.string(), nullable=False),
    pa.field("user_id", pa.string(), nullable=False),
    pa.field("event_type", pa.string(), nullable=False),

    # AI-specific fields
    pa.field("agent_node", pa.string(), nullable=False),  # cual nodo de LangGraph
    pa.field("entity_type", pa.string(), nullable=True),
    pa.field("entity_id", pa.string(), nullable=True),
    pa.field("model_used", pa.string(), nullable=True),
    pa.field("tokens_used", pa.int32(), nullable=True),
    pa.field("latency_ms", pa.int32(), nullable=True),
    pa.field("feedback_type", pa.string(), nullable=True),  # validation, suggestion, motivation

    # Timestamps
    pa.field("created_at", pa.timestamp("us"), nullable=False),

    # Partitioning
    pa.field("year", pa.int32(), nullable=False),
    pa.field("month", pa.int32(), nullable=False),
    pa.field("day", pa.int32(), nullable=False),
])


# ==================== DATACLASSES PARA EVENTOS ====================

@dataclass
class BaseEvent:
    """Base para todos los eventos."""
    event_id: str
    user_id: str
    event_type: str
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para Parquet."""
        data = asdict(self)
        # Agregar campos de particionamiento
        data["year"] = self.created_at.year
        data["month"] = self.created_at.month
        data["day"] = self.created_at.day
        return data


@dataclass
class UserEvent(BaseEvent):
    """Evento de usuario."""
    email: str | None = None
    username: str | None = None
    action: str = "unknown"
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass
class GoalEvent(BaseEvent):
    """Evento de goal."""
    goal_id: str = ""
    title: str | None = None
    status: str | None = None
    priority: str | None = None
    progress_percentage: float | None = None
    ai_generated: bool | None = None
    course_id: str | None = None


@dataclass
class TaskEvent(BaseEvent):
    """Evento de task."""
    task_id: str = ""
    goal_id: str = ""
    title: str | None = None
    task_type: str | None = None
    status: str | None = None
    validation_score: float | None = None
    estimated_hours: float | None = None
    actual_hours: float | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass
class CodeEvent(BaseEvent):
    """Evento de código."""
    code_snapshot_id: str = ""
    task_id: str | None = None
    file_path: str | None = None
    language: str | None = None
    lines_of_code: int | None = None
    validation_passed: bool | None = None
    validation_score: float | None = None
    issues_count: int | None = None


@dataclass
class AIEvent(BaseEvent):
    """Evento de IA."""
    agent_node: str = ""
    entity_type: str | None = None
    entity_id: str | None = None
    model_used: str | None = None
    tokens_used: int | None = None
    latency_ms: int | None = None
    feedback_type: str | None = None


# ==================== HELPERS ====================

def get_schema_for_event_type(event_type: str) -> pa.Schema:
    """
    Obtener schema apropiado según el tipo de evento.

    Args:
        event_type: Tipo de evento (user.*, goal.*, task.*, code.*, ai.*)

    Returns:
        PyArrow schema apropiado
    """
    if event_type.startswith("user."):
        return USER_EVENT_SCHEMA
    elif event_type.startswith("goal."):
        return GOAL_EVENT_SCHEMA
    elif event_type.startswith("task."):
        return TASK_EVENT_SCHEMA
    elif event_type.startswith("code."):
        return CODE_EVENT_SCHEMA
    elif event_type.startswith("ai."):
        return AI_EVENT_SCHEMA
    else:
        return EVENT_SCHEMA


def get_parquet_path(event_type: str, timestamp: datetime, base_path: str = "./data/storage/events") -> str:
    """
    Generar path para archivo Parquet según tipo de evento y fecha.

    Args:
        event_type: Tipo de evento
        timestamp: Timestamp del evento
        base_path: Path base de almacenamiento

    Returns:
        Path completo del archivo Parquet

    Example:
        ./data/storage/events/2024/01/goal_events_2024-01-15.parquet
    """
    category = event_type.split(".")[0]  # user, goal, task, code, ai
    year = timestamp.year
    month = f"{timestamp.month:02d}"
    day = f"{timestamp.day:02d}"
    date_str = timestamp.strftime("%Y-%m-%d")

    return f"{base_path}/{year}/{month}/{category}_events_{date_str}.parquet"


# ==================== EJEMPLO DE USO ====================

"""
# 1. Crear evento
from datetime import datetime
import uuid

event = GoalEvent(
    event_id=str(uuid.uuid4()),
    user_id="user-123",
    event_type="goal.created",
    created_at=datetime.utcnow(),
    goal_id="goal-456",
    title="Aprender FastAPI",
    status="pending",
    priority="high",
    progress_percentage=0.0,
    ai_generated=True,
    course_id="course-789"
)

# 2. Convertir a diccionario
event_dict = event.to_dict()

# 3. Escribir a Parquet
import pyarrow as pa
import pyarrow.parquet as pq

table = pa.Table.from_pylist([event_dict], schema=GOAL_EVENT_SCHEMA)
pq.write_table(table, "goal_events.parquet")

# 4. Leer de Parquet
table = pq.read_table("goal_events.parquet")
df = table.to_pandas()
print(df)

# 5. Query con filtros
import pyarrow.dataset as ds

dataset = ds.dataset("./data/storage/events", format="parquet", partitioning="hive")

# Filtrar por fecha y tipo
filtered = dataset.to_table(
    filter=(
        (ds.field("year") == 2024) &
        (ds.field("month") == 1) &
        (ds.field("event_type") == "goal.created")
    )
)

df = filtered.to_pandas()
"""

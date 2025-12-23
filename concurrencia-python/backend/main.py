"""
CONCURRENCIA Y PARALELISMO EN PYTHON - FastAPI
Ejemplos prácticos de todos los conceptos de concurrencia

Temas cubiertos:
1. IO-bound vs CPU-bound
2. Threading vs Multiprocessing
3. Async/await
4. GIL (Global Interpreter Lock)
5. Race conditions
6. Deadlocks
7. Starvation
8. Semáforos y Locks
9. Colas (Queues)
10. run_in_executor
11. Observabilidad
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import time
import asyncio
from datetime import datetime

# Importar ejemplos
from examples.io_bound import IOBoundExamples
from examples.cpu_bound import CPUBoundExamples
from examples.threading_examples import ThreadingExamples
from examples.multiprocessing_examples import MultiprocessingExamples
from examples.async_examples import AsyncExamples
from examples.race_conditions import RaceConditionExamples
from examples.deadlocks import DeadlockExamples
from examples.queues_examples import QueueExamples
from examples.semaphores import SemaphoreExamples
from utils.observability import metrics_collector, get_system_metrics

app = FastAPI(
    title="Concurrencia y Paralelismo en Python",
    description="Ejemplos prácticos de concurrencia, paralelismo y observabilidad",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar ejemplos
io_bound = IOBoundExamples()
cpu_bound = CPUBoundExamples()
threading_ex = ThreadingExamples()
multiproc_ex = MultiprocessingExamples()
async_ex = AsyncExamples()
race_ex = RaceConditionExamples()
deadlock_ex = DeadlockExamples()
queue_ex = QueueExamples()
semaphore_ex = SemaphoreExamples()

# Modelos
class TaskRequest(BaseModel):
    iterations: int = 5
    delay: float = 1.0

class WorkerRequest(BaseModel):
    num_workers: int = 4
    tasks_per_worker: int = 10

# ============================================================================
# ENDPOINTS - IO-BOUND
# ============================================================================

@app.get("/")
async def root():
    """Información de la API"""
    return {
        "message": "API de Concurrencia y Paralelismo en Python",
        "version": "1.0.0",
        "endpoints": {
            "io_bound": "/io-bound/*",
            "cpu_bound": "/cpu-bound/*",
            "threading": "/threading/*",
            "multiprocessing": "/multiprocessing/*",
            "async": "/async/*",
            "race_conditions": "/race-conditions/*",
            "deadlocks": "/deadlocks/*",
            "queues": "/queues/*",
            "semaphores": "/semaphores/*",
            "observability": "/metrics"
        }
    }

@app.post("/io-bound/sequential")
async def io_bound_sequential(request: TaskRequest):
    """
    IO-bound SECUENCIAL - Bloquea el event loop
    Ejemplo de lo que NO se debe hacer en async
    """
    start = time.time()
    results = io_bound.sequential_requests(request.iterations)
    duration = time.time() - start

    metrics_collector.record_execution("io_bound_sequential", duration)

    return {
        "method": "sequential",
        "iterations": request.iterations,
        "duration": duration,
        "results": results,
        "note": "❌ Bloquea el event loop - NO recomendado en async"
    }

@app.post("/io-bound/threading")
async def io_bound_threading(request: TaskRequest):
    """
    IO-bound con THREADING - Libera el GIL durante IO
    Bueno para operaciones IO-bound
    """
    start = time.time()
    results = await asyncio.get_event_loop().run_in_executor(
        None,
        io_bound.threading_requests,
        request.iterations
    )
    duration = time.time() - start

    metrics_collector.record_execution("io_bound_threading", duration)

    return {
        "method": "threading",
        "iterations": request.iterations,
        "duration": duration,
        "results": results,
        "note": "✅ Usa threads - ideal para IO-bound"
    }

@app.post("/io-bound/async")
async def io_bound_async(request: TaskRequest):
    """
    IO-bound con ASYNC/AWAIT - Mejor opción
    No bloquea, usa cooperative multitasking
    """
    start = time.time()
    results = await io_bound.async_requests(request.iterations)
    duration = time.time() - start

    metrics_collector.record_execution("io_bound_async", duration)

    return {
        "method": "async/await",
        "iterations": request.iterations,
        "duration": duration,
        "results": results,
        "note": "✅✅ Mejor opción - async nativo"
    }

# ============================================================================
# ENDPOINTS - CPU-BOUND
# ============================================================================

@app.post("/cpu-bound/sequential")
async def cpu_bound_sequential(request: TaskRequest):
    """
    CPU-bound SECUENCIAL - Bloquea completamente
    """
    start = time.time()
    result = await asyncio.get_event_loop().run_in_executor(
        None,
        cpu_bound.sequential_calculation,
        request.iterations
    )
    duration = time.time() - start

    metrics_collector.record_execution("cpu_bound_sequential", duration)

    return {
        "method": "sequential",
        "iterations": request.iterations,
        "result": result,
        "duration": duration,
        "note": "❌ Muy lento - ejecuta uno por uno"
    }

@app.post("/cpu-bound/threading")
async def cpu_bound_threading(request: TaskRequest):
    """
    CPU-bound con THREADING - NO mejora performance por el GIL
    Demuestra las limitaciones del GIL
    """
    start = time.time()
    result = await asyncio.get_event_loop().run_in_executor(
        None,
        cpu_bound.threading_calculation,
        request.iterations
    )
    duration = time.time() - start

    metrics_collector.record_execution("cpu_bound_threading", duration)

    return {
        "method": "threading",
        "iterations": request.iterations,
        "result": result,
        "duration": duration,
        "note": "❌ No mejora por el GIL - threads no ayudan en CPU-bound"
    }

@app.post("/cpu-bound/multiprocessing")
async def cpu_bound_multiprocessing(request: TaskRequest):
    """
    CPU-bound con MULTIPROCESSING - Evita el GIL
    Mejor opción para tareas CPU-bound
    """
    start = time.time()
    result = await asyncio.get_event_loop().run_in_executor(
        None,
        cpu_bound.multiprocessing_calculation,
        request.iterations
    )
    duration = time.time() - start

    metrics_collector.record_execution("cpu_bound_multiprocessing", duration)

    return {
        "method": "multiprocessing",
        "iterations": request.iterations,
        "result": result,
        "duration": duration,
        "note": "✅✅ Evita el GIL - mejor para CPU-bound"
    }

# ============================================================================
# ENDPOINTS - RACE CONDITIONS
# ============================================================================

@app.post("/race-conditions/unsafe")
async def race_conditions_unsafe(request: WorkerRequest):
    """
    Demuestra RACE CONDITION sin protección
    Múltiples threads modificando la misma variable
    """
    start = time.time()
    result = await asyncio.get_event_loop().run_in_executor(
        None,
        race_ex.unsafe_counter,
        request.num_workers,
        request.tasks_per_worker
    )
    duration = time.time() - start

    return {
        "method": "unsafe_race_condition",
        "workers": request.num_workers,
        "tasks_per_worker": request.tasks_per_worker,
        "expected": request.num_workers * request.tasks_per_worker,
        "actual": result,
        "lost_increments": (request.num_workers * request.tasks_per_worker) - result,
        "duration": duration,
        "note": "❌ Race condition - resultado incorrecto"
    }

@app.post("/race-conditions/lock")
async def race_conditions_lock(request: WorkerRequest):
    """
    Protege contra race conditions usando LOCK
    """
    start = time.time()
    result = await asyncio.get_event_loop().run_in_executor(
        None,
        race_ex.safe_counter_lock,
        request.num_workers,
        request.tasks_per_worker
    )
    duration = time.time() - start

    return {
        "method": "lock_protected",
        "workers": request.num_workers,
        "tasks_per_worker": request.tasks_per_worker,
        "expected": request.num_workers * request.tasks_per_worker,
        "actual": result,
        "lost_increments": 0,
        "duration": duration,
        "note": "✅ Protegido con Lock - resultado correcto"
    }

# ============================================================================
# ENDPOINTS - DEADLOCKS
# ============================================================================

@app.post("/deadlocks/demonstrate")
async def demonstrate_deadlock():
    """
    Demuestra un DEADLOCK (con timeout para no bloquear)
    """
    start = time.time()
    result = await asyncio.get_event_loop().run_in_executor(
        None,
        deadlock_ex.demonstrate_deadlock
    )
    duration = time.time() - start

    return {
        "method": "deadlock_demonstration",
        "result": result,
        "duration": duration,
        "note": "❌ Deadlock detectado - threads esperando mutuamente"
    }

@app.post("/deadlocks/prevent")
async def prevent_deadlock():
    """
    Previene DEADLOCK usando orden consistente de locks
    """
    start = time.time()
    result = await asyncio.get_event_loop().run_in_executor(
        None,
        deadlock_ex.prevent_deadlock
    )
    duration = time.time() - start

    return {
        "method": "deadlock_prevention",
        "result": result,
        "duration": duration,
        "note": "✅ Sin deadlock - locks adquiridos en orden"
    }

# ============================================================================
# ENDPOINTS - SEMÁFOROS
# ============================================================================

@app.post("/semaphores/rate-limit")
async def semaphore_rate_limit(request: WorkerRequest):
    """
    Usa SEMÁFORO para limitar concurrencia
    """
    start = time.time()
    result = await semaphore_ex.rate_limited_tasks(
        request.num_workers,
        max_concurrent=3
    )
    duration = time.time() - start

    return {
        "method": "semaphore_rate_limit",
        "total_tasks": request.num_workers,
        "max_concurrent": 3,
        "results": result,
        "duration": duration,
        "note": "✅ Semáforo limita a 3 tareas concurrentes"
    }

# ============================================================================
# ENDPOINTS - COLAS
# ============================================================================

@app.post("/queues/producer-consumer")
async def queue_producer_consumer(request: WorkerRequest):
    """
    Patrón PRODUCTOR-CONSUMIDOR con Queue
    """
    start = time.time()
    result = await asyncio.get_event_loop().run_in_executor(
        None,
        queue_ex.producer_consumer_pattern,
        request.num_workers,
        request.tasks_per_worker
    )
    duration = time.time() - start

    return {
        "method": "producer_consumer",
        "producers": 2,
        "consumers": request.num_workers,
        "total_tasks": result["processed"],
        "duration": duration,
        "note": "✅ Queue coordina productores y consumidores"
    }

# ============================================================================
# ENDPOINTS - ASYNC AVANZADO
# ============================================================================

@app.post("/async/gather")
async def async_gather(request: TaskRequest):
    """
    asyncio.gather() - Ejecutar múltiples coroutines
    """
    start = time.time()
    results = await async_ex.gather_example(request.iterations)
    duration = time.time() - start

    return {
        "method": "asyncio.gather",
        "tasks": request.iterations,
        "results": results,
        "duration": duration,
        "note": "✅ Ejecuta coroutines concurrentemente"
    }

@app.post("/async/run-in-executor")
async def async_run_in_executor(request: TaskRequest):
    """
    run_in_executor - Mezclar async con código bloqueante
    """
    start = time.time()
    results = await async_ex.run_in_executor_example(request.iterations)
    duration = time.time() - start

    return {
        "method": "run_in_executor",
        "tasks": request.iterations,
        "results": results,
        "duration": duration,
        "note": "✅ Ejecuta código bloqueante sin bloquear event loop"
    }

# ============================================================================
# ENDPOINTS - OBSERVABILIDAD
# ============================================================================

@app.get("/metrics")
async def get_metrics():
    """
    Métricas de observabilidad
    """
    return metrics.get_metrics()

@app.get("/metrics/prometheus")
async def prometheus_metrics():
    """
    Métricas en formato Prometheus
    """
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return StreamingResponse(
        iter([generate_latest()]),
        media_type=CONTENT_TYPE_LATEST
    )

# ============================================================================
# OBSERVABILIDAD
# ============================================================================

@app.get("/metrics/summary")
async def get_metrics_summary():
    """Resumen de todas las métricas recolectadas"""
    return metrics_collector.get_metrics_summary()

@app.get("/metrics/operation/{operation_name}")
async def get_operation_stats(operation_name: str):
    """Estadísticas de una operación específica"""
    return metrics_collector.get_operation_stats(operation_name)

@app.get("/metrics/system")
async def get_system_info():
    """Información del sistema y proceso actual"""
    return get_system_metrics()

@app.post("/metrics/reset")
async def reset_metrics():
    """Limpiar todas las métricas"""
    metrics_collector.reset()
    return {"message": "Metrics reset successfully"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "gil_info": {
            "note": "Python usa GIL - solo un thread ejecuta bytecode a la vez",
            "io_bound": "Threading libera GIL durante IO - bueno",
            "cpu_bound": "Threading NO ayuda - usar multiprocessing"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

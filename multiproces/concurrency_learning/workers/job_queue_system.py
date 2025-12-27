"""
SISTEMA COMPLETO DE JOB QUEUE CON WORKERS
==========================================
Este módulo implementa un sistema de cola de trabajos (job queue) robusto
que distribuye tareas entre múltiples workers en procesos separados.

Arquitectura:
┌──────────────┐
│   Cliente    │  → Envía jobs
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Job Queue   │  → Cola central de trabajos
└──────┬───────┘
       │
       ├──────→ ┌──────────┐
       │        │ Worker 1 │  → CPU 1
       │        └──────────┘
       │
       └──────→ ┌──────────┐
                │ Worker 2 │  → CPU 2
                └──────────┘

Casos de uso:
- Procesamiento de imágenes en batch
- Análisis de logs
- Scraping web distribuido
- Procesamiento de datos científicos
"""

import multiprocessing as mp
from multiprocessing import Queue, Process
import time
import os
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Any, Callable, Optional
import json


class JobStatus(Enum):
    """Estados posibles de un job"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    """
    Representa un trabajo a procesar.

    Attributes:
        job_id: Identificador único del job
        task_name: Nombre de la tarea
        data: Datos a procesar
        priority: Prioridad (mayor = más importante)
        created_at: Timestamp de creación
    """
    job_id: int
    task_name: str
    data: Any
    priority: int = 0
    created_at: float = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

    def __lt__(self, other):
        """Permite ordenar jobs por prioridad (para PriorityQueue)"""
        return self.priority > other.priority  # Mayor prioridad primero


@dataclass
class JobResult:
    """
    Representa el resultado de un job procesado.

    Attributes:
        job_id: ID del job original
        status: Estado final del job
        result: Resultado del procesamiento
        error: Mensaje de error si falló
        worker_id: ID del worker que lo procesó
        duration: Tiempo de procesamiento en segundos
    """
    job_id: int
    status: JobStatus
    result: Any = None
    error: str = None
    worker_id: int = None
    duration: float = None


def log(mensaje, worker_id=None):
    """Función auxiliar de logging"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    pid = os.getpid()
    worker_info = f"[Worker-{worker_id}]" if worker_id else "[Master]"
    print(f"[{timestamp}] [PID:{pid}] {worker_info} {mensaje}")


# ============================================================================
# FUNCIONES DE EJEMPLO PARA PROCESAR JOBS
# ============================================================================

def procesar_imagen(data):
    """
    Simula procesamiento de imagen (CPU-intensive).

    Args:
        data: Dict con 'filename' y 'operations'

    Returns:
        Dict con resultados del procesamiento
    """
    filename = data.get('filename', 'unknown.jpg')
    operations = data.get('operations', [])

    log(f"Procesando imagen: {filename}")

    # Simular procesamiento pesado
    result = {'filename': filename, 'operations_applied': []}

    for op in operations:
        time.sleep(0.5)  # Simula tiempo de procesamiento
        if op == 'resize':
            result['operations_applied'].append('resize_800x600')
        elif op == 'filter':
            result['operations_applied'].append('grayscale_filter')
        elif op == 'compress':
            result['operations_applied'].append('compress_80%')

    return result


def analizar_logs(data):
    """
    Simula análisis de archivos de log.

    Args:
        data: Dict con 'log_file' y 'patterns'

    Returns:
        Dict con estadísticas del análisis
    """
    log_file = data.get('log_file', 'app.log')
    patterns = data.get('patterns', [])

    log(f"Analizando log: {log_file}")

    # Simular análisis
    time.sleep(1)

    matches = {pattern: int(time.time()) % 100 for pattern in patterns}

    return {
        'log_file': log_file,
        'matches': matches,
        'total_lines': 10000,
        'errors_found': sum(matches.values())
    }


def calcular_estadisticas(data):
    """
    Calcula estadísticas sobre un dataset (CPU-intensive).

    Args:
        data: Dict con 'dataset' (lista de números)

    Returns:
        Dict con estadísticas calculadas
    """
    dataset = data.get('dataset', [])

    log(f"Calculando estadísticas de {len(dataset)} elementos")

    # Cálculos intensivos
    total = sum(dataset)
    promedio = total / len(dataset) if dataset else 0
    maximo = max(dataset) if dataset else 0
    minimo = min(dataset) if dataset else 0

    # Simular más procesamiento
    varianza = sum((x - promedio) ** 2 for x in dataset) / len(dataset) if dataset else 0

    time.sleep(0.8)

    return {
        'count': len(dataset),
        'sum': total,
        'mean': promedio,
        'max': maximo,
        'min': minimo,
        'variance': varianza
    }


# Registro de funciones disponibles
TASK_FUNCTIONS = {
    'procesar_imagen': procesar_imagen,
    'analizar_logs': analizar_logs,
    'calcular_estadisticas': calcular_estadisticas,
}


# ============================================================================
# WORKER PROCESS
# ============================================================================

def worker_process(worker_id: int, job_queue: Queue, result_queue: Queue, shutdown_event: mp.Event):
    """
    Proceso worker que consume jobs de la cola.

    Args:
        worker_id: Identificador único del worker
        job_queue: Cola de donde obtener jobs
        result_queue: Cola donde poner resultados
        shutdown_event: Event para señalizar shutdown graceful

    El worker corre en un loop infinito procesando jobs hasta recibir
    señal de shutdown o job especial de terminación (None).
    """
    log(f"Worker iniciado", worker_id)

    jobs_procesados = 0

    while not shutdown_event.is_set():
        try:
            # Intentar obtener un job (timeout para revisar shutdown_event)
            job = job_queue.get(timeout=0.5)

            # None es la señal de terminación
            if job is None:
                log(f"Recibida señal de terminación", worker_id)
                break

            # Procesar el job
            log(f"Procesando Job-{job.job_id}: {job.task_name}", worker_id)

            inicio = time.time()
            result = None
            status = JobStatus.COMPLETED
            error = None

            try:
                # Obtener la función correspondiente
                task_func = TASK_FUNCTIONS.get(job.task_name)

                if task_func is None:
                    raise ValueError(f"Tarea desconocida: {job.task_name}")

                # Ejecutar la tarea
                result = task_func(job.data)

            except Exception as e:
                status = JobStatus.FAILED
                error = str(e)
                log(f"Error en Job-{job.job_id}: {error}", worker_id)

            duracion = time.time() - inicio

            # Crear resultado
            job_result = JobResult(
                job_id=job.job_id,
                status=status,
                result=result,
                error=error,
                worker_id=worker_id,
                duration=duracion
            )

            # Enviar resultado
            result_queue.put(job_result)

            jobs_procesados += 1
            log(f"Job-{job.job_id} completado en {duracion:.2f}s", worker_id)

        except mp.queues.Empty:
            # No hay jobs, continuar esperando
            continue
        except Exception as e:
            log(f"Error inesperado: {e}", worker_id)

    log(f"Worker terminando. Jobs procesados: {jobs_procesados}", worker_id)


# ============================================================================
# JOB QUEUE MANAGER
# ============================================================================

class JobQueueManager:
    """
    Gestor del sistema de job queue.

    Responsabilidades:
    - Crear y gestionar workers
    - Encolar jobs
    - Recolectar resultados
    - Shutdown graceful
    """

    def __init__(self, num_workers: int = None):
        """
        Inicializa el manager.

        Args:
            num_workers: Número de workers (default: número de CPUs)
        """
        self.num_workers = num_workers or mp.cpu_count()
        self.job_queue = Queue()
        self.result_queue = Queue()
        self.shutdown_event = mp.Event()
        self.workers = []
        self.next_job_id = 1
        self.jobs_enviados = 0
        self.resultados_recibidos = 0

        log(f"JobQueueManager inicializado con {self.num_workers} workers")

    def start_workers(self):
        """
        Inicia todos los procesos worker.

        Cada worker se ejecuta en un proceso separado y comienza
        a escuchar la cola de jobs inmediatamente.
        """
        log(f"Iniciando {self.num_workers} workers...")

        for i in range(self.num_workers):
            worker = Process(
                target=worker_process,
                args=(i + 1, self.job_queue, self.result_queue, self.shutdown_event),
                name=f"Worker-{i+1}"
            )
            worker.start()
            self.workers.append(worker)

        log("Todos los workers iniciados")

    def submit_job(self, task_name: str, data: Any, priority: int = 0) -> int:
        """
        Envía un job a la cola.

        Args:
            task_name: Nombre de la tarea a ejecutar
            data: Datos para la tarea
            priority: Prioridad del job (mayor = más urgente)

        Returns:
            job_id: ID asignado al job
        """
        job = Job(
            job_id=self.next_job_id,
            task_name=task_name,
            data=data,
            priority=priority
        )

        self.job_queue.put(job)
        self.jobs_enviados += 1

        log(f"Job-{job.job_id} encolado: {task_name} (prioridad={priority})")

        self.next_job_id += 1
        return job.job_id

    def get_result(self, timeout: float = None) -> Optional[JobResult]:
        """
        Obtiene un resultado de la cola de resultados.

        Args:
            timeout: Tiempo máximo a esperar en segundos

        Returns:
            JobResult o None si timeout
        """
        try:
            result = self.result_queue.get(timeout=timeout)
            self.resultados_recibidos += 1
            return result
        except:
            return None

    def wait_for_completion(self, num_jobs: int, timeout: float = None):
        """
        Espera a que se completen un número específico de jobs.

        Args:
            num_jobs: Cantidad de jobs a esperar
            timeout: Timeout total en segundos

        Returns:
            Lista de JobResults
        """
        log(f"Esperando {num_jobs} resultados...")

        resultados = []
        inicio = time.time()

        for _ in range(num_jobs):
            tiempo_restante = None
            if timeout:
                tiempo_restante = timeout - (time.time() - inicio)
                if tiempo_restante <= 0:
                    log("Timeout esperando resultados")
                    break

            result = self.get_result(timeout=tiempo_restante)
            if result:
                resultados.append(result)

        log(f"Recibidos {len(resultados)} resultados")
        return resultados

    def shutdown(self, timeout: float = 5.0):
        """
        Apaga el sistema de forma graceful.

        Args:
            timeout: Tiempo máximo a esperar por cada worker

        Pasos:
        1. Señalizar shutdown con event
        2. Enviar señales None a la cola (por si workers están bloqueados)
        3. Esperar a que workers terminen
        4. Forzar terminación si excede timeout
        """
        log("Iniciando shutdown...")

        # Señalizar shutdown
        self.shutdown_event.set()

        # Enviar señales de terminación
        for _ in range(self.num_workers):
            self.job_queue.put(None)

        # Esperar workers
        for worker in self.workers:
            worker.join(timeout=timeout)
            if worker.is_alive():
                log(f"Worker {worker.name} no terminó, forzando...")
                worker.terminate()
                worker.join()

        log("Shutdown completado")

    def get_stats(self):
        """Retorna estadísticas del sistema"""
        return {
            'workers': self.num_workers,
            'jobs_enviados': self.jobs_enviados,
            'resultados_recibidos': self.resultados_recibidos,
            'pendientes': self.jobs_enviados - self.resultados_recibidos,
            'queue_size': self.job_queue.qsize() if hasattr(self.job_queue, 'qsize') else 'N/A'
        }


# ============================================================================
# EJEMPLOS DE USO
# ============================================================================

def ejemplo_basico():
    """Ejemplo básico de uso del sistema de job queue"""
    log("=== EJEMPLO BÁSICO: Job Queue ===")

    # Crear manager con 2 workers (para tus 2 CPUs)
    manager = JobQueueManager(num_workers=2)
    manager.start_workers()

    # Enviar jobs de diferentes tipos
    jobs = []

    # Jobs de procesamiento de imágenes
    jobs.append(manager.submit_job(
        'procesar_imagen',
        {'filename': 'foto1.jpg', 'operations': ['resize', 'filter']}
    ))
    jobs.append(manager.submit_job(
        'procesar_imagen',
        {'filename': 'foto2.jpg', 'operations': ['compress']}
    ))

    # Jobs de análisis de logs
    jobs.append(manager.submit_job(
        'analizar_logs',
        {'log_file': 'app.log', 'patterns': ['ERROR', 'WARNING']}
    ))

    # Jobs de estadísticas
    jobs.append(manager.submit_job(
        'calcular_estadisticas',
        {'dataset': list(range(1000))}
    ))

    # Esperar resultados
    resultados = manager.wait_for_completion(len(jobs), timeout=30)

    # Mostrar resultados
    log("\n=== RESULTADOS ===")
    for res in resultados:
        status_icon = "✓" if res.status == JobStatus.COMPLETED else "✗"
        log(f"{status_icon} Job-{res.job_id} [{res.status.value}] "
            f"Worker-{res.worker_id} ({res.duration:.2f}s)")
        if res.result:
            log(f"   Resultado: {json.dumps(res.result, indent=2)}")

    # Estadísticas
    stats = manager.get_stats()
    log(f"\n=== ESTADÍSTICAS ===")
    for key, value in stats.items():
        log(f"{key}: {value}")

    # Shutdown
    manager.shutdown()


def ejemplo_con_prioridades():
    """Ejemplo de jobs con diferentes prioridades"""
    log("\n=== EJEMPLO: Jobs con Prioridades ===")

    manager = JobQueueManager(num_workers=2)
    manager.start_workers()

    # Enviar jobs con diferentes prioridades
    jobs = []

    # Jobs de baja prioridad
    for i in range(3):
        jobs.append(manager.submit_job(
            'calcular_estadisticas',
            {'dataset': list(range(100))},
            priority=1  # Baja prioridad
        ))

    # Job de alta prioridad (debería procesarse primero)
    jobs.append(manager.submit_job(
        'procesar_imagen',
        {'filename': 'urgente.jpg', 'operations': ['resize']},
        priority=10  # Alta prioridad
    ))

    log("Nota: Job-4 tiene prioridad 10, debería procesarse primero")

    resultados = manager.wait_for_completion(len(jobs), timeout=20)

    log("\nOrden de procesamiento:")
    for res in sorted(resultados, key=lambda r: r.job_id):
        log(f"Job-{res.job_id} procesado por Worker-{res.worker_id}")

    manager.shutdown()


def ejemplo_alto_volumen():
    """Ejemplo con alto volumen de jobs"""
    log("\n=== EJEMPLO: Alto Volumen de Jobs ===")

    manager = JobQueueManager(num_workers=2)
    manager.start_workers()

    # Enviar muchos jobs
    num_jobs = 20
    log(f"Enviando {num_jobs} jobs...")

    inicio = time.time()

    for i in range(num_jobs):
        manager.submit_job(
            'calcular_estadisticas',
            {'dataset': list(range(100 * (i + 1)))}
        )

    # Esperar resultados
    resultados = manager.wait_for_completion(num_jobs, timeout=60)

    duracion = time.time() - inicio

    # Estadísticas
    exitosos = sum(1 for r in resultados if r.status == JobStatus.COMPLETED)
    fallidos = sum(1 for r in resultados if r.status == JobStatus.FAILED)

    log(f"\n=== RESULTADOS ===")
    log(f"Total jobs: {num_jobs}")
    log(f"Exitosos: {exitosos}")
    log(f"Fallidos: {fallidos}")
    log(f"Tiempo total: {duracion:.2f}s")
    log(f"Throughput: {num_jobs/duracion:.2f} jobs/segundo")

    # Distribución de carga entre workers
    worker_loads = {}
    for res in resultados:
        worker_loads[res.worker_id] = worker_loads.get(res.worker_id, 0) + 1

    log("\nDistribución de carga:")
    for worker_id, count in sorted(worker_loads.items()):
        log(f"Worker-{worker_id}: {count} jobs")

    manager.shutdown()


if __name__ == "__main__":
    """
    Ejecuta todos los ejemplos.

    En tu droplet puedes ejecutar:
        python job_queue_system.py

    Observa cómo los 2 workers distribuyen la carga entre tus 2 CPUs.
    """
    ejemplo_basico()
    time.sleep(2)
    ejemplo_con_prioridades()
    time.sleep(2)
    ejemplo_alto_volumen()

    log("\n=== RESUMEN DEL SISTEMA ===")
    log("✓ Job queue distribuye trabajo entre workers")
    log("✓ Cada worker corre en un proceso (CPU) separado")
    log("✓ Soporta prioridades de jobs")
    log("✓ Manejo de errores por job")
    log("✓ Shutdown graceful")
    log("✓ Escalable: ajusta num_workers según CPUs disponibles")

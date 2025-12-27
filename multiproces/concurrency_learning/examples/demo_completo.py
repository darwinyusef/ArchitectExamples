"""
DEMO COMPLETO: Concurrencia y Paralelismo
==========================================
Este script demuestra todos los conceptos del proyecto en un ejemplo práctico.

Simula un sistema de procesamiento de imágenes que:
1. Recibe imágenes para procesar
2. Usa workers multiprocessing para procesamiento CPU-intensive
3. Monitorea el uso de CPU en tiempo real
4. Muestra estadísticas de rendimiento

Esto replica un escenario real de producción.
"""

import multiprocessing as mp
from multiprocessing import Queue, Process
import time
import psutil
import os
from datetime import datetime
from typing import List, Dict
import random


def log(mensaje, source="MAIN"):
    """Función auxiliar de logging"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    pid = os.getpid()
    print(f"[{timestamp}] [PID:{pid}] [{source}] {mensaje}")


# ============================================================================
# SIMULACIÓN DE PROCESAMIENTO DE IMÁGENES
# ============================================================================

class ImagenJob:
    """Representa una imagen a procesar"""
    def __init__(self, job_id: int, filename: str, operaciones: List[str]):
        self.job_id = job_id
        self.filename = filename
        self.operaciones = operaciones
        self.timestamp = time.time()


def procesar_imagen(imagen: ImagenJob) -> Dict:
    """
    Procesa una imagen aplicando operaciones.

    Esta función simula trabajo CPU-intensive real:
    - Decodificación de imagen
    - Redimensionamiento
    - Aplicación de filtros
    - Compresión

    Args:
        imagen: ImagenJob con datos de la imagen

    Returns:
        Dict con resultados del procesamiento
    """
    pid = os.getpid()
    worker_name = mp.current_process().name

    log(f"Procesando {imagen.filename}", worker_name)

    resultados = {
        'job_id': imagen.job_id,
        'filename': imagen.filename,
        'worker_pid': pid,
        'operaciones_aplicadas': [],
        'tiempo_por_operacion': {}
    }

    for operacion in imagen.operaciones:
        inicio_op = time.time()

        if operacion == 'resize':
            # Simular redimensionamiento (CPU-intensive)
            log(f"  └─ Redimensionando {imagen.filename}", worker_name)
            resultado = simular_resize()
            resultados['operaciones_aplicadas'].append('resize_800x600')

        elif operacion == 'filter_blur':
            # Simular filtro de desenfoque
            log(f"  └─ Aplicando blur a {imagen.filename}", worker_name)
            resultado = simular_filtro_blur()
            resultados['operaciones_aplicadas'].append('blur_gaussian')

        elif operacion == 'filter_sharpen':
            # Simular filtro de nitidez
            log(f"  └─ Aplicando sharpen a {imagen.filename}", worker_name)
            resultado = simular_filtro_sharpen()
            resultados['operaciones_aplicadas'].append('sharpen')

        elif operacion == 'compress':
            # Simular compresión
            log(f"  └─ Comprimiendo {imagen.filename}", worker_name)
            resultado = simular_compresion()
            resultados['operaciones_aplicadas'].append('compress_jpeg_80')

        elif operacion == 'thumbnail':
            # Simular creación de miniatura
            log(f"  └─ Creando thumbnail de {imagen.filename}", worker_name)
            resultado = simular_thumbnail()
            resultados['operaciones_aplicadas'].append('thumbnail_200x200')

        duracion_op = time.time() - inicio_op
        resultados['tiempo_por_operacion'][operacion] = duracion_op

    log(f"✓ Completado: {imagen.filename}", worker_name)

    return resultados


def simular_resize():
    """Simula redimensionamiento de imagen (CPU-intensive)"""
    # Operaciones matemáticas que simulan interpolación bilineal
    total = 0
    for i in range(500000):
        total += (i ** 0.5) * (i % 100)
    time.sleep(0.3)
    return total


def simular_filtro_blur():
    """Simula aplicación de filtro de desenfoque"""
    # Simula convolución de matriz
    total = 0
    for i in range(300000):
        total += sum(range(i % 100)) / (i + 1)
    time.sleep(0.2)
    return total


def simular_filtro_sharpen():
    """Simula filtro de nitidez"""
    total = 0
    for i in range(400000):
        total += (i ** 2) % 1000
    time.sleep(0.25)
    return total


def simular_compresion():
    """Simula compresión JPEG"""
    total = 0
    for i in range(350000):
        total += abs(i - 1000) * (i % 50)
    time.sleep(0.2)
    return total


def simular_thumbnail():
    """Simula creación de thumbnail"""
    total = 0
    for i in range(200000):
        total += i ** 0.5
    time.sleep(0.15)
    return total


# ============================================================================
# WORKER PROCESS
# ============================================================================

def worker_process(worker_id: int, job_queue: Queue, result_queue: Queue,
                   stats_queue: Queue, shutdown_event: mp.Event):
    """
    Proceso worker que consume jobs de procesamiento de imágenes.

    Args:
        worker_id: ID del worker
        job_queue: Cola de jobs entrantes
        result_queue: Cola para resultados
        stats_queue: Cola para estadísticas
        shutdown_event: Event para shutdown graceful
    """
    worker_name = f"Worker-{worker_id}"
    log(f"Worker iniciado en CPU", worker_name)

    # Estadísticas del worker
    jobs_procesados = 0
    tiempo_total_procesamiento = 0

    # Intentar configurar CPU affinity (asignar worker a CPU específico)
    try:
        # En un sistema con 2 CPUs, asignar cada worker a un CPU
        cpu_id = (worker_id - 1) % mp.cpu_count()
        process = psutil.Process()
        process.cpu_affinity([cpu_id])
        log(f"Asignado a CPU {cpu_id}", worker_name)
    except (AttributeError, psutil.AccessDenied):
        log(f"No se pudo configurar CPU affinity", worker_name)

    while not shutdown_event.is_set():
        try:
            # Obtener job con timeout
            job = job_queue.get(timeout=0.5)

            if job is None:  # Señal de terminación
                log("Recibida señal de terminación", worker_name)
                break

            # Procesar imagen
            inicio = time.time()
            resultado = procesar_imagen(job)
            duracion = time.time() - inicio

            resultado['duracion_total'] = duracion
            resultado['worker_id'] = worker_id

            # Enviar resultado
            result_queue.put(resultado)

            # Actualizar estadísticas
            jobs_procesados += 1
            tiempo_total_procesamiento += duracion

            # Enviar stats
            stats_queue.put({
                'worker_id': worker_id,
                'jobs_procesados': jobs_procesados,
                'tiempo_total': tiempo_total_procesamiento,
                'promedio': tiempo_total_procesamiento / jobs_procesados
            })

        except mp.queues.Empty:
            continue
        except Exception as e:
            log(f"Error: {e}", worker_name)

    log(f"Terminando. Jobs procesados: {jobs_procesados}", worker_name)


# ============================================================================
# MONITOR DE RENDIMIENTO
# ============================================================================

def monitor_process(stats_queue: Queue, shutdown_event: mp.Event, num_workers: int):
    """
    Proceso que monitorea rendimiento del sistema.

    Args:
        stats_queue: Cola de estadísticas de workers
        shutdown_event: Event de shutdown
        num_workers: Número total de workers
    """
    log("Monitor de rendimiento iniciado", "MONITOR")

    worker_stats = {i: {'jobs': 0, 'tiempo': 0} for i in range(1, num_workers + 1)}

    while not shutdown_event.is_set():
        try:
            # Obtener estadísticas
            stats = stats_queue.get(timeout=1.0)

            worker_id = stats['worker_id']
            worker_stats[worker_id] = {
                'jobs': stats['jobs_procesados'],
                'tiempo': stats['tiempo_total'],
                'promedio': stats['promedio']
            }

            # Mostrar dashboard
            mostrar_dashboard(worker_stats)

        except mp.queues.Empty:
            continue
        except Exception as e:
            log(f"Error en monitor: {e}", "MONITOR")

    log("Monitor terminando", "MONITOR")


def mostrar_dashboard(worker_stats: Dict):
    """Muestra dashboard de rendimiento en consola"""
    # Limpiar pantalla (comentar si no quieres clear)
    # os.system('clear' if os.name != 'nt' else 'cls')

    print("\n" + "="*70)
    print("DASHBOARD DE RENDIMIENTO")
    print("="*70)

    total_jobs = sum(s['jobs'] for s in worker_stats.values())
    total_tiempo = sum(s['tiempo'] for s in worker_stats.values())

    print(f"\nTOTAL: {total_jobs} jobs procesados | {total_tiempo:.1f}s tiempo total")
    print("\nEstadísticas por Worker:")
    print("-"*70)

    for worker_id, stats in sorted(worker_stats.items()):
        if stats['jobs'] > 0:
            barra = "█" * int(stats['jobs'] / max(1, total_jobs) * 40)
            print(f"Worker-{worker_id}: {stats['jobs']:3d} jobs [{barra:<40}] "
                  f"Avg: {stats['promedio']:.2f}s")

    # Uso de CPU actual
    cpu_percent = psutil.cpu_percent(interval=0, percpu=True)
    print(f"\nUso de CPU por core:")
    for i, percent in enumerate(cpu_percent):
        barra = "█" * int(percent / 100 * 30)
        print(f"  CPU{i}: [{barra:<30}] {percent:5.1f}%")

    print("="*70)


# ============================================================================
# SISTEMA PRINCIPAL
# ============================================================================

class SistemaProcesamiento:
    """
    Sistema completo de procesamiento de imágenes con workers.

    Coordina:
    - Workers de procesamiento
    - Monitor de rendimiento
    - Generación de jobs
    - Recolección de resultados
    """

    def __init__(self, num_workers: int = None):
        """
        Inicializa el sistema.

        Args:
            num_workers: Número de workers (default: número de CPUs)
        """
        self.num_workers = num_workers or mp.cpu_count()

        # Colas
        self.job_queue = Queue()
        self.result_queue = Queue()
        self.stats_queue = Queue()

        # Events
        self.shutdown_event = mp.Event()

        # Procesos
        self.workers = []
        self.monitor = None

        # Estadísticas
        self.jobs_enviados = 0
        self.resultados_recibidos = 0

        log(f"Sistema inicializado con {self.num_workers} workers")

    def iniciar(self):
        """Inicia todos los procesos"""
        log("Iniciando sistema...")

        # Iniciar workers
        for i in range(self.num_workers):
            worker = Process(
                target=worker_process,
                args=(i+1, self.job_queue, self.result_queue,
                      self.stats_queue, self.shutdown_event),
                name=f"Worker-{i+1}"
            )
            worker.start()
            self.workers.append(worker)

        # Iniciar monitor
        self.monitor = Process(
            target=monitor_process,
            args=(self.stats_queue, self.shutdown_event, self.num_workers),
            name="Monitor"
        )
        self.monitor.start()

        log(f"✓ {self.num_workers} workers activos")
        log("✓ Monitor de rendimiento activo")

    def enviar_job(self, filename: str, operaciones: List[str]):
        """
        Envía un job de procesamiento.

        Args:
            filename: Nombre del archivo
            operaciones: Lista de operaciones a aplicar
        """
        self.jobs_enviados += 1
        job = ImagenJob(self.jobs_enviados, filename, operaciones)
        self.job_queue.put(job)
        log(f"Job encolado: {filename} ({len(operaciones)} operaciones)")

    def procesar_lote(self, imagenes: List[tuple]):
        """
        Procesa un lote de imágenes.

        Args:
            imagenes: Lista de tuplas (filename, operaciones)
        """
        log(f"\n{'='*70}")
        log(f"Procesando lote de {len(imagenes)} imágenes")
        log(f"{'='*70}\n")

        inicio = time.time()

        # Enviar jobs
        for filename, operaciones in imagenes:
            self.enviar_job(filename, operaciones)

        # Esperar resultados
        resultados = []
        for _ in range(len(imagenes)):
            resultado = self.result_queue.get()
            resultados.append(resultado)
            self.resultados_recibidos += 1

        duracion = time.time() - inicio

        # Mostrar resultados
        self._mostrar_resultados(resultados, duracion)

        return resultados

    def _mostrar_resultados(self, resultados: List[Dict], duracion: float):
        """Muestra resultados del procesamiento"""
        log(f"\n{'='*70}")
        log("RESULTADOS DEL LOTE")
        log(f"{'='*70}\n")

        for res in resultados:
            log(f"✓ {res['filename']}")
            log(f"  Worker: {res['worker_id']} | "
                f"Tiempo: {res['duracion_total']:.2f}s | "
                f"Operaciones: {len(res['operaciones_aplicadas'])}")

        log(f"\nTiempo total del lote: {duracion:.2f}s")
        log(f"Promedio por imagen: {duracion/len(resultados):.2f}s")
        log(f"Throughput: {len(resultados)/duracion:.2f} imágenes/segundo")

        # Distribución de carga
        worker_loads = {}
        for res in resultados:
            wid = res['worker_id']
            worker_loads[wid] = worker_loads.get(wid, 0) + 1

        log("\nDistribución de carga entre workers:")
        for wid, count in sorted(worker_loads.items()):
            pct = (count / len(resultados)) * 100
            log(f"  Worker-{wid}: {count} jobs ({pct:.1f}%)")

    def apagar(self):
        """Apaga el sistema gracefully"""
        log("\nApagando sistema...")

        # Señalizar shutdown
        self.shutdown_event.set()

        # Enviar señales None
        for _ in range(self.num_workers):
            self.job_queue.put(None)

        # Esperar workers
        for worker in self.workers:
            worker.join(timeout=5)
            if worker.is_alive():
                worker.terminate()

        # Esperar monitor
        if self.monitor:
            self.monitor.join(timeout=2)
            if self.monitor.is_alive():
                self.monitor.terminate()

        log("✓ Sistema apagado")


# ============================================================================
# DEMO PRINCIPAL
# ============================================================================

def generar_imagenes_ejemplo(cantidad: int) -> List[tuple]:
    """
    Genera lista de imágenes de ejemplo para procesar.

    Args:
        cantidad: Número de imágenes a generar

    Returns:
        Lista de tuplas (filename, operaciones)
    """
    operaciones_disponibles = [
        'resize', 'filter_blur', 'filter_sharpen',
        'compress', 'thumbnail'
    ]

    imagenes = []

    for i in range(cantidad):
        filename = f"imagen_{i+1:03d}.jpg"

        # Seleccionar operaciones aleatorias
        num_ops = random.randint(2, 4)
        ops = random.sample(operaciones_disponibles, num_ops)

        imagenes.append((filename, ops))

    return imagenes


def demo_completo():
    """
    Demo completo del sistema.

    Ejecuta varios escenarios mostrando las capacidades del sistema.
    """
    log("="*70)
    log("DEMO: Sistema de Procesamiento de Imágenes con Multiprocessing")
    log("="*70)
    log(f"\nSistema: {mp.cpu_count()} CPUs disponibles")
    log(f"Memoria: {psutil.virtual_memory().total / (1024**3):.1f} GB\n")

    # Crear sistema
    sistema = SistemaProcesamiento(num_workers=2)  # Usar 2 workers para tus 2 CPUs
    sistema.iniciar()

    time.sleep(2)  # Dar tiempo a que workers se inicien

    try:
        # ====================================================================
        # ESCENARIO 1: Lote pequeño
        # ====================================================================
        log("\n📸 ESCENARIO 1: Procesando lote pequeño (5 imágenes)")
        imagenes = generar_imagenes_ejemplo(5)
        sistema.procesar_lote(imagenes)

        time.sleep(3)

        # ====================================================================
        # ESCENARIO 2: Lote mediano
        # ====================================================================
        log("\n📸 ESCENARIO 2: Procesando lote mediano (10 imágenes)")
        imagenes = generar_imagenes_ejemplo(10)
        sistema.procesar_lote(imagenes)

        time.sleep(3)

        # ====================================================================
        # ESCENARIO 3: Lote grande
        # ====================================================================
        log("\n📸 ESCENARIO 3: Procesando lote grande (20 imágenes)")
        imagenes = generar_imagenes_ejemplo(20)
        sistema.procesar_lote(imagenes)

        # ====================================================================
        # RESUMEN FINAL
        # ====================================================================
        log("\n" + "="*70)
        log("RESUMEN FINAL")
        log("="*70)
        log(f"Total jobs enviados: {sistema.jobs_enviados}")
        log(f"Total jobs completados: {sistema.resultados_recibidos}")
        log(f"Workers utilizados: {sistema.num_workers}")
        log("="*70)

    except KeyboardInterrupt:
        log("\nDemo interrumpida por usuario")

    finally:
        # Apagar sistema
        sistema.apagar()

    log("\n✓ Demo completada")
    log("\nConceptos demostrados:")
    log("  ✓ Multiprocessing con Pool de workers")
    log("  ✓ Distribución de carga entre CPUs")
    log("  ✓ Job queue con múltiples workers")
    log("  ✓ Monitoreo de rendimiento en tiempo real")
    log("  ✓ CPU affinity para asignar workers a CPUs específicos")
    log("  ✓ Comunicación entre procesos con Queues")
    log("  ✓ Shutdown graceful del sistema")


if __name__ == "__main__":
    demo_completo()

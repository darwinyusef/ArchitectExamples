"""
MONITOR DE CPU Y RECURSOS DEL SISTEMA
======================================
Este módulo monitorea el uso de CPU, memoria y procesos en tiempo real.
Permite visualizar cómo los workers multiprocessing distribuyen carga
entre los CPUs disponibles.

Casos de uso:
- Verificar que workers usan CPUs diferentes
- Monitorear eficiencia del paralelismo
- Detectar bottlenecks
- Optimizar número de workers
- Exportar métricas para Prometheus/Grafana

Instalar dependencias:
    pip install psutil

Para Prometheus/Grafana (opcional):
    pip install prometheus-client
"""

import psutil
import time
import os
import multiprocessing as mp
from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass, asdict
import json


@dataclass
class CPUSnapshot:
    """
    Snapshot del estado de CPU en un momento dado.

    Attributes:
        timestamp: Tiempo de la medición
        cpu_percent_total: Uso total de CPU (%)
        cpu_percent_per_core: Uso por cada core (%)
        cpu_count_logical: Número de CPUs lógicos
        cpu_count_physical: Número de CPUs físicos
        load_average: Carga promedio del sistema (1, 5, 15 min)
    """
    timestamp: float
    cpu_percent_total: float
    cpu_percent_per_core: List[float]
    cpu_count_logical: int
    cpu_count_physical: int
    load_average: tuple


@dataclass
class MemorySnapshot:
    """
    Snapshot del uso de memoria.

    Attributes:
        timestamp: Tiempo de la medición
        total_mb: Memoria total en MB
        available_mb: Memoria disponible en MB
        used_mb: Memoria usada en MB
        percent: Porcentaje de uso
        swap_total_mb: Swap total en MB
        swap_used_mb: Swap usado en MB
        swap_percent: Porcentaje de swap usado
    """
    timestamp: float
    total_mb: float
    available_mb: float
    used_mb: float
    percent: float
    swap_total_mb: float
    swap_used_mb: float
    swap_percent: float


@dataclass
class ProcessInfo:
    """
    Información de un proceso específico.

    Attributes:
        pid: Process ID
        name: Nombre del proceso
        cpu_percent: Uso de CPU (%)
        memory_mb: Memoria usada en MB
        memory_percent: Porcentaje de memoria
        num_threads: Número de threads
        status: Estado del proceso
        cpu_affinity: CPUs asignados al proceso
    """
    pid: int
    name: str
    cpu_percent: float
    memory_mb: float
    memory_percent: float
    num_threads: int
    status: str
    cpu_affinity: List[int]


def log(mensaje):
    """Función auxiliar de logging"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {mensaje}")


# ============================================================================
# FUNCIONES DE MONITOREO
# ============================================================================

def obtener_cpu_snapshot() -> CPUSnapshot:
    """
    Obtiene snapshot actual del uso de CPU.

    Returns:
        CPUSnapshot con métricas actuales

    IMPORTANTE: psutil.cpu_percent() debe llamarse con interval>0
    o llamarse dos veces con delay para obtener mediciones precisas.
    """
    # Obtener uso total (promediado en 0.1s)
    cpu_total = psutil.cpu_percent(interval=0.1)

    # Obtener uso por core
    cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)

    # Contar CPUs
    cpu_logical = psutil.cpu_count(logical=True)
    cpu_physical = psutil.cpu_count(logical=False)

    # Load average (solo en Unix/Linux)
    try:
        load_avg = os.getloadavg()
    except AttributeError:
        # Windows no tiene getloadavg
        load_avg = (0, 0, 0)

    return CPUSnapshot(
        timestamp=time.time(),
        cpu_percent_total=cpu_total,
        cpu_percent_per_core=cpu_per_core,
        cpu_count_logical=cpu_logical,
        cpu_count_physical=cpu_physical,
        load_average=load_avg
    )


def obtener_memory_snapshot() -> MemorySnapshot:
    """
    Obtiene snapshot actual del uso de memoria.

    Returns:
        MemorySnapshot con métricas actuales
    """
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return MemorySnapshot(
        timestamp=time.time(),
        total_mb=mem.total / (1024 * 1024),
        available_mb=mem.available / (1024 * 1024),
        used_mb=mem.used / (1024 * 1024),
        percent=mem.percent,
        swap_total_mb=swap.total / (1024 * 1024),
        swap_used_mb=swap.used / (1024 * 1024),
        swap_percent=swap.percent
    )


def obtener_process_info(pid: int) -> ProcessInfo:
    """
    Obtiene información detallada de un proceso.

    Args:
        pid: Process ID

    Returns:
        ProcessInfo con métricas del proceso

    Útil para monitorear workers multiprocessing específicos.
    """
    try:
        proc = psutil.Process(pid)

        # CPU percent requiere intervalo
        cpu_percent = proc.cpu_percent(interval=0.1)

        # Memoria
        mem_info = proc.memory_info()
        mem_mb = mem_info.rss / (1024 * 1024)
        mem_percent = proc.memory_percent()

        # CPU affinity (a qué CPUs está asignado)
        try:
            cpu_affinity = proc.cpu_affinity()
        except (AttributeError, psutil.AccessDenied):
            # Windows o sin permisos
            cpu_affinity = []

        return ProcessInfo(
            pid=pid,
            name=proc.name(),
            cpu_percent=cpu_percent,
            memory_mb=mem_mb,
            memory_percent=mem_percent,
            num_threads=proc.num_threads(),
            status=proc.status(),
            cpu_affinity=cpu_affinity
        )

    except psutil.NoSuchProcess:
        return None


def listar_procesos_python() -> List[ProcessInfo]:
    """
    Lista todos los procesos Python en ejecución.

    Returns:
        Lista de ProcessInfo de procesos Python

    Útil para identificar workers multiprocessing.
    """
    procesos = []

    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'python' in proc.info['name'].lower():
                info = obtener_process_info(proc.info['pid'])
                if info:
                    procesos.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return procesos


# ============================================================================
# MONITOR EN TIEMPO REAL
# ============================================================================

class CPUMonitor:
    """
    Monitor de CPU en tiempo real.

    Monitorea el sistema continuamente y puede exportar métricas.
    """

    def __init__(self, interval: float = 1.0):
        """
        Inicializa el monitor.

        Args:
            interval: Intervalo de muestreo en segundos
        """
        self.interval = interval
        self.running = False
        self.snapshots: List[CPUSnapshot] = []
        self.memory_snapshots: List[MemorySnapshot] = []

    def start_monitoring(self, duration: float = None):
        """
        Inicia monitoreo en tiempo real.

        Args:
            duration: Duración del monitoreo en segundos (None = infinito)

        Este método bloquea. Para monitoreo en background, ejecutar
        en un thread separado.
        """
        log("=== Iniciando monitoreo de CPU ===")
        log(f"Intervalo: {self.interval}s")
        if duration:
            log(f"Duración: {duration}s")
        else:
            log("Duración: infinito (Ctrl+C para detener)")

        self.running = True
        inicio = time.time()

        try:
            while self.running:
                # Tomar snapshots
                cpu_snap = obtener_cpu_snapshot()
                mem_snap = obtener_memory_snapshot()

                self.snapshots.append(cpu_snap)
                self.memory_snapshots.append(mem_snap)

                # Mostrar en consola
                self._mostrar_snapshot(cpu_snap, mem_snap)

                # Verificar duración
                if duration and (time.time() - inicio) >= duration:
                    break

                # Esperar siguiente intervalo
                time.sleep(self.interval)

        except KeyboardInterrupt:
            log("\nMonitoreo detenido por usuario")

        finally:
            self.running = False
            self._mostrar_resumen()

    def _mostrar_snapshot(self, cpu: CPUSnapshot, mem: MemorySnapshot):
        """Muestra snapshot en consola"""
        timestamp = datetime.fromtimestamp(cpu.timestamp).strftime("%H:%M:%S")

        # Barra de progreso para cada CPU
        cpu_bars = []
        for i, percent in enumerate(cpu.cpu_percent_per_core):
            bar = self._crear_barra(percent, 20)
            cpu_bars.append(f"CPU{i}: [{bar}] {percent:5.1f}%")

        print(f"\n[{timestamp}] " + "="*50)
        print(f"CPU Total: {cpu.cpu_percent_total:5.1f}%")
        for bar in cpu_bars:
            print(f"  {bar}")
        print(f"Memoria:   {mem.percent:5.1f}% ({mem.used_mb:.0f}/{mem.total_mb:.0f} MB)")
        print(f"Load Avg:  {cpu.load_average[0]:.2f}, {cpu.load_average[1]:.2f}, {cpu.load_average[2]:.2f}")

    def _crear_barra(self, percent: float, width: int = 20) -> str:
        """Crea barra de progreso ASCII"""
        filled = int((percent / 100) * width)
        bar = "█" * filled + "░" * (width - filled)
        return bar

    def _mostrar_resumen(self):
        """Muestra resumen del monitoreo"""
        if not self.snapshots:
            return

        log("\n=== RESUMEN DEL MONITOREO ===")

        # Calcular promedios
        avg_cpu_total = sum(s.cpu_percent_total for s in self.snapshots) / len(self.snapshots)
        max_cpu_total = max(s.cpu_percent_total for s in self.snapshots)
        min_cpu_total = min(s.cpu_percent_total for s in self.snapshots)

        avg_mem = sum(s.percent for s in self.memory_snapshots) / len(self.memory_snapshots)
        max_mem = max(s.percent for s in self.memory_snapshots)

        log(f"Muestras recolectadas: {len(self.snapshots)}")
        log(f"CPU Total - Promedio: {avg_cpu_total:.1f}%, Máximo: {max_cpu_total:.1f}%, Mínimo: {min_cpu_total:.1f}%")
        log(f"Memoria - Promedio: {avg_mem:.1f}%, Máximo: {max_mem:.1f}%")

        # Promedio por core
        num_cores = len(self.snapshots[0].cpu_percent_per_core)
        log(f"\nPromedio por CPU core:")
        for i in range(num_cores):
            avg_core = sum(s.cpu_percent_per_core[i] for s in self.snapshots) / len(self.snapshots)
            log(f"  CPU{i}: {avg_core:.1f}%")

    def export_to_json(self, filename: str):
        """Exporta snapshots a JSON"""
        data = {
            'cpu_snapshots': [asdict(s) for s in self.snapshots],
            'memory_snapshots': [asdict(s) for s in self.memory_snapshots]
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        log(f"Datos exportados a {filename}")


# ============================================================================
# MONITOR DE WORKERS MULTIPROCESSING
# ============================================================================

def monitorear_workers(worker_pids: List[int], duration: float = 10):
    """
    Monitorea workers multiprocessing específicos.

    Args:
        worker_pids: Lista de PIDs de workers a monitorear
        duration: Duración del monitoreo

    Muestra qué CPU usa cada worker y su carga.
    """
    log(f"=== Monitoreando {len(worker_pids)} workers ===")
    log(f"PIDs: {worker_pids}")

    inicio = time.time()

    try:
        while (time.time() - inicio) < duration:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] " + "="*60)

            for pid in worker_pids:
                info = obtener_process_info(pid)

                if info:
                    affinity_str = ", ".join(map(str, info.cpu_affinity)) if info.cpu_affinity else "N/A"

                    print(f"Worker PID {pid}:")
                    print(f"  CPU: {info.cpu_percent:5.1f}% | "
                          f"Memoria: {info.memory_mb:6.1f} MB | "
                          f"Threads: {info.num_threads} | "
                          f"CPU Affinity: [{affinity_str}]")
                else:
                    print(f"Worker PID {pid}: Proceso terminado")

            time.sleep(1)

    except KeyboardInterrupt:
        log("\nMonitoreo detenido")


# ============================================================================
# EXPORTAR MÉTRICAS PARA PROMETHEUS
# ============================================================================

def crear_servidor_metricas_prometheus(port: int = 8000):
    """
    Crea servidor HTTP con métricas para Prometheus.

    Args:
        port: Puerto para el servidor de métricas

    Prometheus puede scrapeear métricas de http://localhost:8000

    Requiere: pip install prometheus-client
    """
    try:
        from prometheus_client import start_http_server, Gauge, Info
        import threading
    except ImportError:
        log("ERROR: prometheus-client no instalado")
        log("Instalar con: pip install prometheus-client")
        return

    log(f"=== Iniciando servidor de métricas Prometheus ===")
    log(f"Puerto: {port}")
    log(f"URL: http://localhost:{port}")

    # Definir métricas
    cpu_usage_total = Gauge('cpu_usage_total', 'Uso total de CPU en porcentaje')
    cpu_usage_per_core = Gauge('cpu_usage_per_core', 'Uso de CPU por core', ['core'])
    memory_usage = Gauge('memory_usage_percent', 'Uso de memoria en porcentaje')
    memory_used_mb = Gauge('memory_used_mb', 'Memoria usada en MB')
    load_average = Gauge('system_load_average', 'Carga promedio del sistema', ['interval'])

    system_info = Info('system_info', 'Información del sistema')
    system_info.info({
        'cpu_count_logical': str(psutil.cpu_count(logical=True)),
        'cpu_count_physical': str(psutil.cpu_count(logical=False)),
        'total_memory_mb': str(int(psutil.virtual_memory().total / (1024*1024)))
    })

    # Función que actualiza métricas continuamente
    def actualizar_metricas():
        while True:
            try:
                # CPU
                cpu_total = psutil.cpu_percent(interval=1)
                cpu_per_core = psutil.cpu_percent(interval=0, percpu=True)

                cpu_usage_total.set(cpu_total)

                for i, percent in enumerate(cpu_per_core):
                    cpu_usage_per_core.labels(core=f'cpu{i}').set(percent)

                # Memoria
                mem = psutil.virtual_memory()
                memory_usage.set(mem.percent)
                memory_used_mb.set(mem.used / (1024*1024))

                # Load average
                try:
                    load_avg = os.getloadavg()
                    load_average.labels(interval='1min').set(load_avg[0])
                    load_average.labels(interval='5min').set(load_avg[1])
                    load_average.labels(interval='15min').set(load_avg[2])
                except AttributeError:
                    pass

            except Exception as e:
                log(f"Error actualizando métricas: {e}")

            time.sleep(5)  # Actualizar cada 5 segundos

    # Iniciar servidor HTTP
    start_http_server(port)
    log("✓ Servidor HTTP iniciado")

    # Iniciar actualización de métricas en thread
    thread = threading.Thread(target=actualizar_metricas, daemon=True)
    thread.start()
    log("✓ Actualización de métricas iniciada")

    log("\nMétricas disponibles:")
    log("  - cpu_usage_total")
    log("  - cpu_usage_per_core{core='cpu0'}")
    log("  - memory_usage_percent")
    log("  - memory_used_mb")
    log("  - system_load_average{interval='1min'}")
    log("\nPresiona Ctrl+C para detener")

    try:
        # Mantener programa corriendo
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log("\nServidor detenido")


# ============================================================================
# EJEMPLOS DE USO
# ============================================================================

def ejemplo_monitoreo_basico():
    """Ejemplo básico de monitoreo"""
    log("=== EJEMPLO: Monitoreo Básico ===\n")

    # Snapshot único
    cpu = obtener_cpu_snapshot()
    mem = obtener_memory_snapshot()

    log(f"CPUs: {cpu.cpu_count_physical} físicos, {cpu.cpu_count_logical} lógicos")
    log(f"Uso CPU total: {cpu.cpu_percent_total}%")
    log(f"Uso por core: {cpu.cpu_percent_per_core}")
    log(f"Memoria: {mem.percent}% ({mem.used_mb:.0f}/{mem.total_mb:.0f} MB)")
    log(f"Load average: {cpu.load_average}")


def ejemplo_monitoreo_continuo():
    """Ejemplo de monitoreo continuo"""
    log("=== EJEMPLO: Monitoreo Continuo ===\n")

    monitor = CPUMonitor(interval=0.5)
    monitor.start_monitoring(duration=10)

    # Exportar a JSON
    monitor.export_to_json('cpu_metrics.json')


def ejemplo_monitorear_workers():
    """Ejemplo de monitoreo de workers"""
    from workers.job_queue_system import JobQueueManager

    log("=== EJEMPLO: Monitorear Workers ===\n")

    # Crear workers
    manager = JobQueueManager(num_workers=2)
    manager.start_workers()

    # Obtener PIDs de workers
    worker_pids = [w.pid for w in manager.workers]

    # Enviar jobs para generar carga
    log("Enviando jobs para generar carga...")
    for i in range(10):
        manager.submit_job(
            'calcular_estadisticas',
            {'dataset': list(range(1000000))}
        )

    # Monitorear
    monitorear_workers(worker_pids, duration=15)

    # Cleanup
    manager.shutdown()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        comando = sys.argv[1]

        if comando == 'prometheus':
            # Iniciar servidor Prometheus
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
            crear_servidor_metricas_prometheus(port)

        elif comando == 'monitor':
            # Monitoreo continuo
            ejemplo_monitoreo_continuo()

        elif comando == 'workers':
            # Monitorear workers
            ejemplo_monitorear_workers()

        else:
            log(f"Comando desconocido: {comando}")
            log("Comandos disponibles: prometheus, monitor, workers")

    else:
        # Ejecutar ejemplo básico
        ejemplo_monitoreo_basico()

        log("\n" + "="*60)
        log("Otros comandos disponibles:")
        log("  python cpu_monitor.py monitor      - Monitoreo continuo")
        log("  python cpu_monitor.py workers      - Monitorear workers")
        log("  python cpu_monitor.py prometheus   - Servidor Prometheus")

"""
LOCKS Y MUTEX (MUTUAL EXCLUSION)
=================================
Un Lock (o Mutex) es un mecanismo de sincronización que garantiza que
solo UN thread/proceso puede ejecutar una sección crítica a la vez.

Tipos de Locks en Python:
1. threading.Lock - Para threads (básico)
2. threading.RLock - Lock re-entrante (puede adquirirse múltiples veces por el mismo thread)
3. multiprocessing.Lock - Para procesos
4. threading.Semaphore - Lock con contador (veremos en siguiente módulo)

Conceptos clave:
- SECCIÓN CRÍTICA: Código que accede a recursos compartidos
- MUTUAL EXCLUSION: Solo uno a la vez en la sección crítica
- ATOMICIDAD: Operación que se ejecuta completamente o no se ejecuta

Este módulo exporta métricas detalladas sobre el uso de locks.
"""

import threading
import multiprocessing as mp
from multiprocessing import Process, Lock as MPLock, Value
import time
import random
import os
from datetime import datetime
from prometheus_client import Counter, Gauge, Histogram, start_http_server
from contextlib import contextmanager


def log(mensaje, source="MAIN"):
    """Función auxiliar de logging"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    pid = os.getpid()
    tid = threading.current_thread().ident
    print(f"[{timestamp}] [PID:{pid}] [TID:{tid}] [{source}] {mensaje}")


# ============================================================================
# MÉTRICAS PROMETHEUS
# ============================================================================

lock_acquisitions = Counter(
    'lock_acquisitions_total',
    'Total de adquisiciones de lock',
    ['lock_type', 'lock_name']
)

lock_wait_time = Histogram(
    'lock_wait_duration_seconds',
    'Tiempo esperando adquirir lock',
    ['lock_type', 'lock_name'],
    buckets=[0.0001, 0.001, 0.01, 0.1, 0.5, 1.0, 5.0]
)

lock_hold_time = Histogram(
    'lock_hold_duration_seconds',
    'Tiempo manteniendo el lock',
    ['lock_type', 'lock_name'],
    buckets=[0.0001, 0.001, 0.01, 0.1, 0.5, 1.0]
)

lock_contention = Gauge(
    'lock_contention_threads',
    'Número de threads compitiendo por el lock',
    ['lock_name']
)

deadlock_detected = Counter(
    'deadlocks_detected_total',
    'Número de deadlocks detectados'
)


# ============================================================================
# LOCK INSTRUMENTADO PARA MÉTRICAS
# ============================================================================

class InstrumentedLock:
    """
    Wrapper de Lock que exporta métricas a Prometheus.

    Registra:
    - Tiempo esperando el lock
    - Tiempo manteniendo el lock
    - Número de adquisiciones
    - Contención (threads esperando)
    """

    def __init__(self, name, lock_type="threading"):
        self.name = name
        self.lock_type = lock_type
        self.lock = threading.Lock() if lock_type == "threading" else MPLock()
        self.waiting_count = 0

    def acquire(self, blocking=True, timeout=-1):
        """Adquiere el lock con métricas"""
        self.waiting_count += 1
        lock_contention.labels(lock_name=self.name).set(self.waiting_count)

        inicio = time.time()

        # Intentar adquirir
        if timeout == -1:
            result = self.lock.acquire(blocking=blocking)
        else:
            result = self.lock.acquire(blocking=blocking, timeout=timeout)

        if result:
            # Registrar métricas
            wait_time = time.time() - inicio
            lock_wait_time.labels(
                lock_type=self.lock_type,
                lock_name=self.name
            ).observe(wait_time)

            lock_acquisitions.labels(
                lock_type=self.lock_type,
                lock_name=self.name
            ).inc()

        self.waiting_count -= 1
        lock_contention.labels(lock_name=self.name).set(self.waiting_count)

        return result

    def release(self):
        """Libera el lock"""
        self.lock.release()

    @contextmanager
    def __call__(self):
        """Permite usar con 'with' statement"""
        inicio_hold = time.time()
        self.acquire()
        try:
            yield
        finally:
            hold_time = time.time() - inicio_hold
            lock_hold_time.labels(
                lock_type=self.lock_type,
                lock_name=self.name
            ).observe(hold_time)
            self.release()


# ============================================================================
# EJEMPLO 1: LOCK BÁSICO - THREADING
# ============================================================================

def demo_lock_basico():
    """
    Demuestra uso básico de Lock con threading.

    Escenario: Múltiples workers escriben a un archivo log compartido.
    Sin lock, las líneas se mezclan. Con lock, cada línea es atómica.
    """
    log("=== DEMO: Lock Básico con Threading ===")

    archivo_log = []  # Simula archivo compartido
    lock = InstrumentedLock("file_lock", "threading")

    def escribir_log_sin_lock(worker_id, num_escrituras):
        """Escribe al log SIN protección"""
        for i in range(num_escrituras):
            # PROBLEMA: Esta operación no es atómica
            mensaje = f"Worker-{worker_id}: Mensaje {i}"
            archivo_log.append(mensaje)
            # Otra operación que podría interrumpirse
            time.sleep(0.0001)

    def escribir_log_con_lock(worker_id, num_escrituras):
        """Escribe al log CON protección"""
        for i in range(num_escrituras):
            with lock():  # Sección crítica protegida
                mensaje = f"Worker-{worker_id}: Mensaje {i}"
                archivo_log.append(mensaje)
                time.sleep(0.0001)

    # ========================================================================
    # Prueba 1: Sin lock
    # ========================================================================
    log("\n📝 Prueba 1: Escrituras SIN lock")

    archivo_log.clear()
    threads = []

    for i in range(3):
        t = threading.Thread(
            target=escribir_log_sin_lock,
            args=(i+1, 5)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    log(f"Total de líneas en log: {len(archivo_log)}")
    log("Primeras 5 líneas:")
    for linea in archivo_log[:5]:
        log(f"  {linea}")

    # ========================================================================
    # Prueba 2: Con lock
    # ========================================================================
    log("\n📝 Prueba 2: Escrituras CON lock")

    archivo_log.clear()
    threads = []

    for i in range(3):
        t = threading.Thread(
            target=escribir_log_con_lock,
            args=(i+1, 5)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    log(f"Total de líneas en log: {len(archivo_log)}")
    log("Primeras 5 líneas:")
    for linea in archivo_log[:5]:
        log(f"  {linea}")


# ============================================================================
# EJEMPLO 2: RLOCK - LOCK RE-ENTRANTE
# ============================================================================

class RecursiveCounter:
    """
    Clase que usa operaciones recursivas en sección crítica.

    Problema: Lock normal no puede adquirirse dos veces por el mismo thread.
    Solución: RLock (Reentrant Lock) permite múltiples adquisiciones.
    """

    def __init__(self):
        self.contador = 0
        # RLock puede adquirirse múltiples veces por el MISMO thread
        self.lock = threading.RLock()

    def incrementar_recursivo(self, n):
        """
        Incrementa recursivamente.

        Cada llamada recursiva necesita el lock, pero es el MISMO thread.
        Lock normal causaría DEADLOCK.
        """
        with self.lock:
            if n > 0:
                self.contador += 1
                # Llamada recursiva - NECESITA adquirir lock nuevamente
                self.incrementar_recursivo(n - 1)


def demo_rlock():
    """
    Demuestra diferencia entre Lock y RLock.
    """
    log("\n=== DEMO: RLock (Reentrant Lock) ===")

    # ========================================================================
    # RLock funciona con recursión
    # ========================================================================
    log("\n🔄 Prueba 1: RLock con operación recursiva")

    contador = RecursiveCounter()

    def worker():
        contador.incrementar_recursivo(5)

    threads = [threading.Thread(target=worker) for _ in range(3)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    log(f"Contador final: {contador.contador} (esperado: 15)")

    # ========================================================================
    # Lock normal causaría deadlock
    # ========================================================================
    log("\n🔄 Prueba 2: Demostración por qué Lock normal NO funciona")

    log("Lock normal NO permite re-adquisición por el mismo thread:")
    log("  Thread-1 adquiere lock")
    log("  Thread-1 intenta adquirir lock nuevamente → BLOQUEO")
    log("  Resultado: DEADLOCK del mismo thread consigo mismo")
    log("")
    log("RLock SI permite re-adquisición:")
    log("  Thread-1 adquiere lock (cuenta = 1)")
    log("  Thread-1 adquiere lock nuevamente (cuenta = 2)")
    log("  Thread-1 libera lock (cuenta = 1)")
    log("  Thread-1 libera lock (cuenta = 0)")
    log("  Resultado: ✓ Funciona correctamente")


# ============================================================================
# EJEMPLO 3: LOCK CON TIMEOUT
# ============================================================================

def demo_lock_timeout():
    """
    Demuestra uso de timeout en locks para evitar esperas infinitas.

    En sistemas de producción, SIEMPRE usa timeout para evitar hangs.
    """
    log("\n=== DEMO: Lock con Timeout ===")

    lock = InstrumentedLock("timeout_lock", "threading")

    def worker_lento(worker_id):
        """Worker que mantiene el lock por mucho tiempo"""
        log(f"Worker-{worker_id} intentando adquirir lock", f"W{worker_id}")

        if lock.acquire(timeout=2.0):  # Timeout de 2 segundos
            try:
                log(f"Worker-{worker_id} adquirió lock", f"W{worker_id}")
                time.sleep(5)  # Mantiene lock por 5 segundos
                log(f"Worker-{worker_id} liberando lock", f"W{worker_id}")
            finally:
                lock.release()
        else:
            log(f"Worker-{worker_id} TIMEOUT - no pudo adquirir lock", f"W{worker_id}")

    # Iniciar workers
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker_lento, args=(i+1,))
        threads.append(t)
        t.start()
        time.sleep(0.1)  # Pequeño delay entre starts

    for t in threads:
        t.join()

    log("\n💡 Observa que Workers 2 y 3 hicieron timeout esperando el lock")


# ============================================================================
# EJEMPLO 4: LOCK CON MULTIPROCESSING
# ============================================================================

def worker_multiprocessing(lock, valor_compartido, worker_id, num_ops):
    """
    Worker que usa lock de multiprocessing.

    multiprocessing.Lock funciona ENTRE PROCESOS (no solo threads).
    """
    pid = os.getpid()
    log(f"Worker-{worker_id} iniciado", f"PID-{pid}")

    for i in range(num_ops):
        with lock:
            # Sección crítica
            temp = valor_compartido.value
            time.sleep(0.001)  # Simula trabajo
            valor_compartido.value = temp + 1

            if i % 10 == 0:
                log(f"Worker-{worker_id}: Valor = {valor_compartido.value}",
                    f"PID-{pid}")


def demo_lock_multiprocessing():
    """
    Demuestra lock con multiprocessing.

    Lock de multiprocessing usa mecanismos del OS para sincronización
    entre procesos (no solo threads).
    """
    log("\n=== DEMO: Lock con Multiprocessing ===")

    NUM_PROCESOS = 2
    OPS_POR_PROCESO = 50

    # Crear lock y valor compartido
    lock = MPLock()
    valor_compartido = Value('i', 0)

    log(f"Iniciando {NUM_PROCESOS} procesos...")

    procesos = []
    inicio = time.time()

    for i in range(NUM_PROCESOS):
        p = Process(
            target=worker_multiprocessing,
            args=(lock, valor_compartido, i+1, OPS_POR_PROCESO)
        )
        procesos.append(p)
        p.start()

    for p in procesos:
        p.join()

    duracion = time.time() - inicio

    log(f"\nValor final: {valor_compartido.value}")
    log(f"Esperado: {NUM_PROCESOS * OPS_POR_PROCESO}")
    log(f"Tiempo: {duracion:.2f}s")

    if valor_compartido.value == NUM_PROCESOS * OPS_POR_PROCESO:
        log("✅ Lock de multiprocessing funcionó correctamente")


# ============================================================================
# EJEMPLO 5: CONTENCIÓN DE LOCK (LOCK CONTENTION)
# ============================================================================

def demo_lock_contention():
    """
    Demuestra el impacto de la contención de lock en performance.

    Contention = múltiples threads compitiendo por el mismo lock.
    A mayor contención, menor performance.
    """
    log("\n=== DEMO: Lock Contention (Competencia por Lock) ===")

    def tarea_corta_con_lock(lock, contador, worker_id):
        """Sección crítica CORTA - baja contención"""
        for _ in range(100):
            with lock():
                contador[0] += 1  # Operación rápida

    def tarea_larga_con_lock(lock, contador, worker_id):
        """Sección crítica LARGA - alta contención"""
        for _ in range(100):
            with lock():
                contador[0] += 1
                time.sleep(0.001)  # Simula trabajo dentro del lock

    # ========================================================================
    # Prueba 1: Sección crítica corta (baja contención)
    # ========================================================================
    log("\n⚡ Prueba 1: Sección crítica CORTA")

    lock_corto = InstrumentedLock("short_critical_section", "threading")
    contador = [0]
    threads = []

    inicio = time.time()

    for i in range(10):
        t = threading.Thread(
            target=tarea_corta_con_lock,
            args=(lock_corto, contador, i+1)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    duracion_corta = time.time() - inicio

    log(f"Contador: {contador[0]}")
    log(f"Tiempo: {duracion_corta:.3f}s")

    # ========================================================================
    # Prueba 2: Sección crítica larga (alta contención)
    # ========================================================================
    log("\n🐌 Prueba 2: Sección crítica LARGA")

    lock_largo = InstrumentedLock("long_critical_section", "threading")
    contador = [0]
    threads = []

    inicio = time.time()

    for i in range(10):
        t = threading.Thread(
            target=tarea_larga_con_lock,
            args=(lock_largo, contador, i+1)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    duracion_larga = time.time() - inicio

    log(f"Contador: {contador[0]}")
    log(f"Tiempo: {duracion_larga:.3f}s")

    # Comparación
    diferencia = duracion_larga / duracion_corta
    log(f"\n📊 Sección crítica larga fue {diferencia:.1f}x más lenta")
    log("💡 Mantén secciones críticas lo más CORTAS posible")


# ============================================================================
# EJEMPLO 6: TRY-LOCK (ACQUIRE NO-BLOQUEANTE)
# ============================================================================

def demo_try_lock():
    """
    Demuestra try-lock: intentar adquirir sin bloquear.

    Útil cuando el thread puede hacer trabajo alternativo si el lock no
    está disponible.
    """
    log("\n=== DEMO: Try-Lock (No Bloqueante) ===")

    lock = InstrumentedLock("try_lock", "threading")
    trabajos_alternativos = [0]

    def worker_con_fallback(worker_id, intentos):
        """Worker que hace trabajo alternativo si no puede adquirir lock"""
        log(f"Worker-{worker_id} iniciado", f"W{worker_id}")

        for i in range(intentos):
            # Intentar adquirir sin bloquear
            if lock.acquire(blocking=False):
                try:
                    log(f"Worker-{worker_id} adquirió lock, haciendo trabajo protegido",
                        f"W{worker_id}")
                    time.sleep(0.1)
                finally:
                    lock.release()
            else:
                # No pudo adquirir, hacer trabajo alternativo
                log(f"Worker-{worker_id} lock ocupado, haciendo trabajo alternativo",
                    f"W{worker_id}")
                trabajos_alternativos[0] += 1
                time.sleep(0.05)

    threads = []
    for i in range(5):
        t = threading.Thread(target=worker_con_fallback, args=(i+1, 3))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    log(f"\nTrabajos alternativos ejecutados: {trabajos_alternativos[0]}")
    log("💡 Try-lock evita que threads se bloqueen esperando")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Iniciar servidor de métricas
    log("Iniciando servidor de métricas en puerto 8001")
    start_http_server(8001)
    log("Métricas disponibles en http://localhost:8001")

    log("\n" + "="*70)
    log("DEMOS DE LOCKS Y MUTEX")
    log("="*70)

    try:
        demo_lock_basico()
        time.sleep(1)

        demo_rlock()
        time.sleep(1)

        demo_lock_timeout()
        time.sleep(1)

        demo_lock_multiprocessing()
        time.sleep(1)

        demo_lock_contention()
        time.sleep(1)

        demo_try_lock()

        log("\n" + "="*70)
        log("RESUMEN")
        log("="*70)
        log("✓ Lock garantiza mutual exclusion (solo uno a la vez)")
        log("✓ RLock permite re-adquisición por el mismo thread")
        log("✓ Usa timeout para evitar esperas infinitas")
        log("✓ Lock de multiprocessing funciona entre procesos")
        log("✓ Minimiza secciones críticas para reducir contención")
        log("✓ Try-lock permite hacer trabajo alternativo")
        log("\nMétricas disponibles:")
        log("  - lock_acquisitions_total")
        log("  - lock_wait_duration_seconds")
        log("  - lock_hold_duration_seconds")
        log("  - lock_contention_threads")

        log("\n💡 Mantén este script corriendo para ver métricas en Grafana")
        log("Presiona Ctrl+C para salir")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        log("\nScript detenido por usuario")

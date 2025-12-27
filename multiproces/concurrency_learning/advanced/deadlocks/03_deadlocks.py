"""
DEADLOCKS (INTERBLOQUEOS)
==========================
Un deadlock ocurre cuando dos o más threads/procesos se bloquean mutuamente,
cada uno esperando que el otro libere un recurso.

Condiciones para deadlock (todas deben cumplirse):
1. MUTUAL EXCLUSION: Los recursos no pueden compartirse
2. HOLD AND WAIT: Un thread mantiene recursos mientras espera otros
3. NO PREEMPTION: Los recursos no pueden quitarse forzadamente
4. CIRCULAR WAIT: Existe un ciclo de dependencias

Ejemplo clásico:
    Thread-A: Tiene lock1, espera lock2
    Thread-B: Tiene lock2, espera lock1
    Resultado: Ambos bloqueados para siempre ⚰️

Este módulo demuestra deadlocks y múltiples estrategias para prevenirlos.
"""

import threading
import time
import random
from datetime import datetime
from prometheus_client import Counter, Gauge, Histogram, start_http_server
import os


def log(mensaje, source="MAIN"):
    """Función auxiliar de logging"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    tid = threading.current_thread().ident
    print(f"[{timestamp}] [TID:{tid}] [{source}] {mensaje}")


# ============================================================================
# MÉTRICAS PROMETHEUS
# ============================================================================

deadlock_detected_counter = Counter(
    'deadlocks_detected_total',
    'Total de deadlocks detectados'
)

deadlock_prevented_counter = Counter(
    'deadlocks_prevented_total',
    'Total de deadlocks prevenidos',
    ['strategy']
)

lock_acquisition_order_violations = Counter(
    'lock_order_violations_total',
    'Violaciones del orden de adquisición de locks'
)

timeout_failures = Counter(
    'lock_timeout_failures_total',
    'Fallos por timeout al adquirir locks'
)


# ============================================================================
# EJEMPLO 1: DEADLOCK CLÁSICO (EL PROBLEMA)
# ============================================================================

def demo_deadlock_clasico():
    """
    Demuestra el deadlock clásico de 2 threads y 2 locks.

    ADVERTENCIA: Este código CAUSARÁ un deadlock intencional.
    Usaremos timeout para evitar que se congele.
    """
    log("=== DEMO: Deadlock Clásico (El Problema) ===")

    lock_A = threading.Lock()
    lock_B = threading.Lock()

    def thread_1():
        """
        Thread 1: Adquiere A, luego intenta B

        Timeline:
        T1: Adquiere lock_A ✓
        T1: Intenta adquirir lock_B... ⏳ (bloqueado esperando T2)
        """
        log("Thread-1: Intentando adquirir lock_A", "T1")

        if lock_A.acquire(timeout=5):
            try:
                log("Thread-1: ✓ Adquirió lock_A", "T1")
                time.sleep(0.1)  # Simula trabajo

                log("Thread-1: Intentando adquirir lock_B...", "T1")

                if lock_B.acquire(timeout=5):
                    try:
                        log("Thread-1: ✓ Adquirió lock_B", "T1")
                    finally:
                        lock_B.release()
                else:
                    log("Thread-1: ⚠️  TIMEOUT esperando lock_B", "T1")
                    deadlock_detected_counter.inc()

            finally:
                lock_A.release()
                log("Thread-1: Liberó lock_A", "T1")

    def thread_2():
        """
        Thread 2: Adquiere B, luego intenta A

        Timeline:
        T2: Adquiere lock_B ✓
        T2: Intenta adquirir lock_A... ⏳ (bloqueado esperando T1)

        ¡DEADLOCK! Ambos esperándose mutuamente
        """
        log("Thread-2: Intentando adquirir lock_B", "T2")

        if lock_B.acquire(timeout=5):
            try:
                log("Thread-2: ✓ Adquirió lock_B", "T2")
                time.sleep(0.1)  # Simula trabajo

                log("Thread-2: Intentando adquirir lock_A...", "T2")

                if lock_A.acquire(timeout=5):
                    try:
                        log("Thread-2: ✓ Adquirió lock_A", "T2")
                    finally:
                        lock_A.release()
                else:
                    log("Thread-2: ⚠️  TIMEOUT esperando lock_A", "T2")
                    deadlock_detected_counter.inc()

            finally:
                lock_B.release()
                log("Thread-2: Liberó lock_B", "T2")

    log("\n⚠️  Creando condiciones para deadlock...")
    log("Thread-1: lock_A → lock_B")
    log("Thread-2: lock_B → lock_A")
    log("Resultado esperado: DEADLOCK (ambos en timeout)\n")

    t1 = threading.Thread(target=thread_1, name="Thread-1")
    t2 = threading.Thread(target=thread_2, name="Thread-2")

    t1.start()
    time.sleep(0.05)  # Asegurar que T1 adquiera lock_A primero
    t2.start()

    t1.join()
    t2.join()

    log("\n💀 Deadlock demostrado (detectado por timeout)")


# ============================================================================
# SOLUCIÓN 1: ORDENAMIENTO DE LOCKS
# ============================================================================

def demo_solucion_ordenamiento():
    """
    Previene deadlock estableciendo un ORDEN GLOBAL de adquisición.

    Regla: Todos los threads DEBEN adquirir locks en el mismo orden.

    Orden: lock_A siempre antes que lock_B

    Timeline (sin deadlock):
    T1: Adquiere lock_A
    T2: Intenta lock_A, ESPERA (T2 bloqueado)
    T1: Adquiere lock_B
    T1: Hace trabajo, libera ambos
    T2: Adquiere lock_A
    T2: Adquiere lock_B
    T2: Hace trabajo, libera ambos
    ✓ Sin deadlock
    """
    log("\n=== SOLUCIÓN 1: Ordenamiento de Locks ===")

    lock_A = threading.Lock()
    lock_B = threading.Lock()

    def thread_con_orden(thread_id):
        """
        Thread que SIEMPRE adquiere en orden: A → B

        Esta es la solución más simple y efectiva.
        """
        log(f"Thread-{thread_id}: Adquiriendo en orden A→B", f"T{thread_id}")

        with lock_A:
            log(f"Thread-{thread_id}: ✓ Tiene lock_A", f"T{thread_id}")
            time.sleep(0.1)

            with lock_B:
                log(f"Thread-{thread_id}: ✓ Tiene lock_B", f"T{thread_id}")
                time.sleep(0.1)
                log(f"Thread-{thread_id}: Trabajo completado", f"T{thread_id}")

        deadlock_prevented_counter.labels(strategy='ordenamiento').inc()

    log("\n✅ Ambos threads adquieren en orden: lock_A → lock_B")

    t1 = threading.Thread(target=thread_con_orden, args=(1,))
    t2 = threading.Thread(target=thread_con_orden, args=(2,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    log("\n✓ Sin deadlock: Orden consistente previene ciclos")


# ============================================================================
# SOLUCIÓN 2: LOCK HIERARCHY (JERARQUÍA)
# ============================================================================

class HierarchicalLock:
    """
    Lock con nivel de jerarquía.

    Regla: Solo puedes adquirir locks de nivel MAYOR al que ya tienes.
    Esto garantiza un orden parcial y previene ciclos.
    """

    _thread_locks = threading.local()  # Locks por thread

    def __init__(self, name, level):
        self.name = name
        self.level = level
        self.lock = threading.Lock()

    def acquire(self, blocking=True, timeout=-1):
        """Adquiere lock verificando jerarquía"""
        # Obtener locks actuales del thread
        if not hasattr(self._thread_locks, 'held_locks'):
            self._thread_locks.held_locks = []

        # Verificar que no violamos jerarquía
        for held_lock in self._thread_locks.held_locks:
            if self.level <= held_lock.level:
                error_msg = (f"Violación de jerarquía: "
                           f"Intentando {self.name}(nivel {self.level}) "
                           f"mientras tienes {held_lock.name}(nivel {held_lock.level})")
                log(f"⚠️  {error_msg}", "HIERARCHY")
                lock_acquisition_order_violations.inc()
                raise RuntimeError(error_msg)

        # Adquirir lock
        result = self.lock.acquire(blocking=blocking, timeout=timeout if timeout != -1 else None)

        if result:
            self._thread_locks.held_locks.append(self)

        return result

    def release(self):
        """Libera lock"""
        self.lock.release()
        self._thread_locks.held_locks.remove(self)

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


def demo_solucion_jerarquia():
    """
    Demuestra prevención de deadlock con jerarquía de locks.
    """
    log("\n=== SOLUCIÓN 2: Jerarquía de Locks ===")

    # Locks con niveles
    lock_db = HierarchicalLock("database", level=1)
    lock_cache = HierarchicalLock("cache", level=2)
    lock_log = HierarchicalLock("log", level=3)

    def thread_respetuoso():
        """Thread que respeta jerarquía: 1 → 2 → 3"""
        log("Thread: Adquiriendo en orden jerárquico", "GOOD")

        with lock_db:  # Nivel 1
            log("Thread: ✓ Tiene lock database (nivel 1)", "GOOD")

            with lock_cache:  # Nivel 2 (OK, mayor que 1)
                log("Thread: ✓ Tiene lock cache (nivel 2)", "GOOD")

                with lock_log:  # Nivel 3 (OK, mayor que 2)
                    log("Thread: ✓ Tiene lock log (nivel 3)", "GOOD")

        deadlock_prevented_counter.labels(strategy='jerarquia').inc()
        log("Thread: ✓ Completado sin problemas", "GOOD")

    def thread_violador():
        """Thread que VIOLA jerarquía: 3 → 1 (debería fallar)"""
        log("Thread: Intentando violar jerarquía", "BAD")

        try:
            with lock_log:  # Nivel 3
                log("Thread: ✓ Tiene lock log (nivel 3)", "BAD")

                # Intenta adquirir nivel 1 (menor que 3) → ERROR
                with lock_db:  # Nivel 1
                    log("Thread: ✓ Tiene lock database", "BAD")

        except RuntimeError as e:
            log(f"Thread: ✗ Error (esperado): {e}", "BAD")

    log("\n✅ Thread que respeta jerarquía:")
    t1 = threading.Thread(target=thread_respetuoso)
    t1.start()
    t1.join()

    log("\n❌ Thread que viola jerarquía:")
    t2 = threading.Thread(target=thread_violador)
    t2.start()
    t2.join()


# ============================================================================
# SOLUCIÓN 3: TRY-LOCK CON BACKOFF
# ============================================================================

def demo_solucion_trylock():
    """
    Previene deadlock con try-lock y backoff exponencial.

    Estrategia:
    1. Intenta adquirir todos los locks sin bloquear
    2. Si falla, libera TODOS los locks adquiridos
    3. Espera un tiempo aleatorio (backoff)
    4. Reintenta

    Esto rompe la condición de HOLD AND WAIT.
    """
    log("\n=== SOLUCIÓN 3: Try-Lock con Backoff ===")

    lock_A = threading.Lock()
    lock_B = threading.Lock()

    def adquirir_multiple_con_trylock(thread_id, locks, max_intentos=10):
        """
        Intenta adquirir múltiples locks atómicamente.

        Si no puede adquirir todos, libera los que tenga y reintenta.
        """
        for intento in range(max_intentos):
            locks_adquiridos = []
            exito = True

            # Intentar adquirir todos
            for i, lock in enumerate(locks):
                if lock.acquire(blocking=False):
                    locks_adquiridos.append(lock)
                    log(f"Thread-{thread_id}: ✓ Adquirió lock-{i}", f"T{thread_id}")
                else:
                    # No pudo adquirir, abortar
                    log(f"Thread-{thread_id}: ✗ No pudo adquirir lock-{i}", f"T{thread_id}")
                    exito = False
                    break

            if exito:
                # Adquirió todos, hacer trabajo
                log(f"Thread-{thread_id}: ✓ Adquirió TODOS los locks", f"T{thread_id}")
                time.sleep(0.1)

                # Liberar todos
                for lock in reversed(locks_adquiridos):
                    lock.release()

                log(f"Thread-{thread_id}: ✓ Trabajo completado", f"T{thread_id}")
                deadlock_prevented_counter.labels(strategy='trylock').inc()
                return True

            else:
                # Liberar los que adquirió
                for lock in reversed(locks_adquiridos):
                    lock.release()

                # Backoff exponencial con jitter
                backoff = (2 ** intento) * 0.001 * random.random()
                log(f"Thread-{thread_id}: Reintentando en {backoff*1000:.1f}ms...",
                    f"T{thread_id}")
                time.sleep(backoff)

        log(f"Thread-{thread_id}: ✗ Falló después de {max_intentos} intentos",
            f"T{thread_id}")
        timeout_failures.inc()
        return False

    log("\nDos threads compitiendo por los mismos locks:")

    def thread_worker(thread_id, orden_locks):
        """Worker que usa try-lock"""
        log(f"Thread-{thread_id}: Iniciando", f"T{thread_id}")
        adquirir_multiple_con_trylock(thread_id, orden_locks)

    t1 = threading.Thread(target=thread_worker, args=(1, [lock_A, lock_B]))
    t2 = threading.Thread(target=thread_worker, args=(2, [lock_B, lock_A]))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    log("\n✓ Try-lock previene deadlock retrocediendo y reintentando")


# ============================================================================
# SOLUCIÓN 4: TIMEOUT EN TODOS LOS LOCKS
# ============================================================================

def demo_solucion_timeout():
    """
    Usa timeout en TODAS las adquisiciones de lock.

    Si no puede adquirir en tiempo razonable:
    1. Libera lo que tenga
    2. Reporta el error
    3. Reintenta o falla gracefully

    Esto permite DETECTAR deadlocks en producción.
    """
    log("\n=== SOLUCIÓN 4: Timeout en Locks ===")

    lock_A = threading.Lock()
    lock_B = threading.Lock()

    def thread_con_timeout(thread_id, lock_orden):
        """Thread que usa timeout en todas las adquisiciones"""
        TIMEOUT = 2.0  # 2 segundos

        log(f"Thread-{thread_id}: Iniciando", f"T{thread_id}")

        locks_adquiridos = []

        try:
            for i, lock in enumerate(lock_orden):
                log(f"Thread-{thread_id}: Intentando lock-{i}...", f"T{thread_id}")

                if lock.acquire(timeout=TIMEOUT):
                    locks_adquiridos.append(lock)
                    log(f"Thread-{thread_id}: ✓ Adquirió lock-{i}", f"T{thread_id}")
                else:
                    # Timeout - posible deadlock
                    log(f"Thread-{thread_id}: ⚠️  TIMEOUT en lock-{i} - posible deadlock",
                        f"T{thread_id}")
                    timeout_failures.inc()
                    return False

            # Trabajo
            log(f"Thread-{thread_id}: Haciendo trabajo...", f"T{thread_id}")
            time.sleep(0.5)
            log(f"Thread-{thread_id}: ✓ Completado", f"T{thread_id}")

            return True

        finally:
            # Liberar en orden inverso
            for lock in reversed(locks_adquiridos):
                lock.release()

    log("\n⚠️  Creando condiciones de deadlock con timeout...")

    t1 = threading.Thread(target=thread_con_timeout, args=(1, [lock_A, lock_B]))
    t2 = threading.Thread(target=thread_con_timeout, args=(2, [lock_B, lock_A]))

    t1.start()
    time.sleep(0.05)
    t2.start()

    t1.join()
    t2.join()

    log("\n💡 Timeout permite DETECTAR deadlocks en producción")


# ============================================================================
# EJEMPLO REAL: DINING PHILOSOPHERS (FILÓSOFOS COMENSALES)
# ============================================================================

def demo_dining_philosophers():
    """
    Problema clásico de los filósofos comensales.

    Setup:
    - 5 filósofos sentados en mesa circular
    - 5 tenedores (uno entre cada par)
    - Para comer, filósofo necesita 2 tenedores (izq y der)

    Deadlock:
    - Si todos toman tenedor izquierdo simultáneamente
    - Todos esperan tenedor derecho
    - ¡DEADLOCK!

    Solución: Ordenamiento (filósofos pares toman derecho primero)
    """
    log("\n=== EJEMPLO: Dining Philosophers Problem ===")

    NUM_FILOSOFOS = 5
    tenedores = [threading.Lock() for _ in range(NUM_FILOSOFOS)]

    def filosofo_con_deadlock(id):
        """Filósofo que puede causar deadlock"""
        izq = id
        der = (id + 1) % NUM_FILOSOFOS

        log(f"Filósofo-{id}: Pensando...", f"F{id}")
        time.sleep(random.uniform(0.1, 0.3))

        # PROBLEMA: Todos toman izquierda primero → deadlock
        log(f"Filósofo-{id}: Tomando tenedor izquierdo ({izq})", f"F{id}")
        with tenedores[izq]:
            log(f"Filósofo-{id}: ✓ Tiene tenedor {izq}", f"F{id}")

            log(f"Filósofo-{id}: Intentando tenedor derecho ({der})...", f"F{id}")
            if tenedores[der].acquire(timeout=2.0):
                try:
                    log(f"Filósofo-{id}: ✓ Comiendo", f"F{id}")
                    time.sleep(random.uniform(0.1, 0.2))
                finally:
                    tenedores[der].release()
            else:
                log(f"Filósofo-{id}: ⚠️  TIMEOUT - posible deadlock", f"F{id}")
                deadlock_detected_counter.inc()

    def filosofo_sin_deadlock(id):
        """Filósofo que evita deadlock con ordenamiento"""
        izq = id
        der = (id + 1) % NUM_FILOSOFOS

        # SOLUCIÓN: Orden consistente (menor primero)
        primero = min(izq, der)
        segundo = max(izq, der)

        log(f"Filósofo-{id}: Pensando...", f"F{id}")
        time.sleep(random.uniform(0.1, 0.3))

        log(f"Filósofo-{id}: Tomando tenedores {primero}→{segundo}", f"F{id}")

        with tenedores[primero]:
            with tenedores[segundo]:
                log(f"Filósofo-{id}: ✓ Comiendo", f"F{id}")
                time.sleep(random.uniform(0.1, 0.2))

        deadlock_prevented_counter.labels(strategy='filosofos').inc()

    # Prueba con deadlock
    log("\n⚠️  Versión CON deadlock (orden inconsistente):")
    threads = [threading.Thread(target=filosofo_con_deadlock, args=(i,))
               for i in range(NUM_FILOSOFOS)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    time.sleep(1)

    # Prueba sin deadlock
    log("\n✅ Versión SIN deadlock (orden consistente):")
    threads = [threading.Thread(target=filosofo_sin_deadlock, args=(i,))
               for i in range(NUM_FILOSOFOS)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Iniciar servidor de métricas
    log("Iniciando servidor de métricas en puerto 8002")
    start_http_server(8002)
    log("Métricas disponibles en http://localhost:8002")

    log("\n" + "="*70)
    log("DEMOS DE DEADLOCKS Y SOLUCIONES")
    log("="*70)

    try:
        # El problema
        demo_deadlock_clasico()
        time.sleep(2)

        # Soluciones
        demo_solucion_ordenamiento()
        time.sleep(1)

        demo_solucion_jerarquia()
        time.sleep(1)

        demo_solucion_trylock()
        time.sleep(1)

        demo_solucion_timeout()
        time.sleep(1)

        # Ejemplo clásico
        demo_dining_philosophers()

        log("\n" + "="*70)
        log("RESUMEN: PREVENCIÓN DE DEADLOCKS")
        log("="*70)
        log("Estrategias principales:")
        log("1. ✅ ORDENAMIENTO: Adquirir locks siempre en el mismo orden")
        log("2. ✅ JERARQUÍA: Locks con niveles, solo adquirir hacia arriba")
        log("3. ✅ TRY-LOCK: Retroceder si no puedes adquirir todos")
        log("4. ✅ TIMEOUT: Detectar deadlocks con timeouts")
        log("5. ✅ LOCK-FREE: Usar estructuras lock-free cuando sea posible")
        log("\nMétricas disponibles:")
        log("  - deadlocks_detected_total")
        log("  - deadlocks_prevented_total")
        log("  - lock_order_violations_total")
        log("  - lock_timeout_failures_total")

        log("\n💡 Mantén este script corriendo para ver métricas en Grafana")
        log("Presiona Ctrl+C para salir")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        log("\nScript detenido por usuario")

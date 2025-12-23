"""
DEADLOCKS (Bloqueos Mutuos)
Ocurren cuando dos o más threads esperan por recursos que otros threads tienen.

Condiciones para deadlock (todas deben cumplirse):
1. Mutual exclusion - recurso no compartible
2. Hold and wait - thread tiene recurso y espera otro
3. No preemption - recursos no pueden quitarse forzadamente
4. Circular wait - cadena circular de threads esperando

Prevención:
- Ordenar adquisición de locks
- Usar timeout
- Evitar nested locks
- Lock ordering
"""

import threading
import time
from typing import List

class DeadlockExamples:
    """
    Ejemplos de deadlocks y cómo prevenirlos
    """

    def demonstrate_deadlock(self, timeout: float = 2.0) -> dict:
        """
        ❌ Demuestra un DEADLOCK clásico

        Thread 1: lock A → lock B
        Thread 2: lock B → lock A

        Resultado: ambos esperan mutuamente - deadlock
        """
        lock_a = threading.Lock()
        lock_b = threading.Lock()
        results = {"thread1": None, "thread2": None, "deadlock_detected": False}

        def thread1_work():
            print("🔴 Thread 1: Intentando adquirir Lock A...")
            lock_a.acquire()
            print("✅ Thread 1: Lock A adquirido")

            time.sleep(0.1)  # Dar tiempo para que thread2 adquiera lock_b

            print("🔴 Thread 1: Intentando adquirir Lock B...")
            # Intentar con timeout para no bloquear forever
            if lock_b.acquire(timeout=timeout):
                print("✅ Thread 1: Lock B adquirido")
                results["thread1"] = "success"
                lock_b.release()
            else:
                print("❌ Thread 1: DEADLOCK - No pudo adquirir Lock B")
                results["thread1"] = "deadlock"
                results["deadlock_detected"] = True

            lock_a.release()

        def thread2_work():
            print("🔵 Thread 2: Intentando adquirir Lock B...")
            lock_b.acquire()
            print("✅ Thread 2: Lock B adquirido")

            time.sleep(0.1)  # Dar tiempo para que thread1 adquiera lock_a

            print("🔵 Thread 2: Intentando adquirir Lock A...")
            if lock_a.acquire(timeout=timeout):
                print("✅ Thread 2: Lock A adquirido")
                results["thread2"] = "success"
                lock_a.release()
            else:
                print("❌ Thread 2: DEADLOCK - No pudo adquirir Lock A")
                results["thread2"] = "deadlock"
                results["deadlock_detected"] = True

            lock_b.release()

        t1 = threading.Thread(target=thread1_work, name="Thread-1")
        t2 = threading.Thread(target=thread2_work, name="Thread-2")

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        return results

    def prevent_deadlock(self) -> dict:
        """
        ✅ Previene deadlock usando ORDENAMIENTO CONSISTENTE de locks

        Regla: SIEMPRE adquirir locks en el mismo orden
        Thread 1: lock A → lock B
        Thread 2: lock A → lock B (mismo orden!)
        """
        lock_a = threading.Lock()
        lock_b = threading.Lock()
        results = {"thread1": "success", "thread2": "success", "deadlock_detected": False}

        def thread1_work():
            print("🔴 Thread 1: Intentando adquirir Lock A...")
            with lock_a:
                print("✅ Thread 1: Lock A adquirido")
                time.sleep(0.1)

                print("🔴 Thread 1: Intentando adquirir Lock B...")
                with lock_b:
                    print("✅ Thread 1: Lock B adquirido")
                    # Trabajo aquí
                    time.sleep(0.1)

        def thread2_work():
            print("🔵 Thread 2: Intentando adquirir Lock A...")  # Mismo orden!
            with lock_a:
                print("✅ Thread 2: Lock A adquirido")
                time.sleep(0.1)

                print("🔵 Thread 2: Intentando adquirir Lock B...")
                with lock_b:
                    print("✅ Thread 2: Lock B adquirido")
                    time.sleep(0.1)

        t1 = threading.Thread(target=thread1_work, name="Thread-1")
        t2 = threading.Thread(target=thread2_work, name="Thread-2")

        t1.start()
        t2.start()

        t1.join()
        t2.join()

        return results

    def demonstrate_starvation(self, num_threads: int = 5) -> dict:
        """
        Demuestra STARVATION (inanición)

        Ocurre cuando un thread nunca obtiene acceso a un recurso
        porque otros threads tienen prioridad.
        """
        resource_lock = threading.Lock()
        access_log = []

        def greedy_thread(thread_id: int, iterations: int):
            """Thread que acapara el recurso"""
            for i in range(iterations):
                with resource_lock:
                    access_log.append(f"Thread-{thread_id} (greedy)")
                    time.sleep(0.01)  # Mantiene lock mucho tiempo

        def polite_thread(thread_id: int, iterations: int):
            """Thread que intenta acceder pero es bloqueado"""
            for i in range(iterations):
                acquired = resource_lock.acquire(timeout=0.1)
                if acquired:
                    access_log.append(f"Thread-{thread_id} (polite)")
                    resource_lock.release()
                else:
                    access_log.append(f"Thread-{thread_id} (starved)")
                time.sleep(0.05)

        # Crear threads greedy y polite
        threads = []
        threads.append(threading.Thread(target=greedy_thread, args=(1, 10)))
        for i in range(2, num_threads + 1):
            threads.append(threading.Thread(target=polite_thread, args=(i, 5)))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Analizar cuántas veces cada thread fue starved
        starved_count = len([log for log in access_log if "starved" in log])

        return {
            "total_accesses": len(access_log),
            "starved_attempts": starved_count,
            "starvation_rate": starved_count / len(access_log) if access_log else 0,
            "access_log": access_log[:20],  # Primeros 20 para mostrar
            "note": "Threads polite sufren starvation porque greedy acapara el lock"
        }

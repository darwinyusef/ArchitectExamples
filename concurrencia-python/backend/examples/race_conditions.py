"""
RACE CONDITIONS (Condiciones de Carrera)
Ocurren cuando múltiples threads acceden/modifican datos compartidos sin sincronización.

Soluciones:
- Lock
- RLock (Reentrant Lock)
- Semaphore
- Atomic operations
"""

import threading
import time
from typing import List

class RaceConditionExamples:
    """
    Ejemplos de race conditions y cómo prevenirlas
    """

    def unsafe_counter(self, num_threads: int, increments_per_thread: int) -> int:
        """
        ❌ UNSAFE: Demuestra race condition

        Problema: counter++ NO es atómico, son 3 operaciones:
        1. Leer valor
        2. Incrementar
        3. Escribir valor

        Si Thread A y B leen al mismo tiempo, ambos incrementan el mismo valor.
        Resultado: se pierden increments
        """
        counter = 0

        def increment():
            nonlocal counter
            for _ in range(increments_per_thread):
                # RACE CONDITION AQUÍ:
                temp = counter  # Thread A lee 0
                temp += 1       # Thread A calcula 1
                # Context switch aquí podría causar que Thread B también lea 0
                counter = temp  # Thread A escribe 1 (B escribe 1 también - perdimos un increment!)
                # Simulamos trabajo para aumentar probabilidad de race
                time.sleep(0.0001)

        # Crear y ejecutar threads
        threads = [threading.Thread(target=increment) for _ in range(num_threads)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        return counter

    def safe_counter_lock(self, num_threads: int, increments_per_thread: int) -> int:
        """
        ✅ SAFE: Usa Lock para prevenir race condition

        Lock garantiza que solo un thread accede a la sección crítica a la vez.
        """
        counter = 0
        lock = threading.Lock()

        def increment():
            nonlocal counter
            for _ in range(increments_per_thread):
                with lock:  # Adquiere lock antes de modificar
                    counter += 1
                # Lock se libera automáticamente al salir del with

        threads = [threading.Thread(target=increment) for _ in range(num_threads)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        return counter

    def safe_counter_rlock(self, num_threads: int, increments_per_thread: int) -> int:
        """
        ✅ SAFE: Usa RLock (Reentrant Lock)

        RLock permite que el mismo thread adquiera el lock múltiples veces.
        Útil para funciones recursivas o llamadas anidadas.
        """
        counter = 0
        rlock = threading.RLock()

        def recursive_increment(n):
            nonlocal counter
            with rlock:
                counter += 1
                if n > 1:
                    recursive_increment(n - 1)  # RLock permite re-entrada

        threads = [
            threading.Thread(target=recursive_increment, args=(increments_per_thread,))
            for _ in range(num_threads)
        ]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        return counter

    def demonstrate_race_condition_bank_account(self) -> dict:
        """
        Ejemplo realista: Cuenta bancaria con race condition
        """
        balance = 1000
        lock = threading.Lock()

        transactions_log = []

        def withdraw_unsafe(amount: int, customer: str):
            nonlocal balance
            # RACE CONDITION: check-then-act
            if balance >= amount:
                # Context switch aquí puede causar sobregiro
                time.sleep(0.001)  # Simula procesamiento
                balance -= amount
                transactions_log.append({
                    "customer": customer,
                    "amount": amount,
                    "balance_after": balance,
                    "thread": threading.current_thread().name
                })

        def withdraw_safe(amount: int, customer: str):
            nonlocal balance
            with lock:
                if balance >= amount:
                    time.sleep(0.001)
                    balance -= amount
                    transactions_log.append({
                        "customer": customer,
                        "amount": amount,
                        "balance_after": balance,
                        "thread": threading.current_thread().name,
                        "safe": True
                    })

        # Probar unsafe
        balance = 1000
        transactions_log = []
        threads = [
            threading.Thread(target=withdraw_unsafe, args=(600, f"Customer{i}"))
            for i in range(3)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        unsafe_result = {
            "final_balance": balance,
            "transactions": len(transactions_log),
            "overdraft": balance < 0
        }

        # Probar safe
        balance = 1000
        transactions_log = []
        threads = [
            threading.Thread(target=withdraw_safe, args=(600, f"Customer{i}"))
            for i in range(3)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        safe_result = {
            "final_balance": balance,
            "transactions": len(transactions_log),
            "overdraft": balance < 0
        }

        return {
            "unsafe": unsafe_result,
            "safe": safe_result,
            "note": "Unsafe puede resultar en sobregiro - safe previene esto"
        }

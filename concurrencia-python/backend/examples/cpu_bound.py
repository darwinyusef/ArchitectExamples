"""
EJEMPLOS CPU-BOUND
Operaciones que requieren procesamiento intensivo de CPU
El GIL NO se libera, por lo que threading NO ayuda.
Solución: multiprocessing
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from multiprocessing import Pool, cpu_count
from typing import List

class CPUBoundExamples:
    """
    Ejemplos de operaciones CPU-bound:
    - Cálculos matemáticos complejos
    - Procesamiento de imágenes
    - Análisis de datos
    - Compresión

    REGLA: Para CPU-bound, usa multiprocessing
    El GIL impide que threads ejecuten Python bytecode simultáneamente.
    """

    @staticmethod
    def cpu_intensive_task(n: int) -> int:
        """
        Tarea intensiva de CPU: calcular suma de cuadrados
        """
        return sum(i*i for i in range(n))

    @staticmethod
    def fibonacci(n: int) -> int:
        """
        Fibonacci recursivo - muy CPU intensive
        """
        if n <= 1:
            return n
        return CPUBoundExamples.fibonacci(n-1) + CPUBoundExamples.fibonacci(n-2)

    def sequential_calculation(self, iterations: int) -> dict:
        """
        Cálculos CPU de forma SECUENCIAL
        Tiempo total = sum(task_times)

        ❌ Muy lento pero simple
        """
        start = time.time()
        results = []

        for i in range(iterations):
            result = self.cpu_intensive_task(1000000)
            results.append(result)

        duration = time.time() - start

        return {
            "method": "sequential",
            "iterations": iterations,
            "results": len(results),
            "duration": duration
        }

    def threading_calculation(self, iterations: int) -> dict:
        """
        Cálculos CPU con THREADING

        ❌ NO mejora performance por el GIL
        De hecho puede ser MÁS LENTO por overhead de threads

        El GIL permite que solo un thread ejecute bytecode Python a la vez.
        """
        start = time.time()

        def worker(n):
            return self.cpu_intensive_task(1000000)

        with ThreadPoolExecutor(max_workers=iterations) as executor:
            futures = [executor.submit(worker, i) for i in range(iterations)]
            results = [future.result() for future in futures]

        duration = time.time() - start

        return {
            "method": "threading",
            "iterations": iterations,
            "results": len(results),
            "duration": duration,
            "note": "GIL impide paralelismo real - similar o peor que sequential"
        }

    def multiprocessing_calculation(self, iterations: int) -> dict:
        """
        Cálculos CPU con MULTIPROCESSING

        ✅✅ Evita el GIL - cada proceso tiene su propio intérprete
        Tiempo total ≈ task_time / num_cores

        NOTA: Hay overhead de crear procesos e intercomunicación (IPC)
        """
        start = time.time()

        # Usar número de CPUs disponibles
        num_processes = min(cpu_count(), iterations)

        with ProcessPoolExecutor(max_workers=num_processes) as executor:
            # Cada worker procesa una tarea
            tasks = [1000000] * iterations
            results = list(executor.map(self.cpu_intensive_task, tasks))

        duration = time.time() - start

        return {
            "method": "multiprocessing",
            "iterations": iterations,
            "processes_used": num_processes,
            "cpu_count": cpu_count(),
            "results": len(results),
            "duration": duration,
            "note": "Evita GIL - verdadero paralelismo"
        }

    def compare_all_methods(self, iterations: int = 4) -> dict:
        """
        Compara los 3 métodos y muestra las diferencias
        """
        print(f"\n🧮 Comparando métodos para {iterations} tareas CPU-intensive...\n")

        # Sequential
        print("1️⃣  Ejecutando Sequential...")
        seq_result = self.sequential_calculation(iterations)
        print(f"   ⏱️  {seq_result['duration']:.2f}s\n")

        # Threading (demostrar que NO ayuda)
        print("2️⃣  Ejecutando Threading...")
        thread_result = self.threading_calculation(iterations)
        print(f"   ⏱️  {thread_result['duration']:.2f}s (GIL impide mejora)\n")

        # Multiprocessing
        print("3️⃣  Ejecutando Multiprocessing...")
        mp_result = self.multiprocessing_calculation(iterations)
        print(f"   ⏱️  {mp_result['duration']:.2f}s (🚀 mucho más rápido)\n")

        return {
            "sequential": seq_result,
            "threading": thread_result,
            "multiprocessing": mp_result,
            "speedup_vs_sequential": seq_result["duration"] / mp_result["duration"],
            "gil_impact": {
                "threading_vs_sequential": thread_result["duration"] / seq_result["duration"],
                "note": "Threading similar/peor que sequential por el GIL"
            }
        }

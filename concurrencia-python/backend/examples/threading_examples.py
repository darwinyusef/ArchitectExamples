"""
THREADING - Ejemplos Detallados
Threading es útil para IO-bound, no para CPU-bound (por el GIL)
"""

import threading
import time
import queue
from typing import List, Dict

class ThreadingExamples:
    """Ejemplos completos de threading"""

    def basic_threading(self) -> dict:
        """Ejemplo básico de threads"""
        results = []

        def worker(worker_id: int, delay: float):
            print(f"Worker {worker_id} started")
            time.sleep(delay)
            result = f"Worker {worker_id} completed after {delay}s"
            results.append(result)

        threads = [
            threading.Thread(target=worker, args=(i, 0.5))
            for i in range(5)
        ]

        start = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        duration = time.time() - start

        return {"results": results, "duration": duration}

    def thread_pool_example(self, num_workers: int = 5) -> dict:
        """Thread Pool para reutilizar threads"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        results = []

        def io_task(task_id: int):
            time.sleep(0.3)
            return f"Task {task_id} completed"

        start = time.time()
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(io_task, i) for i in range(10)]
            for future in as_completed(futures):
                results.append(future.result())
        duration = time.time() - start

        return {
            "total_tasks": 10,
            "workers": num_workers,
            "duration": duration,
            "results": results[:5]
        }

    def daemon_threads_example(self) -> dict:
        """Daemon threads - terminan cuando el programa principal termina"""
        results = []

        def background_worker(worker_id: int):
            for i in range(3):
                time.sleep(0.2)
                results.append(f"Background {worker_id} - iteration {i}")

        # Thread normal
        normal_thread = threading.Thread(target=background_worker, args=(1,))
        # Thread daemon
        daemon_thread = threading.Thread(target=background_worker, args=(2,), daemon=True)

        normal_thread.start()
        daemon_thread.start()

        # Solo esperamos al thread normal
        normal_thread.join()

        return {
            "note": "Daemon threads terminan con el programa principal",
            "results": results
        }

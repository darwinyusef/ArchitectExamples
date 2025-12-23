"""
SEMÁFOROS - Limitar concurrencia
"""

import threading
import time
from typing import List

class SemaphoreExamples:
    """Ejemplos de semáforos"""

    async def rate_limited_tasks(self, num_tasks: int, max_concurrent: int = 3) -> List[str]:
        """Limitar número de tareas concurrentes con semáforo"""
        import asyncio

        semaphore = asyncio.Semaphore(max_concurrent)
        results = []

        async def limited_task(task_id: int):
            async with semaphore:
                await asyncio.sleep(0.5)
                result = f"Task {task_id} completed"
                results.append(result)
                return result

        await asyncio.gather(*[limited_task(i) for i in range(num_tasks)])
        return results

    def threading_semaphore_example(self, num_threads: int = 10, max_concurrent: int = 3) -> dict:
        """Semáforo con threading - limitar acceso a recurso compartido"""
        semaphore = threading.Semaphore(max_concurrent)
        results = []
        active_count = []

        def worker(worker_id: int):
            with semaphore:
                active_count.append(worker_id)
                current_active = len([w for w in active_count if w == worker_id])
                results.append(f"Worker {worker_id} acquired semaphore (active: {current_active})")
                time.sleep(0.3)
                results.append(f"Worker {worker_id} released semaphore")

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(num_threads)]

        start = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        duration = time.time() - start

        return {
            "total_workers": num_threads,
            "max_concurrent": max_concurrent,
            "duration": duration,
            "results": results[:10]
        }

    def bounded_semaphore_example(self) -> dict:
        """BoundedSemaphore - previene release() más veces que acquire()"""
        bounded_sem = threading.BoundedSemaphore(2)
        results = []

        # Acquire 2 veces (OK)
        bounded_sem.acquire()
        results.append("First acquire OK")
        bounded_sem.acquire()
        results.append("Second acquire OK")

        # Release 2 veces (OK)
        bounded_sem.release()
        results.append("First release OK")
        bounded_sem.release()
        results.append("Second release OK")

        # Intentar release una vez más (ERROR con BoundedSemaphore)
        try:
            bounded_sem.release()
            results.append("Third release OK - ¡No debería pasar!")
        except ValueError as e:
            results.append(f"Third release BLOCKED: {str(e)}")

        return {
            "note": "BoundedSemaphore previene release() excesivo",
            "results": results
        }

    def connection_pool_example(self, num_requests: int = 10, pool_size: int = 3) -> dict:
        """Simular pool de conexiones con semáforo"""
        pool = threading.Semaphore(pool_size)
        results = []

        def make_request(request_id: int):
            results.append(f"Request {request_id} waiting for connection...")
            with pool:
                results.append(f"Request {request_id} got connection")
                time.sleep(0.2)  # Simular request
                results.append(f"Request {request_id} released connection")

        threads = [threading.Thread(target=make_request, args=(i,)) for i in range(num_requests)]

        start = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        duration = time.time() - start

        return {
            "total_requests": num_requests,
            "pool_size": pool_size,
            "duration": duration,
            "expected_duration": f"~{(num_requests / pool_size) * 0.2:.2f}s",
            "results": results[:15]
        }

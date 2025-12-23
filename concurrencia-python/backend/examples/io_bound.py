"""
EJEMPLOS IO-BOUND
Operaciones que esperan por entrada/salida (red, disco, etc.)
El GIL se libera durante operaciones de IO, por lo que threading ayuda.
"""

import time
import threading
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from typing import List

class IOBoundExamples:
    """
    Ejemplos de operaciones IO-bound:
    - Network requests
    - File I/O
    - Database queries

    REGLA: Para IO-bound, usa async/await o threading
    El GIL se libera durante IO, permitiendo que otros threads ejecuten.
    """

    def simulate_io_operation(self, duration: float = 0.5) -> dict:
        """
        Simula una operación de IO (network request, db query, etc.)
        """
        time.sleep(duration)  # Simula IO - libera el GIL
        return {
            "thread": threading.current_thread().name,
            "duration": duration,
            "timestamp": time.time()
        }

    def sequential_requests(self, num_requests: int) -> List[dict]:
        """
        Operaciones IO de forma SECUENCIAL
        Tiempo total = sum(durations)

        ❌ Problema: Bloquea todo - muy lento
        """
        results = []
        for i in range(num_requests):
            result = self.simulate_io_operation(0.5)
            result["request_id"] = i
            results.append(result)
        return results

    def threading_requests(self, num_requests: int) -> List[dict]:
        """
        Operaciones IO con THREADING
        Tiempo total ≈ max(durations) - mucho más rápido

        ✅ Bueno para IO-bound: El GIL se libera durante sleep/IO
        """
        results = []

        def worker(request_id):
            result = self.simulate_io_operation(0.5)
            result["request_id"] = request_id
            return result

        # Usar ThreadPoolExecutor para gestionar threads
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(worker, i) for i in range(num_requests)]
            results = [future.result() for future in futures]

        return results

    async def async_requests(self, num_requests: int) -> List[dict]:
        """
        Operaciones IO con ASYNC/AWAIT
        Tiempo total ≈ max(durations)

        ✅✅ MEJOR opción: No crea threads, usa cooperative multitasking
        """
        async def async_io_operation(request_id: int) -> dict:
            await asyncio.sleep(0.5)  # Simula async IO
            return {
                "request_id": request_id,
                "thread": threading.current_thread().name,
                "duration": 0.5,
                "timestamp": time.time()
            }

        # Ejecutar todas las coroutines concurrentemente
        results = await asyncio.gather(*[
            async_io_operation(i) for i in range(num_requests)
        ])

        return results

    async def real_http_requests(self, urls: List[str]) -> List[dict]:
        """
        Ejemplo REAL de requests HTTP async
        """
        async with aiohttp.ClientSession() as session:
            async def fetch(url: str) -> dict:
                start = time.time()
                try:
                    async with session.get(url) as response:
                        status = response.status
                        # Opcional: leer respuesta
                        # data = await response.text()
                except Exception as e:
                    status = None

                return {
                    "url": url,
                    "status": status,
                    "duration": time.time() - start
                }

            results = await asyncio.gather(*[fetch(url) for url in urls])
            return results

"""
ASYNC/AWAIT - Ejemplos Avanzados
"""

import asyncio
import time
from typing import List

class AsyncExamples:
    """Ejemplos de async/await"""

    async def gather_example(self, num_tasks: int) -> List[str]:
        """asyncio.gather - ejecutar múltiples coroutines"""
        async def task(task_id: int):
            await asyncio.sleep(0.5)
            return f"Task {task_id} completed"

        results = await asyncio.gather(*[task(i) for i in range(num_tasks)])
        return results

    async def run_in_executor_example(self, num_tasks: int) -> List[str]:
        """run_in_executor - mezclar async con código bloqueante"""
        import concurrent.futures

        def blocking_task(task_id: int):
            time.sleep(0.5)
            return f"Blocking task {task_id} completed"

        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = await asyncio.gather(*[
                loop.run_in_executor(executor, blocking_task, i)
                for i in range(num_tasks)
            ])
        return results

    async def timeout_example(self, timeout: float = 1.0) -> dict:
        """asyncio.wait_for - timeout para tareas async"""
        async def slow_task():
            await asyncio.sleep(2.0)
            return "Completed"

        try:
            result = await asyncio.wait_for(slow_task(), timeout=timeout)
            return {"status": "success", "result": result}
        except asyncio.TimeoutError:
            return {"status": "timeout", "message": f"Task exceeded {timeout}s"}

    async def as_completed_example(self, num_tasks: int) -> List[dict]:
        """asyncio.as_completed - procesar resultados conforme completan"""
        async def task(task_id: int, delay: float):
            await asyncio.sleep(delay)
            return {"task_id": task_id, "delay": delay}

        # Tareas con diferentes delays
        delays = [0.3, 0.1, 0.5, 0.2, 0.4][:num_tasks]
        tasks = [task(i, delays[i]) for i in range(num_tasks)]

        results = []
        for completed_task in asyncio.as_completed(tasks):
            result = await completed_task
            results.append(result)

        return results

    async def semaphore_example(self, num_tasks: int, max_concurrent: int = 3) -> dict:
        """asyncio.Semaphore - limitar concurrencia"""
        semaphore = asyncio.Semaphore(max_concurrent)
        completed = []

        async def limited_task(task_id: int):
            async with semaphore:
                await asyncio.sleep(0.5)
                completed.append(task_id)
                return f"Task {task_id}"

        start = time.time()
        results = await asyncio.gather(*[limited_task(i) for i in range(num_tasks)])
        duration = time.time() - start

        return {
            "total_tasks": num_tasks,
            "max_concurrent": max_concurrent,
            "duration": duration,
            "results": results
        }

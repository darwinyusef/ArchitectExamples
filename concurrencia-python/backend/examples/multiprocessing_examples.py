"""
MULTIPROCESSING - Evita el GIL
Cada proceso tiene su propio intérprete Python
"""

from multiprocessing import Process, Queue, Pool, cpu_count
import time

class MultiprocessingExamples:
    """Ejemplos de multiprocessing"""

    def basic_multiprocessing(self, num_processes: int = 4) -> dict:
        """Ejemplo básico de multiprocessing - evita el GIL"""
        def cpu_task(task_id: int):
            total = 0
            for i in range(1000000):
                total += i * i
            return f"Process {task_id}: {total}"

        start = time.time()
        with Pool(processes=num_processes) as pool:
            results = pool.map(cpu_task, range(num_processes))
        duration = time.time() - start

        return {
            "note": "Multiprocessing evita el GIL - cada proceso tiene su propio intérprete",
            "num_processes": num_processes,
            "cpu_count": cpu_count(),
            "duration": duration,
            "results": results
        }

    def process_with_queue(self, num_items: int = 10) -> dict:
        """Comunicación entre procesos con Queue"""
        def producer(queue: Queue, num_items: int):
            for i in range(num_items):
                queue.put(f"Item-{i}")
                time.sleep(0.1)
            queue.put(None)  # Señal de finalización

        def consumer(queue: Queue, results_queue: Queue):
            processed = []
            while True:
                item = queue.get()
                if item is None:
                    break
                processed.append(f"Processed: {item}")
            results_queue.put(processed)

        task_queue = Queue()
        results_queue = Queue()

        producer_process = Process(target=producer, args=(task_queue, num_items))
        consumer_process = Process(target=consumer, args=(task_queue, results_queue))

        start = time.time()
        producer_process.start()
        consumer_process.start()

        producer_process.join()
        consumer_process.join()
        duration = time.time() - start

        results = results_queue.get()

        return {
            "pattern": "Producer-Consumer with Queue",
            "duration": duration,
            "processed": len(results),
            "results": results[:5]
        }

    def pool_map_example(self, numbers: list = None) -> dict:
        """Pool.map para procesamiento paralelo"""
        if numbers is None:
            numbers = list(range(10))

        def square(n: int):
            time.sleep(0.1)
            return n * n

        start = time.time()
        with Pool(processes=min(cpu_count(), 4)) as pool:
            results = pool.map(square, numbers)
        duration = time.time() - start

        return {
            "input": numbers,
            "output": results,
            "duration": duration,
            "speedup": f"{len(numbers) * 0.1 / duration:.2f}x"
        }

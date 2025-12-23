"""
QUEUES - Comunicación entre threads/processes
"""

import threading
import queue
import time

class QueueExamples:
    """Ejemplos de queues"""

    def producer_consumer_pattern(self, num_consumers: int, num_tasks: int) -> dict:
        """Patrón productor-consumidor"""
        task_queue = queue.Queue()
        results = []

        def producer():
            for i in range(num_tasks):
                task_queue.put(f"Task-{i}")
                time.sleep(0.01)
            # Señal de finalización
            for _ in range(num_consumers):
                task_queue.put(None)

        def consumer():
            while True:
                task = task_queue.get()
                if task is None:
                    break
                time.sleep(0.1)
                results.append(task)
                task_queue.task_done()

        # Iniciar productor
        producer_thread = threading.Thread(target=producer)
        producer_thread.start()

        # Iniciar consumidores
        consumers = [threading.Thread(target=consumer) for _ in range(num_consumers)]
        for c in consumers:
            c.start()

        producer_thread.join()
        for c in consumers:
            c.join()

        return {"processed": len(results), "results": results[:10]}

    def priority_queue_example(self) -> dict:
        """PriorityQueue - procesa items por prioridad"""
        pq = queue.PriorityQueue()
        results = []

        # Añadir items con prioridad (número menor = mayor prioridad)
        items = [
            (3, "Low priority task"),
            (1, "High priority task"),
            (2, "Medium priority task"),
            (1, "Another high priority task")
        ]

        for priority, task in items:
            pq.put((priority, task))

        # Procesar en orden de prioridad
        while not pq.empty():
            priority, task = pq.get()
            results.append({"priority": priority, "task": task})

        return {"results": results}

    def lifo_queue_example(self) -> dict:
        """LifoQueue - Last In First Out (como una pila)"""
        lq = queue.LifoQueue()
        results = []

        # Añadir items
        for i in range(5):
            lq.put(f"Item-{i}")

        # Procesar (último en entrar, primero en salir)
        while not lq.empty():
            item = lq.get()
            results.append(item)

        return {
            "pattern": "LIFO (Stack)",
            "input_order": [f"Item-{i}" for i in range(5)],
            "output_order": results
        }

    def bounded_queue_example(self, max_size: int = 3) -> dict:
        """Queue con tamaño máximo - bloquea cuando está llena"""
        bounded_q = queue.Queue(maxsize=max_size)
        results = []

        def producer():
            for i in range(10):
                bounded_q.put(f"Item-{i}")
                results.append(f"Produced: Item-{i}")
                time.sleep(0.05)

        def consumer():
            for _ in range(10):
                time.sleep(0.1)  # Consume más lento que produce
                item = bounded_q.get()
                results.append(f"Consumed: {item}")

        prod_thread = threading.Thread(target=producer)
        cons_thread = threading.Thread(target=consumer)

        prod_thread.start()
        cons_thread.start()

        prod_thread.join()
        cons_thread.join()

        return {
            "max_size": max_size,
            "note": "Producer blocks when queue is full",
            "events": results[:20]
        }

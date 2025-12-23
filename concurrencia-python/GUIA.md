# Guía Completa de Concurrencia y Paralelismo en Python

## Índice

1. [Fundamentos](#1-fundamentos)
2. [El GIL (Global Interpreter Lock)](#2-el-gil-global-interpreter-lock)
3. [IO-bound vs CPU-bound](#3-io-bound-vs-cpu-bound)
4. [Threading](#4-threading)
5. [Multiprocessing](#5-multiprocessing)
6. [Async/await](#6-asyncawait)
7. [Problemas de Concurrencia](#7-problemas-de-concurrencia)
8. [Primitivas de Sincronización](#8-primitivas-de-sincronización)
9. [Queues y Comunicación](#9-queues-y-comunicación)
10. [Patrones Avanzados](#10-patrones-avanzados)
11. [Observabilidad](#11-observabilidad)
12. [Mejores Prácticas](#12-mejores-prácticas)

---

## 1. Fundamentos

### 1.1 ¿Qué es Concurrencia?

**Concurrencia** es la capacidad de manejar múltiples tareas al mismo tiempo, aunque no necesariamente se ejecuten simultáneamente.

```
Concurrencia (1 core):
T1: ████░░░░████░░░░
T2: ░░░░████░░░░████
    → Las tareas se intercalan
```

### 1.2 ¿Qué es Paralelismo?

**Paralelismo** es la ejecución simultánea de múltiples tareas en diferentes cores.

```
Paralelismo (2 cores):
Core 1: ████████████████
Core 2: ████████████████
    → Ejecución verdaderamente simultánea
```

### 1.3 Diferencias Clave

| Aspecto | Concurrencia | Paralelismo |
|---------|--------------|-------------|
| Definición | Gestionar múltiples tareas | Ejecutar múltiples tareas simultáneamente |
| Hardware | Puede ser 1 core | Requiere múltiples cores |
| Objetivo | Mejor aprovechamiento | Mayor throughput |
| Ejemplo | Servidor web manejando requests | Procesamiento de imagen en GPU |

---

## 2. El GIL (Global Interpreter Lock)

### 2.1 ¿Qué es el GIL?

El GIL es un **mutex global** en CPython que permite que solo un thread ejecute bytecode de Python a la vez.

```python
# Pseudocódigo del GIL
while True:
    acquire_gil()
    execute_bytecode()  # Solo 1 thread puede estar aquí
    release_gil()
```

### 2.2 ¿Por qué existe el GIL?

1. **Gestión de memoria simple**: CPython usa reference counting
2. **Protección de estructuras internas**: Evita race conditions en el intérprete
3. **Integración con C**: Facilita extensiones en C

### 2.3 Implicaciones del GIL

#### Para IO-bound

✅ **El GIL se libera durante I/O**

```python
# Durante operaciones de I/O, el GIL se libera
def fetch_url(url):
    response = requests.get(url)  # GIL liberado aquí
    return response.text

# Threading funciona bien para I/O
with ThreadPoolExecutor() as executor:
    results = executor.map(fetch_url, urls)  # Efectivo
```

#### Para CPU-bound

❌ **El GIL NO se libera durante cálculos**

```python
def calculate(n):
    total = 0
    for i in range(n):  # GIL retenido durante todo el loop
        total += i * i
    return total

# Threading NO ayuda (puede ser peor)
with ThreadPoolExecutor() as executor:
    results = executor.map(calculate, data)  # Inefectivo
```

### 2.4 Visualización del GIL

```
CPU-bound con Threading (1 core efectivo):
─────────────────────────────────────────
Thread 1: ████░░░░░░░░████░░░░░░░░
Thread 2: ░░░░████░░░░░░░░████░░░░
Thread 3: ░░░░░░░░████░░░░░░░░████
          └── Solo 1 ejecuta a la vez

CPU-bound con Multiprocessing (N cores):
─────────────────────────────────────────
Process 1: ████████████████████████
Process 2: ████████████████████████
Process 3: ████████████████████████
           └── Ejecución paralela real
```

### 2.5 Escapar del GIL

1. **Multiprocessing**: Cada proceso tiene su propio intérprete y GIL
2. **Extensiones C**: `nogil` en Cython
3. **NumPy/Pandas**: Liberan GIL en operaciones pesadas
4. **PyPy/GIL-less Python**: Implementaciones alternativas

---

## 3. IO-bound vs CPU-bound

### 3.1 IO-bound

**Definición**: Operaciones limitadas por velocidad de I/O (disco, red, DB)

**Características**:
- Pasan mayoría del tiempo esperando
- CPU mayormente idle
- GIL se libera durante I/O

**Ejemplos**:
```python
# Requests HTTP
response = requests.get('https://api.example.com')

# Lectura de archivos
with open('large_file.txt') as f:
    data = f.read()

# Queries a base de datos
results = db.execute('SELECT * FROM users')

# Sleep
time.sleep(5)
```

**Mejor solución**: Async/await o Threading

### 3.2 CPU-bound

**Definición**: Operaciones limitadas por velocidad de CPU

**Características**:
- CPU al 100%
- Poco tiempo de espera
- GIL es el cuello de botella

**Ejemplos**:
```python
# Cálculos matemáticos
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Procesamiento de datos
data = [x * x for x in range(10_000_000)]

# Compresión
compressed = gzip.compress(large_data)

# Criptografía
hash = hashlib.sha256(data).hexdigest()
```

**Mejor solución**: Multiprocessing

### 3.3 Tabla de Decisión

| Tipo | CPU Usage | Espera I/O | Threading | Multiprocessing | Async |
|------|-----------|------------|-----------|-----------------|-------|
| IO-bound | Bajo | Alta | ✅ Bueno | ⚠️ Overkill | ✅✅ Mejor |
| CPU-bound | Alto | Baja | ❌ Malo | ✅✅ Mejor | ❌ Malo |
| Mixed | Medio | Media | ⚠️ Depende | ✅ Bueno | ✅ Bueno |

### 3.4 Ejemplo Comparativo

```python
import time
import requests
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# IO-bound
def io_task():
    response = requests.get('https://httpbin.org/delay/1')
    return response.status_code

# CPU-bound
def cpu_task():
    return sum(i * i for i in range(10_000_000))

# Comparar IO-bound
print("IO-bound:")
t1 = time.time()
for _ in range(5):
    io_task()
print(f"Secuencial: {time.time() - t1:.2f}s")  # ~5s

t1 = time.time()
with ThreadPoolExecutor(5) as executor:
    list(executor.map(lambda x: io_task(), range(5)))
print(f"Threading: {time.time() - t1:.2f}s")  # ~1s ✅

# Comparar CPU-bound
print("\nCPU-bound:")
t1 = time.time()
for _ in range(4):
    cpu_task()
print(f"Secuencial: {time.time() - t1:.2f}s")  # ~4s

t1 = time.time()
with ThreadPoolExecutor(4) as executor:
    list(executor.map(lambda x: cpu_task(), range(4)))
print(f"Threading: {time.time() - t1:.2f}s")  # ~4s ❌ (GIL)

t1 = time.time()
with ProcessPoolExecutor(4) as executor:
    list(executor.map(lambda x: cpu_task(), range(4)))
print(f"Multiprocessing: {time.time() - t1:.2f}s")  # ~1s ✅
```

---

## 4. Threading

### 4.1 Conceptos Básicos

**Thread**: Hilo de ejecución dentro de un proceso que comparte memoria.

```python
import threading

def worker(name):
    print(f"Thread {name} started")
    time.sleep(2)
    print(f"Thread {name} finished")

# Crear y ejecutar thread
t = threading.Thread(target=worker, args=("A",))
t.start()  # Inicia ejecución
t.join()   # Espera a que termine
```

### 4.2 Thread States

```
NEW → RUNNABLE → RUNNING → TERMINATED
         ↑         ↓
         └── BLOCKED/WAITING
```

### 4.3 Thread Pool

**Ventajas**:
- Reutiliza threads (menos overhead)
- Limita concurrencia
- API simple

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def task(n):
    time.sleep(1)
    return n * n

# Ejecutar tareas
with ThreadPoolExecutor(max_workers=5) as executor:
    # Opción 1: map (orden preservado)
    results = executor.map(task, range(10))

    # Opción 2: submit (más control)
    futures = [executor.submit(task, i) for i in range(10)]

    # Opción 3: as_completed (procesar conforme terminan)
    for future in as_completed(futures):
        result = future.result()
        print(f"Got result: {result}")
```

### 4.4 Daemon Threads

**Daemon**: Thread que termina automáticamente cuando el programa principal termina.

```python
def background_worker():
    while True:
        do_background_work()
        time.sleep(1)

# Thread daemon
t = threading.Thread(target=background_worker, daemon=True)
t.start()

# El programa puede terminar sin esperar a este thread
```

**Usos comunes**:
- Heartbeats
- Monitoring
- Cleanup tasks

### 4.5 Thread Local Storage

```python
import threading

# Variable local a cada thread
thread_local = threading.local()

def worker():
    # Cada thread tiene su propia copia
    thread_local.value = threading.current_thread().name
    print(thread_local.value)

t1 = threading.Thread(target=worker)
t2 = threading.Thread(target=worker)
t1.start()
t2.start()
```

---

## 5. Multiprocessing

### 5.1 Conceptos Básicos

**Process**: Proceso independiente con su propio espacio de memoria y GIL.

```python
from multiprocessing import Process

def worker(name):
    print(f"Process {name} PID: {os.getpid()}")

if __name__ == '__main__':
    p = Process(target=worker, args=("A",))
    p.start()
    p.join()
```

### 5.2 Process Pool

```python
from multiprocessing import Pool, cpu_count

def task(n):
    return n * n

if __name__ == '__main__':
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(task, range(10))
```

### 5.3 Comunicación entre Procesos

#### Queue

```python
from multiprocessing import Process, Queue

def producer(queue):
    for i in range(5):
        queue.put(f"Item {i}")
    queue.put(None)  # Señal de fin

def consumer(queue):
    while True:
        item = queue.get()
        if item is None:
            break
        print(f"Consumed: {item}")

if __name__ == '__main__':
    q = Queue()
    p1 = Process(target=producer, args=(q,))
    p2 = Process(target=consumer, args=(q,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
```

#### Pipe

```python
from multiprocessing import Process, Pipe

def sender(conn):
    conn.send("Hello from child")
    conn.close()

if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p = Process(target=sender, args=(child_conn,))
    p.start()
    print(parent_conn.recv())
    p.join()
```

#### Manager

```python
from multiprocessing import Process, Manager

def worker(shared_dict, key, value):
    shared_dict[key] = value

if __name__ == '__main__':
    with Manager() as manager:
        shared_dict = manager.dict()
        processes = []

        for i in range(5):
            p = Process(target=worker, args=(shared_dict, f"key{i}", i))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        print(dict(shared_dict))
```

### 5.4 Threading vs Multiprocessing

| Aspecto | Threading | Multiprocessing |
|---------|-----------|-----------------|
| Memoria | Compartida | Separada |
| Comunicación | Rápida (mismo espacio) | Lenta (serialización) |
| Overhead | Bajo | Alto |
| GIL | Afectado | No afectado |
| Debugging | Más fácil | Más difícil |
| Uso | IO-bound | CPU-bound |

---

## 6. Async/await

### 6.1 Event Loop

```
Event Loop Cycle:
┌─────────────────────────────────┐
│  1. Check for ready callbacks   │
│  2. Run callbacks                │
│  3. Check for I/O events         │
│  4. Schedule I/O callbacks       │
│  5. Check for timers             │
│  6. Repeat                       │
└─────────────────────────────────┘
```

### 6.2 Coroutines

```python
import asyncio

async def fetch_data(id):
    print(f"Fetching {id}...")
    await asyncio.sleep(1)  # Simular I/O
    return f"Data {id}"

# Ejecutar
async def main():
    result = await fetch_data(1)
    print(result)

asyncio.run(main())
```

### 6.3 Patterns Comunes

#### gather - Ejecutar múltiples coroutines

```python
async def main():
    results = await asyncio.gather(
        fetch_data(1),
        fetch_data(2),
        fetch_data(3)
    )
    print(results)  # ['Data 1', 'Data 2', 'Data 3']
```

#### as_completed - Procesar conforme completan

```python
async def main():
    tasks = [fetch_data(i) for i in range(5)]

    for coro in asyncio.as_completed(tasks):
        result = await coro
        print(f"Got: {result}")
```

#### wait_for - Timeout

```python
async def main():
    try:
        result = await asyncio.wait_for(
            fetch_data(1),
            timeout=0.5
        )
    except asyncio.TimeoutError:
        print("Timeout!")
```

#### create_task - Background tasks

```python
async def background_task():
    while True:
        await asyncio.sleep(1)
        print("Background work")

async def main():
    # Crear tarea en background
    task = asyncio.create_task(background_task())

    # Hacer otra cosa
    await asyncio.sleep(5)

    # Cancelar
    task.cancel()
```

### 6.4 Semaphores en Async

```python
async def limited_task(sem, id):
    async with sem:
        print(f"Task {id} running")
        await asyncio.sleep(1)

async def main():
    # Máximo 3 tareas concurrentes
    sem = asyncio.Semaphore(3)

    await asyncio.gather(*[
        limited_task(sem, i) for i in range(10)
    ])
```

---

## 7. Problemas de Concurrencia

### 7.1 Race Conditions

**Definición**: Múltiples threads acceden a datos compartidos sin sincronización.

```python
# PROBLEMA
counter = 0

def increment():
    global counter
    temp = counter    # T1 lee: 0
    time.sleep(0.001) # T2 lee: 0
    counter = temp + 1 # T1 escribe: 1
                      # T2 escribe: 1  ← ¡Perdimos un incremento!

# Resultado: counter = 1 (esperado: 2)
```

**Solución**: Lock

```python
lock = threading.Lock()

def increment():
    global counter
    with lock:
        temp = counter
        time.sleep(0.001)
        counter = temp + 1
```

### 7.2 Deadlock

**Definición**: Dos o más threads esperan recursos que otros threads tienen.

```python
# PROBLEMA
lock_a = threading.Lock()
lock_b = threading.Lock()

def thread1():
    with lock_a:      # T1 adquiere A
        time.sleep(0.1)
        with lock_b:  # T1 espera B (T2 lo tiene)
            pass

def thread2():
    with lock_b:      # T2 adquiere B
        time.sleep(0.1)
        with lock_a:  # T2 espera A (T1 lo tiene)
            pass

# DEADLOCK: T1 espera T2, T2 espera T1
```

**Solución**: Orden consistente de locks

```python
def thread1():
    with lock_a:  # Siempre A primero
        with lock_b:
            pass

def thread2():
    with lock_a:  # Siempre A primero
        with lock_b:
            pass
```

**Condiciones para Deadlock** (todas deben cumplirse):
1. Mutual exclusion
2. Hold and wait
3. No preemption
4. Circular wait

### 7.3 Starvation

**Definición**: Un thread nunca obtiene recursos porque otros siempre lo adelantan.

```python
# Ejemplo: Priority inversion
high_priority_thread = threading.Thread(target=important_work, daemon=False)
low_priority_thread = threading.Thread(target=background_work, daemon=True)

# Si hay muchos threads de alta prioridad, los de baja pueden nunca ejecutar
```

**Soluciones**:
- Fair locks (FIFO)
- Priority queues
- Aging (aumentar prioridad con tiempo)

### 7.4 Livelock

**Definición**: Threads cambian estado en respuesta a otros pero no progresan.

```python
# Ejemplo: Dos personas en un pasillo
# Ambos se mueven al mismo lado infinitamente
```

---

## 8. Primitivas de Sincronización

### 8.1 Lock (Mutex)

```python
lock = threading.Lock()

# Uso 1: with (recomendado)
with lock:
    critical_section()

# Uso 2: acquire/release manual
lock.acquire()
try:
    critical_section()
finally:
    lock.release()  # Importante: siempre release
```

### 8.2 RLock (Reentrant Lock)

```python
rlock = threading.RLock()

def recursive_function(n):
    with rlock:  # Mismo thread puede re-adquirir
        if n > 0:
            recursive_function(n - 1)
```

### 8.3 Semaphore

```python
# Permite N accesos concurrentes
sem = threading.Semaphore(3)

def worker():
    with sem:  # Máximo 3 threads aquí simultáneamente
        do_work()
```

### 8.4 Event

```python
event = threading.Event()

def waiter():
    print("Waiting...")
    event.wait()  # Bloquea hasta que se active
    print("Event received!")

def setter():
    time.sleep(2)
    event.set()  # Activa el event
```

### 8.5 Condition

```python
condition = threading.Condition()
data = []

def consumer():
    with condition:
        while not data:
            condition.wait()  # Espera notificación
        item = data.pop()
        process(item)

def producer():
    with condition:
        data.append(new_item)
        condition.notify()  # Notifica a un waiter
```

### 8.6 Barrier

```python
barrier = threading.Barrier(3)  # Espera 3 threads

def worker(id):
    print(f"Thread {id} working...")
    time.sleep(random.random())
    print(f"Thread {id} at barrier")
    barrier.wait()  # Todos esperan aquí
    print(f"Thread {id} continuing")
```

---

## 9. Queues y Comunicación

### 9.1 Queue (FIFO)

```python
from queue import Queue

q = Queue()

# Producer
q.put("item1")
q.put("item2")

# Consumer
item = q.get()      # "item1"
q.task_done()       # Marca como procesado

q.join()  # Espera a que todas las tareas se completen
```

### 9.2 LifoQueue (Stack)

```python
from queue import LifoQueue

q = LifoQueue()
q.put(1)
q.put(2)
q.put(3)

print(q.get())  # 3 (último en entrar)
print(q.get())  # 2
print(q.get())  # 1
```

### 9.3 PriorityQueue

```python
from queue import PriorityQueue

pq = PriorityQueue()

# (prioridad, valor)
pq.put((1, "alta prioridad"))
pq.put((3, "baja prioridad"))
pq.put((2, "media prioridad"))

while not pq.empty():
    priority, item = pq.get()
    print(item)
# Output:
# alta prioridad
# media prioridad
# baja prioridad
```

### 9.4 Bounded Queue

```python
# Queue con tamaño máximo
q = Queue(maxsize=10)

q.put(item)        # Bloquea si está llena
q.put(item, block=False)  # Raise Full exception
q.put(item, timeout=5)    # Timeout después de 5s
```

---

## 10. Patrones Avanzados

### 10.1 run_in_executor

**Problema**: Ejecutar código bloqueante en async sin bloquear event loop

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

def blocking_io():
    # Función bloqueante (ej: requests, DB query)
    time.sleep(2)
    return "result"

async def main():
    loop = asyncio.get_event_loop()

    # Ejecutar en thread pool
    result = await loop.run_in_executor(
        None,  # None = usar default executor
        blocking_io
    )

    # Con executor personalizado
    with ThreadPoolExecutor(max_workers=5) as executor:
        result = await loop.run_in_executor(
            executor,
            blocking_io
        )
```

### 10.2 Producer-Consumer

```python
from queue import Queue
import threading

def producer(queue, items):
    for item in items:
        queue.put(item)
        print(f"Produced: {item}")
    # Señal de fin
    queue.put(None)

def consumer(queue):
    while True:
        item = queue.get()
        if item is None:
            break
        print(f"Consumed: {item}")
        queue.task_done()

# Uso
q = Queue()
items = range(10)

prod = threading.Thread(target=producer, args=(q, items))
cons = threading.Thread(target=consumer, args=(q,))

prod.start()
cons.start()

prod.join()
cons.join()
```

### 10.3 Worker Pool

```python
from concurrent.futures import ThreadPoolExecutor

class WorkerPool:
    def __init__(self, num_workers):
        self.executor = ThreadPoolExecutor(max_workers=num_workers)

    def submit_task(self, func, *args):
        return self.executor.submit(func, *args)

    def map_tasks(self, func, items):
        return self.executor.map(func, items)

    def shutdown(self):
        self.executor.shutdown(wait=True)

# Uso
pool = WorkerPool(5)
futures = [pool.submit_task(task, i) for i in range(10)]
results = [f.result() for f in futures]
pool.shutdown()
```

### 10.4 Rate Limiting

```python
import asyncio
from asyncio import Semaphore

class RateLimiter:
    def __init__(self, max_rate, time_period):
        self.semaphore = Semaphore(max_rate)
        self.time_period = time_period

    async def __aenter__(self):
        await self.semaphore.acquire()
        return self

    async def __aexit__(self, *args):
        await asyncio.sleep(self.time_period)
        self.semaphore.release()

# Uso: Máximo 10 requests por segundo
limiter = RateLimiter(10, 1.0)

async def make_request(url):
    async with limiter:
        return await fetch(url)
```

---

## 11. Observabilidad

### 11.1 Métricas Importantes

1. **Duración de operaciones**
2. **CPU usage**
3. **Memoria usage**
4. **Número de threads/procesos**
5. **Tasa de éxito/fallo**
6. **Queue size**

### 11.2 Implementación

```python
import time
import psutil
from dataclasses import dataclass

@dataclass
class Metrics:
    operation: str
    duration: float
    cpu_percent: float
    memory_mb: float
    success: bool

class MetricsCollector:
    def __init__(self):
        self.metrics = []

    def record(self, operation, duration, success=True):
        process = psutil.Process()
        self.metrics.append(Metrics(
            operation=operation,
            duration=duration,
            cpu_percent=process.cpu_percent(),
            memory_mb=process.memory_info().rss / 1024 / 1024,
            success=success
        ))

    def summary(self):
        if not self.metrics:
            return "No metrics"

        total = len(self.metrics)
        successful = sum(1 for m in self.metrics if m.success)
        avg_duration = sum(m.duration for m in self.metrics) / total

        return {
            "total": total,
            "successful": successful,
            "success_rate": f"{successful/total*100:.2f}%",
            "avg_duration": f"{avg_duration:.3f}s"
        }
```

---

## 12. Mejores Prácticas

### 12.1 General

1. **Usa el enfoque correcto**
   - IO-bound → Async > Threading
   - CPU-bound → Multiprocessing

2. **Limita la concurrencia**
   ```python
   # Mal: Sin límite
   tasks = [asyncio.create_task(fetch(url)) for url in huge_list]

   # Bien: Con semáforo
   sem = asyncio.Semaphore(100)
   async def limited_fetch(url):
       async with sem:
           return await fetch(url)
   ```

3. **Maneja errores**
   ```python
   try:
       result = future.result()
   except Exception as e:
       logging.error(f"Task failed: {e}")
   ```

### 12.2 Threading

1. **Usa context managers**
   ```python
   # Bien
   with lock:
       critical_section()

   # Mal
   lock.acquire()
   critical_section()
   lock.release()  # Puede no ejecutarse si hay exception
   ```

2. **Evita locks compartidos cuando sea posible**
   ```python
   # Mejor: usar queue para comunicación
   q = Queue()
   ```

3. **Usa daemon=True para threads de background**
   ```python
   t = threading.Thread(target=monitor, daemon=True)
   ```

### 12.3 Async

1. **Nunca uses código bloqueante**
   ```python
   # Mal
   async def bad():
       time.sleep(1)  # Bloquea event loop

   # Bien
   async def good():
       await asyncio.sleep(1)
   ```

2. **Usa run_in_executor para código bloqueante inevitable**
   ```python
   await loop.run_in_executor(None, requests.get, url)
   ```

3. **Cancela tareas correctamente**
   ```python
   task = asyncio.create_task(long_operation())
   try:
       await asyncio.wait_for(task, timeout=5)
   except asyncio.TimeoutError:
       task.cancel()
       await task  # Espera cancelación
   ```

### 12.4 Multiprocessing

1. **Usa `if __name__ == '__main__':`**
   ```python
   if __name__ == '__main__':
       # Código de multiprocessing aquí
   ```

2. **Serializa solo lo necesario**
   ```python
   # Malo: pasar objetos grandes
   pool.map(process, large_objects)

   # Mejor: pasar IDs y cargar en el worker
   pool.map(process_by_id, object_ids)
   ```

3. **Limpia recursos**
   ```python
   pool.close()
   pool.join()
   ```

### 12.5 Debugging

1. **Logging adecuado**
   ```python
   logging.debug(f"Thread {threading.current_thread().name} starting")
   ```

2. **Nombres descriptivos**
   ```python
   t = threading.Thread(target=worker, name="DataProcessor-1")
   ```

3. **Timeouts**
   ```python
   # Evita deadlocks
   lock.acquire(timeout=5)
   ```

---

## Conclusión

La concurrencia y paralelismo en Python requiere entender:

1. **El GIL y sus implicaciones**
2. **Diferencia entre IO-bound y CPU-bound**
3. **Cuándo usar Threading, Multiprocessing o Async**
4. **Problemas comunes y cómo evitarlos**
5. **Primitivas de sincronización apropiadas**

**Regla de oro**:
- IO-bound → Async/await
- CPU-bound → Multiprocessing
- Mixed → Evaluar caso por caso

Para más ejemplos prácticos, revisa el código en `backend/examples/`.

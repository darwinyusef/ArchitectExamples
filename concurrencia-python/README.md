# Concurrencia y Paralelismo en Python 🚀

Sistema completo de ejemplos prácticos sobre concurrencia, paralelismo y observabilidad en Python con FastAPI.

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Conceptos Cubiertos](#conceptos-cubiertos)
- [Instalación](#instalación)
- [Uso Rápido](#uso-rápido)
- [Endpoints Disponibles](#endpoints-disponibles)
- [Ejemplos Prácticos](#ejemplos-prácticos)
- [Observabilidad](#observabilidad)
- [GIL (Global Interpreter Lock)](#gil-global-interpreter-lock)
- [Cuándo Usar Qué](#cuándo-usar-qué)

## 🎯 Descripción

Este proyecto es una guía práctica completa que demuestra todos los aspectos de la concurrencia y paralelismo en Python, incluyendo:

- Diferencias entre IO-bound y CPU-bound
- Threading vs Multiprocessing
- Async/await y event loops
- Problemas comunes: Race conditions, Deadlocks, Starvation
- Sincronización: Locks, Semaphores, Events
- Comunicación: Queues (FIFO, LIFO, Priority)
- Patrones avanzados: run_in_executor, thread pools
- Observabilidad completa con métricas

## ✨ Conceptos Cubiertos

### 1. IO-bound vs CPU-bound
- **IO-bound**: Operaciones que esperan I/O (red, disco, APIs)
- **CPU-bound**: Cálculos intensivos que usan el procesador

### 2. Threading
- Threads básicos
- Thread pools (ThreadPoolExecutor)
- Daemon threads
- Locks y sincronización

### 3. Multiprocessing
- Procesos independientes (evitan el GIL)
- Process pools
- Comunicación entre procesos (Queues)

### 4. Async/await
- Coroutines y event loops
- asyncio.gather, as_completed
- Timeouts y cancellation
- Semaphores asíncronos

### 5. Problemas de Concurrencia
- **Race Conditions**: Acceso concurrente a recursos
- **Deadlocks**: Bloqueo mutuo de recursos
- **Starvation**: Threads que nunca obtienen recursos

### 6. Sincronización
- **Locks**: Exclusión mutua
- **RLocks**: Locks reentrant
- **Semaphores**: Limitar concurrencia
- **Events**: Señalización entre threads

### 7. Queues
- Queue (FIFO)
- LifoQueue (LIFO/Stack)
- PriorityQueue
- Bounded queues

## 🚀 Instalación

### Opción 1: Local

```bash
# Clonar el repositorio
cd concurrencia-python/backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python main.py
```

### Opción 2: Docker (Recomendado)

```bash
cd concurrencia-python
docker-compose up
```

El servidor estará disponible en: `http://localhost:8000`

## 📖 Uso Rápido

### 1. Ver Documentación Interactiva

Abre tu navegador en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 2. Probar Endpoints

```bash
# IO-bound con threading (recomendado)
curl -X POST http://localhost:8000/io-bound/threading \
  -H "Content-Type: application/json" \
  -d '{"iterations": 5}'

# CPU-bound con multiprocessing (recomendado)
curl -X POST http://localhost:8000/cpu-bound/multiprocessing \
  -H "Content-Type: application/json" \
  -d '{"iterations": 4}'

# Ver métricas
curl http://localhost:8000/metrics/summary
```

## 🌐 Endpoints Disponibles

### IO-bound
- `POST /io-bound/sequential` - Secuencial (bloqueante) ❌
- `POST /io-bound/threading` - Con threads ✅
- `POST /io-bound/async` - Con async/await ✅✅

### CPU-bound
- `POST /cpu-bound/sequential` - Secuencial
- `POST /cpu-bound/threading` - Con threads (no ayuda por GIL) ❌
- `POST /cpu-bound/multiprocessing` - Con procesos ✅✅

### Race Conditions
- `POST /race-conditions/unsafe` - Demuestra race condition
- `POST /race-conditions/lock` - Solución con Lock
- `POST /race-conditions/rlock` - Lock reentrant

### Deadlocks
- `POST /deadlocks/demonstrate` - Demuestra deadlock
- `POST /deadlocks/prevent` - Prevención con orden consistente

### Threading
- `POST /threading/basic` - Threads básicos
- `POST /threading/pool` - Thread pool
- `POST /threading/daemon` - Daemon threads

### Multiprocessing
- `POST /multiprocessing/basic` - Procesos básicos
- `POST /multiprocessing/queue` - Comunicación con queues
- `POST /multiprocessing/pool` - Process pool

### Async/await
- `POST /async/gather` - asyncio.gather
- `POST /async/run-in-executor` - Mezclar async con blocking
- `POST /async/timeout` - Timeouts
- `POST /async/as-completed` - Procesar conforme completan

### Queues
- `POST /queues/producer-consumer` - Patrón productor-consumidor
- `POST /queues/priority` - Priority queue
- `POST /queues/lifo` - LIFO queue (stack)
- `POST /queues/bounded` - Queue con tamaño máximo

### Semaphores
- `POST /semaphores/rate-limit` - Rate limiting
- `POST /semaphores/threading` - Semáforo con threads
- `POST /semaphores/bounded` - BoundedSemaphore
- `POST /semaphores/connection-pool` - Pool de conexiones

### Observabilidad
- `GET /metrics/summary` - Resumen de métricas
- `GET /metrics/operation/{name}` - Stats de operación específica
- `GET /metrics/system` - Métricas del sistema
- `POST /metrics/reset` - Limpiar métricas
- `GET /prometheus/metrics` - Métricas formato Prometheus

## 💡 Ejemplos Prácticos

### Ejemplo 1: Comparar IO-bound

```python
import requests

# 1. Secuencial (lento - 5 segundos)
r1 = requests.post('http://localhost:8000/io-bound/sequential',
                   json={'iterations': 5})
print(f"Sequential: {r1.json()['duration']:.2f}s")

# 2. Threading (rápido - ~1 segundo)
r2 = requests.post('http://localhost:8000/io-bound/threading',
                   json={'iterations': 5})
print(f"Threading: {r2.json()['duration']:.2f}s")

# 3. Async (más rápido - ~1 segundo)
r3 = requests.post('http://localhost:8000/io-bound/async',
                   json={'iterations': 5})
print(f"Async: {r3.json()['duration']:.2f}s")
```

### Ejemplo 2: Demostrar Race Condition

```python
# Sin Lock - resultados inconsistentes
r1 = requests.post('http://localhost:8000/race-conditions/unsafe',
                   json={'num_threads': 10, 'increments_per_thread': 1000})
print(f"Sin Lock: {r1.json()['final_counter']} (esperado: 10000)")

# Con Lock - resultados correctos
r2 = requests.post('http://localhost:8000/race-conditions/lock',
                   json={'num_threads': 10, 'increments_per_thread': 1000})
print(f"Con Lock: {r2.json()['final_counter']} (correcto)")
```

### Ejemplo 3: CPU-bound con GIL

```python
# Threading NO ayuda (por el GIL)
r1 = requests.post('http://localhost:8000/cpu-bound/threading',
                   json={'iterations': 4})
print(f"Threading: {r1.json()['duration']:.2f}s")

# Multiprocessing SÍ ayuda (evita GIL)
r2 = requests.post('http://localhost:8000/cpu-bound/multiprocessing',
                   json={'iterations': 4})
print(f"Multiprocessing: {r2.json()['duration']:.2f}s")
print(f"Speedup: {r1.json()['duration'] / r2.json()['duration']:.2f}x")
```

## 📊 Observabilidad

El sistema incluye observabilidad completa:

```python
# Ver resumen de métricas
r = requests.get('http://localhost:8000/metrics/summary')
print(r.json())

# Métricas del sistema
r = requests.get('http://localhost:8000/metrics/system')
print(r.json())
```

Métricas recolectadas:
- Duración de ejecuciones
- Uso de CPU por operación
- Uso de memoria
- Número de threads/procesos usados
- Tasa de éxito/fallo
- Contadores personalizados

## 🔒 GIL (Global Interpreter Lock)

### ¿Qué es el GIL?

El GIL es un mutex que protege el acceso a objetos Python, permitiendo que solo un thread ejecute bytecode de Python a la vez.

### Implicaciones

1. **IO-bound**: El GIL se libera durante operaciones de I/O
   - ✅ Threading funciona bien
   - ✅ Async funciona excelente

2. **CPU-bound**: El GIL NO se libera durante cálculos
   - ❌ Threading NO ayuda (puede ser más lento)
   - ✅ Multiprocessing evita el GIL

### Ejemplo del GIL

```python
# CPU-bound con threading (malo)
def compute():
    total = 0
    for i in range(10_000_000):
        total += i * i
    return total

# Un thread: 1.0s
# Dos threads: 1.2s (más lento por overhead del GIL)
# Dos procesos: 0.5s (evita el GIL)
```

## 🎓 Cuándo Usar Qué

### IO-bound (APIs, DB, archivos)
1. **Async/await** ✅✅ - Mejor opción
   - Más eficiente en memoria
   - Excelente para miles de conexiones
   ```python
   await asyncio.gather(*[fetch_api(i) for i in range(1000)])
   ```

2. **Threading** ✅ - Buena opción
   - Más simple
   - Bueno para decenas/cientos de operaciones
   ```python
   with ThreadPoolExecutor() as executor:
       results = executor.map(fetch_api, range(100))
   ```

### CPU-bound (cálculos, procesamiento)
1. **Multiprocessing** ✅✅ - Única opción real
   - Evita el GIL
   - Usa todos los cores
   ```python
   with ProcessPoolExecutor() as executor:
       results = executor.map(calculate, data)
   ```

2. **Threading** ❌ - No usar
   - No ayuda por el GIL
   - Puede ser más lento

### Código bloqueante en async
**run_in_executor** ✅
```python
loop = asyncio.get_event_loop()
result = await loop.run_in_executor(None, blocking_function)
```

### Limitar concurrencia
**Semaphore** ✅
```python
sem = asyncio.Semaphore(10)  # Max 10 concurrentes
async with sem:
    await operation()
```

### Comunicación entre workers
**Queue** ✅
```python
queue = Queue()
# Producer
queue.put(item)
# Consumer
item = queue.get()
```

## 📚 Recursos Adicionales

- [GUIA.md](./GUIA.md) - Guía detallada de conceptos
- [Código de ejemplos](./backend/examples/) - Implementaciones completas
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)

## 🐛 Problemas Comunes

### Race Condition
```python
# ❌ Incorrecto
counter += 1

# ✅ Correcto
with lock:
    counter += 1
```

### Deadlock
```python
# ❌ Incorrecto
# Thread 1: lock_a → lock_b
# Thread 2: lock_b → lock_a

# ✅ Correcto - orden consistente
# Thread 1: lock_a → lock_b
# Thread 2: lock_a → lock_b
```

### Blocking en Async
```python
# ❌ Incorrecto
async def bad():
    time.sleep(1)  # Bloquea el event loop

# ✅ Correcto
async def good():
    await asyncio.sleep(1)  # No bloqueante
```

## 📝 Licencia

MIT

## 👥 Autor

Proyecto educativo para aprender concurrencia y paralelismo en Python.

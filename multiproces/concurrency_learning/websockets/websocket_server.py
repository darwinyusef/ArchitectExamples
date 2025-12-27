"""
SERVIDOR WEBSOCKET CON WORKERS MULTIPROCESSING
===============================================
Este módulo implementa un servidor WebSocket que delega trabajo pesado
a workers en procesos separados, manteniendo las conexiones WebSocket
responsivas.

Arquitectura:
┌────────────┐         WebSocket         ┌────────────────┐
│  Cliente   │ ←─────────────────────→  │  Servidor WS   │
└────────────┘                            │  (async I/O)   │
                                          └────────┬───────┘
                                                   │
                                            Job Queue
                                                   │
                                    ┌──────────────┼──────────────┐
                                    │              │              │
                              ┌──────────┐  ┌──────────┐  ┌──────────┐
                              │Worker 1  │  │Worker 2  │  │Worker N  │
                              │(CPU 1)   │  │(CPU 2)   │  │(CPU N)   │
                              └──────────┘  └──────────┘  └──────────┘

Por qué esta arquitectura:
- WebSocket server usa async I/O (no bloquea)
- Workers procesan tareas pesadas en CPUs separados
- El servidor puede manejar muchas conexiones simultáneas
- Los workers se encargan del trabajo CPU-intensive

Instalar dependencias:
    pip install websockets psutil
"""

import asyncio
import websockets
import json
import multiprocessing as mp
from multiprocessing import Process, Queue
import time
from datetime import datetime
from typing import Set, Dict
import signal
import os


def log(mensaje, source="MAIN"):
    """Función auxiliar de logging"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    pid = os.getpid()
    print(f"[{timestamp}] [PID:{pid}] [{source}] {mensaje}")


# ============================================================================
# WORKER PROCESSES - Ejecutan trabajo CPU-intensive
# ============================================================================

def worker_process(worker_id: int, job_queue: Queue, result_queue: Queue):
    """
    Worker que procesa tareas CPU-intensive.

    Args:
        worker_id: ID del worker
        job_queue: Cola de trabajos entrantes
        result_queue: Cola para enviar resultados

    Este worker corre en un proceso separado con su propio CPU.
    """
    log(f"Worker {worker_id} iniciado", f"WORKER-{worker_id}")

    while True:
        try:
            # Obtener job de la cola
            job = job_queue.get()

            if job is None:  # Señal de terminación
                log(f"Worker {worker_id} terminando", f"WORKER-{worker_id}")
                break

            job_id = job['job_id']
            task_type = job['task_type']
            data = job['data']
            client_id = job.get('client_id', 'unknown')

            log(f"Procesando job {job_id} de cliente {client_id}", f"WORKER-{worker_id}")

            # Procesar según tipo de tarea
            inicio = time.time()
            result = None
            error = None

            try:
                if task_type == 'calcular_fibonacci':
                    # Cálculo CPU-intensive
                    n = data.get('n', 30)
                    result = calcular_fibonacci(n)

                elif task_type == 'procesar_imagen':
                    # Simula procesamiento de imagen
                    filename = data.get('filename', 'image.jpg')
                    result = simular_procesamiento_imagen(filename)

                elif task_type == 'analizar_datos':
                    # Análisis de datos pesado
                    dataset = data.get('dataset', list(range(1000)))
                    result = analizar_dataset(dataset)

                elif task_type == 'benchmark':
                    # Benchmark CPU
                    duration = data.get('duration', 2)
                    result = ejecutar_benchmark(duration)

                else:
                    error = f"Tipo de tarea desconocido: {task_type}"

            except Exception as e:
                error = str(e)
                log(f"Error en job {job_id}: {error}", f"WORKER-{worker_id}")

            duracion = time.time() - inicio

            # Enviar resultado
            resultado = {
                'job_id': job_id,
                'client_id': client_id,
                'task_type': task_type,
                'result': result,
                'error': error,
                'worker_id': worker_id,
                'duration': duracion
            }

            result_queue.put(resultado)

            log(f"Job {job_id} completado en {duracion:.2f}s", f"WORKER-{worker_id}")

        except Exception as e:
            log(f"Error en worker loop: {e}", f"WORKER-{worker_id}")


# ============================================================================
# FUNCIONES DE PROCESAMIENTO CPU-INTENSIVE
# ============================================================================

def calcular_fibonacci(n: int) -> dict:
    """
    Calcula números de Fibonacci de forma recursiva (ineficiente a propósito).
    Esto es CPU-intensive y se beneficia de multiprocessing.
    """
    def fib(x):
        if x <= 1:
            return x
        return fib(x-1) + fib(x-2)

    resultado = fib(n)
    return {
        'n': n,
        'fibonacci': resultado,
        'note': 'Calculado recursivamente (CPU-intensive)'
    }


def simular_procesamiento_imagen(filename: str) -> dict:
    """Simula procesamiento de imagen (resize, filtros, etc.)"""
    operaciones = ['cargar', 'redimensionar', 'aplicar_filtro', 'comprimir', 'guardar']
    resultados = []

    for op in operaciones:
        time.sleep(0.3)  # Simula tiempo de procesamiento
        resultados.append(f"{op}_completado")

        # Simular cálculo pesado
        _ = sum(i**2 for i in range(100000))

    return {
        'filename': filename,
        'operaciones': resultados,
        'tamaño_final': '800x600',
        'formato': 'JPEG'
    }


def analizar_dataset(dataset: list) -> dict:
    """Analiza un dataset con cálculos estadísticos"""
    # Cálculos CPU-intensive
    total = sum(dataset)
    promedio = total / len(dataset) if dataset else 0
    maximo = max(dataset) if dataset else 0
    minimo = min(dataset) if dataset else 0

    # Mediana (requiere ordenar)
    sorted_data = sorted(dataset)
    n = len(sorted_data)
    if n % 2 == 0:
        mediana = (sorted_data[n//2-1] + sorted_data[n//2]) / 2
    else:
        mediana = sorted_data[n//2]

    # Varianza
    varianza = sum((x - promedio)**2 for x in dataset) / len(dataset) if dataset else 0
    desviacion_std = varianza ** 0.5

    return {
        'tamaño': len(dataset),
        'suma': total,
        'promedio': promedio,
        'mediana': mediana,
        'maximo': maximo,
        'minimo': minimo,
        'varianza': varianza,
        'desviacion_std': desviacion_std
    }


def ejecutar_benchmark(duration: int) -> dict:
    """Ejecuta un benchmark de CPU por X segundos"""
    log(f"Ejecutando benchmark por {duration}s", "BENCHMARK")

    inicio = time.time()
    iteraciones = 0

    while time.time() - inicio < duration:
        # Operaciones CPU-intensive
        _ = sum(i**2 + i**0.5 for i in range(10000))
        iteraciones += 1

    duracion_real = time.time() - inicio

    return {
        'duracion_solicitada': duration,
        'duracion_real': duracion_real,
        'iteraciones': iteraciones,
        'ops_por_segundo': iteraciones / duracion_real
    }


# ============================================================================
# WEBSOCKET SERVER - Maneja conexiones async
# ============================================================================

class WebSocketServer:
    """
    Servidor WebSocket que coordina workers multiprocessing.

    El servidor usa async I/O para manejar múltiples conexiones WebSocket
    de forma eficiente, mientras delega trabajo pesado a workers.
    """

    def __init__(self, host: str = "localhost", port: int = 8765, num_workers: int = None):
        """
        Inicializa el servidor.

        Args:
            host: Dirección IP del servidor
            port: Puerto del servidor
            num_workers: Número de workers (default: número de CPUs)
        """
        self.host = host
        self.port = port
        self.num_workers = num_workers or mp.cpu_count()

        # Colas para comunicación con workers
        self.job_queue = Queue()
        self.result_queue = Queue()

        # Workers
        self.workers = []

        # Clientes conectados: {websocket: client_id}
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.client_ids: Dict[websockets.WebSocketServerProtocol, str] = {}

        # Contador de jobs
        self.next_job_id = 1

        log(f"WebSocketServer inicializado: {host}:{port}")
        log(f"Workers a crear: {self.num_workers}")

    def start_workers(self):
        """Inicia todos los workers en procesos separados"""
        log(f"Iniciando {self.num_workers} workers...")

        for i in range(self.num_workers):
            worker = Process(
                target=worker_process,
                args=(i+1, self.job_queue, self.result_queue),
                name=f"Worker-{i+1}"
            )
            worker.start()
            self.workers.append(worker)

        log("Todos los workers iniciados")

    async def handle_client(self, websocket, path):
        """
        Handler para cada conexión WebSocket.

        Args:
            websocket: Objeto WebSocket de la conexión
            path: Path de la conexión

        Esta función corre en async, permitiendo manejar muchos clientes
        simultáneamente sin bloquear.
        """
        # Registrar cliente
        client_id = f"client-{len(self.clients) + 1}"
        self.clients.add(websocket)
        self.client_ids[websocket] = client_id

        log(f"Cliente conectado: {client_id} desde {websocket.remote_address}", "WS")

        try:
            # Enviar mensaje de bienvenida
            await websocket.send(json.dumps({
                'type': 'connected',
                'client_id': client_id,
                'message': f'Conectado al servidor. Workers disponibles: {self.num_workers}'
            }))

            # Loop de mensajes del cliente
            async for message in websocket:
                await self.handle_message(websocket, client_id, message)

        except websockets.exceptions.ConnectionClosed:
            log(f"Cliente desconectado: {client_id}", "WS")
        except Exception as e:
            log(f"Error con cliente {client_id}: {e}", "WS")
        finally:
            # Limpiar al desconectar
            self.clients.remove(websocket)
            del self.client_ids[websocket]

    async def handle_message(self, websocket, client_id: str, message: str):
        """
        Procesa un mensaje del cliente.

        Args:
            websocket: WebSocket del cliente
            client_id: ID del cliente
            message: Mensaje recibido (JSON)
        """
        try:
            data = json.loads(message)
            command = data.get('command')

            log(f"Mensaje de {client_id}: {command}", "WS")

            if command == 'submit_job':
                # Cliente solicita procesar un job
                await self.submit_job(websocket, client_id, data)

            elif command == 'get_stats':
                # Cliente solicita estadísticas
                await self.send_stats(websocket)

            elif command == 'ping':
                # Cliente hace ping
                await websocket.send(json.dumps({
                    'type': 'pong',
                    'timestamp': time.time()
                }))

            else:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': f'Comando desconocido: {command}'
                }))

        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Mensaje no es JSON válido'
            }))
        except Exception as e:
            await websocket.send(json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def submit_job(self, websocket, client_id: str, data: dict):
        """
        Envía un job a la cola de workers.

        Args:
            websocket: WebSocket del cliente
            client_id: ID del cliente
            data: Datos del job
        """
        job_id = self.next_job_id
        self.next_job_id += 1

        task_type = data.get('task_type')
        task_data = data.get('data', {})

        # Crear job
        job = {
            'job_id': job_id,
            'client_id': client_id,
            'task_type': task_type,
            'data': task_data
        }

        # Encolar para workers
        self.job_queue.put(job)

        # Confirmar al cliente
        await websocket.send(json.dumps({
            'type': 'job_submitted',
            'job_id': job_id,
            'task_type': task_type,
            'message': 'Job encolado para procesamiento'
        }))

        log(f"Job {job_id} encolado: {task_type}", "WS")

    async def send_stats(self, websocket):
        """Envía estadísticas del servidor al cliente"""
        stats = {
            'type': 'stats',
            'workers': self.num_workers,
            'connected_clients': len(self.clients),
            'pending_jobs': self.job_queue.qsize() if hasattr(self.job_queue, 'qsize') else 'N/A',
            'timestamp': time.time()
        }

        await websocket.send(json.dumps(stats))

    async def process_results(self):
        """
        Tarea async que procesa resultados de workers y los envía a clientes.

        Esta tarea corre continuamente en background, escuchando la cola
        de resultados y enviando respuestas a los clientes correspondientes.
        """
        log("Iniciando procesador de resultados", "RESULTS")

        while True:
            try:
                # Revisar si hay resultados (non-blocking)
                if not self.result_queue.empty():
                    resultado = self.result_queue.get_nowait()

                    client_id = resultado['client_id']
                    log(f"Resultado recibido de worker para {client_id}", "RESULTS")

                    # Encontrar websocket del cliente
                    client_ws = None
                    for ws, cid in self.client_ids.items():
                        if cid == client_id:
                            client_ws = ws
                            break

                    if client_ws:
                        # Enviar resultado al cliente
                        mensaje = {
                            'type': 'job_completed',
                            'job_id': resultado['job_id'],
                            'task_type': resultado['task_type'],
                            'result': resultado['result'],
                            'error': resultado['error'],
                            'worker_id': resultado['worker_id'],
                            'duration': resultado['duration']
                        }

                        await client_ws.send(json.dumps(mensaje))
                        log(f"Resultado enviado a {client_id}", "RESULTS")
                    else:
                        log(f"Cliente {client_id} ya no está conectado", "RESULTS")

                # Pequeña pausa para no consumir CPU
                await asyncio.sleep(0.1)

            except Exception as e:
                log(f"Error procesando resultado: {e}", "RESULTS")
                await asyncio.sleep(0.1)

    async def start_server(self):
        """Inicia el servidor WebSocket"""
        log(f"Iniciando servidor WebSocket en ws://{self.host}:{self.port}")

        # Iniciar workers
        self.start_workers()

        # Iniciar procesador de resultados en background
        asyncio.create_task(self.process_results())

        # Iniciar servidor WebSocket
        async with websockets.serve(self.handle_client, self.host, self.port):
            log("✓ Servidor WebSocket activo y escuchando")
            log(f"✓ {self.num_workers} workers listos")
            log("Esperando conexiones...")

            # Mantener servidor corriendo
            await asyncio.Future()  # Corre por siempre

    def shutdown(self):
        """Apaga el servidor y workers gracefully"""
        log("Cerrando servidor...")

        # Terminar workers
        for _ in range(self.num_workers):
            self.job_queue.put(None)

        for worker in self.workers:
            worker.join(timeout=5)
            if worker.is_alive():
                worker.terminate()

        log("Servidor cerrado")


# ============================================================================
# CLIENTE DE EJEMPLO (para testing)
# ============================================================================

async def ejemplo_cliente():
    """
    Cliente WebSocket de ejemplo para probar el servidor.

    Ejecuta en otra terminal:
        python websocket_server.py client
    """
    uri = "ws://localhost:8765"

    log("Conectando al servidor...", "CLIENT")

    async with websockets.connect(uri) as websocket:
        # Recibir mensaje de bienvenida
        mensaje = await websocket.recv()
        data = json.loads(mensaje)
        log(f"Servidor dice: {data}", "CLIENT")

        # Enviar job de Fibonacci
        log("Enviando job de Fibonacci...", "CLIENT")
        await websocket.send(json.dumps({
            'command': 'submit_job',
            'task_type': 'calcular_fibonacci',
            'data': {'n': 30}
        }))

        # Recibir confirmación
        respuesta = await websocket.recv()
        log(f"Confirmación: {json.loads(respuesta)}", "CLIENT")

        # Esperar resultado
        resultado = await websocket.recv()
        log(f"Resultado: {json.loads(resultado)}", "CLIENT")

        # Enviar job de análisis de datos
        log("\nEnviando job de análisis...", "CLIENT")
        await websocket.send(json.dumps({
            'command': 'submit_job',
            'task_type': 'analizar_datos',
            'data': {'dataset': list(range(1000))}
        }))

        respuesta = await websocket.recv()
        log(f"Confirmación: {json.loads(respuesta)}", "CLIENT")

        resultado = await websocket.recv()
        data = json.loads(resultado)
        log(f"Resultado: Worker-{data['worker_id']} en {data['duration']:.2f}s", "CLIENT")
        log(f"Datos: {data['result']}", "CLIENT")

        # Solicitar estadísticas
        log("\nSolicitando estadísticas...", "CLIENT")
        await websocket.send(json.dumps({
            'command': 'get_stats'
        }))

        stats = await websocket.recv()
        log(f"Stats: {json.loads(stats)}", "CLIENT")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'client':
        # Ejecutar cliente de ejemplo
        asyncio.run(ejemplo_cliente())
    else:
        # Ejecutar servidor
        server = WebSocketServer(
            host="0.0.0.0",  # Escuchar en todas las interfaces
            port=8765,
            num_workers=2  # Usar 2 workers para tus 2 CPUs
        )

        try:
            asyncio.run(server.start_server())
        except KeyboardInterrupt:
            log("\nInterrumpido por usuario")
            server.shutdown()

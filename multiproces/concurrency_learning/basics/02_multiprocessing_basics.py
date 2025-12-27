"""
CONCEPTOS BÁSICOS DE MULTIPROCESSING
=====================================
Multiprocessing crea PROCESOS SEPARADOS, cada uno con su propio intérprete Python
y su propia memoria. Esto significa que EVITA el GIL y permite PARALELISMO REAL.

Diferencias clave con Threading:
┌─────────────────┬──────────────────┬──────────────────────┐
│   Característica│   Threading      │   Multiprocessing    │
├─────────────────┼──────────────────┼──────────────────────┤
│   Memoria       │   Compartida     │   Separada           │
│   GIL           │   Sí (limitante) │   No (cada proceso)  │
│   CPU-bound     │   ✗ Malo         │   ✓ Excelente        │
│   I/O-bound     │   ✓ Bueno        │   ✓ Funciona         │
│   Overhead      │   Bajo           │   Alto               │
│   Comunicación  │   Fácil          │   Requiere IPC       │
└─────────────────┴──────────────────┴──────────────────────┘

Cuándo usar Multiprocessing:
- Cálculos matemáticos intensivos
- Procesamiento de imágenes/video
- Análisis de datos grandes
- Cualquier tarea CPU-bound que pueda dividirse
"""

import multiprocessing as mp
import os
import time
from datetime import datetime


def log(mensaje):
    """
    Función auxiliar para logging con información del proceso.
    Muestra PID (Process ID) para visualizar que son procesos diferentes.
    """
    pid = os.getpid()
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    proceso = mp.current_process().name
    print(f"[{timestamp}] [PID:{pid}] [{proceso}] {mensaje}")


def tarea_cpu_pesada(nombre, iteraciones):
    """
    Tarea CPU-intensive que se beneficia de multiprocessing.

    Args:
        nombre: Identificador de la tarea
        iteraciones: Cantidad de cálculos a realizar

    Esta tarea se ejecutará en un proceso separado con su propio GIL,
    permitiendo que múltiples procesos calculen EN PARALELO en diferentes CPUs.
    """
    log(f"Iniciando cálculo: {nombre}")

    # Cálculo matemático intensivo
    total = 0
    for i in range(iteraciones):
        total += i ** 2 + (i ** 0.5)

    log(f"Completado: {nombre}, resultado={total:.2e}")
    return total


def procesar_datos(datos, multiplicador):
    """
    Simula procesamiento de datos que puede paralelizarse.

    Args:
        datos: Lista de números a procesar
        multiplicador: Factor de multiplicación

    En un caso real, esto podría ser:
    - Procesamiento de imágenes
    - Análisis de logs
    - Transformación de datasets
    """
    pid = os.getpid()
    log(f"Procesando {len(datos)} elementos")

    resultado = [x * multiplicador for x in datos]
    time.sleep(0.5)  # Simula trabajo adicional

    log(f"Procesamiento completado")
    return sum(resultado)


def ejemplo_multiprocessing_basico():
    """
    Demuestra uso básico de multiprocessing.
    Cada proceso se ejecuta en un CPU separado (si hay CPUs disponibles).
    """
    log("=== EJEMPLO: Multiprocessing Básico ===")
    log(f"CPUs disponibles: {mp.cpu_count()}")

    inicio = time.time()

    # Crear procesos
    procesos = []
    for i in range(2):  # Usamos 2 procesos para tus 2 CPUs
        p = mp.Process(
            target=tarea_cpu_pesada,
            args=(f"Proceso-{i+1}", 10_000_000),
            name=f"Worker-{i+1}"
        )
        procesos.append(p)
        p.start()  # Inicia el proceso

    # Esperar a que terminen
    for p in procesos:
        p.join()  # Bloquea hasta que el proceso termine

    duracion = time.time() - inicio
    log(f"Tiempo total: {duracion:.2f}s")
    log("(Los procesos se ejecutaron en paralelo en CPUs diferentes)")


def ejemplo_pool_workers():
    """
    Demuestra el uso de Pool para gestionar workers automáticamente.
    Pool es la forma más común y recomendada de usar multiprocessing.

    Un Pool mantiene N procesos worker listos para ejecutar tareas,
    similar a un "thread pool" pero con procesos reales.
    """
    log("\n=== EJEMPLO: Pool de Workers ===")

    num_cpus = mp.cpu_count()
    log(f"Creando pool con {num_cpus} workers (1 por CPU)")

    # Crear pool de workers
    # processes=None usa todos los CPUs disponibles
    with mp.Pool(processes=num_cpus) as pool:
        # Distribuir tareas entre los workers
        tareas = [
            (f"Tarea-{i+1}", 5_000_000)
            for i in range(4)  # 4 tareas para 2 CPUs
        ]

        log(f"Distribuyendo {len(tareas)} tareas entre {num_cpus} workers")

        inicio = time.time()

        # starmap distribuye las tareas automáticamente
        # Los workers procesarán las tareas en paralelo
        resultados = pool.starmap(tarea_cpu_pesada, tareas)

        duracion = time.time() - inicio

        log(f"Todas las tareas completadas en {duracion:.2f}s")
        log(f"Resultados obtenidos: {len(resultados)}")


def ejemplo_map_paralelo():
    """
    Demuestra pool.map() para procesar listas en paralelo.
    Esto es útil cuando tienes una lista grande de datos a procesar.

    map() divide automáticamente el trabajo entre los workers disponibles.
    """
    log("\n=== EJEMPLO: Map Paralelo ===")

    # Datos a procesar
    datasets = [
        list(range(1000)),
        list(range(2000)),
        list(range(3000)),
        list(range(4000)),
    ]

    log(f"Procesando {len(datasets)} datasets en paralelo")

    inicio = time.time()

    # Usando 2 workers para tus 2 CPUs
    with mp.Pool(processes=2) as pool:
        # Necesitamos una función que acepte un solo argumento para map
        func = lambda datos: procesar_datos(datos, multiplicador=2)

        # map distribuye los datasets entre los workers
        resultados = pool.map(func, datasets)

    duracion = time.time() - inicio

    log(f"Procesamiento completado en {duracion:.2f}s")
    log(f"Resultados: {resultados}")


def ejemplo_comparacion_rendimiento():
    """
    Compara el rendimiento entre ejecución secuencial y paralela.
    Esto demuestra claramente el beneficio del multiprocessing.
    """
    log("\n=== COMPARACIÓN: Secuencial vs Paralelo ===")

    iteraciones = 8_000_000
    num_tareas = 4

    # Ejecución secuencial
    log("Ejecutando secuencialmente...")
    inicio = time.time()
    for i in range(num_tareas):
        tarea_cpu_pesada(f"Secuencial-{i+1}", iteraciones)
    tiempo_secuencial = time.time() - inicio
    log(f"Tiempo secuencial: {tiempo_secuencial:.2f}s")

    # Ejecución paralela con Pool
    log("\nEjecutando en paralelo con Pool...")
    inicio = time.time()
    with mp.Pool(processes=2) as pool:  # 2 CPUs
        tareas = [(f"Paralelo-{i+1}", iteraciones) for i in range(num_tagas)]
        pool.starmap(tarea_cpu_pesada, tareas)
    tiempo_paralelo = time.time() - inicio
    log(f"Tiempo paralelo: {tiempo_paralelo:.2f}s")

    mejora = tiempo_secuencial / tiempo_paralelo
    log(f"\nMejora: {mejora:.2f}x más rápido")
    log(f"Eficiencia: {(mejora/2)*100:.1f}% (ideal sería 100% con 2 CPUs)")


def worker_con_estado(worker_id, cola_tareas, cola_resultados):
    """
    Worker que procesa múltiples tareas de una cola.
    Este patrón es útil para sistemas de job queue.

    Args:
        worker_id: Identificador del worker
        cola_tareas: Queue con tareas pendientes
        cola_resultados: Queue donde poner resultados
    """
    log(f"Worker {worker_id} iniciado y esperando tareas")

    while True:
        try:
            # Obtener tarea de la cola (timeout de 1 segundo)
            tarea = cola_tareas.get(timeout=1)

            if tarea is None:  # Señal de terminación
                log(f"Worker {worker_id} recibió señal de terminar")
                break

            # Procesar tarea
            nombre, iteraciones = tarea
            log(f"Worker {worker_id} procesando: {nombre}")
            resultado = tarea_cpu_pesada(nombre, iteraciones)

            # Enviar resultado
            cola_resultados.put((nombre, resultado))

        except Exception as e:
            log(f"Worker {worker_id} error: {e}")
            break

    log(f"Worker {worker_id} terminado")


def ejemplo_job_queue():
    """
    Demuestra un sistema de job queue con múltiples workers.
    Este patrón es fundamental para sistemas distribuidos.
    """
    log("\n=== EJEMPLO: Job Queue con Workers ===")

    # Crear colas para comunicación entre procesos
    cola_tareas = mp.Queue()
    cola_resultados = mp.Queue()

    # Crear tareas
    tareas = [(f"Job-{i+1}", 3_000_000) for i in range(6)]

    log(f"Encolando {len(tareas)} tareas")
    for tarea in tareas:
        cola_tareas.put(tarea)

    # Crear workers (1 por CPU)
    num_workers = 2
    workers = []
    for i in range(num_workers):
        p = mp.Process(
            target=worker_con_estado,
            args=(i+1, cola_tareas, cola_resultados),
            name=f"Worker-{i+1}"
        )
        workers.append(p)
        p.start()

    # Esperar a que se procesen todas las tareas
    log("Esperando resultados...")
    resultados = []
    for _ in range(len(tareas)):
        resultado = cola_resultados.get()
        resultados.append(resultado)
        log(f"Resultado recibido: {resultado[0]}")

    # Enviar señal de terminación a workers
    for _ in range(num_workers):
        cola_tareas.put(None)

    # Esperar a que terminen
    for p in workers:
        p.join()

    log(f"Todas las tareas completadas. Total resultados: {len(resultados)}")


if __name__ == "__main__":
    """
    IMPORTANTE: En Windows, multiprocessing requiere if __name__ == "__main__"
    para evitar crear procesos infinitos.

    En tu droplet Linux esto no es crítico, pero es buena práctica.
    """
    log(f"Sistema: CPUs disponibles = {mp.cpu_count()}")
    log(f"PID del proceso principal = {os.getpid()}\n")

    ejemplo_multiprocessing_basico()
    ejemplo_pool_workers()
    ejemplo_map_paralelo()
    ejemplo_comparacion_rendimiento()
    ejemplo_job_queue()

    log("\n=== RESUMEN ===")
    log("✓ Multiprocessing permite paralelismo REAL")
    log("✓ Ideal para tareas CPU-intensive")
    log("✓ Usa Pool para gestión automática de workers")
    log("✓ Usa Queue para comunicación entre procesos")

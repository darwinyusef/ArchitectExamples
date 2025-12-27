"""
CONCEPTOS BÁSICOS DE THREADING
===============================
Threading permite ejecutar múltiples tareas CONCURRENTEMENTE en el mismo proceso.
IMPORTANTE: En Python, debido al GIL (Global Interpreter Lock), los threads NO se
ejecutan en paralelo real para código CPU-bound, pero SÍ son útiles para I/O-bound.

Cuándo usar Threading:
- Operaciones de I/O (lectura/escritura de archivos, requests HTTP, etc.)
- Operaciones que esperan respuestas (API calls, database queries)
- Interfaces gráficas que necesitan responder mientras hacen trabajo de fondo

Cuándo NO usar Threading:
- Cálculos matemáticos intensivos (usar multiprocessing)
- Procesamiento de imágenes/video (usar multiprocessing)
"""

import threading
import time
from datetime import datetime


def log(mensaje):
    """
    Función auxiliar para loggear con timestamp y thread ID.
    Esto nos ayuda a visualizar qué thread está ejecutando qué tarea.
    """
    thread_name = threading.current_thread().name
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [{thread_name}] {mensaje}")


def tarea_io_simulada(nombre, duracion):
    """
    Simula una tarea de I/O (como una llamada HTTP o lectura de archivo).

    Args:
        nombre: Identificador de la tarea
        duracion: Tiempo que tarda la operación en segundos

    Durante time.sleep(), el thread libera el GIL permitiendo que otros threads trabajen.
    """
    log(f"Iniciando tarea I/O: {nombre}")
    time.sleep(duracion)  # Simula espera de I/O
    log(f"Completada tarea I/O: {nombre}")
    return f"Resultado de {nombre}"


def tarea_cpu_intensiva(nombre, iteraciones):
    """
    Simula una tarea CPU-intensive (cálculos matemáticos).

    Args:
        nombre: Identificador de la tarea
        iteraciones: Número de cálculos a realizar

    NOTA: Este tipo de tarea NO se beneficia de threading debido al GIL.
    El GIL evita que múltiples threads ejecuten bytecode Python simultáneamente.
    """
    log(f"Iniciando tarea CPU: {nombre}")
    total = 0
    for i in range(iteraciones):
        total += i ** 2
    log(f"Completada tarea CPU: {nombre}, resultado={total}")
    return total


def ejemplo_threading_basico():
    """
    Demuestra el uso básico de threading con tareas I/O-bound.
    Verás que las tareas se ejecutan concurrentemente (no esperan unas a otras).
    """
    log("=== EJEMPLO: Threading Básico con I/O ===")

    inicio = time.time()

    # Crear threads
    threads = []
    for i in range(3):
        # target: función a ejecutar
        # args: argumentos para la función (como tupla)
        # name: nombre descriptivo del thread
        t = threading.Thread(
            target=tarea_io_simulada,
            args=(f"Tarea-{i+1}", 2),
            name=f"Worker-{i+1}"
        )
        threads.append(t)
        t.start()  # Inicia la ejecución del thread

    # Esperar a que todos los threads terminen
    for t in threads:
        t.join()  # Bloquea hasta que el thread termine

    duracion = time.time() - inicio
    log(f"Tiempo total: {duracion:.2f}s")
    log("(Si fuera secuencial: ~6s, con threading: ~2s)")


def ejemplo_threading_vs_secuencial():
    """
    Compara la ejecución secuencial vs threading para tareas I/O.
    Esta es la diferencia clave que hace útil al threading.
    """
    log("\n=== COMPARACIÓN: Secuencial vs Threading ===")

    # Ejecución secuencial
    log("Ejecutando secuencialmente...")
    inicio = time.time()
    for i in range(3):
        tarea_io_simulada(f"Secuencial-{i+1}", 1)
    tiempo_secuencial = time.time() - inicio
    log(f"Tiempo secuencial: {tiempo_secuencial:.2f}s")

    # Ejecución con threading
    log("\nEjecutando con threading...")
    inicio = time.time()
    threads = [
        threading.Thread(target=tarea_io_simulada, args=(f"Thread-{i+1}", 1))
        for i in range(3)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    tiempo_threading = time.time() - inicio
    log(f"Tiempo con threading: {tiempo_threading:.2f}s")

    log(f"\nMejora: {tiempo_secuencial/tiempo_threading:.2f}x más rápido")


def ejemplo_problema_gil():
    """
    Demuestra por qué threading NO ayuda con tareas CPU-intensive.
    El GIL (Global Interpreter Lock) evita paralelismo real en cálculos.
    """
    log("\n=== DEMOSTRACIÓN: El problema del GIL ===")

    iteraciones = 5_000_000

    # Ejecución secuencial
    log("Ejecutando cálculos secuencialmente...")
    inicio = time.time()
    for i in range(2):
        tarea_cpu_intensiva(f"Secuencial-{i+1}", iteraciones)
    tiempo_secuencial = time.time() - inicio
    log(f"Tiempo secuencial: {tiempo_secuencial:.2f}s")

    # Ejecución con threading
    log("\nEjecutando cálculos con threading...")
    inicio = time.time()
    threads = [
        threading.Thread(target=tarea_cpu_intensiva, args=(f"Thread-{i+1}", iteraciones))
        for i in range(2)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    tiempo_threading = time.time() - inicio
    log(f"Tiempo con threading: {tiempo_threading:.2f}s")

    log(f"\nDiferencia: {abs(tiempo_threading - tiempo_secuencial):.2f}s")
    log("NOTA: Threading NO mejora (o empeora) tareas CPU-intensive por el GIL")


if __name__ == "__main__":
    """
    Ejecuta todos los ejemplos en secuencia.
    Observa los timestamps y nombres de threads para entender la concurrencia.
    """
    ejemplo_threading_basico()
    ejemplo_threading_vs_secuencial()
    ejemplo_problema_gil()

    log("\n=== RESUMEN ===")
    log("✓ Threading es excelente para I/O-bound (esperas)")
    log("✗ Threading NO ayuda con CPU-bound (cálculos) por el GIL")
    log("→ Para CPU-bound, usa multiprocessing (siguiente módulo)")

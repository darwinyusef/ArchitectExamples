"""
CONDICIONES DE CARRERA (RACE CONDITIONS)
========================================
Una race condition ocurre cuando múltiples threads/procesos acceden a memoria
compartida simultáneamente, y al menos uno de ellos modifica los datos.

El resultado depende del TIMING de ejecución, haciéndolo no determinístico.

PELIGRO: Race conditions son bugs muy difíciles de detectar porque:
- No siempre ocurren
- Pueden aparecer solo en producción
- Son difíciles de reproducir
- Pueden causar corrupción de datos silenciosa

Este módulo demuestra race conditions y exporta métricas para visualizar
el problema en Grafana.
"""

import threading
import multiprocessing as mp
from multiprocessing import Process, Value, Array, Lock
import time
import random
from datetime import datetime
from prometheus_client import Counter, Gauge, Histogram, start_http_server
import os


def log(mensaje, source="MAIN"):
    """Función auxiliar de logging"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    pid = os.getpid()
    tid = threading.current_thread().ident
    print(f"[{timestamp}] [PID:{pid}] [TID:{tid}] [{source}] {mensaje}")


# ============================================================================
# MÉTRICAS PROMETHEUS
# ============================================================================

# Métricas para race conditions
race_condition_counter = Counter(
    'race_conditions_detected_total',
    'Número total de race conditions detectadas',
    ['type']
)

corrupted_data_gauge = Gauge(
    'corrupted_data_instances',
    'Instancias actuales de datos corruptos'
)

operation_duration = Histogram(
    'concurrent_operation_duration_seconds',
    'Duración de operaciones concurrentes',
    ['operation_type']
)

lock_wait_time = Histogram(
    'lock_wait_time_seconds',
    'Tiempo esperando por locks',
    ['lock_name']
)

# ============================================================================
# EJEMPLO 1: RACE CONDITION CLÁSICA - CONTADOR COMPARTIDO
# ============================================================================

class ContadorInseguro:
    """
    Contador compartido SIN protección.

    Problema: Múltiples threads incrementan el contador simultáneamente.

    Operación de incremento NO es atómica:
    1. Leer valor actual
    2. Incrementar en memoria
    3. Escribir nuevo valor

    Si dos threads ejecutan esto simultáneamente, pueden sobrescribir
    el trabajo del otro.
    """

    def __init__(self):
        self.contador = 0

    def incrementar(self):
        """
        INSEGURO: Lee-modifica-escribe sin protección.

        Timeline de race condition:
        Thread 1: Lee contador=0
        Thread 2: Lee contador=0
        Thread 1: Incrementa a 1, escribe
        Thread 2: Incrementa a 1, escribe  ← ¡Perdió el incremento de T1!
        Resultado: contador=1 (debería ser 2)
        """
        # Simular trabajo que hace la race condition más probable
        temp = self.contador
        time.sleep(0.00001)  # Ventana de vulnerabilidad
        self.contador = temp + 1


class ContadorSeguro:
    """
    Contador compartido CON protección de Lock.

    El Lock garantiza que solo UN thread puede ejecutar la sección
    crítica a la vez.
    """

    def __init__(self):
        self.contador = 0
        self.lock = threading.Lock()

    def incrementar(self):
        """
        SEGURO: Operación protegida por lock.

        Timeline con lock:
        Thread 1: Adquiere lock, lee contador=0
        Thread 2: Intenta lock, BLOQUEADO esperando
        Thread 1: Incrementa a 1, escribe, libera lock
        Thread 2: Adquiere lock, lee contador=1, incrementa a 2
        Resultado: contador=2 (correcto)
        """
        inicio_espera = time.time()

        with self.lock:  # Adquiere automáticamente y libera al salir
            # Registrar tiempo de espera
            espera = time.time() - inicio_espera
            lock_wait_time.labels(lock_name='contador_lock').observe(espera)

            # Sección crítica
            temp = self.contador
            time.sleep(0.00001)
            self.contador = temp + 1


def demo_race_condition_contador():
    """
    Demuestra race condition con contador compartido.

    Ejecuta múltiples threads incrementando el mismo contador.
    Sin protección, el resultado final será INCORRECTO.
    """
    log("=== DEMO: Race Condition en Contador ===")

    NUM_THREADS = 10
    INCREMENTOS_POR_THREAD = 1000
    VALOR_ESPERADO = NUM_THREADS * INCREMENTOS_POR_THREAD

    # ========================================================================
    # Prueba 1: SIN protección (race condition)
    # ========================================================================
    log("\n📊 Prueba 1: Contador INSEGURO (sin lock)")

    contador_inseguro = ContadorInseguro()
    threads = []

    inicio = time.time()

    for i in range(NUM_THREADS):
        t = threading.Thread(
            target=lambda: [contador_inseguro.incrementar()
                          for _ in range(INCREMENTOS_POR_THREAD)],
            name=f"Worker-{i+1}"
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    duracion_inseguro = time.time() - inicio

    resultado_inseguro = contador_inseguro.contador
    diferencia = VALOR_ESPERADO - resultado_inseguro
    porcentaje_error = (diferencia / VALOR_ESPERADO) * 100

    log(f"Valor esperado: {VALOR_ESPERADO}")
    log(f"Valor obtenido: {resultado_inseguro}")
    log(f"Diferencia: {diferencia} ({porcentaje_error:.2f}% error)")
    log(f"Tiempo: {duracion_inseguro:.3f}s")

    if diferencia > 0:
        log(f"⚠️  RACE CONDITION DETECTADA: Perdimos {diferencia} incrementos!")
        race_condition_counter.labels(type='contador').inc(diferencia)
        corrupted_data_gauge.set(diferencia)

    # ========================================================================
    # Prueba 2: CON protección (lock)
    # ========================================================================
    log("\n📊 Prueba 2: Contador SEGURO (con lock)")

    contador_seguro = ContadorSeguro()
    threads = []

    inicio = time.time()

    for i in range(NUM_THREADS):
        t = threading.Thread(
            target=lambda: [contador_seguro.incrementar()
                          for _ in range(INCREMENTOS_POR_THREAD)],
            name=f"Worker-{i+1}"
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    duracion_seguro = time.time() - inicio

    resultado_seguro = contador_seguro.contador
    diferencia = VALOR_ESPERADO - resultado_seguro

    log(f"Valor esperado: {VALOR_ESPERADO}")
    log(f"Valor obtenido: {resultado_seguro}")
    log(f"Diferencia: {diferencia}")
    log(f"Tiempo: {duracion_seguro:.3f}s")

    if diferencia == 0:
        log("✅ CORRECTO: No hay race conditions con lock")
        corrupted_data_gauge.set(0)

    # Comparación
    overhead = ((duracion_seguro - duracion_inseguro) / duracion_inseguro) * 100
    log(f"\n📈 Overhead del lock: {overhead:.2f}%")


# ============================================================================
# EJEMPLO 2: RACE CONDITION EN CUENTA BANCARIA
# ============================================================================

class CuentaBancaria:
    """
    Simula cuenta bancaria con transferencias concurrentes.

    Problema común: Transferencia entre cuentas no es atómica.
    Puede resultar en dinero perdido o duplicado.
    """

    def __init__(self, saldo_inicial, con_lock=False):
        self.saldo = saldo_inicial
        self.lock = threading.Lock() if con_lock else None
        self.transacciones = 0

    def depositar(self, cantidad):
        """Deposita dinero en la cuenta"""
        if self.lock:
            with self.lock:
                self._depositar_interno(cantidad)
        else:
            self._depositar_interno(cantidad)

    def _depositar_interno(self, cantidad):
        saldo_temp = self.saldo
        time.sleep(0.00001)  # Simula operación
        self.saldo = saldo_temp + cantidad
        self.transacciones += 1

    def retirar(self, cantidad):
        """Retira dinero de la cuenta"""
        if self.lock:
            with self.lock:
                return self._retirar_interno(cantidad)
        else:
            return self._retirar_interno(cantidad)

    def _retirar_interno(self, cantidad):
        saldo_temp = self.saldo
        time.sleep(0.00001)  # Simula operación

        if saldo_temp >= cantidad:
            self.saldo = saldo_temp - cantidad
            self.transacciones += 1
            return True
        return False


def transferir(cuenta_origen, cuenta_destino, cantidad, transfer_id):
    """
    Transfiere dinero entre cuentas.

    PROBLEMA: Esta operación tiene DOS pasos:
    1. Retirar de origen
    2. Depositar en destino

    Si algo falla entre los pasos, el dinero se pierde.
    Si dos transferencias ocurren simultáneamente, puede haber race conditions.
    """
    inicio = time.time()

    # Intenta retirar
    if cuenta_origen.retirar(cantidad):
        # Deposita en destino
        cuenta_destino.depositar(cantidad)

        duracion = time.time() - inicio
        operation_duration.labels(operation_type='transferencia').observe(duracion)

        return True

    return False


def demo_race_condition_banco():
    """
    Demuestra race condition en sistema bancario.

    Múltiples threads hacen transferencias entre cuentas simultáneamente.
    El saldo total debe permanecer constante.
    """
    log("\n=== DEMO: Race Condition en Sistema Bancario ===")

    SALDO_INICIAL = 1000
    NUM_CUENTAS = 5
    NUM_THREADS = 20
    TRANSFERENCIAS_POR_THREAD = 50

    # ========================================================================
    # Prueba 1: SIN protección
    # ========================================================================
    log("\n💰 Prueba 1: Sistema bancario INSEGURO")

    # Crear cuentas sin protección
    cuentas_inseguras = [CuentaBancaria(SALDO_INICIAL, con_lock=False)
                         for _ in range(NUM_CUENTAS)]

    saldo_total_inicial = sum(c.saldo for c in cuentas_inseguras)
    log(f"Saldo total inicial: ${saldo_total_inicial}")

    def hacer_transferencias_aleatorias():
        """Worker que hace transferencias aleatorias"""
        for i in range(TRANSFERENCIAS_POR_THREAD):
            # Seleccionar cuentas aleatorias
            origen_idx = random.randint(0, NUM_CUENTAS - 1)
            destino_idx = random.randint(0, NUM_CUENTAS - 1)

            if origen_idx != destino_idx:
                cantidad = random.randint(1, 100)
                transferir(
                    cuentas_inseguras[origen_idx],
                    cuentas_inseguras[destino_idx],
                    cantidad,
                    i
                )

    # Ejecutar transferencias concurrentes
    threads = []
    inicio = time.time()

    for i in range(NUM_THREADS):
        t = threading.Thread(target=hacer_transferencias_aleatorias)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    duracion = time.time() - inicio

    # Verificar integridad
    saldo_total_final = sum(c.saldo for c in cuentas_inseguras)
    diferencia = saldo_total_inicial - saldo_total_final

    log(f"Saldo total final: ${saldo_total_final}")
    log(f"Diferencia: ${diferencia}")
    log(f"Tiempo: {duracion:.3f}s")

    if abs(diferencia) > 0.01:  # Tolerancia para errores de punto flotante
        log(f"⚠️  CORRUPCIÓN DE DATOS: ${abs(diferencia)} perdidos/duplicados!")
        race_condition_counter.labels(type='banco').inc()
        corrupted_data_gauge.set(abs(diferencia))

    # ========================================================================
    # Prueba 2: CON protección
    # ========================================================================
    log("\n💰 Prueba 2: Sistema bancario SEGURO")

    # Crear cuentas con protección
    cuentas_seguras = [CuentaBancaria(SALDO_INICIAL, con_lock=True)
                      for _ in range(NUM_CUENTAS)]

    saldo_total_inicial = sum(c.saldo for c in cuentas_seguras)
    log(f"Saldo total inicial: ${saldo_total_inicial}")

    def hacer_transferencias_seguras():
        """Worker con transferencias protegidas"""
        for i in range(TRANSFERENCIAS_POR_THREAD):
            origen_idx = random.randint(0, NUM_CUENTAS - 1)
            destino_idx = random.randint(0, NUM_CUENTAS - 1)

            if origen_idx != destino_idx:
                cantidad = random.randint(1, 100)
                transferir(
                    cuentas_seguras[origen_idx],
                    cuentas_seguras[destino_idx],
                    cantidad,
                    i
                )

    # Ejecutar transferencias concurrentes
    threads = []
    inicio = time.time()

    for i in range(NUM_THREADS):
        t = threading.Thread(target=hacer_transferencias_seguras)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    duracion = time.time() - inicio

    # Verificar integridad
    saldo_total_final = sum(c.saldo for c in cuentas_seguras)
    diferencia = saldo_total_inicial - saldo_total_final

    log(f"Saldo total final: ${saldo_total_final}")
    log(f"Diferencia: ${diferencia}")
    log(f"Tiempo: {duracion:.3f}s")

    if abs(diferencia) < 0.01:
        log("✅ INTEGRIDAD PRESERVADA: Locks protegieron las transacciones")
        corrupted_data_gauge.set(0)


# ============================================================================
# EJEMPLO 3: RACE CONDITION CON MULTIPROCESSING
# ============================================================================

def incrementar_compartido_inseguro(valor_compartido, num_incrementos):
    """
    Worker que incrementa valor compartido SIN protección.

    En multiprocessing, Value permite compartir memoria entre procesos.
    Pero sin lock, hay race conditions igual que con threads.
    """
    pid = os.getpid()
    log(f"Worker iniciado, {num_incrementos} incrementos", f"PID-{pid}")

    for _ in range(num_incrementos):
        # INSEGURO: Lee-modifica-escribe sin lock
        temp = valor_compartido.value
        # time.sleep(0.000001)  # No necesario, race condition igual ocurre
        valor_compartido.value = temp + 1


def incrementar_compartido_seguro(valor_compartido, lock, num_incrementos):
    """
    Worker que incrementa valor compartido CON protección de lock.
    """
    pid = os.getpid()
    log(f"Worker iniciado, {num_incrementos} incrementos", f"PID-{pid}")

    for _ in range(num_incrementos):
        with lock:
            # SEGURO: Operación atómica protegida
            temp = valor_compartido.value
            valor_compartido.value = temp + 1


def demo_race_condition_multiprocessing():
    """
    Demuestra race condition con multiprocessing.

    Múltiples procesos modifican memoria compartida (Value).
    """
    log("\n=== DEMO: Race Condition con Multiprocessing ===")

    NUM_PROCESOS = 2  # Usar tus 2 CPUs
    INCREMENTOS_POR_PROCESO = 5000
    VALOR_ESPERADO = NUM_PROCESOS * INCREMENTOS_POR_PROCESO

    # ========================================================================
    # Prueba 1: SIN lock
    # ========================================================================
    log("\n🔀 Prueba 1: Memoria compartida INSEGURA")

    # Crear valor compartido (inicializado en 0)
    valor_compartido = Value('i', 0)  # 'i' = signed integer

    procesos = []
    inicio = time.time()

    for i in range(NUM_PROCESOS):
        p = Process(
            target=incrementar_compartido_inseguro,
            args=(valor_compartido, INCREMENTOS_POR_PROCESO),
            name=f"Worker-{i+1}"
        )
        procesos.append(p)
        p.start()

    for p in procesos:
        p.join()

    duracion = time.time() - inicio

    resultado = valor_compartido.value
    diferencia = VALOR_ESPERADO - resultado

    log(f"Valor esperado: {VALOR_ESPERADO}")
    log(f"Valor obtenido: {resultado}")
    log(f"Diferencia: {diferencia}")
    log(f"Tiempo: {duracion:.3f}s")

    if diferencia > 0:
        log(f"⚠️  RACE CONDITION: {diferencia} incrementos perdidos!")
        race_condition_counter.labels(type='multiprocessing').inc(diferencia)

    # ========================================================================
    # Prueba 2: CON lock
    # ========================================================================
    log("\n🔀 Prueba 2: Memoria compartida SEGURA")

    # Crear valor compartido con su propio lock
    valor_compartido = Value('i', 0)
    lock = Lock()  # Lock de multiprocessing

    procesos = []
    inicio = time.time()

    for i in range(NUM_PROCESOS):
        p = Process(
            target=incrementar_compartido_seguro,
            args=(valor_compartido, lock, INCREMENTOS_POR_PROCESO),
            name=f"Worker-{i+1}"
        )
        procesos.append(p)
        p.start()

    for p in procesos:
        p.join()

    duracion = time.time() - inicio

    resultado = valor_compartido.value
    diferencia = VALOR_ESPERADO - resultado

    log(f"Valor esperado: {VALOR_ESPERADO}")
    log(f"Valor obtenido: {resultado}")
    log(f"Diferencia: {diferencia}")
    log(f"Tiempo: {duracion:.3f}s")

    if diferencia == 0:
        log("✅ CORRECTO: Lock previno race conditions entre procesos")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Iniciar servidor de métricas Prometheus
    log("Iniciando servidor de métricas en puerto 8000")
    start_http_server(8000)
    log("Métricas disponibles en http://localhost:8000")

    log("\n" + "="*70)
    log("DEMOS DE RACE CONDITIONS")
    log("="*70)

    try:
        # Demo 1: Contador
        demo_race_condition_contador()

        time.sleep(2)

        # Demo 2: Sistema bancario
        demo_race_condition_banco()

        time.sleep(2)

        # Demo 3: Multiprocessing
        demo_race_condition_multiprocessing()

        log("\n" + "="*70)
        log("RESUMEN")
        log("="*70)
        log("✓ Race conditions ocurren cuando múltiples threads/procesos")
        log("  acceden a memoria compartida sin sincronización")
        log("✓ Resultan en datos corruptos y comportamiento no determinístico")
        log("✓ Se previenen con locks, pero tienen overhead de performance")
        log("✓ Métricas exportadas a Prometheus para visualización")
        log("\nMétricas disponibles:")
        log("  - race_conditions_detected_total")
        log("  - corrupted_data_instances")
        log("  - concurrent_operation_duration_seconds")
        log("  - lock_wait_time_seconds")

        log("\n💡 Mantén este script corriendo para ver métricas en Grafana")
        log("Presiona Ctrl+C para salir")

        # Mantener servidor corriendo
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        log("\nScript detenido por usuario")

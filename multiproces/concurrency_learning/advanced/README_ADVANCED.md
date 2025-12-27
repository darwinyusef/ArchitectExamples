# 🎓 Módulos Avanzados de Concurrencia

## 📚 Contenido Creado

### 1. Race Conditions (`race_conditions/01_race_conditions.py`)
✅ **Completado** - Puerto 8000

**Conceptos cubiertos**:
- Race conditions en contadores compartidos
- Race conditions en sistemas bancarios
- Race conditions con multiprocessing
- Detección y prevención

**Métricas Prometheus**:
```
race_conditions_detected_total
corrupted_data_instances
concurrent_operation_duration_seconds
lock_wait_time_seconds
```

### 2. Locks y Mutex (`locks/02_locks_mutex.py`)
✅ **Completado** - Puerto 8001

**Conceptos cubiertos**:
- Lock básico vs RLock (re-entrante)
- Lock con timeout
- Lock en multiprocessing
- Lock contention (competencia)
- Try-lock (no bloqueante)

**Métricas Prometheus**:
```
lock_acquisitions_total
lock_wait_duration_seconds
lock_hold_duration_seconds
lock_contention_threads
```

### 3. Deadlocks (`deadlocks/03_deadlocks.py`)
✅ **Completado** - Puerto 8002

**Conceptos cubiertos**:
- Deadlock clásico (demostración)
- **Solución 1**: Ordenamiento de locks
- **Solución 2**: Jerarquía de locks
- **Solución 3**: Try-lock con backoff
- **Solución 4**: Timeout en locks
- Problema de los filósofos comensales

**Métricas Prometheus**:
```
deadlocks_detected_total
deadlocks_prevented_total{strategy}
lock_order_violations_total
lock_timeout_failures_total
```

---

## 🚀 Cómo Ejecutar

### Ejecutar todos los módulos simultáneamente

```bash
cd concurrency_learning/advanced

# Terminal 1: Race Conditions
python3 race_conditions/01_race_conditions.py &

# Terminal 2: Locks
python3 locks/02_locks_mutex.py &

# Terminal 3: Deadlocks
python3 deadlocks/03_deadlocks.py &
```

### Ver métricas

```bash
# Race Conditions
curl http://localhost:8000/metrics

# Locks
curl http://localhost:8001/metrics

# Deadlocks
curl http://localhost:8002/metrics
```

---

## 📊 Configuración de Prometheus

Crear archivo `prometheus.yml`:

```yaml
global:
  scrape_interval: 5s
  evaluation_interval: 5s

scrape_configs:
  - job_name: 'race_conditions'
    static_configs:
      - targets: ['localhost:8000']
        labels:
          module: 'race_conditions'

  - job_name: 'locks'
    static_configs:
      - targets: ['localhost:8001']
        labels:
          module: 'locks'

  - job_name: 'deadlocks'
    static_configs:
      - targets: ['localhost:8002']
        labels:
          module: 'deadlocks'
```

Ejecutar Prometheus:

```bash
prometheus --config.file=prometheus.yml
```

Prometheus UI: `http://localhost:9090`

---

## 📈 Dashboards de Grafana

### Dashboard 1: Race Conditions Monitor

**Paneles sugeridos**:

1. **Race Conditions Detectadas** (Counter)
```promql
rate(race_conditions_detected_total[1m])
```

2. **Datos Corruptos** (Gauge)
```promql
corrupted_data_instances
```

3. **Duración de Operaciones** (Histogram)
```promql
histogram_quantile(0.95,
  rate(concurrent_operation_duration_seconds_bucket[5m])
)
```

### Dashboard 2: Lock Performance

**Paneles sugeridos**:

1. **Adquisiciones de Lock** (Counter)
```promql
rate(lock_acquisitions_total[1m])
```

2. **Tiempo de Espera P95** (Histogram)
```promql
histogram_quantile(0.95,
  rate(lock_wait_duration_seconds_bucket[5m])
)
```

3. **Contención de Locks** (Gauge)
```promql
lock_contention_threads
```

4. **Tiempo Manteniendo Lock** (Histogram)
```promql
histogram_quantile(0.99,
  rate(lock_hold_duration_seconds_bucket[5m])
)
```

### Dashboard 3: Deadlock Detection

**Paneles sugeridos**:

1. **Deadlocks Detectados** (Counter)
```promql
increase(deadlocks_detected_total[5m])
```

2. **Deadlocks Prevenidos por Estrategia** (Counter)
```promql
rate(deadlocks_prevented_total[1m])
```

3. **Violaciones de Orden** (Counter)
```promql
increase(lock_order_violations_total[5m])
```

4. **Timeouts de Lock** (Counter)
```promql
rate(lock_timeout_failures_total[1m])
```

---

## 🎯 Queries Útiles de Prometheus

### Detectar problemas de rendimiento

```promql
# Locks que tardan más de 100ms
lock_wait_duration_seconds > 0.1

# Alta contención (más de 5 threads esperando)
lock_contention_threads > 5

# Tasa de race conditions
rate(race_conditions_detected_total[5m]) > 0

# Efectividad de prevención de deadlocks
sum(rate(deadlocks_prevented_total[5m])) by (strategy)
```

### Alertas recomendadas

```yaml
groups:
  - name: concurrency_alerts
    rules:
      # Alta tasa de race conditions
      - alert: HighRaceConditionRate
        expr: rate(race_conditions_detected_total[5m]) > 1
        for: 2m
        annotations:
          summary: "Alta tasa de race conditions detectadas"

      # Deadlock detectado
      - alert: DeadlockDetected
        expr: increase(deadlocks_detected_total[1m]) > 0
        annotations:
          summary: "Deadlock detectado en el sistema"

      # Alta contención de locks
      - alert: HighLockContention
        expr: lock_contention_threads > 10
        for: 5m
        annotations:
          summary: "Alta contención en locks"

      # Tiempo de espera excesivo
      - alert: ExcessiveLockWaitTime
        expr: |
          histogram_quantile(0.95,
            rate(lock_wait_duration_seconds_bucket[5m])
          ) > 1
        for: 5m
        annotations:
          summary: "Tiempo de espera de locks excesivo (P95 > 1s)"
```

---

## 🔬 Experimentos Sugeridos

### Experimento 1: Medir impacto del lock contention

```python
# Variar número de threads y medir throughput
for num_threads in [2, 4, 8, 16, 32]:
    ejecutar_benchmark(num_threads)
    # Observar métricas en Grafana
```

### Experimento 2: Comparar estrategias anti-deadlock

```python
# Ejecutar cada estrategia y comparar:
# - Ordenamiento
# - Jerarquía
# - Try-lock
# - Timeout

# Métricas a comparar:
# - Throughput
# - Latencia P95
# - CPU utilization
```

### Experimento 3: Simular carga alta

```python
# Aumentar gradualmente la carga
# Observar en qué punto aparecen race conditions
# Ver cómo escalan las diferentes soluciones
```

---

## 📖 Conceptos Adicionales

### Semáforos (Próximo módulo)

**Semáforo**: Lock con contador que permite N threads simultáneos.

```python
# Límite de conexiones concurrentes
semaforo = threading.Semaphore(5)  # Max 5 simultáneos

with semaforo:
    # Hacer trabajo
    pass
```

**Usos comunes**:
- Pool de conexiones (DB, HTTP)
- Rate limiting
- Resource pools

### Visibilidad de Memoria (Próximo módulo)

**Problema**: En sistemas multi-core, cada CPU tiene su propio cache.
Los cambios en un CPU pueden no ser visibles inmediatamente en otro.

**Ejemplo**:
```python
# Thread 1
dato = cargar_config()  # CPU 1 cache
listo = True

# Thread 2
while not listo:  # CPU 2 cache (puede no ver cambio)
    pass
usar(dato)  # Puede ver dato viejo
```

**Soluciones en Python**:
- Locks (garantizan memory barrier)
- Queue (thread-safe por diseño)
- multiprocessing.Value (con lock implícito)

---

## 🎓 Mejores Prácticas Resumidas

### 1. Race Conditions
❌ **Evitar**: Acceso sin sincronización a memoria compartida
✅ **Hacer**: Proteger secciones críticas con locks

### 2. Locks
❌ **Evitar**: Secciones críticas largas
✅ **Hacer**: Minimizar código dentro del lock

### 3. Deadlocks
❌ **Evitar**: Orden inconsistente de locks
✅ **Hacer**: Definir orden global o usar jerarquía

### 4. Performance
❌ **Evitar**: Lock contention alta
✅ **Hacer**: Dividir datos para reducir compartición

### 5. Debugging
❌ **Evitar**: Ignorar métricas
✅ **Hacer**: Monitorear con Prometheus/Grafana

---

## 📚 Recursos de Aprendizaje

### Libros recomendados:
- "The Art of Multiprocessor Programming" - Herlihy & Shavit
- "Java Concurrency in Practice" (aplica a Python también)

### Papers clásicos:
- "Dijkstra's Dining Philosophers" (1965)
- "Monitors: An Operating System Structuring Concept" (1974)

### Herramientas:
- ThreadSanitizer (detecta race conditions)
- Helgrind (Valgrind tool para concurrencia)
- py-spy (profiler para Python)

---

## 🚀 Próximos Pasos

1. ✅ Ejecutar todos los módulos
2. ✅ Configurar Prometheus
3. ✅ Crear dashboards en Grafana
4. 📊 Ejecutar experimentos
5. 📈 Analizar métricas
6. 🔧 Optimizar según resultados

---

**¡Feliz aprendizaje de concurrencia avanzada! 🎉**

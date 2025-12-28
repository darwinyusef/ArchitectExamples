# 📖 Índice Completo del Proyecto

## 🎓 Python Concurrency Learning - Proyecto Completo

**Un curso práctico completo sobre concurrencia, paralelismo y sincronización en Python con visualización en tiempo real usando Grafana y Prometheus.**

---

## 📚 Guías de Inicio

| Archivo | Descripción | Para Quién |
|---------|-------------|------------|
| **QUICKSTART.md** | ⚡ Inicio rápido en 5 minutos | Principiantes |
| **README_DOCKER.md** | 🐳 Setup con Docker | Usuarios de Docker |
| **README.md** | 📖 Documentación completa | Todos |
| **DOCKER_SETUP.md** | 🔧 Guía detallada de Docker | Avanzados |
| **INDEX.md** | 📋 Este archivo | Navegación |

---

## 🗂️ Estructura del Proyecto

### 1️⃣ Conceptos Básicos (`basics/`)

| Archivo | Puerto | Temas |
|---------|--------|-------|
| `01_threading_basics.py` | - | Threading, GIL, I/O-bound |
| `02_multiprocessing_basics.py` | - | Procesos, Pool, CPU-bound |

**Aprenderás:**
- Diferencia entre threading y multiprocessing
- El problema del GIL
- Cuándo usar cada uno
- Pool de workers

**Ejecutar:**
```bash
python3 basics/01_threading_basics.py
python3 basics/02_multiprocessing_basics.py
```

---

### 2️⃣ Workers y Job Queues (`workers/`)

| Archivo | Puerto | Temas |
|---------|--------|-------|
| `job_queue_system.py` | - | Job queue, Prioridades, Workers |

**Aprenderás:**
- Sistema de cola de trabajos
- Priorización de jobs
- Worker pools
- Manejo de errores por job

**Ejecutar:**
```bash
python3 workers/job_queue_system.py
```

---

### 3️⃣ WebSockets + Workers (`websockets/`)

| Archivo | Puerto | Temas |
|---------|--------|-------|
| `websocket_server.py` | 8765 | WebSocket, Async I/O, Workers |
| `websocket_client.html` | - | Cliente web interactivo |

**Aprenderás:**
- Servidor WebSocket asíncrono
- Delegar trabajo CPU-intensive
- Arquitectura async + multiprocessing
- Cliente JavaScript

**Ejecutar:**
```bash
# Servidor
python3 websockets/websocket_server.py

# Cliente (en otra terminal)
python3 websockets/websocket_server.py client

# O abrir websocket_client.html en navegador
```

---

### 4️⃣ Monitoreo (`monitoring/`)

| Archivo | Puerto | Temas |
|---------|--------|-------|
| `cpu_monitor.py` | 8003 | CPU, Memoria, Prometheus |

**Aprenderás:**
- Monitorear uso de CPU por core
- Métricas de sistema
- Exportar a Prometheus
- Detectar bottlenecks

**Ejecutar:**
```bash
# Snapshot único
python3 monitoring/cpu_monitor.py

# Monitoreo continuo
python3 monitoring/cpu_monitor.py monitor

# Servidor Prometheus
python3 monitoring/cpu_monitor.py prometheus
```

---

### 5️⃣ Temas Avanzados (`advanced/`)

#### 🔴 Race Conditions

| Archivo | Puerto | Métricas |
|---------|--------|----------|
| `race_conditions/01_race_conditions.py` | 8000 | race_conditions_detected_total, corrupted_data_instances |

**Aprenderás:**
- Qué son las race conditions
- Contador compartido (problema)
- Sistema bancario (ejemplo real)
- Detección y prevención

**Métricas Prometheus:**
```promql
race_conditions_detected_total
corrupted_data_instances
concurrent_operation_duration_seconds
lock_wait_time_seconds
```

---

#### 🔒 Locks y Mutex

| Archivo | Puerto | Métricas |
|---------|--------|----------|
| `locks/02_locks_mutex.py` | 8001 | lock_acquisitions_total, lock_wait_duration_seconds |

**Aprenderás:**
- Lock básico vs RLock
- Lock con timeout
- Lock en multiprocessing
- Lock contention
- Try-lock (no bloqueante)

**Métricas Prometheus:**
```promql
lock_acquisitions_total{lock_type,lock_name}
lock_wait_duration_seconds
lock_hold_duration_seconds
lock_contention_threads
```

---

#### 💀 Deadlocks

| Archivo | Puerto | Métricas |
|---------|--------|----------|
| `deadlocks/03_deadlocks.py` | 8002 | deadlocks_detected_total, deadlocks_prevented_total |

**Aprenderás:**
- Deadlock clásico (demostración)
- **4 Soluciones:**
  1. Ordenamiento de locks
  2. Jerarquía de locks
  3. Try-lock con backoff
  4. Timeout en locks
- Problema de los filósofos comensales

**Métricas Prometheus:**
```promql
deadlocks_detected_total
deadlocks_prevented_total{strategy}
lock_order_violations_total
lock_timeout_failures_total
```

---

### 6️⃣ Ejemplos Prácticos (`examples/`)

| Archivo | Descripción |
|---------|-------------|
| `demo_completo.py` | Sistema completo de procesamiento de imágenes |

**Incluye:**
- Workers con CPU affinity
- Monitor de rendimiento en tiempo real
- Estadísticas detalladas
- Balance de carga entre CPUs

**Ejecutar:**
```bash
python3 examples/demo_completo.py
```

---

### 7️⃣ Docker y Grafana (`docker-compose.yml`, `grafana/`, `prometheus/`)

#### Servicios Docker

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **Grafana** | 3000 | Dashboards y visualización |
| **Prometheus** | 9090 | Motor de métricas |
| **Alertmanager** | 9093 | Gestión de alertas |
| **Node Exporter** | 9100 | Métricas del sistema |

#### Archivos de Configuración

```
docker-compose.yml              # Orquestación
Dockerfile                      # Imagen Python
.dockerignore                   # Exclusiones

prometheus/
├── prometheus.yml              # Config principal
├── alerts.yml                  # 15+ alertas
└── alertmanager.yml            # Config de alertas

grafana/
├── provisioning/
│   ├── datasources/
│   │   └── datasource.yml      # Auto-config
│   └── dashboards/
│       └── dashboard.yml       # Auto-provision
└── dashboards/
    └── dashboards.json         # Dashboard completo
```

**Ejecutar:**
```bash
# Con script de ayuda
./run.sh setup

# O manualmente
docker-compose up -d
```

---

## 📊 Métricas Disponibles

### Concurrencia

```promql
# Race Conditions
race_conditions_detected_total{type}
corrupted_data_instances

# Locks
lock_acquisitions_total{lock_type,lock_name}
lock_wait_duration_seconds{lock_type,lock_name}
lock_hold_duration_seconds{lock_type,lock_name}
lock_contention_threads{lock_name}

# Deadlocks
deadlocks_detected_total
deadlocks_prevented_total{strategy}
lock_order_violations_total
lock_timeout_failures_total
```

### Sistema

```promql
# CPU
cpu_usage_total
cpu_usage_per_core{core}

# Memoria
memory_usage_percent
memory_used_mb

# Sistema
system_load_average{interval}
```

### Performance

```promql
# Operaciones
concurrent_operation_duration_seconds{operation_type}

# General
up{job}
```

---

## 🎯 Rutas de Aprendizaje

### 🟢 Nivel Principiante (2-3 horas)

```bash
# 1. Conceptos básicos
python3 basics/01_threading_basics.py
python3 basics/02_multiprocessing_basics.py

# 2. Job Queue
python3 workers/job_queue_system.py

# 3. Demo completo
python3 examples/demo_completo.py
```

**Conceptos cubiertos:**
- Threading vs Multiprocessing
- GIL
- Pool de workers
- Job queue básico

---

### 🟡 Nivel Intermedio (3-4 horas)

```bash
# 4. WebSocket + Workers
python3 websockets/websocket_server.py

# 5. Monitoreo
python3 monitoring/cpu_monitor.py prometheus

# 6. Setup Grafana
./run.sh docker-start
# Importar dashboard en Grafana
```

**Conceptos cubiertos:**
- Async I/O
- WebSockets
- Monitoreo con Prometheus
- Visualización con Grafana

---

### 🔴 Nivel Avanzado (4-6 horas)

```bash
# 7. Race Conditions
python3 advanced/race_conditions/01_race_conditions.py

# 8. Locks
python3 advanced/locks/02_locks_mutex.py

# 9. Deadlocks
python3 advanced/deadlocks/03_deadlocks.py

# 10. Análisis en Grafana
# Observar métricas y patrones
# Ejecutar experimentos
```

**Conceptos cubiertos:**
- Race conditions
- Secciones críticas
- Locks (Lock, RLock, MPLock)
- Deadlocks (4 soluciones)
- Lock contention
- Métricas de sincronización

---

## 🛠️ Scripts de Utilidad

### `run.sh` - Script Principal

```bash
# Setup completo
./run.sh setup

# Gestión de apps
./run.sh start
./run.sh stop
./run.sh restart
./run.sh status
./run.sh logs

# Docker
./run.sh docker-start
./run.sh docker-stop
./run.sh docker-logs

# Demos
./run.sh demo-basic
./run.sh demo-full
./run.sh demo-ws

# Limpieza
./run.sh clean

# Ayuda
./run.sh help
```

### `grafana/setup_grafana.sh` - Setup Manual

```bash
# Si prefieres instalación manual (sin Docker)
cd grafana
chmod +x setup_grafana.sh
./setup_grafana.sh
```

---

## 📖 Documentación por Tema

### Race Conditions
- **Archivo**: `advanced/race_conditions/01_race_conditions.py`
- **Teoría**: Comentarios internos extensivos
- **Puerto**: 8000
- **Métricas**: race_conditions_detected_total, corrupted_data_instances

### Locks y Mutex
- **Archivo**: `advanced/locks/02_locks_mutex.py`
- **Teoría**: Lock, RLock, timeout, contention, try-lock
- **Puerto**: 8001
- **Métricas**: lock_acquisitions_total, lock_wait_duration_seconds

### Deadlocks
- **Archivo**: `advanced/deadlocks/03_deadlocks.py`
- **Teoría**: 4 condiciones, 4 soluciones, filósofos
- **Puerto**: 8002
- **Métricas**: deadlocks_detected_total, deadlocks_prevented_total

### Semáforos
- **Teoría**: En `advanced/README_ADVANCED.md`
- **Uso**: threading.Semaphore, límite de recursos

### Visibilidad de Memoria
- **Teoría**: En `advanced/README_ADVANCED.md`
- **Problema**: Cache coherence en multi-core
- **Soluciones**: Locks, Queue, Value

---

## 🎓 Conceptos Cubiertos

### Fundamentos
✅ Concurrencia vs Paralelismo
✅ Threading vs Multiprocessing
✅ GIL (Global Interpreter Lock)
✅ I/O-bound vs CPU-bound

### Sincronización
✅ Race Conditions
✅ Secciones Críticas
✅ Mutual Exclusion (Mutex)
✅ Locks (Lock, RLock, Lock de MP)
✅ Semáforos
✅ Deadlocks

### Patrones
✅ Job Queue / Task Queue
✅ Worker Pool
✅ Producer-Consumer
✅ WebSocket + Workers
✅ CPU Affinity

### Monitoreo
✅ Métricas con Prometheus
✅ Dashboards con Grafana
✅ Alertas
✅ Performance monitoring

---

## 🔗 Links Rápidos

### Guías
- [QUICKSTART.md](QUICKSTART.md) - Inicio rápido
- [README.md](README.md) - Documentación completa
- [README_DOCKER.md](README_DOCKER.md) - Setup Docker
- [DOCKER_SETUP.md](DOCKER_SETUP.md) - Guía detallada Docker
- [advanced/README_ADVANCED.md](advanced/README_ADVANCED.md) - Temas avanzados

### Configuración
- [docker-compose.yml](docker-compose.yml) - Servicios Docker
- [prometheus/prometheus.yml](prometheus/prometheus.yml) - Config Prometheus
- [prometheus/alerts.yml](prometheus/alerts.yml) - Reglas de alertas
- [grafana/dashboards.json](grafana/dashboards.json) - Dashboard Grafana

---

## 📊 Dashboards de Grafana

### Paneles Principales

1. **Race Conditions Detected** - Counter
2. **Corrupted Data Instances** - Gauge
3. **Lock Acquisitions by Type** - Graph
4. **Lock Wait Time (P95/P99)** - Graph
5. **Lock Contention** - Graph con alerta
6. **Deadlocks (Detected vs Prevented)** - Graph
7. **Lock Order Violations** - Graph
8. **Lock Timeout Failures** - Graph
9. **Concurrent Operation Duration** - Heatmap
10. **CPU Usage by Core** - Graph
11. **Memory Usage** - Graph

### Queries Útiles

```promql
# Race conditions por segundo
rate(race_conditions_detected_total[1m])

# P95 de lock wait time
histogram_quantile(0.95, rate(lock_wait_duration_seconds_bucket[5m]))

# CPU por core
cpu_usage_per_core{core="cpu0"}

# Deadlocks prevenidos por estrategia
sum(rate(deadlocks_prevented_total[5m])) by (strategy)
```

---

## ✅ Checklist de Setup

### Instalación Inicial
- [ ] Python 3.8+ instalado
- [ ] Dependencias Python: `pip3 install -r requirements.txt`
- [ ] Docker instalado (opcional)
- [ ] Docker Compose instalado (opcional)

### Ejecución
- [ ] Apps Python corriendo en puertos 8000-8003
- [ ] Grafana accesible en puerto 3000
- [ ] Prometheus accesible en puerto 9090
- [ ] Dashboard importado en Grafana
- [ ] Métricas visibles en Prometheus

### Verificación
- [ ] `./run.sh status` muestra todo corriendo
- [ ] `curl http://localhost:8000/metrics` retorna datos
- [ ] Prometheus Targets: http://localhost:9090/targets (all UP)
- [ ] Grafana muestra datos en dashboard

---

## 🎯 Próximos Pasos

1. ✅ Ejecutar `./run.sh setup`
2. ✅ Explorar módulos básicos
3. ✅ Importar dashboard en Grafana
4. ✅ Ejecutar módulos avanzados
5. 📊 Observar métricas en tiempo real
6. 🧪 Experimentar con diferentes escenarios
7. 📈 Analizar resultados
8. 🚀 Aplicar a proyecto real

---

**¡Proyecto completo listo para aprender! 🎉**

Para comenzar: `./run.sh setup`

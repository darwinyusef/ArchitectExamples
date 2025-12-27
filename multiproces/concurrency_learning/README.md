# 🚀 Guía Completa de Concurrencia y Paralelismo en Python

Proyecto educativo completo para aprender concurrencia, paralelismo, multiprocessing y WebSockets en Python, optimizado para sistemas con múltiples CPUs (como tu droplet de Digital Ocean con 2 CPUs).

## 📚 Tabla de Contenidos

1. [Conceptos Fundamentales](#conceptos-fundamentales)
2. [Estructura del Proyecto](#estructura-del-proyecto)
3. [Instalación y Configuración](#instalación-y-configuración)
4. [Guía de Aprendizaje](#guía-de-aprendizaje)
5. [Ejemplos Prácticos](#ejemplos-prácticos)
6. [Integración con Prometheus/Grafana](#integración-con-prometheusgrafana)
7. [Mejores Prácticas](#mejores-prácticas)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Conceptos Fundamentales

### ¿Qué es Concurrencia vs Paralelismo?

```
CONCURRENCIA (Concurrent):
- Múltiples tareas PROGRESAN al mismo tiempo
- Una CPU alterna entre tareas rápidamente
- Útil para I/O-bound (esperas)

    Tiempo →
CPU: [Task A][Task B][Task A][Task B]

PARALELISMO (Parallel):
- Múltiples tareas EJECUTAN al mismo tiempo
- Múltiples CPUs trabajando simultáneamente
- Útil para CPU-bound (cálculos)

    Tiempo →
CPU1: [Task A][Task A][Task A]
CPU2: [Task B][Task B][Task B]
```

### Threading vs Multiprocessing

| Característica | Threading | Multiprocessing |
|----------------|-----------|-----------------|
| **Memoria** | Compartida | Separada |
| **GIL** | Sí (limitante) | No |
| **CPU-bound** | ❌ Malo | ✅ Excelente |
| **I/O-bound** | ✅ Bueno | ✅ Funciona |
| **Overhead** | Bajo | Alto |
| **Comunicación** | Fácil | Queues/Pipes |
| **Debugging** | Difícil | Más fácil |

### El GIL (Global Interpreter Lock)

El GIL es un mutex que protege el acceso a objetos Python, evitando que múltiples threads ejecuten bytecode Python simultáneamente.

```python
# Threading con GIL
# Solo 1 thread ejecuta código Python a la vez
┌────────┐
│Thread 1│ →→→ [GIL] →→→ Ejecuta
└────────┘      ↑
┌────────┐      │
│Thread 2│ →→→ Espera el GIL
└────────┘

# Multiprocessing sin GIL
# Cada proceso tiene su propio GIL
┌──────────┐
│Process 1 │ →→→ [GIL propio] →→→ Ejecuta en CPU1
└──────────┘
┌──────────┐
│Process 2 │ →→→ [GIL propio] →→→ Ejecuta en CPU2
└──────────┘
```

**Conclusión**: Para aprovechar tus 2 CPUs en tareas de cálculo, debes usar **multiprocessing**, no threading.

---

## 📁 Estructura del Proyecto

```
concurrency_learning/
├── basics/
│   ├── 01_threading_basics.py       # Fundamentos de threading
│   └── 02_multiprocessing_basics.py # Fundamentos de multiprocessing
│
├── workers/
│   └── job_queue_system.py          # Sistema de job queue con workers
│
├── websockets/
│   └── websocket_server.py          # Servidor WebSocket + workers
│
├── monitoring/
│   └── cpu_monitor.py               # Monitor de CPU y recursos
│
├── examples/
│   └── demo_completo.py             # Demo completo del sistema
│
└── README.md                         # Esta guía
```

---

## 🛠️ Instalación y Configuración

### En tu Droplet de Digital Ocean

```bash
# 1. Conectar a tu droplet
ssh root@your_droplet_ip

# 2. Instalar Python 3.8+ (si no está instalado)
apt update
apt install python3 python3-pip -y

# 3. Clonar/copiar el proyecto
# (asumiendo que subiste los archivos al droplet)

# 4. Instalar dependencias
pip3 install psutil websockets

# 5. (Opcional) Para Prometheus/Grafana
pip3 install prometheus-client
```

### Verificar tu Sistema

```bash
# Ver número de CPUs
python3 -c "import multiprocessing as mp; print(f'CPUs: {mp.cpu_count()}')"

# Ver memoria
python3 -c "import psutil; print(f'RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB')"
```

Deberías ver:
```
CPUs: 2
RAM: 2.0 GB
```

---

## 📖 Guía de Aprendizaje

### Nivel 1: Conceptos Básicos

#### 1.1 Threading Básico

```bash
cd concurrency_learning/basics
python3 01_threading_basics.py
```

**Qué aprenderás**:
- Diferencia entre ejecución secuencial y concurrente
- Por qué threading es bueno para I/O
- El problema del GIL con tareas CPU-intensive

**Salida esperada**:
```
[12:30:45.123] [Worker-1] Iniciando tarea I/O: Tarea-1
[12:30:45.124] [Worker-2] Iniciando tarea I/O: Tarea-2
[12:30:45.125] [Worker-3] Iniciando tarea I/O: Tarea-3
...
Tiempo total: 2.02s
(Si fuera secuencial: ~6s, con threading: ~2s)
```

#### 1.2 Multiprocessing Básico

```bash
python3 02_multiprocessing_basics.py
```

**Qué aprenderás**:
- Cómo crear procesos separados
- Uso de Pool para gestionar workers
- Distribución de carga entre CPUs
- Comunicación entre procesos con Queues

**Conceptos clave**:
```python
# Pool automático (recomendado)
with mp.Pool(processes=2) as pool:
    resultados = pool.map(funcion, datos)

# Control manual de procesos
proceso = mp.Process(target=funcion, args=(arg1, arg2))
proceso.start()
proceso.join()

# Comunicación entre procesos
cola = mp.Queue()
cola.put(datos)
resultado = cola.get()
```

### Nivel 2: Job Queue System

```bash
cd ../workers
python3 job_queue_system.py
```

**Qué aprenderás**:
- Sistema de cola de trabajos (como Celery/RQ)
- Workers que procesan jobs en background
- Priorización de jobs
- Manejo de errores por job

**Arquitectura**:
```
Cliente → Job Queue → Workers (cada uno en un CPU)
                        ↓
                   Results Queue → Cliente
```

**Casos de uso reales**:
- Procesamiento de imágenes en batch
- Generación de reportes
- Envío de emails masivos
- Análisis de datos

### Nivel 3: WebSockets + Workers

```bash
cd ../websockets

# Terminal 1: Servidor
python3 websocket_server.py

# Terminal 2: Cliente (en otra sesión SSH)
python3 websocket_server.py client
```

**Qué aprenderás**:
- Servidor WebSocket asíncrono
- Delegar trabajo pesado a workers
- Mantener conexiones responsivas
- Arquitectura async + multiprocessing

**Flujo de trabajo**:
```
1. Cliente conecta via WebSocket
2. Cliente envía job (ej: calcular Fibonacci)
3. Servidor encola job para workers
4. Worker en CPU separado procesa job
5. Resultado se envía de vuelta al cliente via WebSocket
```

**Ejemplo de cliente**:
```javascript
// Cliente JavaScript (para navegador)
const ws = new WebSocket('ws://your_droplet_ip:8765');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Recibido:', data);
};

// Enviar job
ws.send(JSON.stringify({
    command: 'submit_job',
    task_type: 'calcular_fibonacci',
    data: { n: 35 }
}));
```

### Nivel 4: Monitoreo

```bash
cd ../monitoring

# Monitoreo básico
python3 cpu_monitor.py

# Monitoreo continuo
python3 cpu_monitor.py monitor

# Servidor Prometheus
python3 cpu_monitor.py prometheus
```

**Qué aprenderás**:
- Monitorear uso de CPU por core
- Ver qué proceso usa qué CPU
- Exportar métricas para Prometheus
- Detectar bottlenecks

**Salida esperada**:
```
[12:45:30] ==================================================
CPU Total:  45.2%
  CPU0: [████████████░░░░░░░░] 60.5%
  CPU1: [██████░░░░░░░░░░░░░░] 30.1%
Memoria:   35.4% (708/2000 MB)
Load Avg:  1.23, 0.98, 0.76
```

### Nivel 5: Demo Completo

```bash
cd ../examples
python3 demo_completo.py
```

**Qué incluye**:
- Sistema completo de procesamiento de imágenes
- Workers con CPU affinity (cada worker en un CPU específico)
- Monitor de rendimiento en tiempo real
- Estadísticas detalladas

**Conceptos avanzados**:
- CPU affinity para asignar workers a CPUs
- Dashboard en tiempo real
- Métricas de throughput
- Distribución de carga

---

## 📊 Integración con Prometheus/Grafana

### Setup en tu Droplet

#### 1. Instalar Prometheus

```bash
# Descargar Prometheus
cd /opt
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
cd prometheus-*

# Configurar prometheus.yml
cat > prometheus.yml << EOF
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: 'python_app'
    static_configs:
      - targets: ['localhost:8000']
EOF

# Ejecutar Prometheus
./prometheus --config.file=prometheus.yml &
```

Prometheus estará en: `http://your_droplet_ip:9090`

#### 2. Instalar Grafana

```bash
# Instalar Grafana
apt-get install -y software-properties-common
add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -
apt-get update
apt-get install grafana

# Iniciar Grafana
systemctl start grafana-server
systemctl enable grafana-server
```

Grafana estará en: `http://your_droplet_ip:3000` (usuario/password: admin/admin)

#### 3. Exportar Métricas desde Python

```bash
cd concurrency_learning/monitoring
python3 cpu_monitor.py prometheus
```

Esto expone métricas en: `http://your_droplet_ip:8000`

#### 4. Configurar Dashboard en Grafana

1. Abrir Grafana: `http://your_droplet_ip:3000`
2. Agregar Prometheus como data source:
   - Configuration → Data Sources → Add Prometheus
   - URL: `http://localhost:9090`
3. Crear dashboard:
   - Create → Dashboard → Add panel

**Queries útiles**:
```promql
# Uso total de CPU
cpu_usage_total

# Uso por CPU core
cpu_usage_per_core{core="cpu0"}
cpu_usage_per_core{core="cpu1"}

# Uso de memoria
memory_usage_percent

# Load average
system_load_average{interval="1min"}
```

**Panel recomendado**:
```
Título: CPU Usage por Core
Query: cpu_usage_per_core
Visualization: Time series
Legend: {{core}}
```

### Ejemplo de Dashboard JSON

```json
{
  "dashboard": {
    "title": "Python Multiprocessing Monitor",
    "panels": [
      {
        "title": "CPU Usage per Core",
        "targets": [
          {
            "expr": "cpu_usage_per_core",
            "legendFormat": "{{core}}"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "targets": [
          {
            "expr": "memory_usage_percent"
          }
        ]
      }
    ]
  }
}
```

---

## 🎓 Mejores Prácticas

### 1. Cuándo Usar Qué

```python
# ✅ Usa Threading para:
- Llamadas HTTP/API
- Lectura/escritura de archivos
- Database queries
- Operaciones de red

# ✅ Usa Multiprocessing para:
- Cálculos matemáticos intensivos
- Procesamiento de imágenes/video
- Machine Learning inference
- Data processing pesado

# ✅ Usa AsyncIO para:
- Servidores web (muchas conexiones)
- WebSockets
- Scraping masivo
- I/O concurrente sin overhead de threads
```

### 2. Optimizar para tus 2 CPUs

```python
import multiprocessing as mp

# Siempre usar número de CPUs disponibles
num_workers = mp.cpu_count()  # = 2 en tu droplet

# Para CPU-intensive: workers = CPUs
with mp.Pool(processes=num_workers) as pool:
    results = pool.map(cpu_intensive_task, data)

# Para I/O-intensive: puedes usar más workers
num_workers = mp.cpu_count() * 2  # = 4

# Para tareas mixtas: empezar con CPUs y ajustar
num_workers = mp.cpu_count()  # Luego monitorear y ajustar
```

### 3. CPU Affinity (Asignar Workers a CPUs)

```python
import psutil
import os

def worker_with_affinity(worker_id):
    # Asignar worker a CPU específico
    cpu_id = (worker_id - 1) % mp.cpu_count()
    process = psutil.Process(os.getpid())
    process.cpu_affinity([cpu_id])

    print(f"Worker {worker_id} asignado a CPU {cpu_id}")
    # ... resto del código del worker
```

**Beneficios**:
- Mejor uso del cache L1/L2 de cada CPU
- Evita context switching entre CPUs
- Rendimiento más predecible

### 4. Manejo de Memoria

```python
# ❌ MAL: Compartir datos grandes entre procesos
datos_grandes = list(range(10_000_000))
with mp.Pool() as pool:
    # Esto COPIA los datos a cada proceso
    results = pool.map(procesar, [datos_grandes] * 10)

# ✅ BIEN: Usar shared memory
from multiprocessing import shared_memory

# Crear shared memory
shm = shared_memory.SharedMemory(create=True, size=1000000)
# ... usar shared memory

# O mejor: procesar en chunks
def procesar_chunk(start, end):
    # Generar datos solo en este proceso
    datos = list(range(start, end))
    return process(datos)

with mp.Pool() as pool:
    results = pool.starmap(procesar_chunk, [
        (0, 5000000),
        (5000000, 10000000)
    ])
```

### 5. Debugging Multiprocessing

```python
# Activar logging detallado
import logging
mp.log_to_stderr(logging.DEBUG)

# Usar try-except en workers
def safe_worker(job):
    try:
        return process(job)
    except Exception as e:
        import traceback
        return {
            'error': str(e),
            'traceback': traceback.format_exc()
        }

# Usar timeout para evitar hangs
result = queue.get(timeout=30)  # Timeout de 30s
```

---

## 🔧 Troubleshooting

### Problema: "Workers no usan CPUs diferentes"

**Solución**: Verificar con htop

```bash
# Instalar htop
apt install htop

# Ejecutar tu programa en una terminal
python3 demo_completo.py

# En otra terminal, ver uso de CPU
htop
# Presiona 't' para vista de árbol
# Verifica que múltiples procesos Python usen CPUs diferentes
```

### Problema: "Queue está llena"

```python
# Usar maxsize
queue = mp.Queue(maxsize=100)

# O procesar en batches
def procesar_en_batches(items, batch_size=50):
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        procesar_batch(batch)
```

### Problema: "Workers no terminan (hang)"

```python
# Usar timeout en joins
worker.join(timeout=10)
if worker.is_alive():
    worker.terminate()
    worker.join()

# Usar Event para shutdown graceful
shutdown_event = mp.Event()

def worker(shutdown_event):
    while not shutdown_event.is_set():
        # ... trabajo
        pass
```

### Problema: "Memoria se llena"

```python
# Procesar en chunks
def procesar_grande(filename):
    with open(filename) as f:
        while True:
            chunk = f.readlines(10000)  # Leer 10k líneas
            if not chunk:
                break
            procesar_chunk(chunk)

# Limpiar después de cada job
import gc
gc.collect()
```

### Problema: "No puedo conectar al WebSocket desde fuera"

```bash
# Verificar firewall
ufw allow 8765/tcp

# Verificar que servidor escucha en 0.0.0.0
# En websocket_server.py:
server = WebSocketServer(
    host="0.0.0.0",  # No "localhost"
    port=8765
)
```

---

## 🚀 Comandos Rápidos

```bash
# Navegación
cd ~/concurrency_learning

# Ejecutar ejemplos básicos
python3 basics/01_threading_basics.py
python3 basics/02_multiprocessing_basics.py

# Job queue
python3 workers/job_queue_system.py

# WebSocket
python3 websockets/websocket_server.py          # Servidor
python3 websockets/websocket_server.py client   # Cliente

# Monitoreo
python3 monitoring/cpu_monitor.py               # Snapshot
python3 monitoring/cpu_monitor.py monitor       # Continuo
python3 monitoring/cpu_monitor.py prometheus    # Prometheus

# Demo completo
python3 examples/demo_completo.py

# Ver procesos Python
ps aux | grep python

# Ver uso de CPU en tiempo real
htop
```

---

## 📝 Ejercicios Propuestos

### Ejercicio 1: Web Scraper Paralelo

Crear un scraper que:
- Use multiprocessing para scraping paralelo
- Procese 50 URLs simultáneamente con 2 workers
- Guarde resultados en una base de datos

### Ejercicio 2: API Server con Workers

Crear API REST que:
- Reciba requests de procesamiento
- Delegue a workers multiprocessing
- Retorne resultados via polling o WebSocket

### Ejercicio 3: Sistema de Thumbnails

Crear sistema que:
- Procese imágenes subidas
- Genere thumbnails de diferentes tamaños
- Use job queue con prioridades

---

## 📚 Recursos Adicionales

- [Python multiprocessing docs](https://docs.python.org/3/library/multiprocessing.html)
- [Understanding the GIL](https://realpython.com/python-gil/)
- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [psutil docs](https://psutil.readthedocs.io/)

---

## 🤝 Próximos Pasos

1. ✅ Ejecuta todos los ejemplos básicos
2. ✅ Entiende la diferencia threading vs multiprocessing
3. ✅ Implementa tu propio job queue
4. ✅ Configura monitoreo con Prometheus/Grafana
5. 🚀 Aplica estos conceptos a tu proyecto real

---

**¿Preguntas?** Revisa los comentarios en cada archivo `.py` - están documentados extensivamente con explicaciones de cada concepto.

**¡Buena suerte aprendiendo concurrencia y paralelismo en Python! 🎉**

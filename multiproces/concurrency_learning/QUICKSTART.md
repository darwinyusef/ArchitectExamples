# 🚀 Guía Rápida: Concurrencia y Paralelismo en Python

## ⚡ Setup Rápido en tu Droplet (2 CPUs / 2 GB RAM)

### 1. Instalación (5 minutos)

```bash
# Conectar a tu droplet
ssh root@your_droplet_ip

# Instalar dependencias
apt update
apt install -y python3 python3-pip

# Instalar paquetes Python
pip3 install psutil websockets prometheus-client

# Clonar/copiar este proyecto a tu droplet
# (asumiendo que los archivos ya están en ~/concurrency_learning)

cd ~/concurrency_learning
```

### 2. Configurar Grafana + Prometheus (10 minutos)

```bash
cd ~/concurrency_learning/grafana

# Ejecutar script de setup automático
chmod +x setup_grafana.sh
./setup_grafana.sh
```

Esto instalará:
- ✅ Prometheus en puerto 9090
- ✅ Grafana en puerto 3000
- ✅ Configuración de alertas
- ✅ Firewall configurado

### 3. Ejecutar Módulos de Concurrencia

#### Opción A: Ejecutar todo en paralelo (Recomendado)

```bash
cd ~/concurrency_learning

# Crear script launcher
cat > run_all.sh << 'EOF'
#!/bin/bash

# Race Conditions
python3 advanced/race_conditions/01_race_conditions.py &
PID1=$!

# Locks
python3 advanced/locks/02_locks_mutex.py &
PID2=$!

# Deadlocks
python3 advanced/deadlocks/03_deadlocks.py &
PID3=$!

# CPU Monitor
python3 monitoring/cpu_monitor.py prometheus &
PID4=$!

echo "Todos los módulos iniciados"
echo "PIDs: $PID1 $PID2 $PID3 $PID4"
echo "Para detener: kill $PID1 $PID2 $PID3 $PID4"

wait
EOF

chmod +x run_all.sh
./run_all.sh
```

#### Opción B: Ejecutar módulos individuales

```bash
# Terminal 1: Race Conditions
python3 advanced/race_conditions/01_race_conditions.py

# Terminal 2: Locks
python3 advanced/locks/02_locks_mutex.py

# Terminal 3: Deadlocks
python3 advanced/deadlocks/03_deadlocks.py

# Terminal 4: Monitor de CPU
python3 monitoring/cpu_monitor.py prometheus
```

### 4. Acceder a las Interfaces Web

```bash
# Obtener IP del droplet
hostname -I | awk '{print $1}'
```

Luego abre en tu navegador:

- **Grafana**: `http://YOUR_DROPLET_IP:3000`
  - Usuario: `admin`
  - Password: `admin`

- **Prometheus**: `http://YOUR_DROPLET_IP:9090`

- **Métricas Python**:
  - Race Conditions: `http://YOUR_DROPLET_IP:8000/metrics`
  - Locks: `http://YOUR_DROPLET_IP:8001/metrics`
  - Deadlocks: `http://YOUR_DROPLET_IP:8002/metrics`

### 5. Importar Dashboard en Grafana

1. Abrir Grafana → `http://YOUR_DROPLET_IP:3000`
2. Login con `admin/admin`
3. Click en "+" → "Import"
4. Copiar contenido de `grafana/dashboards.json`
5. Pegar y click "Load"
6. Seleccionar datasource "Prometheus"
7. Click "Import"

¡Listo! Ahora verás métricas en tiempo real.

---

## 📚 Estructura del Proyecto

```
concurrency_learning/
├── basics/                      # 🎓 Conceptos básicos
│   ├── 01_threading_basics.py
│   └── 02_multiprocessing_basics.py
│
├── workers/                     # 👷 Job Queue System
│   └── job_queue_system.py
│
├── websockets/                  # 🌐 WebSocket + Workers
│   ├── websocket_server.py
│   └── websocket_client.html
│
├── monitoring/                  # 📊 Monitoreo
│   └── cpu_monitor.py
│
├── advanced/                    # 🔥 Temas avanzados
│   ├── race_conditions/         # ⚠️  Race conditions
│   ├── locks/                   # 🔒 Locks y mutex
│   ├── deadlocks/               # 💀 Deadlocks
│   └── README_ADVANCED.md
│
├── grafana/                     # 📈 Configuración Grafana
│   ├── dashboards.json
│   └── setup_grafana.sh
│
├── examples/                    # 💡 Ejemplos prácticos
│   └── demo_completo.py
│
├── README.md                    # 📖 Documentación principal
└── QUICKSTART.md               # ⚡ Esta guía
```

---

## 🎯 Rutas de Aprendizaje

### Principiante → Intermedio (2-3 horas)

```bash
# 1. Conceptos básicos
python3 basics/01_threading_basics.py
python3 basics/02_multiprocessing_basics.py

# 2. Job Queue
python3 workers/job_queue_system.py

# 3. Demo completo
python3 examples/demo_completo.py
```

### Intermedio → Avanzado (3-4 horas)

```bash
# 4. Race Conditions
python3 advanced/race_conditions/01_race_conditions.py

# 5. Locks y Mutex
python3 advanced/locks/02_locks_mutex.py

# 6. Deadlocks
python3 advanced/deadlocks/03_deadlocks.py

# Observar métricas en Grafana mientras se ejecutan
```

### Avanzado → Experto (4-6 horas)

```bash
# 7. WebSocket Server
python3 websockets/websocket_server.py

# 8. Monitoreo avanzado
python3 monitoring/cpu_monitor.py prometheus

# 9. Experimentos personalizados
# Ver advanced/README_ADVANCED.md
```

---

## 🔥 Casos de Uso Reales

### 1. Procesamiento de Imágenes en Batch

```bash
python3 examples/demo_completo.py
```

**Aprenderás**:
- Distribuir carga entre 2 CPUs
- CPU affinity (asignar workers a CPUs específicos)
- Monitoreo de rendimiento
- Métricas de throughput

### 2. API con Workers Asíncronos

```bash
python3 websockets/websocket_server.py
```

**Aprenderás**:
- Async I/O con WebSockets
- Delegar trabajo CPU-intensive a workers
- Mantener conexiones responsivas
- Balance de carga

### 3. Sistema de Colas (Job Queue)

```bash
python3 workers/job_queue_system.py
```

**Aprenderás**:
- Patrón producer-consumer
- Priorización de jobs
- Manejo de errores
- Escalabilidad

---

## 📊 Métricas Clave en Grafana

### Panel 1: Race Conditions
```promql
rate(race_conditions_detected_total[1m])
```
**Qué observar**: Debe ser 0. Si >0, hay bugs de concurrencia.

### Panel 2: Lock Wait Time (P95)
```promql
histogram_quantile(0.95, rate(lock_wait_duration_seconds_bucket[5m]))
```
**Qué observar**: Debe ser <100ms. Si >1s, hay contención alta.

### Panel 3: Deadlocks
```promql
increase(deadlocks_detected_total[5m])
```
**Qué observar**: Debe ser 0 siempre.

### Panel 4: CPU por Core
```promql
cpu_usage_per_core{core="cpu0"}
cpu_usage_per_core{core="cpu1"}
```
**Qué observar**: Ambos CPUs deben estar balanceados (~50% cada uno).

---

## 🐛 Troubleshooting Común

### Problema: "No se conecta a Grafana"

```bash
# Verificar que Grafana está corriendo
systemctl status grafana-server

# Ver logs
journalctl -u grafana-server -f

# Verificar firewall
ufw status
ufw allow 3000/tcp
```

### Problema: "Prometheus no ve métricas"

```bash
# Verificar que scripts Python están corriendo
ps aux | grep python

# Verificar que puertos están abiertos
netstat -tulpn | grep 800

# Probar métricas manualmente
curl http://localhost:8000/metrics
```

### Problema: "Workers no usan CPUs diferentes"

```bash
# Instalar htop para ver uso de CPU
apt install htop

# Ejecutar htop
htop
# Presiona 't' para vista de árbol
# Presiona 'F5' para vista de árbol
```

### Problema: "Race conditions no se detectan"

```python
# Aumentar número de threads/procesos
NUM_THREADS = 20  # En lugar de 10

# Aumentar operaciones
INCREMENTOS = 10000  # En lugar de 1000

# Race conditions son más probables con más concurrencia
```

---

## 💡 Tips y Trucos

### 1. Ver métricas en tiempo real

```bash
# Opción 1: watch con curl
watch -n 1 'curl -s http://localhost:8000/metrics | grep race_conditions'

# Opción 2: Prometheus UI
# Ir a http://YOUR_IP:9090
# Ejecutar query: race_conditions_detected_total
```

### 2. Generar carga para testing

```python
# En otro terminal, ejecutar múltiples veces
for i in {1..10}; do
    python3 examples/demo_completo.py &
done

# Observar métricas en Grafana
```

### 3. Exportar métricas para análisis

```bash
# Desde Grafana
# Panel → Share → Export → Save to file

# Desde Prometheus API
curl 'http://localhost:9090/api/v1/query?query=lock_wait_duration_seconds' \
  | jq . > metrics.json
```

### 4. Crear alertas personalizadas

Editar `/opt/prometheus/alerts.yml`:

```yaml
- alert: CustomAlert
  expr: your_metric > threshold
  for: 5m
  annotations:
    summary: "Tu alerta personalizada"
```

Luego:
```bash
systemctl restart prometheus
```

---

## 🎓 Conceptos Clave Resumidos

| Concepto | Qué es | Cuándo usar |
|----------|--------|-------------|
| **Threading** | Concurrencia en mismo proceso | I/O-bound (HTTP, files) |
| **Multiprocessing** | Paralelismo real (múltiples CPUs) | CPU-bound (cálculos) |
| **Lock** | Mutex para secciones críticas | Proteger datos compartidos |
| **RLock** | Lock re-entrante | Llamadas recursivas |
| **Semaphore** | Lock con contador | Pool de recursos |
| **Queue** | Cola thread-safe | Producer-consumer |
| **Race Condition** | Acceso simultáneo sin sync | ¡Bug a evitar! |
| **Deadlock** | Bloqueo mutuo | ¡Bug a evitar! |

---

## 📖 Comandos Útiles

```bash
# Ver procesos Python
ps aux | grep python

# Ver uso de CPU en tiempo real
htop

# Ver métricas Prometheus
curl http://localhost:8000/metrics

# Logs de Grafana
journalctl -u grafana-server -f

# Logs de Prometheus
journalctl -u prometheus -f

# Detener todos los procesos Python
pkill -f python3

# Reiniciar servicios
systemctl restart grafana-server
systemctl restart prometheus
```

---

## 🚀 Próximos Pasos

1. ✅ Ejecutar módulos básicos
2. ✅ Configurar Grafana
3. ✅ Importar dashboards
4. 📊 Ejecutar experimentos personalizados
5. 📈 Analizar métricas
6. 🔧 Optimizar según resultados
7. 🎯 Aplicar a tu proyecto real

---

## 📚 Recursos Adicionales

- **README.md** - Documentación completa
- **advanced/README_ADVANCED.md** - Temas avanzados
- **Cada .py tiene comentarios extensivos** - Aprende leyendo el código

---

**¿Preguntas? Revisa los comentarios en cada archivo `.py` - están super documentados!**

**¡Feliz aprendizaje de concurrencia! 🎉**

# 🐳 Setup con Docker - Guía Completa

## ✨ ¡Configuración Completa de Docker Lista!

He creado una configuración completa de Docker Compose con:

✅ **Prometheus** - Recolección de métricas
✅ **Grafana** - Visualización de dashboards
✅ **Alertmanager** - Gestión de alertas
✅ **Node Exporter** - Métricas del sistema
✅ **Auto-provisioning** - Datasources y dashboards automáticos

---

## 🚀 Quick Start (3 comandos)

```bash
# 1. Instalar Docker (si no lo tienes)
curl -fsSL https://get.docker.com | sh
apt-get install -y docker-compose

# 2. Iniciar todo
cd ~/concurrency_learning
./run.sh setup

# 3. Abrir Grafana
# http://YOUR_DROPLET_IP:3000 (admin/admin)
```

¡Eso es todo! 🎉

---

## 📁 Archivos Docker Creados

```
concurrency_learning/
├── docker-compose.yml              ✅ Orquestación de servicios
├── Dockerfile                      ✅ Imagen Python (opcional)
├── .dockerignore                   ✅ Exclusiones
├── run.sh                          ✅ Script de gestión
│
├── prometheus/
│   ├── prometheus.yml              ✅ Config de Prometheus
│   ├── alerts.yml                  ✅ 15+ reglas de alertas
│   └── alertmanager.yml            ✅ Config de alertas
│
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── datasource.yml      ✅ Auto-config Prometheus
│       └── dashboards/
│           └── dashboard.yml       ✅ Auto-provision dashboards
│
├── DOCKER_SETUP.md                 ✅ Guía detallada
└── README_DOCKER.md                ✅ Este archivo
```

---

## 🎯 Uso del Script `run.sh`

### Comandos Principales

```bash
# Setup completo (primera vez)
./run.sh setup

# Iniciar aplicaciones Python
./run.sh start

# Ver estado
./run.sh status

# Ver logs en tiempo real
./run.sh logs

# Detener todo
./run.sh stop

# Reiniciar
./run.sh restart

# Limpiar todo
./run.sh clean
```

### Comandos Docker

```bash
# Solo Docker (Grafana + Prometheus)
./run.sh docker-start
./run.sh docker-stop
./run.sh docker-logs
```

### Demos

```bash
# Demos básicos
./run.sh demo-basic

# Demo completo
./run.sh demo-full

# WebSocket server
./run.sh demo-ws
```

---

## 📊 Servicios y Puertos

| Servicio | Puerto | URL | Descripción |
|----------|--------|-----|-------------|
| **Grafana** | 3000 | http://IP:3000 | Dashboards y visualización |
| **Prometheus** | 9090 | http://IP:9090 | Motor de métricas |
| **Alertmanager** | 9093 | http://IP:9093 | Gestión de alertas |
| **Node Exporter** | 9100 | http://IP:9100 | Métricas del sistema |
| Race Conditions | 8000 | http://IP:8000/metrics | App Python |
| Locks | 8001 | http://IP:8001/metrics | App Python |
| Deadlocks | 8002 | http://IP:8002/metrics | App Python |
| CPU Monitor | 8003 | http://IP:8003/metrics | App Python |
| WebSocket | 8765 | ws://IP:8765 | WebSocket server |

---

## 🔧 Configuración de Prometheus

### Targets Configurados

```yaml
✓ prometheus (auto-monitoreo)
✓ node-exporter (métricas del sistema)
✓ race_conditions (puerto 8000)
✓ locks (puerto 8001)
✓ deadlocks (puerto 8002)
✓ cpu_monitor (puerto 8003)
✓ websocket_server (puerto 8765)
```

### Alertas Configuradas (15+)

**Concurrencia:**
- HighRaceConditionRate
- DataCorruption
- DeadlockDetected
- HighLockContention
- ExcessiveLockWaitTime
- LockOrderViolation
- HighLockTimeoutRate

**Performance:**
- HighCPUUsage
- CPUImbalance
- HighMemoryUsage
- SwapInUse
- HighLoadAverage

**Aplicación:**
- SlowOperations
- ApplicationDown

**Sistema:**
- DiskSpaceLow
- TooManyProcesses

---

## 📈 Grafana Auto-Provisioning

### Datasource Automático

✅ Prometheus ya está configurado como datasource
✅ No necesitas configurar manualmente
✅ URL: http://prometheus:9090

### Dashboard Automático

Para importar el dashboard:

1. Abre Grafana: http://YOUR_IP:3000
2. Login: admin / admin
3. **+** → **Import**
4. Copia contenido de `grafana/dashboards.json`
5. **Load** → **Import**

### Paneles Incluidos (11 paneles)

1. Race Conditions Detected
2. Corrupted Data Instances
3. Lock Acquisitions by Type
4. Lock Wait Time (P95/P99)
5. Lock Contention
6. Deadlocks (Detected vs Prevented)
7. Lock Order Violations
8. Lock Timeout Failures
9. Concurrent Operation Duration (Heatmap)
10. System CPU Usage by Core
11. Memory Usage

---

## 🎓 Flujo de Trabajo Completo

### Primera Vez (Setup)

```bash
# 1. En tu droplet
cd ~/concurrency_learning

# 2. Ejecutar setup
./run.sh setup

# Esto hace:
# - Instala dependencias Python
# - Inicia Docker (Grafana + Prometheus)
# - Inicia apps Python
# - Muestra status
```

### Uso Diario

```bash
# Iniciar
./run.sh start

# Verificar que todo está OK
./run.sh status

# Ver métricas en Grafana
# http://YOUR_IP:3000

# Ver logs si hay problemas
./run.sh logs

# Detener al terminar
./run.sh stop
```

### Debugging

```bash
# Ver qué procesos están corriendo
ps aux | grep python

# Ver qué puertos están abiertos
netstat -tulpn | grep -E '(3000|8000|9090)'

# Ver logs de Docker
docker-compose logs -f grafana

# Probar métricas directamente
curl http://localhost:8000/metrics

# Ver targets en Prometheus
curl http://localhost:9090/api/v1/targets | jq
```

---

## 🔥 Características Avanzadas

### 1. Persistencia de Datos

Los datos se guardan en volúmenes Docker:

```bash
# Ver volúmenes
docker volume ls

# Backup de Grafana
docker run --rm \
  -v concurrency_learning_grafana_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/grafana-backup.tar.gz -C /data .

# Restaurar
docker run --rm \
  -v concurrency_learning_grafana_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/grafana-backup.tar.gz -C /data
```

### 2. Configurar Notificaciones

**Slack:**

Editar `prometheus/alertmanager.yml`:

```yaml
receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/XXX'
        channel: '#alerts'
```

**Email:**

```yaml
receivers:
  - name: 'email'
    email_configs:
      - to: 'tu-email@example.com'
        from: 'alerts@example.com'
        smarthost: smtp.gmail.com:587
        auth_username: 'user@gmail.com'
        auth_password: 'app-password'
```

### 3. Escalado

```bash
# Agregar más replicas en docker-compose.yml
services:
  app:
    deploy:
      replicas: 3
```

### 4. Límites de Recursos

```yaml
services:
  prometheus:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

---

## 💡 Tips y Trucos

### Ver Uso de Recursos en Tiempo Real

```bash
# Docker stats
docker stats

# htop del sistema
htop

# Métricas de Prometheus
curl http://localhost:9090/api/v1/query?query=up
```

### Queries Útiles de Prometheus

```promql
# Race conditions por segundo
rate(race_conditions_detected_total[1m])

# P95 de lock wait time
histogram_quantile(0.95, rate(lock_wait_duration_seconds_bucket[5m]))

# CPU por core
cpu_usage_per_core{core="cpu0"}

# Memoria usada
memory_usage_percent
```

### Exportar Métricas

```bash
# Desde Prometheus API
curl 'http://localhost:9090/api/v1/query?query=up' | jq > metrics.json

# Desde Grafana
# Panel → Share → Export → JSON
```

---

## 🐛 Troubleshooting Común

### Problema: "Cannot connect to Docker daemon"

```bash
systemctl start docker
systemctl enable docker
```

### Problema: "Port already in use"

```bash
# Ver qué usa el puerto
netstat -tulpn | grep 3000

# Cambiar puerto en docker-compose.yml
ports:
  - "3001:3000"
```

### Problema: "Prometheus no ve apps Python"

```bash
# Verificar que apps están corriendo
./run.sh status

# Verificar conexión
curl http://localhost:8000/metrics

# Ver targets en Prometheus
# http://YOUR_IP:9090/targets
```

### Problema: "Sin datos en Grafana"

```bash
# 1. Verificar datasource
# Grafana → Settings → Data Sources → Test

# 2. Ver logs
docker-compose logs -f grafana

# 3. Verificar query
# Edit panel → Ver expression
```

---

## 📚 Documentación Adicional

- **DOCKER_SETUP.md** - Guía detallada de Docker
- **QUICKSTART.md** - Guía rápida general
- **README.md** - Documentación completa
- **advanced/README_ADVANCED.md** - Temas avanzados

---

## 🎯 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    TU NAVEGADOR                         │
│  http://IP:3000 (Grafana)  http://IP:9090 (Prometheus) │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │   DOCKER NETWORK      │
         │   (monitoring)        │
         │                       │
         │  ┌─────────────────┐  │
         │  │   Grafana       │  │
         │  │   (port 3000)   │  │
         │  └────────┬────────┘  │
         │           │           │
         │  ┌────────▼────────┐  │
         │  │  Prometheus     │◄─┼─ Scrapes
         │  │  (port 9090)    │  │
         │  └────────┬────────┘  │
         │           │           │
         │  ┌────────▼────────┐  │
         │  │ Alertmanager    │  │
         │  │  (port 9093)    │  │
         │  └─────────────────┘  │
         │                       │
         │  ┌─────────────────┐  │
         │  │ Node Exporter   │  │
         │  │  (port 9100)    │  │
         │  └─────────────────┘  │
         └───────────────────────┘
                     │
         ┌───────────▼───────────────┐
         │   HOST (tu droplet)       │
         │                           │
         │  Python Apps:             │
         │  ├─ race_conditions:8000  │
         │  ├─ locks:8001            │
         │  ├─ deadlocks:8002        │
         │  ├─ cpu_monitor:8003      │
         │  └─ websocket:8765        │
         └───────────────────────────┘
```

---

## ✅ Checklist de Verificación

Después de `./run.sh setup`:

- [ ] Docker containers corriendo: `docker-compose ps`
- [ ] Grafana accesible: http://IP:3000
- [ ] Prometheus accesible: http://IP:9090
- [ ] Apps Python corriendo: `./run.sh status`
- [ ] Métricas disponibles: `curl http://localhost:8000/metrics`
- [ ] Targets UP en Prometheus: http://IP:9090/targets
- [ ] Dashboard importado en Grafana
- [ ] Datos visibles en dashboard

---

**¡Docker setup completo y listo para usar! 🐳🎉**

Para más detalles, ver `DOCKER_SETUP.md`

# 🐳 Guía de Setup con Docker

## 🚀 Setup Rápido (5 minutos)

### Pre-requisitos

En tu droplet de Digital Ocean:

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Instalar Docker Compose
apt-get install -y docker-compose

# Verificar instalación
docker --version
docker-compose --version
```

### Iniciar Stack Completo

```bash
# 1. Clonar/copiar proyecto al droplet
cd ~/concurrency_learning

# 2. Iniciar Prometheus + Grafana + Alertmanager
docker-compose up -d

# 3. Verificar que todo está corriendo
docker-compose ps

# Deberías ver:
# - prometheus       (puerto 9090)
# - grafana          (puerto 3000)
# - alertmanager     (puerto 9093)
# - node-exporter    (puerto 9100)
```

### Ejecutar Apps Python (en el host, no en Docker)

```bash
# Las apps Python corren en el HOST (no en Docker)
# Esto permite aprovechar multiprocessing con tus 2 CPUs

# Terminal 1: Race Conditions
python3 advanced/race_conditions/01_race_conditions.py &

# Terminal 2: Locks
python3 advanced/locks/02_locks_mutex.py &

# Terminal 3: Deadlocks
python3 advanced/deadlocks/03_deadlocks.py &

# Terminal 4: CPU Monitor
python3 monitoring/cpu_monitor.py prometheus &

# Ver procesos
ps aux | grep python
```

**¿Por qué Python en el host?**
- Docker tiene overhead en multiprocessing
- Queremos medir CPU usage real del droplet
- Mejor demostración de CPU affinity
- Más fácil debuggear

---

## 📊 Acceso a Servicios

### Desde tu navegador:

```
Grafana:       http://YOUR_DROPLET_IP:3000
Usuario:       admin
Password:      admin

Prometheus:    http://YOUR_DROPLET_IP:9090

Alertmanager:  http://YOUR_DROPLET_IP:9093

Node Exporter: http://YOUR_DROPLET_IP:9100/metrics
```

### Importar Dashboard en Grafana

1. Abrir Grafana: `http://YOUR_DROPLET_IP:3000`
2. Login: `admin` / `admin`
3. Click en **+** → **Import**
4. Copiar contenido de `grafana/dashboards.json`
5. Pegar y click **Load**
6. Click **Import**

¡Listo! Verás métricas en tiempo real.

---

## 🔧 Comandos Docker Útiles

### Ver logs

```bash
# Todos los servicios
docker-compose logs -f

# Solo Prometheus
docker-compose logs -f prometheus

# Solo Grafana
docker-compose logs -f grafana

# Últimas 100 líneas
docker-compose logs --tail=100 grafana
```

### Reiniciar servicios

```bash
# Reiniciar todo
docker-compose restart

# Reiniciar solo Prometheus
docker-compose restart prometheus

# Reiniciar solo Grafana
docker-compose restart grafana
```

### Detener y limpiar

```bash
# Detener servicios (mantiene datos)
docker-compose stop

# Detener y eliminar contenedores (mantiene datos)
docker-compose down

# Eliminar TODO incluyendo volúmenes (⚠️ pierde datos)
docker-compose down -v

# Limpiar imágenes no usadas
docker system prune -a
```

### Ver uso de recursos

```bash
# Uso de CPU/memoria de contenedores
docker stats

# Espacio en disco
docker system df

# Detalles de un contenedor
docker inspect prometheus
```

---

## 🔍 Troubleshooting

### Problema: "Cannot connect to Docker daemon"

```bash
# Iniciar servicio Docker
systemctl start docker

# Habilitar en boot
systemctl enable docker

# Verificar status
systemctl status docker
```

### Problema: "Port already in use"

```bash
# Ver qué proceso usa el puerto
netstat -tulpn | grep 3000

# Matar proceso
kill -9 <PID>

# O cambiar puerto en docker-compose.yml
# ports:
#   - "3001:3000"  # Host:Container
```

### Problema: "Prometheus no ve métricas Python"

```bash
# Verificar que apps Python están corriendo
ps aux | grep python

# Verificar puertos abiertos
netstat -tulpn | grep 800

# Probar endpoint manualmente
curl http://localhost:8000/metrics

# En Linux, usar host.docker.internal
# Ya está configurado en prometheus.yml
```

### Problema: "Grafana no muestra datos"

```bash
# 1. Verificar que Prometheus tiene datos
curl http://localhost:9090/api/v1/targets

# 2. Verificar datasource en Grafana
# Settings → Data Sources → Prometheus → Test

# 3. Ver logs de Grafana
docker-compose logs -f grafana

# 4. Verificar queries en Dashboard
# Edit panel → Ver query
```

---

## 📁 Estructura de Archivos Docker

```
concurrency_learning/
├── docker-compose.yml              # Orquestación de servicios
├── Dockerfile                      # Imagen Python (opcional)
├── .dockerignore                   # Archivos a ignorar
│
├── prometheus/
│   ├── prometheus.yml              # Config de Prometheus
│   ├── alerts.yml                  # Reglas de alertas
│   └── alertmanager.yml            # Config de Alertmanager
│
└── grafana/
    ├── provisioning/
    │   ├── datasources/
    │   │   └── datasource.yml      # Auto-config de Prometheus
    │   └── dashboards/
    │       └── dashboard.yml       # Auto-provision dashboards
    └── dashboards/
        └── dashboards.json         # Dashboard JSON
```

---

## 🎯 Configuración Avanzada

### Cambiar passwords

**Grafana** - Editar `docker-compose.yml`:
```yaml
environment:
  - GF_SECURITY_ADMIN_PASSWORD=tu_password_seguro
```

**Prometheus** - Habilitar autenticación básica:
```yaml
# Crear archivo web.yml
basic_auth_users:
  admin: $2y$10$... # bcrypt hash
```

### Persistencia de datos

Los datos se guardan en volúmenes Docker:
```bash
# Ver volúmenes
docker volume ls

# Inspeccionar volumen
docker volume inspect concurrency_learning_grafana_data

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

### Configurar alertas por email

Editar `prometheus/alertmanager.yml`:

```yaml
receivers:
  - name: 'email'
    email_configs:
      - to: 'tu-email@example.com'
        from: 'alertmanager@example.com'
        smarthost: smtp.gmail.com:587
        auth_username: 'tu-email@gmail.com'
        auth_password: 'tu-app-password'
```

### Configurar alertas por Slack

```yaml
receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
        title: '🚨 {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

---

## 🚀 Setup para Producción

### 1. Usar Docker Swarm o Kubernetes

```bash
# Inicializar Swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml monitoring
```

### 2. Configurar HTTPS con Nginx

```yaml
# Agregar a docker-compose.yml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
    - ./ssl:/etc/nginx/ssl
```

### 3. Límites de recursos

```yaml
# En docker-compose.yml
services:
  prometheus:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 4. Healthchecks

```yaml
services:
  grafana:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

---

## 📊 Monitoreo del Stack Docker

### Dashboard de Docker en Grafana

Importar dashboard oficial de Docker:
1. Grafana → Import → ID: `193`
2. Seleccionar datasource Prometheus
3. Import

### cAdvisor (Container Advisor)

Agregar a `docker-compose.yml`:

```yaml
cadvisor:
  image: gcr.io/cadvisor/cadvisor:latest
  container_name: cadvisor
  ports:
    - "8080:8080"
  volumes:
    - /:/rootfs:ro
    - /var/run:/var/run:ro
    - /sys:/sys:ro
    - /var/lib/docker/:/var/lib/docker:ro
  networks:
    - monitoring
```

Agregar a `prometheus/prometheus.yml`:

```yaml
- job_name: 'cadvisor'
  static_configs:
    - targets: ['cadvisor:8080']
```

---

## 🎓 Mejores Prácticas

### ✅ DO:
- Usar volúmenes para persistencia
- Configurar límites de recursos
- Hacer backups regulares
- Usar secrets para passwords
- Monitorear logs con `docker-compose logs`
- Actualizar imágenes regularmente

### ❌ DON'T:
- No usar `latest` tag en producción
- No exponer puertos innecesarios
- No correr como root si no es necesario
- No hardcodear passwords en docker-compose.yml
- No ignorar logs de errores

---

## 🔗 Links Útiles

- **Docker Compose Docs**: https://docs.docker.com/compose/
- **Prometheus Docker**: https://hub.docker.com/r/prom/prometheus
- **Grafana Docker**: https://hub.docker.com/r/grafana/grafana
- **Node Exporter**: https://github.com/prometheus/node_exporter

---

## 🎯 Quick Commands Cheatsheet

```bash
# Iniciar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Detener
docker-compose stop

# Eliminar
docker-compose down

# Ver stats
docker stats

# Entrar a contenedor
docker exec -it grafana /bin/bash

# Ver redes
docker network ls

# Ver volúmenes
docker volume ls

# Limpiar todo
docker system prune -a --volumes
```

---

**¡Todo listo con Docker! 🐳🎉**

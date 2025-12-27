#!/bin/bash
# Script para configurar Grafana automáticamente en Digital Ocean droplet

echo "=================================="
echo "Setup de Grafana + Prometheus"
echo "=================================="

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Instalar Prometheus
echo -e "${YELLOW}[1/5] Instalando Prometheus...${NC}"

cd /opt
wget -q https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xzf prometheus-2.45.0.linux-amd64.tar.gz
mv prometheus-2.45.0.linux-amd64 prometheus
cd prometheus

# Crear configuración de Prometheus
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 5s
  evaluation_interval: 5s
  external_labels:
    monitor: 'python-concurrency'

scrape_configs:
  - job_name: 'race_conditions'
    static_configs:
      - targets: ['localhost:8000']
        labels:
          module: 'race_conditions'
          app: 'python_concurrency'

  - job_name: 'locks'
    static_configs:
      - targets: ['localhost:8001']
        labels:
          module: 'locks'
          app: 'python_concurrency'

  - job_name: 'deadlocks'
    static_configs:
      - targets: ['localhost:8002']
        labels:
          module: 'deadlocks'
          app: 'python_concurrency'

  - job_name: 'cpu_monitor'
    static_configs:
      - targets: ['localhost:8000']
        labels:
          module: 'monitoring'
          app: 'python_concurrency'

# Alerting rules
rule_files:
  - 'alerts.yml'
EOF

# Crear reglas de alertas
cat > alerts.yml << 'EOF'
groups:
  - name: concurrency_alerts
    interval: 30s
    rules:
      # Alta tasa de race conditions
      - alert: HighRaceConditionRate
        expr: rate(race_conditions_detected_total[5m]) > 1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Alta tasa de race conditions"
          description: "{{ $value }} race conditions por segundo detectadas"

      # Deadlock detectado
      - alert: DeadlockDetected
        expr: increase(deadlocks_detected_total[1m]) > 0
        labels:
          severity: critical
        annotations:
          summary: "Deadlock detectado"
          description: "Se detectó un deadlock en el sistema"

      # Alta contención de locks
      - alert: HighLockContention
        expr: lock_contention_threads > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Alta contención en locks"
          description: "{{ $value }} threads esperando por locks"

      # Tiempo de espera excesivo
      - alert: ExcessiveLockWaitTime
        expr: histogram_quantile(0.95, rate(lock_wait_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Tiempo de espera excesivo"
          description: "P95 de espera: {{ $value }}s (umbral: 1s)"

      # CPU alta
      - alert: HighCPUUsage
        expr: cpu_usage_total > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Uso de CPU alto"
          description: "CPU usage: {{ $value }}%"

      # Memoria alta
      - alert: HighMemoryUsage
        expr: memory_usage_percent > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Uso de memoria alto"
          description: "Memoria usage: {{ $value }}%"
EOF

echo -e "${GREEN}✓ Prometheus configurado${NC}"

# 2. Crear servicio systemd para Prometheus
echo -e "${YELLOW}[2/5] Creando servicio systemd para Prometheus...${NC}"

cat > /etc/systemd/system/prometheus.service << 'EOF'
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=root
Group=root
Type=simple
ExecStart=/opt/prometheus/prometheus \
  --config.file=/opt/prometheus/prometheus.yml \
  --storage.tsdb.path=/opt/prometheus/data \
  --web.console.templates=/opt/prometheus/consoles \
  --web.console.libraries=/opt/prometheus/console_libraries

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable prometheus
systemctl start prometheus

echo -e "${GREEN}✓ Prometheus service creado y iniciado${NC}"
echo -e "   Prometheus UI: http://$(hostname -I | awk '{print $1}'):9090"

# 3. Instalar Grafana
echo -e "${YELLOW}[3/5] Instalando Grafana...${NC}"

apt-get install -y software-properties-common
wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -
add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
apt-get update
apt-get install -y grafana

echo -e "${GREEN}✓ Grafana instalado${NC}"

# 4. Configurar Grafana
echo -e "${YELLOW}[4/5] Configurando Grafana...${NC}"

# Iniciar Grafana
systemctl enable grafana-server
systemctl start grafana-server

# Esperar a que Grafana esté listo
sleep 10

# Configurar datasource de Prometheus via API
curl -X POST http://admin:admin@localhost:3000/api/datasources \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://localhost:9090",
    "access": "proxy",
    "isDefault": true
  }'

echo -e "${GREEN}✓ Grafana configurado${NC}"
echo -e "   Grafana UI: http://$(hostname -I | awk '{print $1}'):3000"
echo -e "   Usuario: admin / Contraseña: admin"

# 5. Configurar firewall
echo -e "${YELLOW}[5/5] Configurando firewall...${NC}"

# Asegurar que ufw está instalado
if ! command -v ufw &> /dev/null; then
    apt-get install -y ufw
fi

# Permitir puertos necesarios
ufw allow 22/tcp    # SSH
ufw allow 3000/tcp  # Grafana
ufw allow 9090/tcp  # Prometheus
ufw allow 8000:8002/tcp  # Python metrics exporters

# No habilitar ufw automáticamente para evitar bloquear SSH
echo -e "${YELLOW}⚠️  Firewall configurado pero NO habilitado${NC}"
echo -e "   Para habilitar: sudo ufw enable"

echo ""
echo -e "${GREEN}=================================="
echo "✓ Setup completado"
echo "==================================${NC}"
echo ""
echo "Servicios disponibles:"
echo "  - Prometheus: http://$(hostname -I | awk '{print $1}'):9090"
echo "  - Grafana:    http://$(hostname -I | awk '{print $1}'):3000 (admin/admin)"
echo ""
echo "Próximos pasos:"
echo "  1. Acceder a Grafana"
echo "  2. Importar dashboard desde grafana/dashboards.json"
echo "  3. Ejecutar scripts de Python para generar métricas"
echo ""
echo "Comandos útiles:"
echo "  sudo systemctl status prometheus"
echo "  sudo systemctl status grafana-server"
echo "  sudo journalctl -u prometheus -f"
echo "  sudo journalctl -u grafana-server -f"
echo ""

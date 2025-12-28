# 📊 Guía de Grafana para Monitoreo de ML

## 🎯 Introducción

Esta guía te ayudará a usar Grafana para monitorear tu sistema de detección de fraude y modelos de Machine Learning.

---

## 🚀 Acceso a Grafana

### 1. Iniciar Servicios

```bash
# Iniciar todos los servicios (incluido Grafana)
docker-compose up -d

# O usar el Makefile
make start
```

### 2. Acceder a la Interfaz

```
URL: http://localhost:3000
Usuario: admin
Contraseña: admin
```

**Nota**: En el primer acceso, Grafana puede pedirte cambiar la contraseña. Puedes omitir este paso para desarrollo.

---

## 📊 Dashboards Pre-configurados

El proyecto incluye 2 dashboards listos para usar:

### 1. **Fraud Detection Overview** (`fraud_overview`)

**Propósito**: Monitorear transacciones en tiempo real

**Paneles incluidos**:
- Total Transactions (stat)
- Fraud Transactions (stat)
- Fraud Rate % (stat)
- Avg Transaction Amount (stat)
- Transactions Over Time (timeseries)
- Transactions by Category (piechart)
- Fraud vs Normal by Hour (timeseries)

**Refresh**: Cada 5 segundos

**Acceso**:
- Dashboard → Fraud Detection Overview
- URL: http://localhost:3000/d/fraud_overview

### 2. **Model Performance Monitoring** (`model_performance`)

**Propósito**: Seguimiento de métricas de modelos ML

**Paneles incluidos**:
- Model Metrics Over Time (accuracy, precision, recall, F1)
- Current Accuracy (gauge)
- Current F1 Score (gauge)
- True Positives (stat)
- False Positives (stat)
- Precision vs Recall (timeseries)
- Confusion Matrix Components (stacked bars)

**Refresh**: Cada 30 segundos

**Acceso**:
- Dashboard → Model Performance Monitoring
- URL: http://localhost:3000/d/model_performance

---

## 🗄️ Datasource Configurado

### PostgreSQL Connection

**Configuración automática**:
```yaml
Name: PostgreSQL
Type: postgres
Host: postgres:5432
Database: spark_ml_db
User: spark_user
Password: spark_password
```

**Verificar conexión**:
1. Configuration (⚙️) → Data Sources
2. Click en "PostgreSQL"
3. Scroll down → "Save & Test"
4. Deberías ver: "Database Connection OK"

---

## 📈 Crear Dashboard Personalizado

### Paso 1: Crear Nuevo Dashboard

```
1. Click en "+" en sidebar izquierdo
2. Seleccionar "Dashboard"
3. Click en "Add new panel"
```

### Paso 2: Configurar Query

**Ejemplo - Total de Transacciones**:

```sql
-- En el editor de Query
SELECT COUNT(*) as "Total Transactions"
FROM transactions_raw;
```

**Configuración**:
- Format: Table
- Datasource: PostgreSQL

### Paso 3: Configurar Visualización

**Panel Type**: Stat (para métricas simples)

**Field Options**:
- Unit: `short` (para números enteros)
- Color mode: `value`
- Graph mode: `area`

### Paso 4: Guardar Panel

```
1. Click en "Apply" (esquina superior derecha)
2. Click en "Save dashboard" (icono de disquete)
3. Dar nombre al dashboard
4. Click en "Save"
```

---

## 🔍 Ejemplos de Queries Útiles

### 1. Transacciones por Día

```sql
SELECT
    DATE(timestamp) as time,
    COUNT(*) as count
FROM transactions_raw
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY DATE(timestamp)
ORDER BY time;
```

**Panel Type**: Time series
**Format**: Time series

### 2. Fraud Rate por Categoría

```sql
SELECT
    merchant_category,
    (COUNT(*) FILTER (WHERE is_fraud = 1)::float /
     COUNT(*)::float * 100) as fraud_rate
FROM transactions_raw
GROUP BY merchant_category
ORDER BY fraud_rate DESC;
```

**Panel Type**: Bar chart
**Format**: Table

### 3. Top 10 Montos Fraudulentos

```sql
SELECT
    transaction_id,
    amount,
    merchant_category,
    timestamp
FROM transactions_raw
WHERE is_fraud = 1
ORDER BY amount DESC
LIMIT 10;
```

**Panel Type**: Table
**Format**: Table

### 4. Métricas de Modelo Actual

```sql
SELECT
    model_name,
    accuracy,
    precision,
    recall,
    f1_score,
    created_at
FROM model_metrics
ORDER BY created_at DESC
LIMIT 1;
```

**Panel Type**: Stat (multiple values)
**Format**: Table

### 5. Evolución de F1 Score

```sql
SELECT
    created_at as time,
    f1_score
FROM model_metrics
WHERE created_at >= NOW() - INTERVAL '30 days'
ORDER BY created_at;
```

**Panel Type**: Time series
**Format**: Time series

### 6. Distribución de Transacciones por Hora

```sql
SELECT
    transaction_hour,
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE is_fraud = 1) as fraud_count
FROM transactions_raw
GROUP BY transaction_hour
ORDER BY transaction_hour;
```

**Panel Type**: Bar gauge
**Format**: Table

---

## 🎨 Tipos de Visualizaciones

### 1. **Stat** - Métricas Simples

**Cuándo usar**: Mostrar un único valor o conjunto pequeño de valores
**Ejemplos**: Total transactions, Fraud rate, Current accuracy

**Configuración recomendada**:
```
Color mode: value
Graph mode: area
Orientation: auto
```

### 2. **Time Series** - Series Temporales

**Cuándo usar**: Mostrar tendencias en el tiempo
**Ejemplos**: Transacciones por día, métricas de modelo

**Configuración recomendada**:
```
Draw style: line
Fill opacity: 10
Line interpolation: smooth
Show points: auto
```

### 3. **Gauge** - Medidores

**Cuándo usar**: Mostrar valor actual con umbrales
**Ejemplos**: Accuracy, F1 score

**Configuración recomendada**:
```
Thresholds:
  - Red: 0 - 0.80
  - Yellow: 0.80 - 0.90
  - Green: 0.90 - 1.0
```

### 4. **Bar Chart** - Gráficos de Barras

**Cuándo usar**: Comparar categorías
**Ejemplos**: Transacciones por categoría, fraude por región

**Configuración recomendada**:
```
Orientation: auto
Display mode: gradient
```

### 5. **Pie Chart** - Gráficos Circulares

**Cuándo usar**: Mostrar proporciones
**Ejemplos**: Distribución de categorías, fraude vs normal

**Configuración recomendada**:
```
Pie type: pie (o donut)
Legend: right
```

### 6. **Table** - Tablas

**Cuándo usar**: Mostrar datos detallados
**Ejemplos**: Top transacciones, lista de alertas

**Configuración recomendada**:
```
Show header: true
Column alignment: auto
Enable sorting: true
```

---

## ⚙️ Configuraciones Avanzadas

### 1. Variables de Dashboard

**Crear variable de tiempo**:

```
1. Dashboard settings (⚙️) → Variables
2. Add variable
3. Name: time_range
4. Type: Interval
5. Values: 1h,6h,12h,1d,7d,30d
```

**Usar en query**:
```sql
SELECT * FROM transactions_raw
WHERE timestamp >= NOW() - INTERVAL '$time_range';
```

### 2. Alertas

**Configurar alerta (Grafana 8.0+)**:

```
1. Edit panel
2. Alert tab
3. Create Alert Rule
4. Condition: avg() OF query(A, 5m, now) IS ABOVE 10
5. Evaluate every: 1m
6. For: 5m
7. Notifications: Email/Slack
```

**Ejemplo - Alerta de Fraud Rate Alto**:

```sql
SELECT
    (COUNT(*) FILTER (WHERE is_fraud = 1)::float /
     COUNT(*)::float * 100) as fraud_rate
FROM transactions_raw
WHERE timestamp >= NOW() - INTERVAL '5 minutes';
```

**Condition**: `fraud_rate > 5.0`

### 3. Refresh Automático

**Configurar**:
```
1. Dashboard settings (⚙️)
2. Time options
3. Auto refresh: 5s, 10s, 30s, 1m, 5m, 15m, 30m, 1h
```

**Recomendaciones**:
- Datos en tiempo real: 5s - 10s
- Métricas de modelo: 30s - 1m
- Dashboards históricos: 5m - 15m

### 4. Anotaciones

**Marcar eventos importantes**:

```sql
-- Crear tabla de eventos
CREATE TABLE ml_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50),
    description TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Query para anotaciones
SELECT
    timestamp as time,
    description as text,
    event_type as tags
FROM ml_events
WHERE timestamp >= $__timeFrom()
  AND timestamp <= $__timeTo();
```

**Configurar en Grafana**:
```
1. Dashboard settings → Annotations
2. Add annotation query
3. Datasource: PostgreSQL
4. Query: [query de arriba]
```

---

## 🔧 Troubleshooting

### Problema 1: "Database Connection Failed"

**Solución**:
```bash
# Verificar que PostgreSQL está corriendo
docker-compose ps postgres

# Ver logs de PostgreSQL
docker-compose logs postgres

# Reiniciar servicios
docker-compose restart postgres grafana
```

### Problema 2: "No data in dashboard"

**Verificar**:
```bash
# Conectar a PostgreSQL
docker exec -it spark_postgres psql -U spark_user -d spark_ml_db

# Verificar datos
SELECT COUNT(*) FROM transactions_raw;
SELECT COUNT(*) FROM model_metrics;
```

**Solución**:
```bash
# Ejecutar notebook 08 para generar datos
jupyter notebook notebooks/08_proyecto_final_integracion.ipynb
```

### Problema 3: "Panel rendering error"

**Solución**:
- Verificar formato de query (time_series vs table)
- Asegurarse de usar nombres de columna correctos
- Verificar que la query retorna datos
- Revisar logs de Grafana: `docker-compose logs grafana`

### Problema 4: Grafana no carga

**Solución**:
```bash
# Verificar puerto 3000 no está en uso
lsof -i :3000

# Reiniciar Grafana
docker-compose restart grafana

# Ver logs
docker-compose logs -f grafana
```

---

## 📊 Best Practices

### 1. Organización de Dashboards

```
📁 Production Monitoring/
  ├─ Fraud Detection Overview
  ├─ Model Performance
  └─ System Health

📁 Development/
  ├─ Experiment Tracking
  ├─ Data Quality
  └─ Performance Testing
```

### 2. Naming Conventions

**Dashboards**:
- Descriptivos: "Fraud Detection Overview"
- No usar abreviaciones confusas

**Panels**:
- Concisos pero claros: "Total Transactions"
- Incluir unidades: "Avg Amount (USD)"

**Queries**:
- Comentar queries complejas
- Usar alias descriptivos: `as "Total Count"`

### 3. Performance

**Optimizaciones**:
```sql
-- ❌ Malo: Full table scan
SELECT * FROM transactions_raw;

-- ✅ Bueno: Filtrado y límite
SELECT * FROM transactions_raw
WHERE timestamp >= NOW() - INTERVAL '1 hour'
LIMIT 1000;

-- ✅ Mejor: Agregación
SELECT
    DATE_TRUNC('hour', timestamp) as time,
    COUNT(*) as count
FROM transactions_raw
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY time
ORDER BY time;
```

### 4. Umbrales de Color

**Métricas de modelo** (accuracy, F1, etc.):
```
🔴 Red:    0.00 - 0.80 (Poor)
🟡 Yellow: 0.80 - 0.90 (Good)
🟢 Green:  0.90 - 1.00 (Excellent)
```

**Fraud rate**:
```
🟢 Green:  0.0 - 3.0  (Normal)
🟡 Yellow: 3.0 - 5.0  (Warning)
🔴 Red:    5.0+       (Critical)
```

### 5. Documentación

**En cada panel**:
- Descripción clara del panel
- Explicación de la métrica
- Umbrales y su significado
- Acciones a tomar si hay alertas

---

## 🎯 Casos de Uso

### Caso 1: Monitoreo en Tiempo Real

**Objetivo**: Detectar fraude inmediatamente

**Setup**:
1. Dashboard: Fraud Detection Overview
2. Refresh: 5s
3. Alertas configuradas para fraud_rate > 5%
4. Notificaciones a Slack/Email

### Caso 2: Evaluación de Modelo

**Objetivo**: Verificar performance después de re-entrenar

**Setup**:
1. Dashboard: Model Performance
2. Refresh: 30s
3. Comparar métricas con baseline
4. Verificar no hay degradación

### Caso 3: Análisis Histórico

**Objetivo**: Identificar patrones de fraude

**Setup**:
1. Time range: Last 30 days
2. Refresh: 15m (no crítico)
3. Análisis por categoría, hora, día de semana
4. Exportar datos para análisis profundo

### Caso 4: Debugging

**Objetivo**: Investigar anomalías

**Setup**:
1. Tabla con transacciones sospechosas
2. Filtros por categoría, monto, ubicación
3. Links a logs y trazas
4. Timeline de eventos

---

## 📚 Recursos Adicionales

### Documentación Oficial

- [Grafana Documentation](https://grafana.com/docs/)
- [PostgreSQL Datasource](https://grafana.com/docs/grafana/latest/datasources/postgres/)
- [Dashboard Best Practices](https://grafana.com/docs/grafana/latest/best-practices/)

### Ejemplos de Dashboards

- [Grafana Dashboard Library](https://grafana.com/grafana/dashboards/)
- Buscar: "PostgreSQL", "Machine Learning", "Monitoring"

### Plugins Útiles

```bash
# Instalar desde Grafana UI
Configuration → Plugins → [Search]

# Plugins recomendados:
- Clock Panel
- Pie Chart (legacy)
- Plotly Panel
- FlowCharting
```

---

## 🚀 Siguiente Nivel

### 1. Integración con MLflow

**Idea**: Crear dashboard que muestre experimentos de MLflow

```sql
-- Conectar a MLflow database
-- Query de ejemplo:
SELECT
    experiment_id,
    metric_key,
    metric_value,
    timestamp
FROM metrics
WHERE experiment_id = 1
ORDER BY timestamp;
```

### 2. Streaming con Kafka

**Idea**: Dashboard de datos en tiempo real desde Kafka

Requiere:
- Kafka Connect + PostgreSQL Sink
- Streaming pipeline
- Dashboard con latencia sub-segundo

### 3. Multi-datasource

**Idea**: Combinar PostgreSQL + Prometheus + Loki

Dashboards que muestren:
- Datos de negocio (PostgreSQL)
- Métricas de infraestructura (Prometheus)
- Logs de aplicación (Loki)

---

## 📋 Checklist de Dashboard

Antes de poner en producción:

- [ ] Todas las queries están optimizadas
- [ ] Hay índices en columnas de timestamp
- [ ] Refresh rate es apropiado
- [ ] Alertas configuradas y probadas
- [ ] Notificaciones funcionan
- [ ] Dashboard tiene descripción
- [ ] Paneles tienen tooltips explicativos
- [ ] Umbrales de color están bien definidos
- [ ] Permisos configurados correctamente
- [ ] Dashboard está versionado (export JSON)
- [ ] Documentación actualizada

---

## 🎉 Conclusión

Ahora tienes las herramientas para:
- ✅ Monitorear transacciones en tiempo real
- ✅ Seguir performance de modelos ML
- ✅ Crear dashboards personalizados
- ✅ Configurar alertas efectivas
- ✅ Optimizar queries para performance
- ✅ Aplicar best practices de visualización

**Siguiente paso**: Ejecuta el notebook 08, genera datos, y explora los dashboards!

```bash
# Start everything
make init

# Open Grafana
open http://localhost:3000

# Login: admin/admin

# Explore dashboards!
```

---

**Happy Monitoring! 📊✨**

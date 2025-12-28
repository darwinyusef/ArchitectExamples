# 📊 Configuración de Grafana - Resumen

## ✅ Componentes Instalados

### 1. Servicio Grafana en Docker Compose

**Archivo**: `docker-compose.yml`

```yaml
grafana:
  image: grafana/grafana:latest
  container_name: spark_grafana
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=admin
    - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource,grafana-piechart-panel
  volumes:
    - grafana_data:/var/lib/grafana
    - ./grafana/provisioning:/etc/grafana/provisioning
    - ./grafana/dashboards:/var/lib/grafana/dashboards
```

### 2. Datasource PostgreSQL

**Archivo**: `grafana/provisioning/datasources/postgres.yml`

- Conexión automática a PostgreSQL
- Base de datos: `spark_ml_db`
- Usuario: `spark_user`

### 3. Provisioning de Dashboards

**Archivo**: `grafana/provisioning/dashboards/dashboard.yml`

- Auto-carga dashboards desde `/var/lib/grafana/dashboards`
- Actualización cada 10 segundos
- Permite edición desde UI

### 4. Dashboard: Fraud Detection Overview

**Archivo**: `grafana/dashboards/fraud_detection_overview.json`

**Paneles (8 total)**:
1. Total Transactions (stat)
2. Fraud Transactions (stat)
3. Fraud Rate % (stat)
4. Avg Transaction Amount (stat)
5. Transactions Over Time (timeseries)
6. Transactions by Category (piechart)
7. Fraud vs Normal by Hour (timeseries stacked)

**Características**:
- Refresh: 5 segundos
- Time range: Last 6 hours
- UID: `fraud_overview`

**Queries**:
```sql
-- Total Transactions
SELECT COUNT(*) as "Total Transactions" FROM transactions_raw;

-- Fraud Count
SELECT COUNT(*) as "Fraud Count" FROM transactions_raw WHERE is_fraud = 1;

-- Fraud Rate
SELECT (COUNT(*) FILTER (WHERE is_fraud = 1)::float / COUNT(*)::float * 100) as "Fraud Rate" FROM transactions_raw;

-- Transactions Over Time
SELECT timestamp as time, COUNT(*) FROM transactions_raw GROUP BY timestamp ORDER BY timestamp;

-- By Category
SELECT merchant_category, COUNT(*) as count FROM transactions_raw GROUP BY merchant_category;

-- Fraud vs Normal by Hour
SELECT transaction_hour as time,
       COUNT(*) FILTER (WHERE is_fraud = 0) as "Normal",
       COUNT(*) FILTER (WHERE is_fraud = 1) as "Fraud"
FROM transactions_raw
GROUP BY transaction_hour
ORDER BY transaction_hour;
```

### 5. Dashboard: Model Performance Monitoring

**Archivo**: `grafana/dashboards/model_performance.json`

**Paneles (8 total)**:
1. Model Metrics Over Time (timeseries - accuracy, precision, recall, F1)
2. Current Accuracy (gauge)
3. Current F1 Score (gauge)
4. True Positives (stat)
5. False Positives (stat)
6. Precision vs Recall (timeseries)
7. Confusion Matrix Components (timeseries stacked bars)

**Características**:
- Refresh: 30 segundos
- Time range: Last 24 hours
- UID: `model_performance`

**Queries**:
```sql
-- Model Metrics
SELECT created_at as time, accuracy, precision, recall, f1_score
FROM model_metrics
ORDER BY created_at;

-- Current Accuracy
SELECT accuracy FROM model_metrics ORDER BY created_at DESC LIMIT 1;

-- Confusion Matrix Components
SELECT created_at as time, true_positives, false_positives, false_negatives
FROM model_metrics
ORDER BY created_at;
```

### 6. Guía de Usuario

**Archivo**: `GRAFANA_GUIDE.md`

**Contenido**:
- Instrucciones de acceso
- Descripción de dashboards
- Ejemplos de queries útiles
- Tipos de visualizaciones
- Configuraciones avanzadas (alertas, variables, anotaciones)
- Troubleshooting
- Best practices

---

## 🚀 Inicio Rápido

### 1. Levantar Servicios

```bash
# Iniciar todos los servicios
docker-compose up -d

# Verificar que Grafana está corriendo
docker-compose ps grafana

# Ver logs
docker-compose logs -f grafana
```

### 2. Acceder a Grafana

```
URL: http://localhost:3000
Usuario: admin
Contraseña: admin
```

### 3. Verificar Datasource

1. Ir a Configuration (⚙️) → Data Sources
2. Click en "PostgreSQL"
3. Scroll down → Click "Save & Test"
4. Deberías ver: "Database Connection OK" ✅

### 4. Ver Dashboards

**Opción 1: Desde el menú**
1. Click en Dashboards (⧉) en sidebar
2. Verás:
   - Fraud Detection Overview
   - Model Performance Monitoring

**Opción 2: URLs directas**
- http://localhost:3000/d/fraud_overview
- http://localhost:3000/d/model_performance

### 5. Generar Datos

Para que los dashboards muestren datos, ejecuta el notebook 08:

```bash
# Iniciar Jupyter
jupyter notebook

# Abrir y ejecutar
notebooks/08_proyecto_final_integracion.ipynb
```

Este notebook:
1. Genera 100,000 transacciones
2. Guarda en PostgreSQL (`transactions_raw`)
3. Entrena modelos
4. Guarda métricas en PostgreSQL (`model_metrics`)

---

## 📊 Estructura de Datos

### Tabla: `transactions_raw`

Columnas usadas en dashboards:
- `timestamp` - Fecha/hora de transacción
- `transaction_hour` - Hora del día (0-23)
- `amount` - Monto de transacción
- `merchant_category` - Categoría del comercio
- `is_fraud` - 0 (normal) o 1 (fraude)

### Tabla: `model_metrics`

Columnas usadas en dashboards:
- `created_at` - Timestamp de evaluación
- `model_name` - Nombre del modelo
- `accuracy` - Exactitud del modelo
- `precision` - Precisión
- `recall` - Recall
- `f1_score` - F1 Score
- `true_positives` - TP
- `false_positives` - FP
- `false_negatives` - FN

---

## 🎨 Personalización

### Crear Nuevo Panel

1. Ir a dashboard
2. Click en "Add panel" (arriba a la derecha)
3. Configurar query en PostgreSQL
4. Seleccionar tipo de visualización
5. Click en "Apply"

### Modificar Dashboard Existente

1. Abrir dashboard
2. Click en ⚙️ (settings) arriba a la derecha
3. Enable edit mode
4. Click en título del panel → Edit
5. Hacer cambios
6. Click "Apply"
7. Save dashboard (icono disquete)

### Agregar Alertas

1. Edit panel
2. Alert tab
3. Create Alert Rule
4. Configurar condición
5. Configurar notificaciones (Email, Slack, etc.)

---

## 🔍 Queries Útiles Adicionales

### Transacciones de Alto Riesgo

```sql
SELECT
    transaction_id,
    amount,
    merchant_category,
    timestamp,
    is_fraud
FROM transactions_raw
WHERE amount > 1000
   OR is_international = 1
ORDER BY timestamp DESC
LIMIT 100;
```

### Distribución de Fraude por País

```sql
SELECT
    location,
    COUNT(*) as total_transactions,
    COUNT(*) FILTER (WHERE is_fraud = 1) as fraud_count,
    (COUNT(*) FILTER (WHERE is_fraud = 1)::float / COUNT(*)::float * 100) as fraud_rate
FROM transactions_raw
GROUP BY location
ORDER BY fraud_rate DESC;
```

### Performance de Modelos Comparado

```sql
SELECT
    model_name,
    AVG(accuracy) as avg_accuracy,
    AVG(f1_score) as avg_f1,
    MAX(created_at) as last_update
FROM model_metrics
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY model_name
ORDER BY avg_f1 DESC;
```

---

## 📈 Métricas Recomendadas

### Para Negocio

- **Total Transactions**: Volumen de operaciones
- **Fraud Rate %**: Tasa de fraude (objetivo: < 3%)
- **Average Transaction Amount**: Monto promedio
- **Transactions by Category**: Distribución por categoría

### Para Data Science

- **Model Accuracy**: Exactitud del modelo (objetivo: > 95%)
- **F1 Score**: Balance precision/recall (objetivo: > 0.90)
- **Precision**: Porcentaje de predicciones correctas de fraude
- **Recall**: Porcentaje de fraudes detectados

### Para DevOps

- **Query Performance**: Tiempo de respuesta de queries
- **Data Freshness**: Última actualización de datos
- **System Health**: Estado de servicios
- **Alert Status**: Alertas activas

---

## 🛠️ Troubleshooting

### Dashboard en blanco

**Causa**: No hay datos en PostgreSQL

**Solución**:
```bash
# Verificar datos
docker exec -it spark_postgres psql -U spark_user -d spark_ml_db -c "SELECT COUNT(*) FROM transactions_raw;"

# Si retorna 0, ejecutar notebook 08
jupyter notebook notebooks/08_proyecto_final_integracion.ipynb
```

### "Database Connection Failed"

**Causa**: PostgreSQL no está corriendo o credenciales incorrectas

**Solución**:
```bash
# Verificar PostgreSQL
docker-compose ps postgres

# Reiniciar
docker-compose restart postgres grafana
```

### Queries lentas

**Causa**: Falta índice en columnas

**Solución**:
```sql
-- Crear índices
CREATE INDEX idx_timestamp ON transactions_raw(timestamp);
CREATE INDEX idx_is_fraud ON transactions_raw(is_fraud);
CREATE INDEX idx_created_at ON model_metrics(created_at);
```

### Grafana no carga

**Causa**: Puerto 3000 en uso o servicio no corriendo

**Solución**:
```bash
# Verificar puerto
lsof -i :3000

# Ver logs
docker-compose logs grafana

# Reiniciar
docker-compose restart grafana
```

---

## 📝 Checklist de Verificación

Antes de usar en producción:

- [x] Grafana corriendo en http://localhost:3000
- [x] Login funciona (admin/admin)
- [x] Datasource PostgreSQL conectado
- [x] Dashboard "Fraud Detection Overview" visible
- [x] Dashboard "Model Performance Monitoring" visible
- [ ] Datos visibles en todos los paneles
- [ ] Refresh automático funcionando
- [ ] Queries optimizadas con índices
- [ ] Alertas configuradas
- [ ] Notificaciones probadas
- [ ] Documentación revisada

---

## 🎯 Próximos Pasos

### Nivel 1: Básico
1. Explorar dashboards pre-configurados
2. Generar datos con notebook 08
3. Familiarizarse con queries SQL

### Nivel 2: Intermedio
1. Crear paneles personalizados
2. Configurar alertas
3. Modificar umbrales de color

### Nivel 3: Avanzado
1. Crear dashboard de sistema completo
2. Integrar con múltiples datasources
3. Implementar anotaciones de eventos
4. Configurar variables de dashboard

---

## 📚 Documentación

- **Guía Completa**: [GRAFANA_GUIDE.md](GRAFANA_GUIDE.md)
- **Proyecto Final**: [PROYECTO_FINAL.md](PROYECTO_FINAL.md)
- **Notebook 08**: [notebooks/08_proyecto_final_integracion.ipynb](notebooks/08_proyecto_final_integracion.ipynb)
- **README Principal**: [README.md](README.md)

---

## 🎉 Resumen

Has añadido exitosamente:

✅ **Servicio Grafana** en Docker Compose
✅ **Datasource PostgreSQL** auto-configurado
✅ **2 Dashboards** pre-construidos
✅ **8 Paneles** en Fraud Detection Overview
✅ **8 Paneles** en Model Performance Monitoring
✅ **Guía completa** de uso (GRAFANA_GUIDE.md)
✅ **Documentación** actualizada

**Total archivos creados/modificados**: 7

---

**Happy Monitoring! 📊✨**

**Siguiente**: Ejecuta `make init` y abre http://localhost:3000

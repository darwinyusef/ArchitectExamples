# 🎯 Proyecto Final: Sistema de Detección de Fraude End-to-End

## Descripción General

Sistema completo de detección de fraude en transacciones bancarias que integra todas las tecnologías del stack moderno de MLOps y Data Engineering.

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    SISTEMA DE DETECCIÓN DE FRAUDE                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│  │PostgreSQL│───>│  Spark   │───>│ Parquet  │───>│  MLflow  │ │
│  │  (Raw)   │    │Transform │    │ Storage  │    │ Tracking │ │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
│       │                │                                 │       │
│       │                ▼                                 │       │
│       │         ┌──────────┐                            │       │
│       │         │  SciPy   │                            │       │
│       │         │Statistics│                            │       │
│       │         └──────────┘                            │       │
│       │                │                                 │       │
│       │                ▼                                 ▼       │
│       │         ┌──────────┐                     ┌──────────┐  │
│       │         │ Sklearn  │────────────────────>│  Model   │  │
│       │         │ Training │                     │ Registry │  │
│       │         └──────────┘                     └──────────┘  │
│       │                │                                 │       │
│       │                ▼                                 │       │
│       │         ┌──────────┐                            │       │
│       │         │Matplotlib│                            │       │
│       │         │ Seaborn  │                            │       │
│       │         └──────────┘                            │       │
│       │                                                  │       │
│       ▼                                                  ▼       │
│  ┌──────────┐                                    ┌──────────┐  │
│  │PostgreSQL│<───────────────────────────────────│Prediction│  │
│  │(Results) │                                    │ Service  │  │
│  └──────────┘                                    └──────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                    Orquestado por Apache Airflow
```

---

## 📊 Stack Tecnológico

| Componente | Tecnología | Propósito |
|-----------|------------|-----------|
| **Procesamiento** | Apache Spark 3.5.0 | Procesamiento distribuido de datos |
| **Orquestación** | Apache Airflow 2.8.0 | Automatización de pipelines |
| **ML Tracking** | MLflow 2.9.2 | Gestión de experimentos y modelos |
| **ML Framework** | Scikit-learn 1.3.2 | Entrenamiento de modelos |
| **Estadística** | SciPy 1.11.4 | Análisis estadístico |
| **Almacenamiento** | PostgreSQL 15 | Base de datos relacional |
| **Formato Datos** | Apache Parquet | Almacenamiento columnar eficiente |
| **Visualización** | Matplotlib, Seaborn | Gráficos y reportes |
| **Monitoreo** | Grafana 10.x | Dashboards en tiempo real |
| **MLOps** | MLflow + Airflow | Ciclo de vida ML en producción |

---

## 🎓 Conceptos Integrados

### 1. **Data Engineering**
- ✅ Ingesta de datos desde múltiples fuentes
- ✅ Transformaciones con Spark
- ✅ Almacenamiento eficiente con Parquet
- ✅ Persistencia en PostgreSQL

### 2. **Feature Engineering**
- ✅ Creación de features derivadas
- ✅ Encoding de variables categóricas
- ✅ Normalización con StandardScaler
- ✅ Feature selection

### 3. **Machine Learning**
- ✅ Entrenamiento de múltiples modelos
- ✅ Comparación y selección del mejor
- ✅ Evaluación con métricas apropiadas
- ✅ Manejo de datos desbalanceados

### 4. **MLOps**
- ✅ Tracking de experimentos con MLflow
- ✅ Versionado de modelos
- ✅ Model Registry
- ✅ Automatización con Airflow
- ✅ Monitoring y alertas

### 5. **Análisis Estadístico**
- ✅ Tests de normalidad (Shapiro-Wilk)
- ✅ Tests de hipótesis (t-test)
- ✅ Análisis de distribuciones
- ✅ Correlaciones

### 6. **Visualización**
- ✅ Distribuciones de datos
- ✅ Confusion Matrix
- ✅ ROC y Precision-Recall curves
- ✅ Feature importance
- ✅ Comparación de modelos

---

## 📝 Pasos del Proyecto

### **PASO 1: Setup e Inicialización** ✅
- Configurar Spark, MLflow, PostgreSQL
- Crear estructura de directorios
- Verificar conexiones

### **PASO 2: Generación de Datos** ✅
- 100,000 transacciones sintéticas
- 5% de fraudes (desbalanceado)
- Patrones realistas de fraude

### **PASO 3: Almacenamiento PostgreSQL** ✅
- Guardar datos raw en base de datos
- Crear tablas necesarias
- Verificar integridad

### **PASO 4: Procesamiento con Spark y Parquet** ✅
- Convertir a Spark DataFrame
- Guardar en formato Parquet
- Optimizar particionamiento

### **PASO 5: Análisis Exploratorio (EDA)** ✅
- Estadísticas descriptivas
- Tests estadísticos con SciPy
- Visualizaciones con Matplotlib/Seaborn
- Tracking en MLflow

### **PASO 6: Feature Engineering** ✅
- Crear 7 nuevas features
- Encoding categórico
- Cálculo de risk score
- Guardar en Parquet

### **PASO 7: Preparación para ML** ✅
- Vector assembler
- StandardScaler
- Train/test split (80/20)
- Conversión a NumPy arrays

### **PASO 8: Entrenamiento de Modelos** ✅
- RandomForest
- GradientBoosting
- LogisticRegression
- Tracking completo en MLflow

### **PASO 9: Comparación de Modelos** ✅
- Métricas de evaluación
- Visualización comparativa
- Selección del mejor modelo

### **PASO 10: Evaluación Detallada** ✅
- Classification report
- Confusion matrix
- ROC y PR curves
- Feature importance

### **PASO 11: Guardar Resultados** ✅
- Predicciones en PostgreSQL
- Métricas de modelos
- Versionado de resultados

### **PASO 12: Resumen y MLOps** ✅
- Resumen ejecutivo
- Próximos pasos
- Deployment plan

### **PASO 13: Automatización con Airflow** ✅
- DAG completo
- Tasks bien definidas
- Manejo de errores
- Alertas automáticas

---

## 🚀 Cómo Ejecutar el Proyecto

### Opción 1: Notebook Completo

```bash
# 1. Iniciar servicios
docker-compose up -d

# 2. Abrir Jupyter
jupyter notebook

# 3. Ejecutar notebook
# notebooks/08_proyecto_final_integracion.ipynb
```

### Opción 2: Pipeline con Airflow

```bash
# 1. Iniciar Airflow
docker-compose up -d

# 2. Acceder a Airflow UI
# http://localhost:8080

# 3. Activar DAG
# fraud_detection_pipeline

# 4. Trigger manual o esperar schedule
```

### Opción 3: Paso a Paso

```bash
# 1. Setup
make init

# 2. Ejecutar notebook paso a paso
jupyter notebook notebooks/08_proyecto_final_integracion.ipynb

# 3. Ver resultados en MLflow
# http://localhost:5000

# 4. Verificar PostgreSQL
make db-connect
```

---

## 📈 Resultados Esperados

### Métricas del Modelo
- **Accuracy**: > 0.95
- **Precision**: > 0.85
- **Recall**: > 0.75
- **F1-Score**: > 0.80
- **AUC-ROC**: > 0.90

### Performance del Sistema
- **Procesamiento**: 100K transacciones en < 2 min
- **Entrenamiento**: 3 modelos en < 5 min
- **Inferencia**: < 100ms por transacción

### Almacenamiento
- **Parquet**: ~50% reducción vs CSV
- **PostgreSQL**: Indexado para queries rápidas
- **MLflow**: Todos los artifacts trackeados

---

## 🔧 Archivos Generados

```
proyecto-final/
├── data/
│   ├── raw/                      # Datos originales
│   ├── processed/                # Datos procesados
│   └── parquet/                  # Formato Parquet
│       ├── transactions/
│       └── transactions_featured/
│
├── visualizations/
│   ├── 01_eda_distributions.png
│   ├── 04_model_comparison.png
│   ├── 05_confusion_matrix.png
│   ├── 05_roc_pr_curves.png
│   └── 05_feature_importance.png
│
├── models/
│   ├── classification_report.txt
│   └── feature_importance.csv
│
└── airflow/
    └── dags/
        └── fraud_detection_pipeline.py
```

---

## 📊 Visualizaciones Clave

### 1. Distribución de Datos
- Histogramas de montos
- Distribución por hora del día
- Distancia desde casa
- Categorías de comercios

### 2. Métricas de Modelos
- Barras de comparación
- Métricas por modelo
- Tiempos de entrenamiento

### 3. Evaluación de Clasificación
- Confusion Matrix (absoluta y normalizada)
- Curvas ROC y Precision-Recall
- Feature importance con cumulative

---

## 🎯 Casos de Uso en Producción

### 1. **Detección en Tiempo Real**
```python
# API Flask
@app.route('/predict', methods=['POST'])
def predict_fraud():
    transaction = request.json
    features = extract_features(transaction)
    probability = model.predict_proba([features])[0][1]

    if probability > 0.7:
        send_alert(transaction)

    return {'fraud_probability': probability}
```

### 2. **Batch Processing Diario**
- Procesar transacciones del día anterior
- Actualizar métricas de modelo
- Generar reportes ejecutivos

### 3. **Retraining Automático**
- Trigger cuando performance degrada
- A/B testing de nuevos modelos
- Promoción automática a producción

### 4. **Monitoring Continuo con Grafana** ⭐
- Dashboards en tiempo real
- Métricas de modelo (accuracy, precision, recall, F1)
- Monitoreo de transacciones
- Alertas automáticas

**Dashboards incluidos**:
1. **Fraud Detection Overview**: Transacciones y fraude en tiempo real
2. **Model Performance Monitoring**: Métricas de ML y confusion matrix

**Acceso**: http://localhost:3000 (admin/admin)

📖 Ver [GRAFANA_GUIDE.md](GRAFANA_GUIDE.md) para guía completa

---

## 🔐 Seguridad y Compliance

### Best Practices Implementadas
- ✅ Credenciales en variables de entorno
- ✅ Logs sin información sensible
- ✅ Trazabilidad completa (MLflow)
- ✅ Versionado de modelos
- ✅ Auditoría de predicciones

### Regulaciones
- **GDPR**: Explicabilidad con feature importance
- **PCI-DSS**: Seguridad en manejo de datos
- **SOC 2**: Logs y trazabilidad

---

## 📚 Aprendizajes Clave

### Technical Skills
1. **Spark**: Procesamiento distribuido eficiente
2. **MLflow**: Gestión completa de ciclo de vida ML
3. **Airflow**: Orquestación robusta de pipelines
4. **Parquet**: Almacenamiento columnar optimizado
5. **PostgreSQL**: Persistencia y queries eficientes

### MLOps Best Practices
1. **Reproducibilidad**: Todo trackeado en MLflow
2. **Automatización**: Airflow para pipelines
3. **Monitoreo**: Métricas y alertas
4. **Versionado**: Modelos y datos
5. **Escalabilidad**: Spark para big data

### Data Science
1. **Feature Engineering**: Creación de features significativas
2. **Modelo Balanceado**: Métricas apropiadas para datos desbalanceados
3. **Evaluación**: Múltiples métricas, no solo accuracy
4. **Visualización**: Comunicación clara de resultados

---

## 🚧 Próximos Pasos

### Corto Plazo
- [ ] Deploy del modelo como API REST
- [ ] Implementar data validation (Great Expectations)
- [ ] Añadir tests unitarios
- [ ] CI/CD con GitHub Actions

### Mediano Plazo
- [x] Dashboard en tiempo real (Grafana) ✅
- [ ] Streaming con Kafka/Spark Streaming
- [ ] A/B testing framework
- [ ] Feature store (Feast)

### Largo Plazo
- [ ] Kubernetes deployment
- [ ] Multi-modelo ensemble
- [ ] AutoML con Optuna
- [ ] Explicabilidad avanzada (SHAP)

---

## 💡 Tips y Troubleshooting

### Error: PostgreSQL Connection Refused
```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps postgres

# Reiniciar si es necesario
docker-compose restart postgres
```

### Error: MLflow Tracking URI
```bash
# Verificar MLflow
curl http://localhost:5000/health

# Revisar logs
docker-compose logs mlflow
```

### Error: Spark Memory
```python
# Ajustar memoria en SparkSession
spark = SparkSession.builder \
    .config("spark.driver.memory", "2g") \
    .config("spark.executor.memory", "2g") \
    .getOrCreate()
```

### Airflow DAG no aparece
```bash
# Verificar sintaxis
python airflow/dags/fraud_detection_pipeline.py

# Reiniciar scheduler
docker-compose restart airflow-scheduler
```

---

## 📖 Recursos Adicionales

### Documentación
- [Notebook Completo](notebooks/08_proyecto_final_integracion.ipynb)
- [DAG de Airflow](airflow/dags/fraud_detection_pipeline.py)
- [Guía de Visualizaciones](VISUALIZATION_GUIDE.md)
- [Guía de Grafana](GRAFANA_GUIDE.md) ⭐ NUEVO
- [Quick Start](QUICKSTART.md)

### Tutoriales
- [Spark ML Guide](https://spark.apache.org/docs/latest/ml-guide.html)
- [MLflow Tutorial](https://mlflow.org/docs/latest/tutorials-and-examples/tutorial.html)
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)

### Papers
- "Fraud Detection using Machine Learning"
- "MLOps: Continuous delivery for ML"
- "Feature Engineering for Machine Learning"

---

## 👥 Créditos

**Autor**: Yusef González
**Proyecto**: Sistema de Detección de Fraude End-to-End
**Versión**: 1.0
**Fecha**: Diciembre 2024

**Tecnologías**: Spark, MLflow, Airflow, Scikit-learn, SciPy, PostgreSQL, Parquet, Matplotlib, Seaborn

---

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

## 🎓 Conclusión

Este proyecto demuestra la integración completa de un stack moderno de MLOps y Data Engineering. Cubre desde la ingesta de datos hasta el deployment en producción, pasando por feature engineering, entrenamiento de modelos, evaluación y automatización.

**¡Felicidades por completar este proyecto end-to-end!** 🎉

Ahora tienes las habilidades para:
- ✅ Diseñar sistemas ML escalables
- ✅ Implementar MLOps best practices
- ✅ Orquestar pipelines complejos
- ✅ Trackear y versionar experimentos
- ✅ Visualizar y comunicar resultados
- ✅ Deployar modelos en producción

---

**¿Preguntas o Feedback?**
Abre un issue en el repositorio o contacta al equipo de desarrollo.

🚀 Happy Learning & Building! 🚀

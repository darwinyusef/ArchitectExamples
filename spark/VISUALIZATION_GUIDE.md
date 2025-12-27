# Guía de Visualizaciones con MLflow

Esta guía te muestra cómo integrar Matplotlib, Seaborn y Plotly con MLflow para crear visualizaciones profesionales de tus modelos de ML.

## 📊 Resumen Rápido

**¿Por qué visualizar con MLflow?**
- ✅ Trazabilidad completa de experimentos
- ✅ Comparación visual entre modelos
- ✅ Reproducibilidad de resultados
- ✅ Documentación automática

## 🎨 Tipos de Visualizaciones

### 1. Exploración de Datos

```python
import matplotlib.pyplot as plt
import mlflow

with mlflow.start_run():
    # Crear gráfico
    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=30)
    plt.title('Distribución de Datos')

    # Guardar y log
    plt.savefig('distribution.png', dpi=150)
    mlflow.log_artifact('distribution.png', artifact_path='exploration')
    plt.show()
```

### 2. Confusion Matrix con Seaborn

```python
import seaborn as sns
from sklearn.metrics import confusion_matrix

with mlflow.start_run():
    # Calcular matriz
    cm = confusion_matrix(y_true, y_pred)

    # Visualizar con seaborn
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')

    # Guardar
    plt.savefig('confusion_matrix.png', dpi=150, bbox_inches='tight')
    mlflow.log_artifact('confusion_matrix.png', artifact_path='evaluation')
    plt.close()
```

### 3. ROC Curve

```python
from sklearn.metrics import roc_curve, auc

with mlflow.start_run():
    # Calcular ROC
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    roc_auc = auc(fpr, tpr)

    # Graficar
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2,
             label=f'ROC curve (AUC = {roc_auc:.3f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Guardar
    plt.savefig('roc_curve.png', dpi=150)
    mlflow.log_artifact('roc_curve.png')
    mlflow.log_metric('roc_auc', roc_auc)
    plt.close()
```

### 4. Feature Importance

```python
with mlflow.start_run():
    # Obtener importancias
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1][:15]

    # Visualizar con seaborn
    plt.figure(figsize=(10, 8))
    importance_df = pd.DataFrame({
        'feature': [feature_names[i] for i in indices],
        'importance': importances[indices]
    })

    sns.barplot(data=importance_df, y='feature', x='importance',
                palette='viridis')
    plt.title('Top 15 Feature Importances')
    plt.tight_layout()

    # Guardar imagen y CSV
    plt.savefig('feature_importance.png', dpi=150)
    mlflow.log_artifact('feature_importance.png')

    importance_df.to_csv('feature_importance.csv', index=False)
    mlflow.log_artifact('feature_importance.csv')
    plt.close()
```

### 5. Gráficos Interactivos con Plotly

```python
import plotly.graph_objects as go

with mlflow.start_run():
    # Crear gráfico interactivo
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=fpr, y=tpr,
        mode='lines',
        name=f'ROC (AUC={roc_auc:.3f})',
        line=dict(color='darkorange', width=3)
    ))

    fig.update_layout(
        title='Interactive ROC Curve',
        xaxis_title='False Positive Rate',
        yaxis_title='True Positive Rate',
        hovermode='closest'
    )

    # Guardar como HTML
    fig.write_html('roc_interactive.html')
    mlflow.log_artifact('roc_interactive.html', artifact_path='interactive')
```

## 🔧 Best Practices

### 1. Organizar Artifacts por Categoría

```python
with mlflow.start_run():
    # Exploración
    mlflow.log_artifact('distribution.png', artifact_path='exploration')

    # Evaluación
    mlflow.log_artifact('confusion_matrix.png', artifact_path='evaluation')
    mlflow.log_artifact('roc_curve.png', artifact_path='evaluation')

    # Análisis
    mlflow.log_artifact('feature_importance.png', artifact_path='analysis')

    # Interactivos
    mlflow.log_artifact('dashboard.html', artifact_path='interactive')
```

### 2. Alta Resolución para Publicaciones

```python
# Para papers o presentaciones
plt.savefig('figure.png', dpi=300, bbox_inches='tight')

# Para web/dashboards
plt.savefig('figure.png', dpi=150, bbox_inches='tight')

# Para exploración rápida
plt.savefig('figure.png', dpi=100)
```

### 3. Estilo Consistente

```python
# Al inicio del notebook
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar estilo global
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('husl')
sns.set_context('notebook', font_scale=1.2)
```

### 4. Limpiar Figuras

```python
# Siempre cerrar figuras después de guardar
plt.savefig('plot.png')
mlflow.log_artifact('plot.png')
plt.close()  # ← Importante para liberar memoria
```

### 5. Nombres Descriptivos

```python
# ❌ Malo
plt.savefig('plot1.png')
plt.savefig('fig2.png')

# ✅ Bueno
plt.savefig('confusion_matrix_test_set.png')
plt.savefig('roc_curve_random_forest_v2.png')
plt.savefig('feature_importance_top20.png')
```

## 📈 Ejemplos Completos

### Dashboard Completo de Modelo

```python
def create_model_dashboard(model, X_test, y_test, feature_names):
    """Crear dashboard completo de evaluación"""

    with mlflow.start_run(run_name='model-dashboard'):
        # Predicciones
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]

        # Crear figura con múltiples subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))

        # 1. Confusion Matrix
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0, 0])
        axes[0, 0].set_title('Confusion Matrix')

        # 2. ROC Curve
        from sklearn.metrics import roc_curve, auc
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        roc_auc = auc(fpr, tpr)
        axes[0, 1].plot(fpr, tpr, lw=2, label=f'AUC = {roc_auc:.3f}')
        axes[0, 1].plot([0, 1], [0, 1], 'k--', lw=2)
        axes[0, 1].set_title('ROC Curve')
        axes[0, 1].legend()

        # 3. Feature Importance
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1][:10]
            axes[1, 0].barh(range(10), importances[indices])
            axes[1, 0].set_yticks(range(10))
            axes[1, 0].set_yticklabels([feature_names[i] for i in indices])
            axes[1, 0].set_title('Top 10 Features')

        # 4. Prediction Distribution
        axes[1, 1].hist(y_pred_proba, bins=50, alpha=0.7)
        axes[1, 1].set_title('Prediction Score Distribution')
        axes[1, 1].set_xlabel('Probability')

        plt.tight_layout()
        plt.savefig('dashboard.png', dpi=150, bbox_inches='tight')
        mlflow.log_artifact('dashboard.png')
        mlflow.log_metric('roc_auc', roc_auc)
        plt.close()
```

### Comparación de Múltiples Modelos

```python
def compare_models_visual(results_dict):
    """Comparar varios modelos visualmente"""

    with mlflow.start_run(run_name='model-comparison'):
        models = list(results_dict.keys())
        metrics = ['accuracy', 'precision', 'recall', 'f1']

        # Crear DataFrame
        df = pd.DataFrame(results_dict).T

        # Crear subplots
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        for idx, metric in enumerate(metrics):
            row, col = idx // 2, idx % 2
            sns.barplot(data=df.reset_index(),
                       x='index', y=metric,
                       ax=axes[row, col],
                       palette='Set2')
            axes[row, col].set_title(f'{metric.capitalize()} Comparison')
            axes[row, col].set_xlabel('Model')
            axes[row, col].set_ylabel(metric.capitalize())
            axes[row, col].tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig('model_comparison.png', dpi=150)
        mlflow.log_artifact('model_comparison.png')
        plt.close()

        # También crear tabla
        df.to_html('comparison_table.html')
        mlflow.log_artifact('comparison_table.html')
```

## 🎯 Patrones Comunes

### Patrón 1: Explorar → Entrenar → Visualizar

```python
# 1. Exploración
with mlflow.start_run(run_name='exploration'):
    plot_distributions(data)
    plot_correlations(data)
    mlflow.log_artifacts('./plots/exploration')

# 2. Entrenamiento
with mlflow.start_run(run_name='training'):
    model = train_model(X_train, y_train)
    mlflow.sklearn.log_model(model, 'model')

# 3. Evaluación
with mlflow.start_run(run_name='evaluation'):
    plot_confusion_matrix(y_test, y_pred)
    plot_roc_curve(y_test, y_pred_proba)
    plot_feature_importance(model)
    mlflow.log_artifacts('./plots/evaluation')
```

### Patrón 2: Logging en el Mismo Run

```python
with mlflow.start_run(run_name='complete-experiment') as run:
    # Entrenar
    model.fit(X_train, y_train)

    # Métricas
    y_pred = model.predict(X_test)
    mlflow.log_metric('accuracy', accuracy_score(y_test, y_pred))

    # Visualizaciones
    plot_and_log_confusion_matrix(y_test, y_pred, run.info.run_id)
    plot_and_log_roc_curve(y_test, y_pred_proba, run.info.run_id)

    # Modelo
    mlflow.sklearn.log_model(model, 'model')
```

## 🔍 Ver Visualizaciones en MLflow UI

### Opción 1: En la UI Web

1. Abre http://localhost:5000
2. Navega al experimento
3. Haz clic en un run
4. Ve a la pestaña "Artifacts"
5. Haz clic en cualquier imagen/HTML para visualizar

### Opción 2: Programáticamente

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Listar artifacts de un run
artifacts = client.list_artifacts(run_id)
for artifact in artifacts:
    print(f"{artifact.path} ({artifact.file_size} bytes)")

# Descargar artifacts
client.download_artifacts(run_id, 'plots', dst_path='./downloads')
```

## 📚 Recursos

- **Notebook completo**: `notebooks/07_mlflow_visualizations.ipynb`
- **Matplotlib Gallery**: https://matplotlib.org/stable/gallery/
- **Seaborn Examples**: https://seaborn.pydata.org/examples/
- **Plotly Charts**: https://plotly.com/python/
- **MLflow Docs**: https://mlflow.org/docs/latest/tracking.html#logging-artifacts

## 💡 Tips Avanzados

### 1. Logging Automático de Todas las Figuras

```python
def auto_log_figures():
    """Guardar automáticamente todas las figuras creadas"""
    import matplotlib.pyplot as plt

    figures = [plt.figure(n) for n in plt.get_fignums()]
    for i, fig in enumerate(figures):
        filename = f'figure_{i}.png'
        fig.savefig(filename, dpi=150, bbox_inches='tight')
        mlflow.log_artifact(filename)
        plt.close(fig)
```

### 2. Crear GIF de Evolución

```python
import imageio

with mlflow.start_run():
    images = []
    for epoch in range(epochs):
        # Entrenar y plotear
        plot_decision_boundary(model, epoch)
        plt.savefig(f'epoch_{epoch}.png')
        images.append(imageio.imread(f'epoch_{epoch}.png'))
        plt.close()

    # Crear GIF
    imageio.mimsave('training_evolution.gif', images, duration=0.5)
    mlflow.log_artifact('training_evolution.gif')
```

### 3. Dashboard HTML Personalizado

```python
html_template = """
<html>
<head><title>Model Report</title></head>
<body>
    <h1>Model Performance Report</h1>
    <img src="confusion_matrix.png" width="600">
    <img src="roc_curve.png" width="600">
    <h2>Metrics</h2>
    <ul>
        <li>Accuracy: {accuracy:.4f}</li>
        <li>F1-Score: {f1:.4f}</li>
    </ul>
</body>
</html>
"""

with mlflow.start_run():
    # Guardar visualizaciones
    plot_confusion_matrix()
    plot_roc_curve()

    # Crear HTML
    html = html_template.format(accuracy=acc, f1=f1_score)
    with open('report.html', 'w') as f:
        f.write(html)

    mlflow.log_artifact('report.html')
```

---

¡Ahora puedes crear visualizaciones profesionales y trackearlas en MLflow! 🎨📊

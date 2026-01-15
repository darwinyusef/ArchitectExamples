// Configuración
const API_BASE_URL = '';

// Estado global
let experimentoActual = null;
let runsSeleccionados = new Set();

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    cargarResumen();
    cargarExperimentos();
    cargarModelos();
});

// ==================== RESUMEN ====================

async function cargarResumen() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/mlops/summary`);
        const data = await response.json();

        document.getElementById('totalExperiments').textContent = data.total_experiments || 0;
        document.getElementById('totalRuns').textContent = data.total_runs || 0;
        document.getElementById('totalModels').textContent = data.total_models || 0;
        document.getElementById('activeModels').textContent = data.active_models || 0;
    } catch (error) {
        console.error('Error cargando resumen:', error);
        mostrarToast('Error cargando resumen de MLflow', 'error');
    }
}

// ==================== EXPERIMENTOS ====================

async function cargarExperimentos() {
    const lista = document.getElementById('experimentsList');
    lista.innerHTML = '<p class="loading-message">Cargando experimentos...</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/mlops/experiments`);
        const experimentos = await response.json();

        if (experimentos.length === 0) {
            lista.innerHTML = '<p class="empty-message">No hay experimentos disponibles. Ejecuta: python modelo_laser_mlflow.py</p>';
            return;
        }

        lista.innerHTML = '';
        experimentos.forEach(exp => {
            const card = crearExperimentCard(exp);
            lista.appendChild(card);
        });
    } catch (error) {
        console.error('Error cargando experimentos:', error);
        lista.innerHTML = '<p class="empty-message">Error cargando experimentos. Asegúrate de que MLflow esté configurado.</p>';
    }
}

function crearExperimentCard(exp) {
    const div = document.createElement('div');
    div.className = 'experiment-card fade-in-up';
    div.onclick = () => seleccionarExperimento(exp.experiment_id, exp.name);

    div.innerHTML = `
        <div class="experiment-header">
            <div class="experiment-name">${exp.name}</div>
            <div class="experiment-id">ID: ${exp.experiment_id}</div>
        </div>
        <div class="experiment-stats">
            <div class="experiment-stat">
                <div class="experiment-stat-value">${exp.lifecycle_stage || 'active'}</div>
                <div class="experiment-stat-label">Estado</div>
            </div>
        </div>
    `;

    return div;
}

async function seleccionarExperimento(experimentId, experimentName) {
    experimentoActual = experimentId;

    // Destacar experimento seleccionado
    document.querySelectorAll('.experiment-card').forEach(card => {
        card.classList.remove('active');
    });
    event.currentTarget.classList.add('active');

    // Mostrar sección de runs
    document.getElementById('experimentName').textContent = experimentName;
    document.getElementById('runsSection').style.display = 'block';

    // Cargar runs
    await cargarRuns();
}

// ==================== RUNS ====================

async function cargarRuns() {
    if (!experimentoActual) return;

    const lista = document.getElementById('runsList');
    lista.innerHTML = '<p class="loading-message">Cargando runs...</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/mlops/experiments/${experimentoActual}/runs`);
        const runs = await response.json();

        if (runs.length === 0) {
            lista.innerHTML = '<p class="empty-message">No hay runs en este experimento</p>';
            return;
        }

        lista.innerHTML = '';
        runs.forEach(run => {
            const card = crearRunCard(run);
            lista.appendChild(card);
        });
    } catch (error) {
        console.error('Error cargando runs:', error);
        lista.innerHTML = '<p class="empty-message">Error cargando runs</p>';
    }
}

function crearRunCard(run) {
    const div = document.createElement('div');
    div.className = 'run-card fade-in-up';

    const runIdShort = run.run_id.substring(0, 8);
    const status = run.status || 'FINISHED';
    const timestamp = new Date(run.start_time).toLocaleString('es-CO');

    // Métricas principales
    const metricas = run.metrics || {};
    const r2 = metricas.r2_score !== undefined ? metricas.r2_score.toFixed(4) : 'N/A';
    const mse = metricas.mse !== undefined ? metricas.mse.toFixed(2) : 'N/A';
    const rmse = metricas.rmse !== undefined ? metricas.rmse.toFixed(2) : 'N/A';
    const mae = metricas.mae !== undefined ? metricas.mae.toFixed(2) : 'N/A';

    div.innerHTML = `
        <input type="checkbox" onchange="toggleRunSelection('${run.run_id}')">
        <div class="run-header">
            <div>
                <div class="run-id-short">Run: ${runIdShort}...</div>
                <div class="run-timestamp">${timestamp}</div>
            </div>
            <div class="run-status ${status.toLowerCase()}">${status}</div>
        </div>
        <div class="run-metrics-grid">
            <div class="run-metric">
                <div class="run-metric-label">R² Score</div>
                <div class="run-metric-value ${getMetricClass('r2', r2)}">${r2}</div>
            </div>
            <div class="run-metric">
                <div class="run-metric-label">MSE</div>
                <div class="run-metric-value">${mse}</div>
            </div>
            <div class="run-metric">
                <div class="run-metric-label">RMSE</div>
                <div class="run-metric-value">${rmse}</div>
            </div>
            <div class="run-metric">
                <div class="run-metric-label">MAE</div>
                <div class="run-metric-value">${mae}</div>
            </div>
        </div>
        <button onclick="verDetallesRun('${run.run_id}'); event.stopPropagation();" class="btn btn-primary" style="margin-top: 15px; width: 100%;">
            🔍 Ver Detalles
        </button>
    `;

    return div;
}

function getMetricClass(metricName, value) {
    if (value === 'N/A') return '';

    if (metricName === 'r2') {
        const numValue = parseFloat(value);
        if (numValue >= 0.95) return 'metric-excellent';
        if (numValue >= 0.85) return 'metric-good';
        if (numValue >= 0.70) return 'metric-warning';
        return 'metric-poor';
    }

    return '';
}

function toggleRunSelection(runId) {
    if (runsSeleccionados.has(runId)) {
        runsSeleccionados.delete(runId);
    } else {
        runsSeleccionados.add(runId);
    }

    // Habilitar/deshabilitar botón de comparar
    const compareBtn = document.getElementById('compareBtn');
    compareBtn.disabled = runsSeleccionados.size < 2;
}

// ==================== DETALLES DE RUN ====================

async function verDetallesRun(runId) {
    mostrarLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/api/mlops/runs/${runId}`);
        const run = await response.json();

        mostrarDetallesRun(run);
        document.getElementById('runDetailsSection').style.display = 'block';
        document.getElementById('runDetailsSection').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error('Error cargando detalles del run:', error);
        mostrarToast('Error cargando detalles del run', 'error');
    } finally {
        mostrarLoading(false);
    }
}

function mostrarDetallesRun(run) {
    document.getElementById('runId').textContent = run.run_id;

    // Información general
    const info = `
        <div class="detail-item">
            <span class="detail-label">Run ID:</span>
            <span class="detail-value">${run.run_id}</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">Experimento:</span>
            <span class="detail-value">${run.experiment_id}</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">Estado:</span>
            <span class="detail-value">${run.status}</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">Inicio:</span>
            <span class="detail-value">${new Date(run.start_time).toLocaleString('es-CO')}</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">Usuario:</span>
            <span class="detail-value">${run.user_id || 'N/A'}</span>
        </div>
    `;
    document.getElementById('runInfo').innerHTML = info;

    // Parámetros
    const params = run.params || {};
    const paramsHTML = Object.entries(params).map(([key, value]) => `
        <div class="detail-item">
            <span class="detail-label">${key}:</span>
            <span class="detail-value">${value}</span>
        </div>
    `).join('');
    document.getElementById('runParams').innerHTML = paramsHTML || '<p class="empty-message">No hay parámetros</p>';

    // Métricas
    const metrics = run.metrics || {};
    const metricsHTML = Object.entries(metrics).map(([key, value]) => `
        <div class="detail-item">
            <span class="detail-label">${key}:</span>
            <span class="detail-value number">${typeof value === 'number' ? value.toFixed(4) : value}</span>
        </div>
    `).join('');
    document.getElementById('runMetrics').innerHTML = metricsHTML || '<p class="empty-message">No hay métricas</p>';

    // Artefactos
    const artifacts = run.artifacts || [];
    const artifactsHTML = artifacts.map(artifact => `
        <div class="artifact-item">
            <span class="artifact-name">📄 ${artifact}</span>
            <a href="${API_BASE_URL}/api/mlops/runs/${run.run_id}/artifacts/${artifact}"
               class="artifact-download" download>
                ⬇ Descargar
            </a>
        </div>
    `).join('');
    document.getElementById('runArtifacts').innerHTML = artifactsHTML || '<p class="empty-message">No hay artefactos</p>';
}

function cerrarDetalles() {
    document.getElementById('runDetailsSection').style.display = 'none';
}

// ==================== COMPARACIÓN ====================

async function compararRuns() {
    if (runsSeleccionados.size < 2) {
        mostrarToast('Selecciona al menos 2 runs para comparar', 'warning');
        return;
    }

    mostrarLoading(true);

    try {
        const runIds = Array.from(runsSeleccionados).join(',');
        const response = await fetch(`${API_BASE_URL}/api/mlops/runs/compare?run_ids=${runIds}`);
        const comparison = await response.json();

        mostrarComparacion(comparison);
        document.getElementById('comparisonSection').style.display = 'block';
        document.getElementById('comparisonSection').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error('Error comparando runs:', error);
        mostrarToast('Error comparando runs', 'error');
    } finally {
        mostrarLoading(false);
    }
}

function mostrarComparacion(comparison) {
    const container = document.getElementById('comparisonTable');

    // Crear tabla
    let html = '<table class="comparison-table"><thead><tr>';
    html += '<th>Métrica/Parámetro</th>';

    comparison.runs.forEach(run => {
        html += `<th>Run ${run.run_id.substring(0, 8)}...</th>`;
    });
    html += '</tr></thead><tbody>';

    // Métricas
    const allMetrics = new Set();
    comparison.runs.forEach(run => {
        Object.keys(run.metrics || {}).forEach(metric => allMetrics.add(metric));
    });

    allMetrics.forEach(metric => {
        html += `<tr><td><strong>${metric}</strong></td>`;
        const values = comparison.runs.map(run => run.metrics?.[metric]);
        const bestValue = metric.includes('r2') ? Math.max(...values.filter(v => v !== undefined)) :
                         Math.min(...values.filter(v => v !== undefined));

        comparison.runs.forEach(run => {
            const value = run.metrics?.[metric];
            const isBest = value === bestValue && value !== undefined;
            html += `<td class="${isBest ? 'comparison-best' : ''}">
                ${value !== undefined ? value.toFixed(4) : 'N/A'}
            </td>`;
        });
        html += '</tr>';
    });

    // Parámetros
    const allParams = new Set();
    comparison.runs.forEach(run => {
        Object.keys(run.params || {}).forEach(param => allParams.add(param));
    });

    if (allParams.size > 0) {
        html += '<tr><td colspan="' + (comparison.runs.length + 1) + '" style="background: #e5e7eb; font-weight: bold;">Parámetros</td></tr>';

        allParams.forEach(param => {
            html += `<tr><td>${param}</td>`;
            comparison.runs.forEach(run => {
                const value = run.params?.[param];
                html += `<td>${value || 'N/A'}</td>`;
            });
            html += '</tr>';
        });
    }

    html += '</tbody></table>';
    container.innerHTML = html;
}

function cerrarComparacion() {
    document.getElementById('comparisonSection').style.display = 'none';
}

// ==================== MODELOS ====================

async function cargarModelos() {
    const lista = document.getElementById('modelsList');
    lista.innerHTML = '<p class="loading-message">Cargando modelos...</p>';

    try {
        const response = await fetch(`${API_BASE_URL}/api/mlops/models`);
        const modelos = await response.json();

        if (modelos.length === 0) {
            lista.innerHTML = '<p class="empty-message">No hay modelos registrados</p>';
            return;
        }

        lista.innerHTML = '';
        modelos.forEach(model => {
            const card = crearModelCard(model);
            lista.appendChild(card);
        });
    } catch (error) {
        console.error('Error cargando modelos:', error);
        lista.innerHTML = '<p class="empty-message">Error cargando modelos</p>';
    }
}

function crearModelCard(model) {
    const div = document.createElement('div');
    div.className = 'model-card fade-in-up';

    const latestVersion = model.latest_versions?.[0] || {};
    const stage = latestVersion.current_stage || 'None';

    div.innerHTML = `
        <div class="model-header">
            <div class="model-name">${model.name}</div>
            <div class="model-badge ${stage.toLowerCase()}">${stage}</div>
        </div>
        <div class="model-versions">
            <strong>Última versión:</strong> ${latestVersion.version || 'N/A'}<br>
            <strong>Run ID:</strong> <code>${latestVersion.run_id?.substring(0, 16) || 'N/A'}...</code>
        </div>
    `;

    return div;
}

// ==================== UTILIDADES ====================

function abrirMLflowUI() {
    window.open('http://localhost:5000', '_blank');
}

function mostrarLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (show) {
        overlay.classList.add('active');
    } else {
        overlay.classList.remove('active');
    }
}

function mostrarToast(mensaje, tipo = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${tipo}`;
    toast.textContent = mensaje;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}
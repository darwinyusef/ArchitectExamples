// Configuración
const API_BASE_URL = '';  // Mismo dominio que FastAPI
const HISTORY_KEY = 'cotizaciones_historial';

// Estado global
let historial = [];

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    cargarEstadisticas();
    cargarProductos();
    cargarHistorial();
    inicializarFormulario();

    // Auto-refresh de estadísticas cada 30 segundos
    setInterval(cargarEstadisticas, 30000);
});

// Cargar estadísticas del servicio
async function cargarEstadisticas() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        const data = await response.json();

        document.getElementById('totalCotizaciones').textContent = data.total_cotizaciones;
        document.getElementById('cotizacionesExitosas').textContent = data.cotizaciones_exitosas;
        document.getElementById('errores').textContent = data.errores;
        document.getElementById('uptime').textContent = Math.round(data.uptime_segundos / 60);
    } catch (error) {
        console.error('Error cargando estadísticas:', error);
    }
}

// Cargar productos predefinidos
async function cargarProductos() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/productos`);
        const productos = await response.json();

        const grid = document.getElementById('productsGrid');
        grid.innerHTML = '';

        for (const [nombre, specs] of Object.entries(productos)) {
            const card = crearProductCard(nombre, specs);
            grid.appendChild(card);
        }
    } catch (error) {
        console.error('Error cargando productos:', error);
        mostrarToast('Error cargando productos', 'error');
    }
}

// Crear tarjeta de producto
function crearProductCard(nombre, specs) {
    const div = document.createElement('div');
    div.className = 'product-card fade-in';

    // Extraer solo "caja-X" del nombre (ej: "Caja 1 (Pequeña)" -> "caja-1")
    const match = nombre.match(/Caja\s+(\d+)/i);
    const slug = match ? `caja-${match[1]}` : nombre.toLowerCase().replace(/\s+/g, '-').replace(/[()]/g, '');

    div.innerHTML = `
        <div class="product-title">${nombre}</div>
        <div class="product-specs">
            <div><span>Tiempo:</span> <strong>${specs.tiempo_seg}s</strong></div>
            <div><span>Material:</span> <strong>${specs.material_cm2}cm²</strong></div>
            <div><span>Energía:</span> <strong>${specs.energia_kwh}kWh</strong></div>
        </div>
        <button class="btn btn-product" onclick="cotizarProducto('${slug}')">
            💰 Cotizar
        </button>
        <div class="product-result" id="result-${slug}" style="display: none;"></div>
    `;

    return div;
}

// Cotizar producto predefinido
async function cotizarProducto(slug) {
    mostrarLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/productos/${slug}/cotizar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();

        // Mostrar resultado en la tarjeta del producto
        const resultDiv = document.getElementById(`result-${slug}`);
        resultDiv.style.display = 'block';
        resultDiv.innerHTML = `
            <div><span>Costo:</span> <span>$${data.costo_produccion.toFixed(2)} COP</span></div>
            <div><span>Precio:</span> <span class="price">$${data.precio_al_detal.toFixed(2)} COP</span></div>
        `;

        // Agregar al historial
        agregarAlHistorial(data);

        mostrarToast('Cotización calculada exitosamente', 'success');
    } catch (error) {
        console.error('Error cotizando producto:', error);
        mostrarToast('Error al cotizar producto', 'error');
    } finally {
        mostrarLoading(false);
    }
}

// Inicializar formulario de cotización personalizada
function inicializarFormulario() {
    const form = document.getElementById('cotizacionForm');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const tiempoSeg = parseFloat(document.getElementById('tiempoSeg').value);
        const materialCm2 = parseFloat(document.getElementById('materialCm2').value);
        const energiaKwh = parseFloat(document.getElementById('energiaKwh').value);

        // Validación
        if (tiempoSeg <= 0 || materialCm2 <= 0 || energiaKwh <= 0) {
            mostrarToast('Todos los valores deben ser mayores que cero', 'error');
            return;
        }

        await crearCotizacionPersonalizada(tiempoSeg, materialCm2, energiaKwh);
    });
}

// Crear cotización personalizada
async function crearCotizacionPersonalizada(tiempoSeg, materialCm2, energiaKwh) {
    mostrarLoading(true);

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/cotizar`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tiempo_seg: tiempoSeg,
                material_cm2: materialCm2,
                energia_kwh: energiaKwh
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error en la solicitud');
        }

        const data = await response.json();

        // Mostrar resultado
        mostrarResultado(data);

        // Agregar al historial
        agregarAlHistorial(data);

        // Limpiar formulario
        document.getElementById('cotizacionForm').reset();

        mostrarToast('Cotización calculada exitosamente', 'success');
    } catch (error) {
        console.error('Error creando cotización:', error);
        mostrarToast(`Error: ${error.message}`, 'error');
    } finally {
        mostrarLoading(false);
    }
}

// Mostrar resultado de cotización
function mostrarResultado(data) {
    const section = document.getElementById('resultSection');
    section.style.display = 'block';
    section.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    document.getElementById('resultId').textContent = `ID: ${data.id_cotizacion.substring(0, 8)}...`;
    document.getElementById('resultParams').textContent =
        `${data.parametros.tiempo_seg}s, ${data.parametros.material_cm2}cm², ${data.parametros.energia_kwh}kWh`;
    document.getElementById('resultCosto').textContent = `$${data.costo_produccion.toFixed(2)} COP`;
    document.getElementById('resultPrecio').textContent = `$${data.precio_al_detal.toFixed(2)} COP`;
    document.getElementById('resultMargen').textContent = `${((data.margen_aplicado - 1) * 100).toFixed(0)}%`;
    document.getElementById('resultTimestamp').textContent = new Date(data.timestamp).toLocaleString('es-CO');
}

// Historial
function cargarHistorial() {
    const stored = localStorage.getItem(HISTORY_KEY);
    historial = stored ? JSON.parse(stored) : [];
    renderizarHistorial();
}

function agregarAlHistorial(cotizacion) {
    historial.unshift(cotizacion);

    // Mantener solo las últimas 20 cotizaciones
    if (historial.length > 20) {
        historial = historial.slice(0, 20);
    }

    localStorage.setItem(HISTORY_KEY, JSON.stringify(historial));
    renderizarHistorial();

    // Actualizar estadísticas
    cargarEstadisticas();
}

function renderizarHistorial() {
    const lista = document.getElementById('historyList');

    if (historial.length === 0) {
        lista.innerHTML = '<p class="empty-message">No hay cotizaciones en el historial</p>';
        return;
    }

    lista.innerHTML = historial.map((item, index) => `
        <div class="history-item fade-in">
            <div class="history-header">
                <span>${new Date(item.timestamp).toLocaleString('es-CO')}</span>
                <span>ID: ${item.id_cotizacion.substring(0, 8)}...</span>
            </div>
            <div class="history-data">
                <div>
                    <strong>Parámetros:</strong><br>
                    ${item.parametros.tiempo_seg}s,
                    ${item.parametros.material_cm2}cm²,
                    ${item.parametros.energia_kwh}kWh
                </div>
                <div>
                    <strong>Costo:</strong> $${item.costo_produccion.toFixed(2)} COP<br>
                    <strong style="color: var(--success-color);">Precio:</strong>
                    <strong style="color: var(--success-color);">$${item.precio_al_detal.toFixed(2)} COP</strong>
                </div>
            </div>
        </div>
    `).join('');
}

function limpiarHistorial() {
    if (confirm('¿Estás seguro de que quieres limpiar todo el historial?')) {
        historial = [];
        localStorage.removeItem(HISTORY_KEY);
        renderizarHistorial();
        mostrarToast('Historial limpiado', 'success');
    }
}

// Utilidades
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

// Validación en tiempo real
document.addEventListener('DOMContentLoaded', () => {
    const inputs = document.querySelectorAll('input[type="number"]');

    inputs.forEach(input => {
        input.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            if (value < 0) {
                e.target.value = '';
            }
        });
    });
});

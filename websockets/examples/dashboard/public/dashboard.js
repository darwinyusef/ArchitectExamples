const socket = io();

// Elementos del DOM
const usersCount = document.getElementById('users-count');
const revenueElement = document.getElementById('revenue');
const ordersElement = document.getElementById('orders');
const conversionElement = document.getElementById('conversion');
const cpuBar = document.getElementById('cpu-bar');
const cpuValue = document.getElementById('cpu-value');
const memoryBar = document.getElementById('memory-bar');
const memoryValue = document.getElementById('memory-value');
const networkBar = document.getElementById('network-bar');
const networkValue = document.getElementById('network-value');
const ordersList = document.getElementById('orders-list');
const alertsList = document.getElementById('alerts-list');

// Configurar gráfico
const ctx = document.getElementById('trendsChart').getContext('2d');
const trendsChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      {
        label: 'Usuarios',
        data: [],
        borderColor: '#3498db',
        backgroundColor: 'rgba(52, 152, 219, 0.1)',
        tension: 0.4
      },
      {
        label: 'Revenue ($)',
        data: [],
        borderColor: '#2ecc71',
        backgroundColor: 'rgba(46, 204, 113, 0.1)',
        tension: 0.4,
        yAxisID: 'y1'
      }
    ]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    scales: {
      y: {
        type: 'linear',
        display: true,
        position: 'left',
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        grid: {
          drawOnChartArea: false,
        },
      }
    },
    plugins: {
      legend: {
        display: true,
        position: 'top'
      }
    },
    animation: {
      duration: 300
    }
  }
});

// Recibir estado inicial
socket.on('initial-state', (data) => {
  updateMetrics(data.metrics);
  updateSystemStats(data.systemStats);
  updateOrders(data.recentOrders);
  updateAlerts(data.alerts);
  updateChart(data.history);
});

// Actualizar métricas
socket.on('metrics-update', (data) => {
  updateMetrics(data.metrics);
  updateSystemStats(data.systemStats);
  updateChart(data.history);
});

// Nueva orden
socket.on('new-order', (order) => {
  addOrder(order);
});

// Actualizar alertas
socket.on('alerts-update', (alerts) => {
  updateAlerts(alerts);
});

// Funciones de actualización
function updateMetrics(metrics) {
  usersCount.textContent = metrics.users.toLocaleString();
  revenueElement.textContent = `$${metrics.revenue.toLocaleString()}`;
  ordersElement.textContent = metrics.orders.toLocaleString();
  conversionElement.textContent = `${metrics.conversion}%`;
}

function updateSystemStats(stats) {
  cpuBar.style.width = `${stats.cpu}%`;
  cpuValue.textContent = stats.cpu;
  memoryBar.style.width = `${stats.memory}%`;
  memoryValue.textContent = stats.memory;
  networkBar.style.width = `${Math.min(stats.network / 10, 100)}%`;
  networkValue.textContent = stats.network;
}

function updateChart(history) {
  trendsChart.data.labels = history.timestamps;
  trendsChart.data.datasets[0].data = history.users;
  trendsChart.data.datasets[1].data = history.revenue;
  trendsChart.update('none');
}

function updateOrders(orders) {
  if (orders.length === 0) {
    ordersList.innerHTML = '<div class="empty-state">No hay órdenes aún</div>';
    return;
  }

  ordersList.innerHTML = orders.map(order => `
    <div class="order-item">
      <div>
        <div class="order-product">${order.product}</div>
        <div style="font-size: 12px; color: #7f8c8d;">${order.customer}</div>
      </div>
      <div class="order-amount">$${order.amount.toLocaleString()}</div>
    </div>
  `).join('');
}

function addOrder(order) {
  const emptyState = ordersList.querySelector('.empty-state');
  if (emptyState) {
    ordersList.innerHTML = '';
  }

  const orderItem = document.createElement('div');
  orderItem.className = 'order-item';
  orderItem.innerHTML = `
    <div>
      <div class="order-product">${order.product}</div>
      <div style="font-size: 12px; color: #7f8c8d;">${order.customer}</div>
    </div>
    <div class="order-amount">$${order.amount.toLocaleString()}</div>
  `;

  ordersList.insertBefore(orderItem, ordersList.firstChild);

  // Limitar a 10 órdenes visibles
  const items = ordersList.querySelectorAll('.order-item');
  if (items.length > 10) {
    ordersList.removeChild(items[items.length - 1]);
  }
}

function updateAlerts(alerts) {
  if (alerts.length === 0) {
    alertsList.innerHTML = '<div class="empty-state">No hay alertas</div>';
    return;
  }

  alertsList.innerHTML = alerts.map(alert => `
    <div class="alert alert-${alert.type}">
      <span>${alert.message}</span>
      <span style="font-size: 11px;">${new Date(alert.timestamp).toLocaleTimeString()}</span>
    </div>
  `).join('');
}

function clearAlerts() {
  socket.emit('clear-alerts');
  alertsList.innerHTML = '<div class="empty-state">No hay alertas</div>';
}

socket.on('connect', () => {
  console.log('✅ Conectado al dashboard');
});

socket.on('disconnect', () => {
  console.log('❌ Desconectado del dashboard');
});

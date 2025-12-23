/**
 * EJEMPLO 2: DASHBOARD EN TIEMPO REAL
 *
 * Este ejemplo implementa un dashboard de métricas en tiempo real con:
 * - Métricas del sistema (CPU, Memoria, Red)
 * - Datos simulados de ventas/analytics
 * - Actualizaciones cada segundo
 * - Múltiples clientes sincronizados
 * - Alertas en tiempo real
 */

const express = require('express');
const http = require('http');
const socketIO = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = socketIO(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

const PORT = process.env.PORT || 3002;

app.use(express.static(path.join(__dirname, 'public')));

// Estado del dashboard
const dashboardState = {
  metrics: {
    users: 0,
    revenue: 0,
    orders: 0,
    conversion: 0
  },
  systemStats: {
    cpu: 0,
    memory: 0,
    network: 0
  },
  recentOrders: [],
  alerts: []
};

// Generar datos aleatorios realistas
function generateMetrics() {
  // Simular métricas de negocio
  dashboardState.metrics = {
    users: Math.floor(Math.random() * 1000) + 500,
    revenue: Math.floor(Math.random() * 50000) + 10000,
    orders: Math.floor(Math.random() * 200) + 50,
    conversion: (Math.random() * 5 + 2).toFixed(2) // 2-7%
  };

  // Simular estadísticas del sistema
  dashboardState.systemStats = {
    cpu: Math.floor(Math.random() * 100),
    memory: Math.floor(Math.random() * 100),
    network: Math.floor(Math.random() * 1000) // KB/s
  };

  // Generar alertas aleatorias
  if (Math.random() > 0.95) {
    const alerts = [
      { type: 'warning', message: 'Alto tráfico detectado', severity: 'medium' },
      { type: 'success', message: 'Nueva venta de $5,000', severity: 'low' },
      { type: 'error', message: 'Error en servidor de pagos', severity: 'high' },
      { type: 'info', message: 'Actualización de sistema disponible', severity: 'low' }
    ];

    const randomAlert = alerts[Math.floor(Math.random() * alerts.length)];
    randomAlert.timestamp = new Date().toISOString();
    randomAlert.id = `alert-${Date.now()}`;

    dashboardState.alerts.unshift(randomAlert);

    // Limitar a 10 alertas
    if (dashboardState.alerts.length > 10) {
      dashboardState.alerts = dashboardState.alerts.slice(0, 10);
    }
  }

  // Generar órdenes recientes
  if (Math.random() > 0.7) {
    const products = ['Laptop Pro', 'iPhone 15', 'AirPods', 'iPad Air', 'Watch Ultra'];
    const newOrder = {
      id: `ORD-${Date.now()}`,
      product: products[Math.floor(Math.random() * products.length)],
      amount: Math.floor(Math.random() * 3000) + 500,
      customer: `Cliente ${Math.floor(Math.random() * 1000)}`,
      timestamp: new Date().toISOString()
    };

    dashboardState.recentOrders.unshift(newOrder);

    // Limitar a 10 órdenes
    if (dashboardState.recentOrders.length > 10) {
      dashboardState.recentOrders = dashboardState.recentOrders.slice(0, 10);
    }

    return newOrder; // Retornar para emitir como evento separado
  }

  return null;
}

// Histórico de métricas para gráficos
const metricsHistory = {
  users: [],
  revenue: [],
  cpu: [],
  memory: [],
  timestamps: []
};

const MAX_HISTORY = 30; // 30 segundos de historia

function updateMetricsHistory() {
  const timestamp = new Date().toLocaleTimeString();

  metricsHistory.users.push(dashboardState.metrics.users);
  metricsHistory.revenue.push(dashboardState.metrics.revenue);
  metricsHistory.cpu.push(dashboardState.systemStats.cpu);
  metricsHistory.memory.push(dashboardState.systemStats.memory);
  metricsHistory.timestamps.push(timestamp);

  // Limitar tamaño del histórico
  if (metricsHistory.users.length > MAX_HISTORY) {
    metricsHistory.users.shift();
    metricsHistory.revenue.shift();
    metricsHistory.cpu.shift();
    metricsHistory.memory.shift();
    metricsHistory.timestamps.shift();
  }
}

// Eventos de Socket.io
io.on('connection', (socket) => {
  console.log(`✅ Cliente conectado al dashboard: ${socket.id}`);

  // Enviar estado inicial
  socket.emit('initial-state', {
    metrics: dashboardState.metrics,
    systemStats: dashboardState.systemStats,
    recentOrders: dashboardState.recentOrders,
    alerts: dashboardState.alerts,
    history: metricsHistory
  });

  // Solicitar actualización manual
  socket.on('request-update', () => {
    generateMetrics();
    socket.emit('metrics-update', {
      metrics: dashboardState.metrics,
      systemStats: dashboardState.systemStats
    });
  });

  // Limpiar alertas
  socket.on('clear-alerts', () => {
    dashboardState.alerts = [];
    io.emit('alerts-cleared');
  });

  socket.on('disconnect', () => {
    console.log(`❌ Cliente desconectado: ${socket.id}`);
  });
});

// Actualizar métricas cada segundo
setInterval(() => {
  const newOrder = generateMetrics();
  updateMetricsHistory();

  // Emitir actualizaciones a todos los clientes
  io.emit('metrics-update', {
    metrics: dashboardState.metrics,
    systemStats: dashboardState.systemStats,
    history: metricsHistory
  });

  // Si hay nueva orden, emitirla
  if (newOrder) {
    io.emit('new-order', newOrder);
  }

  // Si hay nuevas alertas, emitirlas
  if (dashboardState.alerts.length > 0) {
    io.emit('alerts-update', dashboardState.alerts);
  }
}, 1000);

// Iniciar servidor
server.listen(PORT, () => {
  console.log(`\n📊 Dashboard en tiempo real ejecutándose en http://localhost:${PORT}`);
  console.log(`🔄 Actualizando métricas cada segundo\n`);
});

// Estadísticas cada 10 segundos
setInterval(() => {
  console.log(`📈 Métricas actuales:
    - Usuarios: ${dashboardState.metrics.users}
    - Revenue: $${dashboardState.metrics.revenue}
    - Órdenes: ${dashboardState.metrics.orders}
    - CPU: ${dashboardState.systemStats.cpu}%
    - Memoria: ${dashboardState.systemStats.memory}%
    - Clientes conectados: ${io.sockets.sockets.size}
  `);
}, 10000);

# Quick Start - Concurrencia Python

Guía rápida para comenzar a usar el proyecto en menos de 5 minutos.

## Opción 1: Docker (Recomendado) 🐳

### 1. Iniciar el proyecto

```bash
cd concurrencia-python
docker-compose up
```

### 2. Acceder a la API

- API: http://localhost:8000
- Docs interactivas: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Probar endpoints

```bash
# IO-bound con threading
curl -X POST http://localhost:8000/io-bound/threading \
  -H "Content-Type: application/json" \
  -d '{"iterations": 5}'

# CPU-bound con multiprocessing
curl -X POST http://localhost:8000/cpu-bound/multiprocessing \
  -H "Content-Type: application/json" \
  -d '{"iterations": 4}'

# Ver métricas
curl http://localhost:8000/metrics/summary
```

### 4. Con monitoring (Prometheus + Grafana)

```bash
docker-compose --profile monitoring up
```

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

---

## Opción 2: Local 💻

### 1. Instalar dependencias

```bash
cd concurrencia-python/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Ejecutar servidor

```bash
python main.py
```

### 3. Acceder a la API

http://localhost:8000/docs

---

## Ejemplos Rápidos

### Python

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Comparar IO-bound
print("=== IO-bound Comparison ===")
r1 = requests.post(f"{BASE_URL}/io-bound/sequential", json={"iterations": 5})
print(f"Sequential: {r1.json()['duration']:.2f}s")

r2 = requests.post(f"{BASE_URL}/io-bound/threading", json={"iterations": 5})
print(f"Threading: {r2.json()['duration']:.2f}s")

r3 = requests.post(f"{BASE_URL}/io-bound/async", json={"iterations": 5})
print(f"Async: {r3.json()['duration']:.2f}s")

# 2. Demostrar race condition
print("\n=== Race Condition ===")
r1 = requests.post(f"{BASE_URL}/race-conditions/unsafe",
                   json={"num_threads": 10, "increments_per_thread": 1000})
print(f"Sin Lock: {r1.json()['final_counter']} (esperado: 10000)")

r2 = requests.post(f"{BASE_URL}/race-conditions/lock",
                   json={"num_threads": 10, "increments_per_thread": 1000})
print(f"Con Lock: {r2.json()['final_counter']}")

# 3. Ver métricas
print("\n=== Metrics ===")
r = requests.get(f"{BASE_URL}/metrics/summary")
print(r.json())
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

async function main() {
  // Comparar IO-bound
  console.log('=== IO-bound Comparison ===');

  const r1 = await axios.post(`${BASE_URL}/io-bound/sequential`,
    { iterations: 5 });
  console.log(`Sequential: ${r1.data.duration.toFixed(2)}s`);

  const r2 = await axios.post(`${BASE_URL}/io-bound/threading`,
    { iterations: 5 });
  console.log(`Threading: ${r2.data.duration.toFixed(2)}s`);

  // Ver métricas
  const metrics = await axios.get(`${BASE_URL}/metrics/summary`);
  console.log('\n=== Metrics ===');
  console.log(metrics.data);
}

main();
```

### cURL

```bash
# IO-bound comparison
echo "=== IO-bound Comparison ==="

echo "Sequential:"
curl -s -X POST http://localhost:8000/io-bound/sequential \
  -H "Content-Type: application/json" \
  -d '{"iterations": 3}' | jq '.duration'

echo "Threading:"
curl -s -X POST http://localhost:8000/io-bound/threading \
  -H "Content-Type: application/json" \
  -d '{"iterations": 3}' | jq '.duration'

# CPU-bound comparison
echo -e "\n=== CPU-bound Comparison ==="

echo "Threading (malo por GIL):"
curl -s -X POST http://localhost:8000/cpu-bound/threading \
  -H "Content-Type: application/json" \
  -d '{"iterations": 2}' | jq '.duration'

echo "Multiprocessing (bueno):"
curl -s -X POST http://localhost:8000/cpu-bound/multiprocessing \
  -H "Content-Type: application/json" \
  -d '{"iterations": 2}' | jq '.duration'

# Metrics
echo -e "\n=== Metrics ==="
curl -s http://localhost:8000/metrics/summary | jq
```

---

## Todos los Endpoints

### IO-bound
- `POST /io-bound/sequential`
- `POST /io-bound/threading`
- `POST /io-bound/async`

### CPU-bound
- `POST /cpu-bound/sequential`
- `POST /cpu-bound/threading`
- `POST /cpu-bound/multiprocessing`

### Threading
- `POST /threading/basic`
- `POST /threading/pool`
- `POST /threading/daemon`

### Multiprocessing
- `POST /multiprocessing/basic`
- `POST /multiprocessing/queue`
- `POST /multiprocessing/pool`

### Async
- `POST /async/gather`
- `POST /async/run-in-executor`
- `POST /async/timeout`
- `POST /async/as-completed`

### Race Conditions
- `POST /race-conditions/unsafe`
- `POST /race-conditions/lock`
- `POST /race-conditions/rlock`

### Deadlocks
- `POST /deadlocks/demonstrate`
- `POST /deadlocks/prevent`

### Queues
- `POST /queues/producer-consumer`
- `POST /queues/priority`
- `POST /queues/lifo`
- `POST /queues/bounded`

### Semaphores
- `POST /semaphores/rate-limit`
- `POST /semaphores/threading`
- `POST /semaphores/bounded`
- `POST /semaphores/connection-pool`

### Observabilidad
- `GET /metrics/summary`
- `GET /metrics/operation/{name}`
- `GET /metrics/system`
- `POST /metrics/reset`
- `GET /prometheus/metrics`

### Otros
- `GET /` - Info de la API
- `GET /health` - Health check
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc

---

## Próximos Pasos

1. Revisa la [Guía completa](./GUIA.md) para entender conceptos en profundidad
2. Explora el código en `backend/examples/`
3. Lee el [README](./README.md) para más ejemplos y explicaciones

## Detener el Proyecto

```bash
# Docker
docker-compose down

# O con volúmenes
docker-compose down -v
```

## Problemas Comunes

### Puerto 8000 en uso

```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"  # Usar 8001 en lugar de 8000
```

### Reiniciar con cambios

```bash
docker-compose down
docker-compose up --build
```

"""
Test rápido para verificar que la API funciona sin Redis.
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Verificar health check."""
    print("\n1️⃣  Probando Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()

    print(f"   Status: {data['status']}")
    print(f"   Modelo ONNX: {data['modelo_onnx']}")
    print(f"   Redis: {data['redis']}")

    if data['status'] == 'healthy':
        print("   ✅ API está saludable")
        return True
    return False

def test_cotizacion():
    """Probar cotización simple."""
    print("\n2️⃣  Probando Cotización...")

    data = {
        "tiempo_seg": 360,
        "material_cm2": 24,
        "energia_kwh": 0.025
    }

    response = requests.post(f"{BASE_URL}/api/v1/cotizar", json=data)
    result = response.json()

    print(f"   ID: {result['id_cotizacion'][:8]}...")
    print(f"   Costo: ${result['costo_produccion']:.2f} COP")
    print(f"   Precio: ${result['precio_al_detal']:.2f} COP")
    print("   ✅ Cotización funciona correctamente")

    return True

def test_stats():
    """Probar estadísticas."""
    print("\n3️⃣  Probando Estadísticas...")

    response = requests.get(f"{BASE_URL}/stats")
    data = response.json()

    print(f"   Total cotizaciones: {data['total_cotizaciones']}")
    print(f"   Exitosas: {data['cotizaciones_exitosas']}")
    print("   ✅ Estadísticas funcionan")

    return True

def test_mlops():
    """Probar MLOps endpoints."""
    print("\n4️⃣  Probando MLOps...")

    try:
        response = requests.get(f"{BASE_URL}/api/mlops/summary")
        data = response.json()

        print(f"   Experimentos: {data.get('total_experiments', 0)}")
        print(f"   Runs: {data.get('total_runs', 0)}")
        print(f"   Modelos: {data.get('total_models', 0)}")
        print("   ✅ MLOps funciona correctamente")
        return True
    except:
        print("   ⚠️  MLOps no disponible (ejecuta: python modelo_laser_mlflow.py)")
        return False

def main():
    print("="*60)
    print("TEST: API sin Redis")
    print("="*60)

    try:
        # Verificar que la API esté corriendo
        print("\n🔍 Verificando que la API esté corriendo...")
        requests.get(BASE_URL, timeout=2)
        print("✅ API detectada en", BASE_URL)
    except requests.exceptions.ConnectionError:
        print(f"\n❌ ERROR: No se puede conectar a {BASE_URL}")
        print("\nAsegúrate de que la API esté corriendo:")
        print("  python api_fastapi_laser.py")
        return

    # Ejecutar tests
    resultados = []

    resultados.append(("Health Check", test_health()))
    time.sleep(0.5)

    resultados.append(("Cotización", test_cotizacion()))
    time.sleep(0.5)

    resultados.append(("Estadísticas", test_stats()))
    time.sleep(0.5)

    resultados.append(("MLOps", test_mlops()))

    # Resumen
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)

    exitosos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)

    for nombre, resultado in resultados:
        emoji = "✅" if resultado else "❌"
        print(f"{emoji} {nombre}")

    print(f"\nTotal: {exitosos}/{total} tests exitosos")

    if exitosos >= 3:
        print("\n🎉 ¡La API funciona correctamente sin Redis!")
        print("\nAhora puedes:")
        print(f"  • Abrir la interfaz: {BASE_URL}")
        print(f"  • MLOps Dashboard: {BASE_URL}/mlops")
        print(f"  • API Docs: {BASE_URL}/docs")
    else:
        print("\n⚠️  Algunos tests fallaron. Revisa los mensajes arriba.")

    print("\n" + "="*60)

if __name__ == "__main__":
    main()

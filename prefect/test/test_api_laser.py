"""
Script de prueba para la API FastAPI de cotización láser.
"""

import requests
import json
from typing import Dict, Any

# Configuración
BASE_URL = "http://localhost:8000"


def print_response(titulo: str, response: requests.Response):
    """Imprime la respuesta formateada."""
    print(f"\n{'='*60}")
    print(f"🧪 {titulo}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response:\n{json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")


def test_root():
    """Probar endpoint raíz."""
    response = requests.get(f"{BASE_URL}/")
    print_response("Test: Root Endpoint", response)
    return response.status_code == 200


def test_health():
    """Probar endpoint de salud."""
    response = requests.get(f"{BASE_URL}/health")
    print_response("Test: Health Check", response)
    return response.status_code == 200


def test_stats():
    """Probar endpoint de estadísticas."""
    response = requests.get(f"{BASE_URL}/stats")
    print_response("Test: Estadísticas", response)
    return response.status_code == 200


def test_cotizacion_simple():
    """Probar cotización simple."""
    data = {
        "tiempo_seg": 360,
        "material_cm2": 24,
        "energia_kwh": 0.025
    }

    response = requests.post(f"{BASE_URL}/api/v1/cotizar", json=data)
    print_response("Test: Cotización Simple (Caja Pequeña)", response)

    if response.status_code == 200:
        cotizacion = response.json()
        print(f"\n💰 Resultado:")
        print(f"   Costo Producción: ${cotizacion['costo_produccion']:.2f} COP")
        print(f"   Precio al Detal: ${cotizacion['precio_al_detal']:.2f} COP")
        print(f"   Margen: {cotizacion['margen_aplicado']*100:.0f}%")
        return True

    return False


def test_cotizacion_lote():
    """Probar cotización en lote."""
    data = {
        "cotizaciones": [
            {"tiempo_seg": 360, "material_cm2": 24, "energia_kwh": 0.025},  # Caja 1
            {"tiempo_seg": 240, "material_cm2": 26, "energia_kwh": 0.016},  # Caja 2
            {"tiempo_seg": 300, "material_cm2": 48, "energia_kwh": 0.020},  # Caja 3
        ]
    }

    response = requests.post(f"{BASE_URL}/api/v1/cotizar/lote", json=data)
    print_response("Test: Cotización en Lote (3 cajas)", response)

    if response.status_code == 200:
        resultado = response.json()
        print(f"\n📦 Resultados del lote:")
        print(f"   Total procesadas: {resultado['total_procesadas']}")
        print(f"   Exitosas: {resultado['exitosas']}")
        print(f"   Errores: {resultado['errores']}")

        for i, cotizacion in enumerate(resultado['resultados'], 1):
            print(f"\n   Pieza {i}:")
            print(f"      Costo: ${cotizacion['costo_produccion']:.2f} COP")
            print(f"      Precio: ${cotizacion['precio_al_detal']:.2f} COP")

        return True

    return False


def test_productos_predefinidos():
    """Probar obtención de productos predefinidos."""
    response = requests.get(f"{BASE_URL}/api/v1/productos")
    print_response("Test: Productos Predefinidos", response)
    return response.status_code == 200


def test_cotizar_producto_predefinido():
    """Probar cotización de producto predefinido."""
    response = requests.post(f"{BASE_URL}/api/v1/productos/caja-1/cotizar")
    print_response("Test: Cotizar Caja 1 (Producto Predefinido)", response)
    return response.status_code == 200


def test_obtener_cotizacion():
    """Probar obtención de cotización por ID."""
    # Primero crear una cotización
    data = {
        "tiempo_seg": 360,
        "material_cm2": 24,
        "energia_kwh": 0.025
    }

    response_crear = requests.post(f"{BASE_URL}/api/v1/cotizar", json=data)

    if response_crear.status_code == 200:
        cotizacion = response_crear.json()
        id_cotizacion = cotizacion["id_cotizacion"]

        # Ahora obtener la cotización por ID
        response_obtener = requests.get(f"{BASE_URL}/api/v1/cotizar/{id_cotizacion}")
        print_response(f"Test: Obtener Cotización por ID ({id_cotizacion})", response_obtener)

        return response_obtener.status_code == 200

    return False


def test_validacion_parametros():
    """Probar validación de parámetros inválidos."""
    # Parámetros negativos
    data = {
        "tiempo_seg": -360,
        "material_cm2": 24,
        "energia_kwh": 0.025
    }

    response = requests.post(f"{BASE_URL}/api/v1/cotizar", json=data)
    print_response("Test: Validación (parámetros negativos - debe fallar)", response)

    # Este test pasa si la API rechaza la solicitud
    return response.status_code == 422


def run_all_tests():
    """Ejecutar todos los tests."""
    print("\n" + "="*60)
    print("🚀 INICIANDO TESTS DE LA API DE COTIZACIÓN LÁSER")
    print("="*60)

    tests = [
        ("Root Endpoint", test_root),
        ("Health Check", test_health),
        ("Estadísticas", test_stats),
        ("Productos Predefinidos", test_productos_predefinidos),
        ("Cotización Simple", test_cotizacion_simple),
        ("Cotización en Lote", test_cotizacion_lote),
        ("Cotizar Producto Predefinido", test_cotizar_producto_predefinido),
        ("Obtener Cotización por ID", test_obtener_cotizacion),
        ("Validación de Parámetros", test_validacion_parametros),
    ]

    resultados = []

    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except requests.exceptions.ConnectionError:
            print(f"\n❌ Error: No se pudo conectar a la API en {BASE_URL}")
            print("   Asegúrate de que el servidor esté corriendo:")
            print("   python api_fastapi_laser.py")
            return
        except Exception as e:
            print(f"\n❌ Error en test '{nombre}': {e}")
            resultados.append((nombre, False))

    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE TESTS")
    print("="*60)

    exitosos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)

    for nombre, resultado in resultados:
        emoji = "✅" if resultado else "❌"
        print(f"{emoji} {nombre}")

    print(f"\n{'='*60}")
    print(f"Total: {exitosos}/{total} tests exitosos ({exitosos/total*100:.1f}%)")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run_all_tests()

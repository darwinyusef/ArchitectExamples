import onnxruntime as ort
import numpy as np
from prefect import task, flow
from typing import List, Dict, Tuple
import os


@task(name="Cargar modelo ONNX")
def cargar_modelo_onnx(model_path: str) -> Tuple[ort.InferenceSession, str]:
    """
    Carga el modelo ONNX para inferencia.

    Args:
        model_path: Ruta al archivo ONNX

    Returns:
        Tupla con (sesión de inferencia, nombre del input)
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Modelo ONNX no encontrado en: {model_path}")

    try:
        session = ort.InferenceSession(model_path)
        input_name = session.get_inputs()[0].name
        print(f"✅ Modelo ONNX cargado correctamente desde: {model_path}")
        return session, input_name
    except Exception as e:
        raise RuntimeError(f"❌ Error al cargar el modelo: {e}")


@task(name="Realizar inferencia")
def realizar_inferencia(
    session: ort.InferenceSession,
    input_name: str,
    tiempo: float,
    area: float,
    energia: float,
    margen: float = 1.3
) -> Dict[str, float]:
    """
    Realiza la inferencia con el modelo ONNX.

    Args:
        session: Sesión de inferencia ONNX
        input_name: Nombre del input del modelo
        tiempo: Tiempo de corte en segundos
        area: Área del material en cm²
        energia: Energía consumida en kWh
        margen: Margen de valoración al mercado (default: 1.3 = 30%)

    Returns:
        Diccionario con costo de producción y precio de venta
    """
    # Preparar los datos como un array de 32 bits
    datos_entrada = np.array([[tiempo, area, energia]], dtype=np.float32)

    # Ejecutar la inferencia
    resultado = session.run(None, {input_name: datos_entrada})
    costo_produccion = float(resultado[0][0])

    # Aplicar margen de valoración
    precio_detal = costo_produccion * margen

    return {
        'costo_produccion': costo_produccion,
        'precio_detal': precio_detal,
        'margen_aplicado': margen
    }


@task(name="Procesar múltiples cotizaciones")
def procesar_cotizaciones(
    session: ort.InferenceSession,
    input_name: str,
    productos: Dict[str, List[float]],
    margen: float = 1.3
) -> List[Dict]:
    """
    Procesa múltiples cotizaciones en batch.

    Args:
        session: Sesión de inferencia ONNX
        input_name: Nombre del input del modelo
        productos: Diccionario con productos y sus especificaciones
        margen: Margen de valoración al mercado

    Returns:
        Lista de diccionarios con resultados
    """
    resultados = []

    for nombre, specs in productos.items():
        cotizacion = realizar_inferencia(
            session,
            input_name,
            specs[0],  # tiempo
            specs[1],  # area
            specs[2],  # energia
            margen
        )

        resultado = {
            'producto': nombre,
            **cotizacion,
            'tiempo_seg': specs[0],
            'material_cm2': specs[1],
            'energia_kwh': specs[2]
        }

        resultados.append(resultado)

    return resultados


@flow(name="Pipeline de Inferencia ONNX")
def pipeline_inferencia(
    model_path: str = "costos_cajas_laser.onnx",
    costo_kwh: float = 765.37,
    margen: float = 1.3
):
    """
    Flujo de inferencia usando el modelo ONNX exportado.

    Args:
        model_path: Ruta al modelo ONNX
        costo_kwh: Costo por kWh de EPM
        margen: Margen de valoración al mercado
    """
    print("=" * 60)
    print("SIMULADOR DE PRECIOS ANTIOQUIA 2026")
    print("=" * 60)

    # 1. Cargar modelo
    session, input_name = cargar_modelo_onnx(model_path)

    # 2. Definir productos para cotización
    productos = {
        "Caja 1 (Pequeña)": [360, 24, 0.025],
        "Caja 2 (Mediana)": [240, 26, 0.016],
        "Caja 3 (Grande)": [300, 48, 0.020]
    }

    # 3. Procesar cotizaciones
    resultados = procesar_cotizaciones(session, input_name, productos, margen)

    # 4. Mostrar resultados
    print("\n--- COTIZACIONES GENERADAS ---")
    for resultado in resultados:
        print(f"\n📦 {resultado['producto']}:")
        print(f"   Especificaciones:")
        print(f"     - Tiempo: {resultado['tiempo_seg']} segundos")
        print(f"     - Material: {resultado['material_cm2']} cm²")
        print(f"     - Energía: {resultado['energia_kwh']} kWh")
        print(f"   Costo de energía: ${costo_kwh * resultado['energia_kwh']:.2f} COP")
        print(f"   💰 Costo Producción: ${resultado['costo_produccion']:.2f} COP")
        print(f"   💵 Precio Sugerido: ${resultado['precio_detal']:.2f} COP")

    print("\n" + "=" * 60)
    print("INFERENCIA COMPLETADA")
    print("=" * 60)

    return resultados


@flow(name="Cotización personalizada")
def cotizacion_personalizada(
    tiempo_seg: float,
    material_cm2: float,
    energia_kwh: float,
    model_path: str = "costos_cajas_laser.onnx",
    margen: float = 1.3
):
    """
    Genera una cotización para un producto personalizado.

    Args:
        tiempo_seg: Tiempo de corte en segundos
        material_cm2: Área del material en cm²
        energia_kwh: Energía consumida en kWh
        model_path: Ruta al modelo ONNX
        margen: Margen de valoración al mercado
    """
    print("=" * 60)
    print("COTIZACIÓN PERSONALIZADA")
    print("=" * 60)

    # 1. Cargar modelo
    session, input_name = cargar_modelo_onnx(model_path)

    # 2. Realizar inferencia
    resultado = realizar_inferencia(
        session,
        input_name,
        tiempo_seg,
        material_cm2,
        energia_kwh,
        margen
    )

    # 3. Mostrar resultado
    print(f"\n📋 Especificaciones del producto:")
    print(f"   - Tiempo de corte: {tiempo_seg} segundos")
    print(f"   - Área de material: {material_cm2} cm²")
    print(f"   - Consumo energético: {energia_kwh} kWh")
    print(f"\n💰 Resultados:")
    print(f"   - Costo de Producción: ${resultado['costo_produccion']:.2f} COP")
    print(f"   - Precio de Venta Sugerido: ${resultado['precio_detal']:.2f} COP")
    print(f"   - Margen aplicado: {(margen - 1) * 100:.0f}%")

    print("\n" + "=" * 60)

    return resultado


if __name__ == "__main__":
    # Ejemplo 1: Inferencia con productos predefinidos
    print("\n🔷 EJEMPLO 1: Productos predefinidos")
    resultados_batch = pipeline_inferencia()

    # Ejemplo 2: Cotización personalizada
    print("\n\n🔷 EJEMPLO 2: Producto personalizado")
    cotizacion_custom = cotizacion_personalizada(
        tiempo_seg=450,
        material_cm2=35,
        energia_kwh=0.030
    )
"""
Script de diagnóstico para entender la estructura del modelo ONNX.
"""

import numpy as np
import onnxruntime as ort
import os

MODELO_ONNX_PATH = "costos_cajas_laser.onnx"

def diagnosticar_modelo():
    print("="*60)
    print("DIAGNÓSTICO DEL MODELO ONNX")
    print("="*60)

    # Verificar que existe
    if not os.path.exists(MODELO_ONNX_PATH):
        print(f"\n❌ ERROR: No se encuentra el archivo {MODELO_ONNX_PATH}")
        print("   Ejecuta: python modelo_laser_mlflow.py")
        return

    print(f"\n✅ Modelo encontrado: {MODELO_ONNX_PATH}")

    # Cargar modelo
    try:
        session = ort.InferenceSession(MODELO_ONNX_PATH)
        print("✅ Modelo cargado exitosamente")
    except Exception as e:
        print(f"❌ Error cargando modelo: {e}")
        return

    # Información de inputs
    print("\n" + "="*60)
    print("INPUTS DEL MODELO")
    print("="*60)

    for input_meta in session.get_inputs():
        print(f"\nNombre: {input_meta.name}")
        print(f"Shape: {input_meta.shape}")
        print(f"Tipo: {input_meta.type}")

    # Información de outputs
    print("\n" + "="*60)
    print("OUTPUTS DEL MODELO")
    print("="*60)

    for output_meta in session.get_outputs():
        print(f"\nNombre: {output_meta.name}")
        print(f"Shape: {output_meta.shape}")
        print(f"Tipo: {output_meta.type}")

    # Prueba de inferencia con datos de ejemplo (Caja 1 - Pequeña)
    print("\n" + "="*60)
    print("PRUEBA DE INFERENCIA")
    print("="*60)

    test_params = [360, 24, 0.025]  # Caja 1 (Pequeña)
    print(f"\nParámetros de prueba: {test_params}")
    print("  tiempo_seg: 360")
    print("  material_cm2: 24")
    print("  energia_kwh: 0.025")

    # Preparar input
    input_name = session.get_inputs()[0].name
    input_array = np.array([test_params], dtype=np.float32)

    print(f"\nInput array shape: {input_array.shape}")
    print(f"Input array dtype: {input_array.dtype}")
    print(f"Input array:\n{input_array}")

    # Ejecutar inferencia
    try:
        resultado = session.run(None, {input_name: input_array})

        print("\n" + "-"*60)
        print("RESULTADO DE LA INFERENCIA")
        print("-"*60)

        print(f"\nTipo de resultado: {type(resultado)}")
        print(f"Cantidad de outputs: {len(resultado)}")

        for i, output in enumerate(resultado):
            print(f"\nOutput {i}:")
            print(f"  Tipo: {type(output)}")
            print(f"  Shape: {output.shape if hasattr(output, 'shape') else 'N/A'}")
            print(f"  Dtype: {output.dtype if hasattr(output, 'dtype') else 'N/A'}")
            print(f"  Contenido:\n  {output}")

            # Intentar diferentes formas de extraer el valor
            print(f"\n  Intentando extraer valor escalar:")

            # Método 1: Direct indexing
            try:
                valor1 = output[0]
                print(f"    output[0]: {valor1} (tipo: {type(valor1)})")

                if hasattr(valor1, '__getitem__'):
                    valor2 = valor1[0]
                    print(f"    output[0][0]: {valor2} (tipo: {type(valor2)})")
            except Exception as e:
                print(f"    ❌ Error con indexing: {e}")

            # Método 2: Using .item()
            try:
                if hasattr(output, 'item'):
                    valor_item = output.item()
                    print(f"    output.item(): {valor_item} (tipo: {type(valor_item)})")
                elif hasattr(output[0], 'item'):
                    valor_item = output[0].item()
                    print(f"    output[0].item(): {valor_item} (tipo: {type(valor_item)})")
            except Exception as e:
                print(f"    ⚠️  .item() no disponible o falló: {e}")

            # Método 3: Using flat
            try:
                if hasattr(output, 'flat'):
                    valor_flat = next(output.flat)
                    print(f"    next(output.flat): {valor_flat} (tipo: {type(valor_flat)})")
            except Exception as e:
                print(f"    ⚠️  .flat falló: {e}")

            # Método 4: Using flatten
            try:
                if hasattr(output, 'flatten'):
                    valor_flatten = output.flatten()[0]
                    print(f"    output.flatten()[0]: {valor_flatten} (tipo: {type(valor_flatten)})")
            except Exception as e:
                print(f"    ⚠️  .flatten() falló: {e}")

        # Calcular precio con margen
        print("\n" + "="*60)
        print("CÁLCULO DE PRECIO")
        print("="*60)

        # Usar el método que funcione
        output = resultado[0]
        if hasattr(output, 'flatten'):
            costo_base = float(output.flatten()[0])
        elif hasattr(output, 'item'):
            costo_base = float(output.item())
        elif hasattr(output[0], 'item'):
            costo_base = float(output[0].item())
        else:
            costo_base = float(output[0][0])

        precio_mercado = costo_base * 1.3  # Margen del 30%

        print(f"\n✅ Costo de producción: ${costo_base:.2f} COP")
        print(f"✅ Precio al detal (30% margen): ${precio_mercado:.2f} COP")

    except Exception as e:
        print(f"\n❌ Error durante inferencia: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*60)
    print("FIN DEL DIAGNÓSTICO")
    print("="*60)

if __name__ == "__main__":
    diagnosticar_modelo()

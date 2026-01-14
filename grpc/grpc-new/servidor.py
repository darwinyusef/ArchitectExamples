import grpc
from concurrent import futures
import time

# Importar los archivos generados por protoc
import mensaje_pb2
import mensaje_pb2_grpc


class ServicioSaludoImpl(mensaje_pb2_grpc.ServicioSaludoServicer):
    """Implementación del servicio definido en el .proto"""

    def EnviarSaludo(self, request, context):
        """Método que recibe el saludo y responde"""
        nombre = request.nombre
        print(f"📩 Servidor recibió: {nombre}")

        # Crear y devolver la respuesta
        respuesta = mensaje_pb2.RespuestaSaludo()
        respuesta.mensaje = f"Hola {nombre}! Bienvenido a gRPC"

        return respuesta


def ejecutar_servidor():
    """Función que inicia el servidor gRPC"""
    # Crear el servidor
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Registrar el servicio
    mensaje_pb2_grpc.add_ServicioSaludoServicer_to_server(
        ServicioSaludoImpl(), servidor
    )

    # Configurar el puerto
    puerto = '50051'
    servidor.add_insecure_port(f'0.0.0.0:{puerto}')

    # Iniciar el servidor
    servidor.start()
    print(f"🚀 Servidor gRPC iniciado en el puerto {puerto}")
    print("⏳ Esperando conexiones...")

    try:
        # Mantener el servidor activo
        while True:
            time.sleep(86400)  # 24 horas
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servidor...")
        servidor.stop(0)


if __name__ == '__main__':
    ejecutar_servidor()

import grpc

# Importar los archivos generados por protoc
import mensaje_pb2
import mensaje_pb2_grpc


def ejecutar_cliente():
    """Función que ejecuta el cliente gRPC"""
    # Conectar al servidor
    canal = grpc.insecure_channel('localhost:50051')
    stub = mensaje_pb2_grpc.ServicioSaludoStub(canal)

    # Crear el mensaje a enviar
    solicitud = mensaje_pb2.SolicitudSaludo()
    solicitud.nombre = "Darwin"

    print(f"📤 Cliente enviando: {solicitud.nombre}")

    try:
        # Enviar la solicitud y recibir la respuesta
        respuesta = stub.EnviarSaludo(solicitud)
        print(f"📨 Cliente recibió: {respuesta.mensaje}")
    except grpc.RpcError as e:
        print(f"❌ Error: {e.details()}")
    finally:
        canal.close()


if __name__ == '__main__':
    ejecutar_cliente()

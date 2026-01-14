# Guía Básica de gRPC - Proyecto de Aprendizaje

## ¿Qué es gRPC?

gRPC es un framework de comunicación entre aplicaciones que permite que un cliente y un servidor se comuniquen de manera eficiente usando Protocol Buffers (protobuf).

## Estructura del Proyecto

```
grpc-unitem/
├── mensaje.proto          # Definición del servicio y mensajes
├── servidor.py            # Servidor gRPC
├── cliente.py             # Cliente gRPC
└── GUIA_GRPC_BASICO.md   # Esta guía
```

## Paso 1: Instalación de Dependencias

Instala las librerías necesarias de Python:

```bash
pip install grpcio grpcio-tools
```

**¿Qué instalamos?**
- `grpcio`: La librería principal de gRPC
- `grpcio-tools`: Herramientas para compilar archivos .proto

## Paso 2: Compilar el Archivo .proto

El archivo `mensaje.proto` define nuestro servicio y los mensajes. Necesitamos compilarlo para generar código Python:

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. mensaje.proto
```

**¿Qué hace este comando?**
- `-I.`: Indica que busque archivos .proto en el directorio actual
- `--python_out=.`: Genera el archivo con los mensajes (mensaje_pb2.py)
- `--grpc_python_out=.`: Genera el archivo con el servicio (mensaje_pb2_grpc.py)

**Resultado:** Se crearán dos archivos:
- `mensaje_pb2.py` - Contiene las clases para los mensajes
- `mensaje_pb2_grpc.py` - Contiene el servicio y el stub del cliente

## Paso 3: Iniciar el Servidor

En una terminal, ejecuta:

```bash
python servidor.py
```

Verás el mensaje:
```
🚀 Servidor gRPC iniciado en el puerto 50051
⏳ Esperando conexiones...
```

**El servidor está escuchando en el puerto 50051**

## Paso 4: Ejecutar el Cliente

En otra terminal (deja el servidor corriendo), ejecuta:

```bash
python cliente.py
```

### Resultado Esperado:

**En el cliente verás:**
```
📤 Cliente enviando: Darwin
📨 Cliente recibió: Hola Darwin! Bienvenido a gRPC
```

**En el servidor verás:**
```
📩 Servidor recibió: Darwin
```

## ¿Cómo Funciona?

### 1. Definición del Servicio (mensaje.proto)

```protobuf
service ServicioSaludo {
  rpc EnviarSaludo (SolicitudSaludo) returns (RespuestaSaludo) {}
}
```

- Define un servicio llamado `ServicioSaludo`
- Tiene un método `EnviarSaludo` que recibe `SolicitudSaludo` y devuelve `RespuestaSaludo`

### 2. El Servidor (servidor.py)

```python
class ServicioSaludoImpl(mensaje_pb2_grpc.ServicioSaludoServicer):
    def EnviarSaludo(self, request, context):
        # Procesa la solicitud y devuelve una respuesta
```

- Implementa el servicio definido en el .proto
- Escucha en el puerto 50051
- Recibe el nombre y responde con un saludo

### 3. El Cliente (cliente.py)

```python
canal = grpc.insecure_channel('localhost:50051')
stub = mensaje_pb2_grpc.ServicioSaludoStub(canal)
respuesta = stub.EnviarSaludo(solicitud)
```

- Conecta al servidor en localhost:50051
- Crea un stub (proxy) del servicio
- Llama al método `EnviarSaludo` y recibe la respuesta

## Flujo de Comunicación

```
Cliente                     Servidor
   |                           |
   |  1. Conecta al puerto     |
   |-------------------------->|
   |                           |
   |  2. EnviarSaludo("Darwin")|
   |-------------------------->|
   |                           |
   |    3. Procesa solicitud   |
   |                           |
   |  4. "Hola Darwin!..."     |
   |<--------------------------|
   |                           |
```

## Personalización

### Cambiar el nombre en el cliente

Edita `cliente.py` línea 14:

```python
solicitud.nombre = "TuNombre"  # Cambia esto
```

### Cambiar el mensaje de respuesta

Edita `servidor.py` línea 18:

```python
respuesta.mensaje = f"Tu mensaje personalizado para {nombre}"
```

## Comandos Rápidos

```bash
# 1. Instalar dependencias
pip install grpcio grpcio-tools

# 2. Compilar proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. mensaje.proto

# 3. En terminal 1 - Iniciar servidor
python servidor.py

# 4. En terminal 2 - Ejecutar cliente
python cliente.py
```

## Conceptos Clave

- **Protocol Buffers (.proto)**: Lenguaje para definir la estructura de datos
- **Servidor**: Implementa el servicio y escucha peticiones
- **Cliente**: Se conecta al servidor y hace llamadas RPC
- **Stub**: Objeto que representa el servicio en el cliente
- **Canal**: Conexión entre cliente y servidor

## Próximos Pasos

Una vez que funcione este ejemplo básico, puedes:

1. Agregar más campos a los mensajes
2. Crear múltiples métodos en el servicio
3. Implementar streaming (servidor/cliente)
4. Agregar autenticación
5. Usar gRPC con otros lenguajes

## Solución de Problemas

**Error: "No module named 'mensaje_pb2'"**
- Solución: Ejecuta el comando de compilación del paso 2

**Error: "failed to connect to all addresses"**
- Solución: Verifica que el servidor esté corriendo

**Puerto ocupado**
- Solución: Cambia el puerto en servidor.py y cliente.py

## Recursos Adicionales

- [Documentación oficial de gRPC](https://grpc.io/docs/)
- [Protocol Buffers Guide](https://protobuf.dev/)

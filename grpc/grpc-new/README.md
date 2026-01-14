# Proyecto Básico de gRPC

Proyecto de aprendizaje de gRPC con Python - Envío simple de un dato de extremo a extremo.

## Inicio Rápido

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Compilar el archivo proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. mensaje.proto

# 3. Ejecutar el servidor (en una terminal)
python servidor.py

# 4. Ejecutar el cliente (en otra terminal)
python cliente.py
```

## Documentación Completa

Lee [GUIA_GRPC_BASICO.md](GUIA_GRPC_BASICO.md) para una guía paso a paso detallada.

## Archivos del Proyecto

- `mensaje.proto` - Definición del servicio y mensajes Protocol Buffers
- `servidor.py` - Implementación del servidor gRPC
- `cliente.py` - Implementación del cliente gRPC
- `GUIA_GRPC_BASICO.md` - Guía completa paso a paso
- `requirements.txt` - Dependencias de Python
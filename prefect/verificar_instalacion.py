"""
Script de verificación de instalación del Sistema de Cotización Láser.
Verifica que todos los componentes estén correctamente configurados.
"""

import os
import sys
from pathlib import Path

# Colores para la terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(message):
    print(f"{Colors.GREEN}✓{Colors.END} {message}")

def print_error(message):
    print(f"{Colors.RED}✗{Colors.END} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠{Colors.END} {message}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ{Colors.END} {message}")

def print_header(message):
    print(f"\n{Colors.BOLD}{message}{Colors.END}")
    print("=" * 60)

def verificar_python():
    """Verifica la versión de Python."""
    print_header("Verificando Python")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version.major >= 3 and version.minor >= 9:
        print_success(f"Python {version_str} (requerido: Python 3.9+)")
        return True
    else:
        print_error(f"Python {version_str} - Se requiere Python 3.9 o superior")
        return False

def verificar_dependencias():
    """Verifica que las dependencias estén instaladas."""
    print_header("Verificando Dependencias")

    dependencias = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'onnxruntime': 'ONNX Runtime',
        'numpy': 'NumPy',
        'redis': 'Redis',
        'pydantic': 'Pydantic',
        'jinja2': 'Jinja2'
    }

    todos_ok = True

    for modulo, nombre in dependencias.items():
        try:
            __import__(modulo)
            print_success(f"{nombre} instalado")
        except ImportError:
            print_error(f"{nombre} NO instalado")
            todos_ok = False

    if not todos_ok:
        print_info("\nPara instalar las dependencias faltantes:")
        print_info("  pip install -r requirements_redis.txt")

    return todos_ok

def verificar_archivos():
    """Verifica que los archivos necesarios existan."""
    print_header("Verificando Archivos del Proyecto")

    archivos_requeridos = [
        ('api_fastapi_laser.py', 'API FastAPI principal', True),
        ('modelo_laser_mlflow.py', 'Script de entrenamiento', True),
        ('templates/index.html', 'Template HTML', True),
        ('static/css/styles.css', 'Estilos CSS', True),
        ('static/js/main.js', 'JavaScript principal', True),
        ('requirements_redis.txt', 'Archivo de dependencias', True),
        ('costos_cajas_laser.onnx', 'Modelo ONNX', False),  # Opcional, se genera
    ]

    todos_ok = True
    modelo_existe = False

    for archivo, descripcion, requerido in archivos_requeridos:
        path = Path(archivo)
        if path.exists():
            print_success(f"{descripcion}: {archivo}")
            if archivo == 'costos_cajas_laser.onnx':
                modelo_existe = True
        else:
            if requerido:
                print_error(f"{descripcion}: {archivo} NO ENCONTRADO")
                todos_ok = False
            else:
                print_warning(f"{descripcion}: {archivo} no encontrado (se generará)")

    if not modelo_existe:
        print_info("\nPara generar el modelo ONNX:")
        print_info("  python modelo_laser_mlflow.py")

    return todos_ok, modelo_existe

def verificar_estructura_directorios():
    """Verifica la estructura de directorios."""
    print_header("Verificando Estructura de Directorios")

    directorios = [
        ('templates', 'Directorio de templates Jinja2'),
        ('static', 'Directorio de archivos estáticos'),
        ('static/css', 'Directorio de estilos CSS'),
        ('static/js', 'Directorio de JavaScript'),
    ]

    todos_ok = True

    for directorio, descripcion in directorios:
        path = Path(directorio)
        if path.exists() and path.is_dir():
            print_success(f"{descripcion}: {directorio}/")
        else:
            print_error(f"{descripcion}: {directorio}/ NO EXISTE")
            todos_ok = False

    if not todos_ok:
        print_info("\nPara crear los directorios faltantes:")
        print_info("  mkdir -p templates static/css static/js")

    return todos_ok

def verificar_puertos():
    """Verifica que el puerto 8000 esté disponible."""
    print_header("Verificando Disponibilidad de Puertos")

    import socket

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        resultado = sock.connect_ex(('localhost', 8000))
        sock.close()

        if resultado == 0:
            print_warning("Puerto 8000 en uso - El servidor puede estar corriendo")
            print_info("  Si no está corriendo, usa: uvicorn api_fastapi_laser:app --port 8080")
            return False
        else:
            print_success("Puerto 8000 disponible")
            return True
    except Exception as e:
        print_warning(f"No se pudo verificar el puerto: {e}")
        return True

def verificar_redis():
    """Verifica la conexión a Redis (opcional)."""
    print_header("Verificando Redis (Opcional)")

    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

    try:
        import redis

        # Intentar conexión
        r = redis.from_url(redis_url, socket_connect_timeout=2, decode_responses=True)
        r.ping()
        print_success(f"Conectado a Redis: {redis_url}")
        return True
    except ImportError:
        print_warning("Biblioteca redis no instalada (opcional para pub/sub)")
        return False
    except Exception as e:
        print_warning(f"No se pudo conectar a Redis: {e}")
        print_info("Redis es opcional - La API REST funcionará sin él")
        return False

def main():
    """Función principal."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("   VERIFICACIÓN DE INSTALACIÓN")
    print("   Sistema de Cotización Láser con FastAPI + ONNX")
    print("=" * 60)
    print(Colors.END)

    resultados = {}

    # Ejecutar verificaciones
    resultados['python'] = verificar_python()
    resultados['dependencias'] = verificar_dependencias()
    resultados['estructura'] = verificar_estructura_directorios()
    resultados['archivos'], resultados['modelo'] = verificar_archivos()
    resultados['puertos'] = verificar_puertos()
    resultados['redis'] = verificar_redis()

    # Resumen
    print_header("Resumen de Verificación")

    checks = [
        ('Python 3.9+', resultados['python'], True),
        ('Dependencias', resultados['dependencias'], True),
        ('Estructura de directorios', resultados['estructura'], True),
        ('Archivos del proyecto', resultados['archivos'], True),
        ('Modelo ONNX', resultados['modelo'], False),
        ('Puerto disponible', resultados['puertos'], False),
        ('Redis', resultados['redis'], False),
    ]

    criticos_ok = True

    for nombre, resultado, critico in checks:
        estado = "✓" if resultado else ("✗" if critico else "⚠")
        color = Colors.GREEN if resultado else (Colors.RED if critico else Colors.YELLOW)
        tipo = " (CRÍTICO)" if critico and not resultado else " (opcional)" if not critico else ""

        print(f"{color}{estado}{Colors.END} {nombre}{tipo}")

        if critico and not resultado:
            criticos_ok = False

    print("\n" + "=" * 60)

    if criticos_ok and resultados['modelo']:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ Sistema listo para usar!{Colors.END}\n")
        print(f"{Colors.BOLD}Para iniciar el servidor:{Colors.END}")
        print("  python api_fastapi_laser.py")
        print("\nLuego accede a: http://localhost:8000")
        return 0

    elif criticos_ok and not resultados['modelo']:
        print(f"{Colors.YELLOW}{Colors.BOLD}⚠ Casi listo - Falta generar el modelo{Colors.END}\n")
        print(f"{Colors.BOLD}Pasos siguientes:{Colors.END}")
        print("1. Generar el modelo ONNX:")
        print("     python modelo_laser_mlflow.py")
        print("\n2. Iniciar el servidor:")
        print("     python api_fastapi_laser.py")
        print("\n3. Acceder a: http://localhost:8000")
        return 0

    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Faltan componentes críticos{Colors.END}\n")
        print(f"{Colors.BOLD}Pasos para resolver:{Colors.END}")

        if not resultados['dependencias']:
            print("\n1. Instalar dependencias:")
            print("     pip install -r requirements_redis.txt")

        if not resultados['estructura'] or not resultados['archivos']:
            print("\n2. Verificar que todos los archivos del proyecto estén presentes")

        print("\n3. Ejecutar este script nuevamente:")
        print("     python verificar_instalacion.py")

        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
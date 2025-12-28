#!/bin/bash
# Script de gestión del proyecto Python Concurrency Learning

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
print_banner() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  Python Concurrency Learning - Gestión Rápida             ║"
    echo "║  Concurrencia, Paralelismo, Grafana & Prometheus          ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Funciones de ayuda
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Verificar dependencias
check_dependencies() {
    log_info "Verificando dependencias..."

    # Python 3
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 no está instalado"
        exit 1
    fi
    log_success "Python 3: $(python3 --version)"

    # Docker (opcional)
    if command -v docker &> /dev/null; then
        log_success "Docker: $(docker --version)"
    else
        log_warning "Docker no instalado (opcional para Grafana/Prometheus)"
    fi

    # Docker Compose (opcional)
    if command -v docker-compose &> /dev/null; then
        log_success "Docker Compose: $(docker-compose --version)"
    else
        log_warning "Docker Compose no instalado (opcional)"
    fi
}

# Instalar dependencias Python
install_python_deps() {
    log_info "Instalando dependencias Python..."
    pip3 install -r requirements.txt
    log_success "Dependencias Python instaladas"
}

# Iniciar stack Docker (Grafana + Prometheus)
start_docker() {
    log_info "Iniciando stack Docker (Grafana + Prometheus)..."

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose no está instalado"
        log_info "Instalar con: apt-get install docker-compose"
        exit 1
    fi

    docker-compose up -d

    log_success "Stack Docker iniciado"
    echo ""
    log_info "Servicios disponibles:"
    echo "  - Grafana:      http://$(hostname -I | awk '{print $1}'):3000 (admin/admin)"
    echo "  - Prometheus:   http://$(hostname -I | awk '{print $1}'):9090"
    echo "  - Alertmanager: http://$(hostname -I | awk '{print $1}'):9093"
    echo ""
}

# Detener stack Docker
stop_docker() {
    log_info "Deteniendo stack Docker..."
    docker-compose stop
    log_success "Stack Docker detenido"
}

# Ver logs de Docker
logs_docker() {
    docker-compose logs -f
}

# Ejecutar todas las apps Python
start_python_apps() {
    log_info "Iniciando aplicaciones Python..."

    # Crear directorio para PIDs
    mkdir -p .pids

    # Race Conditions (puerto 8000)
    python3 advanced/race_conditions/01_race_conditions.py > logs/race_conditions.log 2>&1 &
    echo $! > .pids/race_conditions.pid
    log_success "Race Conditions iniciado (PID: $!, puerto 8000)"

    sleep 1

    # Locks (puerto 8001)
    python3 advanced/locks/02_locks_mutex.py > logs/locks.log 2>&1 &
    echo $! > .pids/locks.pid
    log_success "Locks iniciado (PID: $!, puerto 8001)"

    sleep 1

    # Deadlocks (puerto 8002)
    python3 advanced/deadlocks/03_deadlocks.py > logs/deadlocks.log 2>&1 &
    echo $! > .pids/deadlocks.pid
    log_success "Deadlocks iniciado (PID: $!, puerto 8002)"

    sleep 1

    # CPU Monitor (puerto 8003)
    python3 monitoring/cpu_monitor.py prometheus > logs/cpu_monitor.log 2>&1 &
    echo $! > .pids/cpu_monitor.pid
    log_success "CPU Monitor iniciado (PID: $!, puerto 8003)"

    echo ""
    log_success "Todas las aplicaciones Python iniciadas"
    log_info "Ver logs en: tail -f logs/*.log"
}

# Detener todas las apps Python
stop_python_apps() {
    log_info "Deteniendo aplicaciones Python..."

    if [ -d ".pids" ]; then
        for pidfile in .pids/*.pid; do
            if [ -f "$pidfile" ]; then
                pid=$(cat "$pidfile")
                if kill -0 "$pid" 2>/dev/null; then
                    kill "$pid"
                    log_success "Proceso $pid detenido"
                fi
                rm "$pidfile"
            fi
        done
        rmdir .pids 2>/dev/null || true
    fi

    # Backup: matar todos los procesos Python que exportan métricas
    pkill -f "race_conditions" || true
    pkill -f "locks_mutex" || true
    pkill -f "deadlocks" || true
    pkill -f "cpu_monitor" || true

    log_success "Aplicaciones Python detenidas"
}

# Ver status
status() {
    echo ""
    log_info "Estado de servicios:"
    echo ""

    # Docker
    echo -e "${YELLOW}Docker:${NC}"
    if command -v docker &> /dev/null; then
        docker-compose ps
    else
        echo "  Docker no instalado"
    fi

    echo ""

    # Python apps
    echo -e "${YELLOW}Aplicaciones Python:${NC}"
    if [ -d ".pids" ]; then
        for pidfile in .pids/*.pid; do
            if [ -f "$pidfile" ]; then
                pid=$(cat "$pidfile")
                name=$(basename "$pidfile" .pid)
                if kill -0 "$pid" 2>/dev/null; then
                    echo -e "  ${GREEN}✓${NC} $name (PID: $pid)"
                else
                    echo -e "  ${RED}✗${NC} $name (no corriendo)"
                fi
            fi
        done
    else
        echo "  No hay aplicaciones corriendo"
    fi

    echo ""

    # Puertos
    echo -e "${YELLOW}Puertos en uso:${NC}"
    netstat -tulpn 2>/dev/null | grep -E ':(3000|8000|8001|8002|8003|9090|9093)' || echo "  Ninguno"

    echo ""
}

# Ver logs de apps Python
logs_python() {
    if [ ! -d "logs" ]; then
        log_error "No hay logs disponibles"
        exit 1
    fi

    log_info "Mostrando logs (Ctrl+C para salir)..."
    tail -f logs/*.log
}

# Ejecutar demos
demo_basico() {
    log_info "Ejecutando demo básico..."
    python3 basics/01_threading_basics.py
    echo ""
    python3 basics/02_multiprocessing_basics.py
}

demo_completo() {
    log_info "Ejecutando demo completo..."
    python3 examples/demo_completo.py
}

demo_websocket() {
    log_info "Ejecutando servidor WebSocket..."
    log_info "Abre websockets/websocket_client.html en tu navegador"
    python3 websockets/websocket_server.py
}

# Setup completo
full_setup() {
    print_banner

    check_dependencies
    echo ""

    log_info "Instalando dependencias Python..."
    install_python_deps
    echo ""

    # Crear directorio de logs
    mkdir -p logs

    if command -v docker-compose &> /dev/null; then
        start_docker
        echo ""
        sleep 5  # Esperar a que Docker esté listo
    fi

    start_python_apps
    echo ""

    status
    echo ""

    log_success "Setup completo!"
    echo ""
    log_info "Próximos pasos:"
    echo "  1. Abre Grafana: http://$(hostname -I | awk '{print $1}'):3000"
    echo "  2. Login: admin / admin"
    echo "  3. Importa dashboard desde grafana/dashboards.json"
    echo "  4. Observa métricas en tiempo real"
    echo ""
    log_info "Comandos útiles:"
    echo "  ./run.sh status    - Ver estado"
    echo "  ./run.sh logs      - Ver logs"
    echo "  ./run.sh stop      - Detener todo"
    echo ""
}

# Detener todo
stop_all() {
    log_info "Deteniendo todos los servicios..."
    stop_python_apps
    echo ""

    if command -v docker-compose &> /dev/null; then
        stop_docker
    fi

    log_success "Todos los servicios detenidos"
}

# Limpiar todo
clean() {
    log_warning "Esto eliminará todos los datos y contenedores"
    read -p "¿Continuar? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        stop_all

        if command -v docker-compose &> /dev/null; then
            log_info "Eliminando contenedores y volúmenes..."
            docker-compose down -v
        fi

        log_info "Limpiando archivos..."
        rm -rf logs/* .pids

        log_success "Limpieza completa"
    fi
}

# Menú de ayuda
show_help() {
    print_banner
    echo "Uso: ./run.sh [comando]"
    echo ""
    echo "Comandos disponibles:"
    echo ""
    echo "  ${GREEN}setup${NC}          Setup completo (Docker + Python apps)"
    echo "  ${GREEN}start${NC}          Iniciar todas las apps"
    echo "  ${GREEN}stop${NC}           Detener todas las apps"
    echo "  ${GREEN}restart${NC}        Reiniciar todas las apps"
    echo "  ${GREEN}status${NC}         Ver estado de servicios"
    echo "  ${GREEN}logs${NC}           Ver logs en tiempo real"
    echo ""
    echo "  ${BLUE}docker-start${NC}   Iniciar solo Docker (Grafana/Prometheus)"
    echo "  ${BLUE}docker-stop${NC}    Detener Docker"
    echo "  ${BLUE}docker-logs${NC}    Ver logs de Docker"
    echo ""
    echo "  ${YELLOW}demo-basic${NC}     Ejecutar demos básicos"
    echo "  ${YELLOW}demo-full${NC}      Ejecutar demo completo"
    echo "  ${YELLOW}demo-ws${NC}        Ejecutar servidor WebSocket"
    echo ""
    echo "  ${RED}clean${NC}          Limpiar todo (⚠️  elimina datos)"
    echo "  ${RED}help${NC}           Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  ./run.sh setup          # Setup inicial completo"
    echo "  ./run.sh start          # Iniciar aplicaciones"
    echo "  ./run.sh status         # Ver qué está corriendo"
    echo "  ./run.sh logs           # Ver logs"
    echo ""
}

# Main
main() {
    case "${1:-help}" in
        setup)
            full_setup
            ;;
        start)
            start_python_apps
            ;;
        stop)
            stop_all
            ;;
        restart)
            stop_all
            sleep 2
            start_python_apps
            ;;
        status)
            status
            ;;
        logs)
            logs_python
            ;;
        docker-start)
            start_docker
            ;;
        docker-stop)
            stop_docker
            ;;
        docker-logs)
            logs_docker
            ;;
        demo-basic)
            demo_basico
            ;;
        demo-full)
            demo_completo
            ;;
        demo-ws)
            demo_websocket
            ;;
        clean)
            clean
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Comando desconocido: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Ejecutar
main "$@"

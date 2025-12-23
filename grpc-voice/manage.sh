#!/bin/bash

# Script de gestión para gRPC Voice Streaming
# Simplifica el manejo de diferentes configuraciones Docker Compose

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para imprimir con color
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "\n${BOLD}$1${NC}\n"
}

# Función de ayuda
show_help() {
    cat << EOF
${BOLD}Gestión de gRPC Voice Streaming${NC}

${BOLD}USO:${NC}
    ./manage.sh [comando] [opciones]

${BOLD}COMANDOS PRINCIPALES:${NC}

    ${GREEN}start [modo]${NC}
        Iniciar servicios en el modo especificado
        Modos disponibles:
            full        - Sistema completo (Backend + Frontend + RabbitMQ + Whisper + Envoy)
            dev         - Solo servicios (RabbitMQ + Whisper + Envoy)
            whisper     - Solo Whisper API
            basic       - Sistema sin Whisper (original)

    ${GREEN}stop [modo]${NC}
        Detener servicios del modo especificado
        Si no se especifica modo, detiene todos

    ${GREEN}restart [modo]${NC}
        Reiniciar servicios

    ${GREEN}logs [servicio]${NC}
        Ver logs
        Servicios: backend, frontend, whisper, rabbitmq, envoy

    ${GREEN}status${NC}
        Ver estado de todos los servicios

    ${GREEN}clean${NC}
        Limpiar contenedores, volúmenes e imágenes

    ${GREEN}health${NC}
        Verificar salud de todos los servicios

    ${GREEN}setup${NC}
        Configuración inicial (backend y frontend)

${BOLD}EJEMPLOS:${NC}

    # Iniciar sistema completo
    ./manage.sh start full

    # Iniciar solo servicios (desarrollo)
    ./manage.sh start dev

    # Ver logs del backend
    ./manage.sh logs backend

    # Verificar estado
    ./manage.sh status

    # Limpiar todo
    ./manage.sh clean

${BOLD}DESARROLLO LOCAL:${NC}

    # 1. Iniciar servicios
    ./manage.sh start dev

    # 2. Backend (terminal separada)
    cd backend && python main.py

    # 3. Frontend (terminal separada)
    cd frontend && npm run dev

EOF
}

# Función para iniciar servicios
start_services() {
    local mode=$1

    case $mode in
        full)
            print_header "🚀 Iniciando sistema completo..."
            print_info "Incluye: Backend + Frontend + RabbitMQ + Whisper + Envoy"
            docker-compose -f docker-compose.full.yml up -d
            print_info "✓ Sistema completo iniciado"
            show_urls
            ;;

        dev)
            print_header "🛠️  Iniciando servicios de desarrollo..."
            print_info "Incluye: RabbitMQ + Whisper + Envoy"
            docker-compose -f docker-compose.dev.yml up -d
            print_info "✓ Servicios iniciados"
            print_warn "Recuerda iniciar backend y frontend localmente:"
            echo "  cd backend && python main.py"
            echo "  cd frontend && npm run dev"
            ;;

        whisper)
            print_header "🎤 Iniciando Whisper API..."
            docker-compose -f docker-compose.whisper.yml up -d
            print_info "✓ Whisper API iniciado"
            echo "  Whisper API: http://localhost:9000"
            echo "  Docs: http://localhost:9000/docs"
            ;;

        basic)
            print_header "🚀 Iniciando sistema básico..."
            print_info "Incluye: Backend + Frontend + RabbitMQ + Envoy"
            print_warn "Requiere Whisper externo o configurado localmente"
            docker-compose up -d
            print_info "✓ Sistema básico iniciado"
            show_urls
            ;;

        *)
            print_error "Modo desconocido: $mode"
            echo "Modos disponibles: full, dev, whisper, basic"
            exit 1
            ;;
    esac
}

# Función para detener servicios
stop_services() {
    local mode=$1

    if [ -z "$mode" ]; then
        print_header "⏹️  Deteniendo todos los servicios..."
        docker-compose -f docker-compose.full.yml down 2>/dev/null || true
        docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
        docker-compose -f docker-compose.whisper.yml down 2>/dev/null || true
        docker-compose down 2>/dev/null || true
        print_info "✓ Todos los servicios detenidos"
        return
    fi

    case $mode in
        full)
            print_info "Deteniendo sistema completo..."
            docker-compose -f docker-compose.full.yml down
            ;;
        dev)
            print_info "Deteniendo servicios de desarrollo..."
            docker-compose -f docker-compose.dev.yml down
            ;;
        whisper)
            print_info "Deteniendo Whisper API..."
            docker-compose -f docker-compose.whisper.yml down
            ;;
        basic)
            print_info "Deteniendo sistema básico..."
            docker-compose down
            ;;
        *)
            print_error "Modo desconocido: $mode"
            exit 1
            ;;
    esac

    print_info "✓ Servicios detenidos"
}

# Función para ver logs
show_logs() {
    local service=$1

    if [ -z "$service" ]; then
        print_info "Mostrando logs de todos los servicios..."
        docker-compose -f docker-compose.full.yml logs -f --tail=100 2>/dev/null || \
        docker-compose -f docker-compose.dev.yml logs -f --tail=100 2>/dev/null || \
        docker-compose logs -f --tail=100
    else
        print_info "Mostrando logs de: $service"
        docker-compose -f docker-compose.full.yml logs -f --tail=100 $service 2>/dev/null || \
        docker-compose -f docker-compose.dev.yml logs -f --tail=100 $service 2>/dev/null || \
        docker-compose logs -f --tail=100 $service
    fi
}

# Función para ver estado
show_status() {
    print_header "📊 Estado de los servicios"

    echo -e "\n${BOLD}Docker Compose Full:${NC}"
    docker-compose -f docker-compose.full.yml ps 2>/dev/null || echo "  No activo"

    echo -e "\n${BOLD}Docker Compose Dev:${NC}"
    docker-compose -f docker-compose.dev.yml ps 2>/dev/null || echo "  No activo"

    echo -e "\n${BOLD}Docker Compose Whisper:${NC}"
    docker-compose -f docker-compose.whisper.yml ps 2>/dev/null || echo "  No activo"

    echo -e "\n${BOLD}Docker Compose Basic:${NC}"
    docker-compose ps 2>/dev/null || echo "  No activo"
}

# Función para mostrar URLs
show_urls() {
    print_header "🌐 Servicios disponibles"
    echo "  Frontend:       http://localhost:3000"
    echo "  Backend API:    http://localhost:8001"
    echo "  API Docs:       http://localhost:8001/docs"
    echo "  gRPC Server:    localhost:50051"
    echo "  RabbitMQ UI:    http://localhost:15672 (guest/guest)"
    echo "  Whisper API:    http://localhost:9000"
    echo "  Whisper Docs:   http://localhost:9000/docs"
    echo "  Envoy (gRPC-Web): http://localhost:8080"
    echo "  Envoy Admin:    http://localhost:9901"
}

# Función para verificar salud
check_health() {
    print_header "🏥 Verificando salud de servicios"

    services=(
        "http://localhost:8001/health|Backend API"
        "http://localhost:3000|Frontend"
        "http://localhost:15672|RabbitMQ"
        "http://localhost:9000/health|Whisper API"
        "http://localhost:9901/ready|Envoy"
    )

    for service in "${services[@]}"; do
        IFS='|' read -r url name <<< "$service"

        if curl -sf "$url" > /dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} $name"
        else
            echo -e "  ${RED}✗${NC} $name"
        fi
    done
}

# Función para limpiar
clean_all() {
    print_header "🧹 Limpiando servicios..."

    read -p "¿Eliminar volúmenes también? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Deteniendo y eliminando contenedores, volúmenes e imágenes..."
        docker-compose -f docker-compose.full.yml down -v --rmi local 2>/dev/null || true
        docker-compose -f docker-compose.dev.yml down -v --rmi local 2>/dev/null || true
        docker-compose -f docker-compose.whisper.yml down -v --rmi local 2>/dev/null || true
        docker-compose down -v --rmi local 2>/dev/null || true
    else
        print_info "Deteniendo y eliminando solo contenedores..."
        docker-compose -f docker-compose.full.yml down 2>/dev/null || true
        docker-compose -f docker-compose.dev.yml down 2>/dev/null || true
        docker-compose -f docker-compose.whisper.yml down 2>/dev/null || true
        docker-compose down 2>/dev/null || true
    fi

    print_info "✓ Limpieza completada"
}

# Función para setup inicial
setup_project() {
    print_header "🔧 Configurando proyecto..."

    # Backend
    if [ ! -d "backend/venv" ]; then
        print_info "Configurando backend..."
        cd backend
        chmod +x setup.sh
        ./setup.sh
        cd ..
    else
        print_info "Backend ya configurado"
    fi

    # Frontend
    if [ ! -d "frontend/node_modules" ]; then
        print_info "Configurando frontend..."
        cd frontend
        npm install
        cd ..
    else
        print_info "Frontend ya configurado"
    fi

    print_info "✓ Setup completado"
}

# Main
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    case $1 in
        start)
            if [ -z "$2" ]; then
                print_error "Especifica un modo: full, dev, whisper, basic"
                exit 1
            fi
            start_services $2
            ;;
        stop)
            stop_services $2
            ;;
        restart)
            stop_services $2
            sleep 2
            start_services $2
            ;;
        logs)
            show_logs $2
            ;;
        status)
            show_status
            ;;
        health)
            check_health
            ;;
        clean)
            clean_all
            ;;
        setup)
            setup_project
            ;;
        urls)
            show_urls
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Comando desconocido: $1"
            echo "Usa './manage.sh help' para ver la ayuda"
            exit 1
            ;;
    esac
}

main "$@"

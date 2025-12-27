.PHONY: help setup install start stop restart logs clean test jupyter

# Colores para output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Mostrar ayuda
	@echo "========================================="
	@echo "Spark MLflow Learning - Comandos"
	@echo "========================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

setup: ## Setup completo del proyecto
	@echo "$(GREEN)Configurando proyecto...$(NC)"
	@chmod +x scripts/*.sh
	@./scripts/setup.sh

install: ## Instalar dependencias Python
	@echo "$(GREEN)Instalando dependencias...$(NC)"
	@pip install -r requirements.txt
	@echo "$(GREEN)✓ Dependencias instaladas$(NC)"

start: ## Iniciar servicios (MLflow, PostgreSQL, Airflow)
	@echo "$(GREEN)Iniciando servicios...$(NC)"
	@docker-compose up -d
	@echo ""
	@echo "$(GREEN)Esperando a que los servicios estén listos...$(NC)"
	@sleep 10
	@make status

stop: ## Detener servicios
	@echo "$(YELLOW)Deteniendo servicios...$(NC)"
	@docker-compose down
	@echo "$(GREEN)✓ Servicios detenidos$(NC)"

restart: ## Reiniciar servicios
	@make stop
	@make start

status: ## Ver estado de los servicios
	@echo "$(GREEN)Estado de los servicios:$(NC)"
	@docker-compose ps
	@echo ""
	@echo "Servicios disponibles:"
	@echo "  • MLflow UI:      http://localhost:5000"
	@echo "  • Airflow UI:     http://localhost:8080 (admin/admin)"
	@echo "  • PgAdmin:        http://localhost:5050"
	@echo "  • PostgreSQL:     localhost:5432"

logs: ## Ver logs de todos los servicios
	@docker-compose logs -f

logs-mlflow: ## Ver logs de MLflow
	@docker-compose logs -f mlflow

logs-airflow: ## Ver logs de Airflow
	@docker-compose logs -f airflow-webserver airflow-scheduler

logs-postgres: ## Ver logs de PostgreSQL
	@docker-compose logs -f postgres

clean: ## Limpiar archivos temporales
	@echo "$(YELLOW)Limpiando archivos temporales...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.log" -delete 2>/dev/null || true
	@rm -f *.db derby.log 2>/dev/null || true
	@rm -rf metastore_db spark-warehouse 2>/dev/null || true
	@echo "$(GREEN)✓ Limpieza completada$(NC)"

clean-all: clean ## Limpiar todo (incluyendo volúmenes Docker)
	@echo "$(RED)⚠ ADVERTENCIA: Esto eliminará todos los datos en PostgreSQL y MLflow$(NC)"
	@echo "¿Estás seguro? [y/N] " && read ans && [ $${ans:-N} = y ]
	@docker-compose down -v
	@echo "$(GREEN)✓ Todo limpiado$(NC)"

jupyter: ## Iniciar Jupyter Notebook
	@echo "$(GREEN)Iniciando Jupyter Notebook...$(NC)"
	@jupyter notebook

test: ## Ejecutar tests básicos
	@echo "$(GREEN)Ejecutando tests...$(NC)"
	@python -c "import pyspark; print('✓ PySpark:', pyspark.__version__)"
	@python -c "import mlflow; print('✓ MLflow:', mlflow.__version__)"
	@python -c "import torch; print('✓ PyTorch:', torch.__version__)"
	@python -c "import tensorflow; print('✓ TensorFlow:', tensorflow.__version__)"
	@python -c "import sklearn; print('✓ Scikit-learn:', sklearn.__version__)"
	@echo "$(GREEN)✓ Todas las dependencias están instaladas correctamente$(NC)"

env: ## Crear archivo .env desde .env.example
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✓ Archivo .env creado$(NC)"; \
		echo "$(YELLOW)⚠ Revisa y edita .env con tus configuraciones$(NC)"; \
	else \
		echo "$(YELLOW)⚠ .env ya existe$(NC)"; \
	fi

db-connect: ## Conectar a PostgreSQL CLI
	@docker-compose exec postgres psql -U spark_user -d spark_ml_db

mlflow-ui: ## Abrir MLflow UI en el navegador
	@echo "$(GREEN)Abriendo MLflow UI...$(NC)"
	@open http://localhost:5000 || xdg-open http://localhost:5000 || echo "Abre manualmente: http://localhost:5000"

airflow-ui: ## Abrir Airflow UI en el navegador
	@echo "$(GREEN)Abriendo Airflow UI...$(NC)"
	@open http://localhost:8080 || xdg-open http://localhost:8080 || echo "Abre manualmente: http://localhost:8080"

pgadmin-ui: ## Abrir PgAdmin UI en el navegador
	@echo "$(GREEN)Abriendo PgAdmin UI...$(NC)"
	@open http://localhost:5050 || xdg-open http://localhost:5050 || echo "Abre manualmente: http://localhost:5050"

init: setup install env start ## Inicialización completa (setup + install + start)
	@echo ""
	@echo "$(GREEN)=========================================$(NC)"
	@echo "$(GREEN)✓ Inicialización completada!$(NC)"
	@echo "$(GREEN)=========================================$(NC)"
	@echo ""
	@echo "Siguiente paso: ejecuta 'make jupyter' para abrir los notebooks"

all: init ## Alias para init

.DEFAULT_GOAL := help

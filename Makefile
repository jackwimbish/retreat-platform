.PHONY: help build up down logs init shell-backend shell-frontend clean restart

# Default target
help:
	@echo "Available commands:"
	@echo "  make build        - Build Docker images"
	@echo "  make up          - Start all services"
	@echo "  make down        - Stop all services"
	@echo "  make logs        - View logs (Ctrl+C to exit)"
	@echo "  make init        - Run initialization scripts"
	@echo "  make shell-backend - Open shell in backend container"
	@echo "  make shell-frontend - Open shell in frontend container"
	@echo "  make clean       - Stop services and remove volumes"
	@echo "  make restart     - Restart all services"

# Build Docker images
build:
	docker-compose build

# Start services
up:
	docker-compose up -d
	@echo "Services starting..."
	@echo "Backend: http://localhost:8080/Plone"
	@echo "Frontend: http://localhost:3000"
	@echo "Use 'make logs' to view logs"

# Stop services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Run initialization scripts
init:
	@echo "Stopping backend to run initialization..."
	docker-compose stop backend
	@echo "Running initialization scripts..."
	docker-compose run --rm backend python /app/init_all.py
	@echo "Starting backend again..."
	docker-compose up -d backend

# Open shell in backend container
shell-backend:
	docker-compose exec backend /bin/bash

# Open shell in frontend container  
shell-frontend:
	docker-compose exec frontend /bin/bash

# Clean everything (including volumes)
clean:
	docker-compose down -v
	@echo "Stopped services and removed volumes"

# Restart services
restart:
	docker-compose restart
	@echo "Services restarted"

# Development shortcuts
dev: up logs

# Check if services are running
status:
	docker-compose ps

# Run a specific setup script
run-script:
	@read -p "Enter script name (e.g., setup_user_roles_fixed.py): " script; \
	echo "Stopping backend to run script..."; \
	docker-compose stop backend; \
	docker-compose run --rm backend bash -c "cd /app/instance && zconsole run etc/zope.conf /app/$$script"; \
	echo "Starting backend again..."; \
	docker-compose up -d backend
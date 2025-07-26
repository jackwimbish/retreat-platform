# Docker Setup for Camp Coordinator

This Docker setup allows you to run the entire Camp Coordinator platform with a single command.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)
- `.env` file configured (see below)

## Quick Start

1. **Copy and configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

2. **Build and start the services:**
   ```bash
   make build
   make up
   ```

3. **Wait for services to start, then initialize the site:**
   ```bash
   # Check that backend is running
   make status
   
   # Run initialization (this will temporarily stop the backend)
   make init
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8080/Plone
   - Admin login: admin/admin

## Available Commands

```bash
make help          # Show all available commands
make build         # Build Docker images
make up            # Start all services
make down          # Stop all services
make logs          # View logs (Ctrl+C to exit)
make init          # Run initialization scripts
make shell-backend # Open shell in backend container
make shell-frontend # Open shell in frontend container
make clean         # Stop services and remove all data
make restart       # Restart all services
```

## Development Workflow

### Starting Development
```bash
make up     # Start services in background
make logs   # Watch logs in foreground
```

### Running Individual Setup Scripts
```bash
make run-script
# Enter script name when prompted, e.g.: setup_user_roles_fixed.py
```

### Making Code Changes
- **Frontend**: Changes in `frontend/src` are automatically hot-reloaded
- **Backend**: Most Python changes require restarting: `make restart`

### Accessing Container Shells
```bash
make shell-backend  # Access backend container
make shell-frontend # Access frontend container
```

## Initialization Scripts

The `make init` command runs these scripts in order:
1. `setup_content_types.py` - Creates Issue and Participant content types
2. `setup_user_roles_fixed.py` - Configures roles and permissions
3. `protect_homepage_simple.py` - Sets homepage permissions
4. `setup_default_content.py` - Creates default folders and content
5. `switch_to_one_state_workflow.py` - Simplifies workflow for issues

It also attempts to install the OIDC plugin automatically.

## Manual OIDC Setup (if automatic installation fails)

1. Access: http://localhost:8080/Plone/prefs_install_products_form
2. Login as admin/admin
3. Check "OAuth2/OIDC Authentication"
4. Click "Install"
5. Configure at: http://localhost:8080/Plone/@@oidc-controlpanel

## Troubleshooting

### Services won't start
```bash
make down
make clean
make build
make up
```

### Backend can't connect to database
The first start might take longer. Wait 60 seconds before running `make init`.

### Frontend hot reload not working
```bash
make restart
```

### Permission errors
If you see permission errors, ensure Docker Desktop has file sharing enabled for your project directory.

## Data Persistence

Data is stored in Docker volumes:
- `plone-filestorage`: Plone database
- `plone-blobstorage`: Uploaded files and portraits

To completely reset:
```bash
make clean  # This removes all data!
```

## Running Without Docker

The traditional setup still works:
```bash
# Backend
cd backend
source venv/bin/activate
python start_plone.py

# Frontend
cd frontend
yarn start
```

## Production Deployment

For production, create a `docker-compose.prod.yml` with:
- No volume mounts for source code
- Production environment variables
- SSL/TLS configuration
- Proper secrets management
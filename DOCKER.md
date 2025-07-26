# Docker Setup for Camp Coordinator

This document describes how to run the Camp Coordinator application using Docker.

## Prerequisites

- Docker and Docker Compose installed
- Port 3000 (frontend) and 8080 (backend) available

## Quick Start

```bash
# Build the containers
make build

# Start the services
make start

# Initialize the site with default content (first time only)
make init

# View logs
make logs

# Stop the services
make stop

# Clean up everything (including volumes)
make clean
```

## Access Points

After starting the services:

- **Frontend (Volto)**: http://localhost:3000
- **Backend API**: http://localhost:8080/Plone/++api++
- **Backend Classic UI**: http://localhost:8080/Plone
- **Default login**: admin/admin

## Architecture

The Docker setup consists of:

1. **Backend Container**:
   - Plone 6.1 with custom retreat package
   - Python 3.11
   - ZODB file storage
   - Automatic site initialization

2. **Frontend Container**:
   - Volto (React-based UI)
   - Node.js 18
   - Production build (no hot-reloading in Docker)
   - Connected to backend via internal network

## Development Notes

### Hot Reloading
Hot reloading is disabled in the Docker setup to avoid webpack-dev-server networking complexities. 
For development with hot reloading, run the frontend locally:

```bash
cd frontend
yarn start
```

### Customizations
- Custom content types (Issue)
- Google OAuth integration
- Email notifications with Resend
- User role management
- Public portrait endpoint for authenticated users

### Volumes
- `plone-filestorage`: Persistent database storage
- `plone-blobstorage`: File/image storage

### Environment Variables
Create a `.env` file in the backend directory with:
```
RESEND_API_KEY=your_resend_api_key_here
```

## Troubleshooting

### Frontend showing classic Plone UI
This usually means plone.volto isn't installed. Run:
```bash
make init
```

### Port conflicts
If ports 3000 or 8080 are in use, modify the port mappings in `docker-compose.yml`.

### Permission errors
The Docker containers run as root internally. File permissions are handled automatically.

### Rebuild after code changes
```bash
make build
make restart
```
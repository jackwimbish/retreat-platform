# Plone Backend Setup

This backend runs Plone 6.1 with Volto support and includes automatic initialization.

## Prerequisites

- Python 3.8+ 
- virtualenv

## Initial Setup

1. Create and activate virtualenv:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install Plone:
```bash
pip install Plone==6.1.0 plone.restapi waitress
```

## Running Plone

Simply run the start script:

```bash
./start_plone.py
```

This script will automatically:
- Create the Plone instance if it doesn't exist
- Initialize a new Plone site with Volto support
- Configure CORS for the frontend
- Start the server with all necessary settings

## What Happens on First Run

1. Creates a WSGI instance with admin/admin credentials
2. Creates a Plone site named "Plone" with:
   - Title: "Retreat Platform"
   - Volto frontend support enabled
   - REST API enabled
   - CORS configured for http://localhost:3000

## Access Points

- Backend UI: http://localhost:8080/Plone (limited when Volto is enabled)
- REST API: http://localhost:8080/Plone/++api++/
- Frontend: http://localhost:3000 (Volto)
- Admin credentials: admin/admin

## Manual Commands

If you need to run commands manually:

```bash
# Start server only (no auto-init)
cd instance
source ../venv/bin/activate
CORS_ALLOW_ORIGIN='http://localhost:3000' runwsgi etc/zope.ini

# Run console commands
cd instance
source ../venv/bin/activate
zconsole run etc/zope.conf your_script.py
```

## Resetting Everything

To start fresh:
```bash
rm -rf instance/var
./start_plone.py
```

This will create a new database and reinitialize everything.
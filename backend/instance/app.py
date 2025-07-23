#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Simple Plone 6.1 instance runner"""

import os
import sys
from pathlib import Path

# Add instance directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configuration
INSTANCE_HOME = Path(__file__).parent
DATA_DIR = INSTANCE_HOME / "var"
FILESTORAGE_DIR = DATA_DIR / "filestorage"
BLOBSTORAGE_DIR = DATA_DIR / "blobstorage"

# Create directories
FILESTORAGE_DIR.mkdir(parents=True, exist_ok=True)
BLOBSTORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Configure Zope
import Zope2
from Testing.makerequest import makerequest
from AccessControl.SecurityManagement import newSecurityManager

# Set up configuration
os.environ.update({
    'INSTANCE_HOME': str(INSTANCE_HOME),
    'ZOPE_CONF': '',
    'EVENT_LOG_FILE': '',
})

def create_app():
    """Create Plone application"""
    # Configure database
    from ZODB import DB
    from ZODB.FileStorage import FileStorage
    from ZODB.blob import BlobStorage
    
    storage = FileStorage(str(FILESTORAGE_DIR / 'Data.fs'))
    blob_storage = BlobStorage(str(BLOBSTORAGE_DIR), storage)
    db = DB(blob_storage)
    
    # Get Zope app
    conn = db.open()
    app = conn.root()['Application']
    
    # Check if Plone site exists
    if 'Plone' not in app:
        print("Creating Plone site...")
        # Add Plone site
        from Products.CMFPlone.factory import addPloneSite
        app = makerequest(app)
        # Set up security
        acl_users = app.acl_users
        user = acl_users.getUserById('admin')
        if user is None:
            acl_users._doAddUser('admin', 'admin', ['Manager'], [])
            user = acl_users.getUserById('admin')
        newSecurityManager(None, user)
        
        # Create site
        addPloneSite(
            app,
            'Plone',
            title='Retreat Platform',
            profile_id='plone.volto:default',
            extension_ids=['plone.restapi:default'],
            default_language='en',
        )
        
        import transaction
        transaction.commit()
        print("Plone site created!")
    
    return app

def configure_cors(app):
    """Configure CORS for Volto"""
    plone = app.Plone
    registry = plone.portal_registry
    
    # CORS settings
    cors_settings = {
        'plone.rest.cors_enabled': True,
        'plone.rest.cors_allow_origin': ['http://localhost:3000'],
        'plone.rest.cors_allow_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
        'plone.rest.cors_allow_credentials': True,
        'plone.rest.cors_allow_headers': ['Accept', 'Content-Type', 'Authorization'],
        'plone.rest.cors_expose_headers': ['Content-Length', 'X-My-Header'],
        'plone.rest.cors_max_age': 3600,
    }
    
    for key, value in cors_settings.items():
        if key in registry:
            registry[key] = value
    
    import transaction
    transaction.commit()
    print("CORS configured for Volto!")

def main():
    """Main entry point"""
    print("Starting Plone 6.1...")
    
    # Create app
    app = create_app()
    
    # Configure CORS
    app = makerequest(app)
    acl_users = app.acl_users
    user = acl_users.getUserById('admin')
    if user:
        newSecurityManager(None, user)
    configure_cors(app)
    
    # Run server
    from waitress import serve
    from plone.rest import router
    
    # Create WSGI app
    def application(environ, start_response):
        # Set Zope globals
        import Zope2
        Zope2.startup()
        app = Zope2.app()
        
        # Handle request
        from ZPublisher.WSGIPublisher import publish_module
        return publish_module(environ, start_response)
    
    print("\\nPlone is running at http://localhost:8080")
    print("Admin credentials: admin/admin")
    print("API endpoint: http://localhost:8080/Plone/++api++/")
    print("\\nPress Ctrl+C to stop the server")
    
    serve(application, host='0.0.0.0', port=8080)

if __name__ == '__main__':
    main()
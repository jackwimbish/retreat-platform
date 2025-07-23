#!/usr/bin/env python
"""Create Plone site using Zope console"""

# This script should be run with:
# bin/zconsole run create_site.py

from AccessControl.SecurityManagement import newSecurityManager
from Testing.makerequest import makerequest
import transaction

# Get the Zope app
app = globals()['app']
app = makerequest(app)

# Login as admin
acl_users = app.acl_users
user = acl_users.getUserById('admin')
if user is None:
    print("Creating admin user...")
    acl_users._doAddUser('admin', 'admin', ['Manager'], [])
    user = acl_users.getUserById('admin')
newSecurityManager(None, user)

# Check if Plone site already exists
if 'Plone' in app.objectIds():
    print("Plone site already exists!")
else:
    print("Creating Plone site...")
    
    # Import the site creation function
    from Products.CMFPlone.factory import addPloneSite
    
    # Create the site with Products.CMFPlone:plone profile
    site = addPloneSite(
        app,
        'Plone',
        title='Retreat Platform',
        description='Retreat Experience Platform',
        profile_id='Products.CMFPlone:plone',
        extension_ids=['plone.restapi:default'],
        default_language='en',
        setup_content=False
    )
    
    # Commit the transaction
    transaction.commit()
    print("✓ Plone site created successfully!")
    print("URL: http://localhost:8080/Plone")
    print("API: http://localhost:8080/Plone/++api++/")
    print("Admin: admin/admin")

# Configure CORS
print("\nConfiguring CORS...")
if 'Plone' in app.objectIds():
    plone = app.Plone
    from plone.registry.interfaces import IRegistry
    from zope.component import getUtility
    
    registry = getUtility(IRegistry, context=plone)
    
    # Set CORS configuration
    cors_settings = {
        'plone.cors_enabled': True,
        'plone.allowed_cors_origins': ['http://localhost:3000'],
        'plone.cors_allow_methods': ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT'],
        'plone.cors_allow_credentials': True,
        'plone.cors_allow_headers': ['Accept', 'Authorization', 'Content-Type'],
        'plone.cors_expose_headers': ['Content-Length', 'X-My-Header'],
        'plone.cors_max_age': 3600
    }
    
    for key, value in cors_settings.items():
        try:
            registry[key] = value
            print(f"✓ Set {key}")
        except KeyError:
            print(f"✗ Could not set {key} - key not found")
    
    transaction.commit()
    print("\n✓ CORS configuration complete!")
    print("Volto can now connect to http://localhost:8080/Plone/++api++/")
"""
Automatic site initialization for Plone
This module is imported by a custom WSGI application to set up the site automatically
"""

import os
import transaction
from AccessControl.SecurityManagement import newSecurityManager
from Testing.makerequest import makerequest
from Products.CMFPlone.factory import addPloneSite
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


def initialize_plone_site(app):
    """Initialize Plone site with Volto configuration"""
    
    # Check if initialization is needed
    if 'Plone' in app.objectIds():
        print("Plone site already exists")
        return
    
    print("Initializing new Plone site...")
    
    # Make request
    app = makerequest(app)
    
    # Login as admin
    acl_users = app.acl_users
    user = acl_users.getUserById('admin')
    if user is None:
        print("Creating admin user...")
        acl_users._doAddUser('admin', 'admin', ['Manager'], [])
        user = acl_users.getUserById('admin')
    newSecurityManager(None, user)
    
    # Create site with classic profile first
    print("Creating Plone site...")
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
    
    # Install Volto support
    print("Installing Volto support...")
    from Products.CMFCore.utils import getToolByName
    setup_tool = getToolByName(site, 'portal_setup')
    
    # Set site as local site manager first
    from zope.site.hooks import setSite
    setSite(site)
    
    # Now install Volto
    try:
        setup_tool.runAllImportStepsFromProfile('profile-plone.volto:default')
        print("✓ Volto support installed")
    except Exception as e:
        print(f"Warning: Could not install Volto profile: {e}")
    
    # Configure CORS using environment variables
    print("Configuring CORS...")
    cors_origin = os.environ.get('CORS_ALLOW_ORIGIN', 'http://localhost:3000')
    
    # Commit changes
    transaction.commit()
    
    print("\n✓ Site initialization complete!")
    print(f"Site URL: http://localhost:8080/Plone")
    print(f"API URL: http://localhost:8080/Plone/++api++/")
    print(f"Admin credentials: admin/admin")
    print(f"CORS configured for: {cors_origin}")
    
    return site
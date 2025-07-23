#!/usr/bin/env python
"""Install Volto add-on in the Plone site"""

from AccessControl.SecurityManagement import newSecurityManager
from Testing.makerequest import makerequest
import transaction

# Get the Zope app
app = globals()['app']
app = makerequest(app)

# Login as admin
acl_users = app.acl_users
user = acl_users.getUserById('admin')
if user:
    newSecurityManager(None, user)

# Get Plone site
if 'Plone' in app.objectIds():
    plone = app.Plone
    
    # Get the addon installer using the modern method
    from Products.CMFCore.utils import getToolByName
    from Products.GenericSetup.tool import SetupTool
    
    setup_tool = getToolByName(plone, 'portal_setup')
    
    # Check if plone.volto profile is already installed
    profile_id = 'plone.volto:default'
    installed = setup_tool.getLastVersionForProfile(profile_id) != 'unknown'
    
    if not installed:
        print("Installing plone.volto...")
        setup_tool.runAllImportStepsFromProfile('profile-%s' % profile_id)
        transaction.commit()
        print("✓ plone.volto installed successfully!")
    else:
        print("plone.volto is already installed")
    
    print("\nVolto support is now enabled!")
    print("The Plone backend is configured for Volto")
    print("Access your site at: http://localhost:3000")
else:
    print("Error: Plone site not found")
#!/usr/bin/env python
# Script to create or update the alerts folder in Plone

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import transaction
from plone import api
from AccessControl.SecurityManagement import newSecurityManager
from Testing.makerequest import makerequest

# Setup Zope environment
app = makerequest(app)
plone = app.Plone
newSecurityManager(None, plone.acl_users.getUser('admin'))

# Check if alerts folder exists
if 'alerts' not in plone.objectIds():
    # Create alerts folder
    plone.invokeFactory('Document', 'alerts',
                       title='Camp Alerts',
                       description='Emergency alerts and announcements')
    alerts_folder = plone['alerts']
    
    # Set permissions for alerts folder - staff can manage, everyone can view
    folder_permissions = [
        ('View', ['Manager', 'Editor', 'Member', 'Authenticated']),
        ('Access contents information', ['Manager', 'Editor', 'Member', 'Authenticated']),
        ('Add portal content', ['Manager', 'Editor']),
        ('retreat.AddCampAlert', ['Manager', 'Editor']),
    ]
    
    for permission, roles in folder_permissions:
        alerts_folder.manage_permission(permission, roles=roles, acquire=False)
    
    transaction.commit()
    print('✓ Alerts folder created successfully')
else:
    # Update permissions if folder exists
    alerts_folder = plone['alerts']
    folder_permissions = [
        ('View', ['Manager', 'Editor', 'Member', 'Authenticated']),
        ('Access contents information', ['Manager', 'Editor', 'Member', 'Authenticated']),
        ('Add portal content', ['Manager', 'Editor']),
        ('retreat.AddCampAlert', ['Manager', 'Editor']),
    ]
    
    for permission, roles in folder_permissions:
        alerts_folder.manage_permission(permission, roles=roles, acquire=False)
    
    transaction.commit()
    print('✓ Alerts folder permissions updated')

print('Done!')
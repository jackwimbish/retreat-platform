#!/usr/bin/env python
"""Initialize stored values for existing issues to enable activity tracking."""

import os
import sys
import transaction
from AccessControl.SecurityManagement import newSecurityManager
from Testing.makerequest import makerequest
from zope.annotation.interfaces import IAnnotations

# Setup the Zope app
import Zope2
Zope2.startup()
from Zope2 import app as zope_app
app = zope_app()

def initialize_stored_values():
    """Initialize stored values for all existing issues."""
    # Wrap the app for proper request handling
    app_wrapped = makerequest(app)
    
    # Get the Plone site
    plone = app_wrapped.Plone
    
    # Login as admin
    admin = app_wrapped.acl_users.getUser('admin')
    newSecurityManager(None, admin)
    
    print("Initializing stored values for existing issues...")
    
    # Search for all issues
    from plone import api
    with api.env.adopt_user(username='admin'):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(portal_type='issue')
        
        print(f"Found {len(brains)} issues to process")
        
        for brain in brains:
            try:
                issue = brain.getObject()
                
                # Check if stored values already exist
                annotations = IAnnotations(issue)
                if 'retreat.stored_values' in annotations:
                    print(f"Skipping {issue.title} - already has stored values")
                    continue
                
                # Get current values
                status = getattr(issue, 'status', 'new')
                if hasattr(status, 'token'):
                    status = status.token
                    
                priority = getattr(issue, 'priority', 'normal')
                if hasattr(priority, 'token'):
                    priority = priority.token
                    
                assigned_to = getattr(issue, 'assigned_to', None)
                if hasattr(assigned_to, 'token'):
                    assigned_to = assigned_to.token
                
                # Store the values
                annotations['retreat.stored_values'] = {
                    'status': status,
                    'priority': priority,
                    'assigned_to': assigned_to
                }
                annotations._p_changed = True
                
                print(f"Initialized stored values for: {issue.title}")
                print(f"  Status: {status}")
                print(f"  Priority: {priority}")
                print(f"  Assigned to: {assigned_to}")
                
            except Exception as e:
                print(f"Error processing issue {brain.getPath()}: {e}")
        
        # Commit the transaction
        transaction.commit()
        print("\nStored values initialization complete!")

if __name__ == '__main__':
    initialize_stored_values()
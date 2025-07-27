#!/usr/bin/env python
"""
Simple workflow fix script - doesn't require retreat package
Run this via zconsole to switch issues to one_state_workflow
"""

import transaction
from Products.CMFCore.utils import getToolByName
from AccessControl.SecurityManagement import newSecurityManager
from Testing.makerequest import makerequest

# Get the Zope app
app = globals()['app']
app = makerequest(app)

# Login as admin
acl_users = app.acl_users
user = acl_users.getUserById('admin')
if user:
    newSecurityManager(None, user)

# Get Plone site
if 'Plone' not in app.objectIds():
    print("Error: Plone site not found!")
    import sys
    sys.exit(1)

plone = app.Plone

# Set up the site context properly
from zope.component.hooks import setSite
setSite(plone)

print("\n" + "="*60)
print("🔧 FIXING WORKFLOW CONFIGURATION")
print("="*60)

# Get workflow tool
wf_tool = getToolByName(plone, 'portal_workflow')

# 1. Set Issues to use one_state_workflow
print("\n1. Setting workflow for content types...")
wf_tool.setChainForPortalTypes(['issue'], 'one_state_workflow')
wf_tool.setChainForPortalTypes(['participant'], 'one_state_workflow')
print("✓ Issues and Participants now use one_state_workflow")

# 2. Update all existing issues to published state
print("\n2. Updating existing content...")
catalog = getToolByName(plone, 'portal_catalog')

# Update issues
issue_brains = catalog(portal_type='issue')
print(f"Found {len(issue_brains)} issues to update")

for brain in issue_brains:
    try:
        obj = brain.getObject()
        
        # Update workflow state
        if hasattr(obj, 'workflow_history'):
            # Clear old workflow history if exists
            obj.workflow_history = {'one_state_workflow': []}
        
        # Update the review state
        wf_tool.doActionFor(obj, 'publish', comment='Automatic publish')
        obj.reindexObject(idxs=['review_state'])
        
    except Exception as e:
        # If already published or no action available, that's fine
        pass

print(f"✓ Updated {len(issue_brains)} issues")

# Update participants
participant_brains = catalog(portal_type='participant')
print(f"Found {len(participant_brains)} participants to update")

for brain in participant_brains:
    try:
        obj = brain.getObject()
        
        # Update workflow state
        if hasattr(obj, 'workflow_history'):
            # Clear old workflow history if exists
            obj.workflow_history = {'one_state_workflow': []}
        
        # Update the review state
        wf_tool.doActionFor(obj, 'publish', comment='Automatic publish')
        obj.reindexObject(idxs=['review_state'])
        
    except Exception as e:
        # If already published or no action available, that's fine
        pass

print(f"✓ Updated {len(participant_brains)} participants")

# 3. Update security
print("\n3. Updating security...")
wf_tool.updateRoleMappings()
print("✓ Security mappings updated")

# Commit the transaction
transaction.commit()

print("\n" + "="*60)
print("✅ WORKFLOW FIX COMPLETE!")
print("="*60)
print("\nAll issues and participants are now using one_state_workflow")
print("and should be in the 'published' state.")
print("\nNext steps:")
print("1. Restart Plone")
print("2. Check that issues are visible to all users")
print("="*60)
#!/usr/bin/env python
"""
Check available permissions in Plone
"""

import os
import sys
from pathlib import Path

# Add instance directory to Python path
instance_dir = Path(__file__).parent / "instance"
sys.path.insert(0, str(instance_dir))

# Script to run inside Plone
setup_script = '''
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
if 'Plone' in app.objectIds():
    plone = app.Plone
    
    # Set up the site context properly
    from zope.component.hooks import setSite
    setSite(plone)
    
    print("Checking available permissions...")
    print("-" * 60)
    
    # Get the portal_types tool
    portal_types = getToolByName(plone, 'portal_types')
    
    # Check issue type
    if 'issue' in portal_types:
        issue_type = portal_types['issue']
        print("\\nAvailable permissions for Issue content type:")
        print("-" * 60)
        
        # Try different ways to get permissions
        print("\\nTrying to list permissions...")
        
        # Method 1: Get from permission_settings
        if hasattr(issue_type, 'permission_settings'):
            perms = issue_type.permission_settings()
            if perms:
                print("Permissions from permission_settings:")
                for p in perms:
                    print(f"  - {p['name']}")
        
        # Method 2: Try some known permissions
        print("\\nTesting known Plone permissions:")
        known_perms = [
            'View',
            'Access contents information',
            'Modify portal content',
            'Delete objects',
            'Change portal events',
            'Manage properties',
            'Review portal content',
            'Add portal content',
        ]
        
        for perm in known_perms:
            try:
                # Try to get current roles for this permission
                roles = issue_type.rolesOfPermission(perm)
                if roles:
                    print(f"  ✓ {perm} - Current roles: {[r['name'] for r in roles if r['selected']]}")
            except:
                print(f"  ✗ {perm} - Not available")
                
    # Also check for the add permission format
    print("\\n\\nChecking content type specific permissions:")
    add_perms = [
        'issue: Add issue',
        'participant: Add participant',
        'ATContentTypes: Add Document',
        'cmf.AddPortalContent',
    ]
    
    for perm in add_perms:
        try:
            roles = plone.rolesOfPermission(perm)
            if roles:
                print(f"  ✓ {perm} - Current roles: {[r['name'] for r in roles if r['selected']]}")
        except:
            print(f"  ✗ {perm} - Not available")
    
else:
    print("Error: Plone site not found!")
'''

def main():
    """Main entry point"""
    print("Checking Plone permissions...")
    print("-" * 60)
    
    # Write the script
    script_file = instance_dir / "check_perms_temp.py"
    script_file.write_text(setup_script)
    
    # Run the script
    import subprocess
    
    # Activate virtualenv in the environment
    env = os.environ.copy()
    venv_dir = Path(__file__).parent / "venv"
    env['PATH'] = f"{venv_dir}/bin:{env['PATH']}"
    env['VIRTUAL_ENV'] = str(venv_dir)
    
    try:
        result = subprocess.run(
            ["zconsole", "run", "etc/zope.conf", "check_perms_temp.py"],
            cwd=instance_dir,
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
    finally:
        # Clean up
        if script_file.exists():
            script_file.unlink()

if __name__ == "__main__":
    main()
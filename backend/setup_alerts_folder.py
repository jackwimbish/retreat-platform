#!/usr/bin/env python
"""
Setup alerts folder for Camp Coordinator
Creates the /alerts folder with proper permissions
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
    
    print("Setting up alerts folder for Camp Coordinator...")
    print("-" * 60)
    
    # Create /alerts folder if it doesn't exist
    if 'alerts' not in plone.objectIds():
        print("\\nCreating /alerts folder...")
        
        # Create as a Document (standard Plone type)
        plone.invokeFactory(
            'Document',
            id='alerts',
            title='Camp Alerts',
            description='Emergency alerts and announcements'
        )
        alerts_folder = plone['alerts']
        
        print(f"✓ Created folder: /alerts")
        print(f"  Title: {alerts_folder.title}")
        print(f"  Type: {alerts_folder.portal_type}")
        
        # Set up permissions for the alerts folder
        print("\\nConfiguring permissions for /alerts folder...")
        
        # Define permissions for the folder
        folder_permissions = [
            # All authenticated users can view alerts
            ('View', ['Manager', 'Editor', 'Member', 'Authenticated']),
            ('Access contents information', ['Manager', 'Editor', 'Member', 'Authenticated']),
            
            # Only staff can add alerts
            ('Add portal content', ['Manager', 'Editor']),
            ('retreat: Add Camp Alert', ['Manager', 'Editor']),
            
            # Only managers and editors can modify the folder itself
            ('Modify portal content', ['Manager', 'Editor']),
            ('Delete objects', ['Manager', 'Editor']),
        ]
        
        # Apply permissions
        for permission, roles in folder_permissions:
            try:
                alerts_folder.manage_permission(permission, roles=roles, acquire=False)
                print(f"  ✓ Set '{permission}' for roles: {', '.join(roles)}")
            except (AttributeError, ValueError):
                # Skip custom permissions that might not exist yet
                if permission == 'retreat.AddCampAlert' or permission == 'retreat: Add Camp Alert':
                    print(f"  ! Skipping custom permission '{permission}' (will be set later)")
                else:
                    raise
        
        # Make sure the folder is published/visible
        workflow_tool = getToolByName(plone, 'portal_workflow')
        if workflow_tool.getInfoFor(alerts_folder, 'review_state', None) == 'private':
            try:
                workflow_tool.doActionFor(alerts_folder, 'publish')
                print("  ✓ Published the folder")
            except:
                print("  ! Could not publish (workflow might not support it)")
        
        # Commit transaction
        transaction.commit()
        print("\\n✓ Alerts folder created successfully!")
        
    else:
        print("\\n! Alerts folder already exists - updating permissions...")
        
        alerts_folder = plone['alerts']
        
        # Update permissions
        folder_permissions = [
            ('View', ['Manager', 'Editor', 'Member', 'Authenticated']),
            ('Access contents information', ['Manager', 'Editor', 'Member', 'Authenticated']),
            ('Add portal content', ['Manager', 'Editor']),
            ('Modify portal content', ['Manager', 'Editor']),
            ('Delete objects', ['Manager', 'Editor']),
        ]
        
        for permission, roles in folder_permissions:
            alerts_folder.manage_permission(permission, roles=roles, acquire=False)
            print(f"  ✓ Updated '{permission}' for roles: {', '.join(roles)}")
        
        transaction.commit()
        print("\\n✓ Alerts folder permissions updated!")
    
    print("-" * 60)
    print("Done!")
    
else:
    print("Error: Plone site not found!")
'''

def main():
    """Main entry point"""
    print("Setting up Camp Coordinator alerts folder...")
    print("-" * 60)
    
    # Write the script
    script_file = instance_dir / "setup_alerts_temp.py"
    script_file.write_text(setup_script)
    
    # Run the script
    import subprocess
    
    # Activate virtualenv in the environment
    env = os.environ.copy()
    venv_dir = Path(__file__).parent / "venv"
    backend_dir = Path(__file__).parent
    env['PATH'] = f"{venv_dir}/bin:{env['PATH']}"
    env['VIRTUAL_ENV'] = str(venv_dir)
    # Add src directory to Python path for custom code
    env['PYTHONPATH'] = f"{backend_dir}/src:{env.get('PYTHONPATH', '')}"
    
    try:
        result = subprocess.run(
            ["zconsole", "run", "etc/zope.conf", "setup_alerts_temp.py"],
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
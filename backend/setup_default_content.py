#!/usr/bin/env python
"""
Setup default content for Camp Coordinator
Creates the /issues folder with proper permissions
Run this after the site and user roles are created
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
    
    print("Setting up default content for Camp Coordinator...")
    print("-" * 60)
    
    # 1. Create /issues folder if it doesn't exist
    if 'issues' not in plone.objectIds():
        print("\\nCreating /issues folder...")
        
        # First, let's check what content types are available
        portal_types = getToolByName(plone, 'portal_types')
        available_types = portal_types.listContentTypes()
        print(f"\\nAvailable content types: {', '.join(available_types)}")
        
        # Create as a Document (which we know exists)
        plone.invokeFactory(
            'Document',
            id='issues',
            title='Issues',
            description='Maintenance and facility issues tracker'
        )
        issues_folder = plone['issues']
        
        print(f"✓ Created folder: /issues")
        print(f"  Title: {issues_folder.title}")
        print(f"  Type: {issues_folder.portal_type}")
        
        # Set up permissions for the issues folder
        print("\\nConfiguring permissions for /issues folder...")
        
        # Define permissions for the folder
        # This ensures all authenticated users can view issues created within
        folder_permissions = [
            # Everyone can view the folder and its contents
            ('View', ['Manager', 'Editor', 'Member', 'Authenticated']),
            ('Access contents information', ['Manager', 'Editor', 'Member', 'Authenticated']),
            
            # Only specific roles can add content
            ('Add portal content', ['Manager', 'Editor', 'Member']),
            
            # Only managers and editors can modify the folder itself
            ('Modify portal content', ['Manager', 'Editor']),
            ('Delete objects', ['Manager', 'Editor']),
        ]
        
        # Apply permissions
        for permission, roles in folder_permissions:
            issues_folder.manage_permission(permission, roles=roles, acquire=False)
            print(f"  ✓ Set '{permission}' for roles: {', '.join(roles)}")
        
        # IMPORTANT: Set layout for issues dashboard
        issues_folder.setLayout('issues_dashboard_view')
        print("  ✓ Set layout to 'issues_dashboard_view'")
        
        # Make sure the folder is published/visible
        workflow_tool = getToolByName(plone, 'portal_workflow')
        if workflow_tool.getInfoFor(issues_folder, 'review_state', None) == 'private':
            try:
                workflow_tool.doActionFor(issues_folder, 'publish')
                print("  ✓ Published the folder")
            except:
                print("  ℹ️  Could not publish folder (might not have workflow)")
        
    else:
        print("✓ /issues folder already exists")
    
    # 2. Set up other default content (future expansion)
    # You can add more default content creation here, such as:
    # - /participants folder for participant directory
    # - /resources folder for camp resources
    # - /announcements folder for news/updates
    # etc.
    
    # Commit transaction
    transaction.commit()
    
    print("\\n" + "="*60)
    print("✅ Default content setup complete!")
    print("="*60)
    print("\\nCreated content:")
    print("- /issues folder with proper permissions")
    print("  • All authenticated users can VIEW issues")
    print("  • Members, Staff, and Admins can CREATE issues")
    print("  • Only Staff and Admins can MODIFY/DELETE others' issues")
    print("  • Members can still edit their OWN issues (via Owner role)")
    print("")
    print("Next steps:")
    print("1. Visit http://localhost:3000/issues to see the dashboard")
    print("2. Create new issues - they will inherit proper permissions")
    print("3. Test with different user roles to verify access")
    
else:
    print("Error: Plone site not found!")
'''

def main():
    """Main entry point"""
    print("Setting up Camp Coordinator default content...")
    print("-" * 60)
    
    # Write the script
    script_file = instance_dir / "setup_content_temp.py"
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
            ["zconsole", "run", "etc/zope.conf", "setup_content_temp.py"],
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
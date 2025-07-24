#!/usr/bin/env python
"""
Protect the homepage from anonymous users
Forces login before seeing any content
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
    
    print("Protecting site from anonymous users...")
    print("-" * 60)
    
    # Method 1: Protect the entire site root
    print("\\nSetting site-wide permissions...")
    
    # Remove View permission for Anonymous at the site root
    # This will make the entire site require login
    plone.manage_permission(
        'View', 
        ['Manager', 'Editor', 'Member', 'Reviewer', 'Contributor', 'Authenticated'], 
        acquire=False
    )
    
    print("✓ Site root view permission updated")
    print("  - Anonymous users cannot view any content")
    print("  - Will be redirected to login")
    
    # Ensure the login form itself is accessible
    # Plone handles this automatically for its login views
    
    # Also protect specific content if it exists
    protected_paths = ['front-page', 'index_html', 'index', 'home']
    
    for path in protected_paths:
        if hasattr(plone, path):
            obj = getattr(plone, path)
            print(f"\\nFound content at /{path}")
            obj.manage_permission(
                'View',
                ['Manager', 'Editor', 'Member', 'Reviewer', 'Contributor', 'Authenticated'],
                acquire=False
            )
            print(f"✓ Protected /{path}")
    
    # Check if there's an issues folder to ensure it's protected
    if hasattr(plone, 'issues'):
        print("\\nProtecting /issues folder...")
        issues_folder = plone.issues
        issues_folder.manage_permission(
            'View',
            ['Manager', 'Editor', 'Member', 'Authenticated'],
            acquire=False
        )
        print("✓ Issues folder protected")
    
    # Commit transaction
    transaction.commit()
    
    print("\\n" + "="*60)
    print("✅ Site protection complete!")
    print("="*60)
    print("\\nResults:")
    print("- The entire site now requires login")
    print("- Anonymous users → redirected to login page")
    print("- All authenticated users can access the site")
    print("")
    print("To test:")
    print("1. Clear your browser cache/cookies")
    print("2. Open an incognito/private browser window")
    print("3. Go to http://localhost:3000")
    print("4. You should see the login page")
    print("")
    print("Login with any of these users:")
    print("- admin/admin (Administrator)")
    print("- director/director123 (Admin)")
    print("- staff1/staff123 (Staff)")
    print("- participant1/participant123 (Participant)")
    
else:
    print("Error: Plone site not found!")
'''

def main():
    """Main entry point"""
    print("Setting up site protection...")
    print("-" * 60)
    
    # Write the script
    script_file = instance_dir / "protect_site_temp.py"
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
            ["zconsole", "run", "etc/zope.conf", "protect_site_temp.py"],
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
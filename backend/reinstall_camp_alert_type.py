#!/usr/bin/env python
"""
Reinstall camp_alert content type profile
Updates the camp_alert type with fixed schema
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
    
    print("Reinstalling camp_alert content type...")
    print("-" * 60)
    
    # Get the portal_setup tool
    portal_setup = getToolByName(plone, 'portal_setup')
    
    # Reimport the types
    print("Reimporting content types...")
    try:
        # Import the types.xml which includes camp_alert
        portal_setup.runImportStepFromProfile(
            'profile-content_type_profiles:default',
            'typeinfo',
            run_dependencies=False
        )
        print("✓ Content types reimported successfully")
    except Exception as e:
        print(f"! Error reimporting types: {e}")
    
    # Verify the type exists
    portal_types = getToolByName(plone, 'portal_types')
    if 'camp_alert' in portal_types:
        print("✓ camp_alert content type found in portal_types")
        
        # Update workflow
        workflow_tool = getToolByName(plone, 'portal_workflow')
        workflow_tool.setChainForPortalTypes(['camp_alert'], 'one_state_workflow')
        print("✓ Workflow updated for camp_alert")
    else:
        print("! camp_alert content type not found after reimport")
    
    # Commit transaction
    transaction.commit()
    print("\\n✓ Camp Alert content type reinstalled!")
    print("-" * 60)
    
else:
    print("Error: Plone site not found!")
'''

def main():
    """Main entry point"""
    print("Reinstalling Camp Alert content type...")
    print("-" * 60)
    
    # Write the script
    script_file = instance_dir / "reinstall_camp_alert_temp.py"
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
            ["zconsole", "run", "etc/zope.conf", "reinstall_camp_alert_temp.py"],
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
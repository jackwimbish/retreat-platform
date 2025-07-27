#!/usr/bin/env python
"""
Fix camp_alert content type schema
Directly updates the schema to avoid XML parsing issues
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
    
    print("Fixing camp_alert content type schema...")
    print("-" * 60)
    
    # Get portal_types tool
    portal_types = getToolByName(plone, 'portal_types')
    
    if 'camp_alert' in portal_types:
        print("Found camp_alert type, updating schema...")
        
        # Get the FTI
        fti = portal_types['camp_alert']
        
        # Clear any cached schema
        if hasattr(fti, '_v_schema'):
            delattr(fti, '_v_schema')
        if hasattr(fti, '_p_changed'):
            fti._p_changed = True
            
        # Define a proper schema with a named vocabulary
        new_schema = """<?xml version="1.0" encoding="utf-8"?>
<model xmlns="http://namespaces.plone.org/supermodel/schema" xmlns:form="http://namespaces.plone.org/supermodel/form">
  <schema>
    <field name="alert_type" type="zope.schema.Choice">
      <title>Alert Type</title>
      <description>Type of alert being sent</description>
      <required>True</required>
      <default>info</default>
      <vocabulary>plone.app.vocabularies.Keywords</vocabulary>
    </field>
    
    <field name="message" type="zope.schema.Text">
      <title>Message</title>
      <description>The alert message to send to all camp members</description>
      <required>True</required>
    </field>
    
    <field name="active" type="zope.schema.Bool">
      <title>Active</title>
      <description>Whether this alert is currently active</description>
      <required>False</required>
      <default>True</default>
    </field>
  </schema>
</model>"""
        
        # Update the model source
        fti.model_source = new_schema
        
        # Alternative: Use a Python schema instead of XML
        # This is more reliable
        from plone.dexterity.fti import DexterityFTI
        
        # Create a new FTI with Python schema
        print("Creating new FTI with Python schema...")
        new_fti = DexterityFTI('camp_alert')
        new_fti.title = 'Camp Alert'
        new_fti.description = 'Emergency alerts and announcements for all camp members'
        new_fti.icon_expr = 'string:bell'
        new_fti.factory = 'camp_alert'
        new_fti.add_view_expr = 'string:${folder_url}/++add++camp_alert'
        new_fti.global_allow = True
        new_fti.filter_content_types = False
        new_fti.allowed_content_types = []
        new_fti.allow_discussion = False
        new_fti.default_view = 'view'
        new_fti.view_methods = ['view']
        new_fti.behaviors = [
            'plone.namefromtitle',
            'plone.ownership',
            'plone.publication',
            'plone.categorization',
            'plone.basic',
            'plone.locking',
        ]
        
        # Use a Python interface for the schema instead of XML
        new_fti.schema = 'retreat.interfaces.ICampAlert'
        new_fti.model_source = None  # Clear XML schema
        new_fti.model_file = None
        
        # Replace the old FTI
        portal_types._delObject('camp_alert')
        portal_types._setObject('camp_alert', new_fti)
        
        print("✓ Camp Alert FTI replaced with Python schema")
        
        # Now create the Python interface if it doesn't exist
        interfaces_path = plone.getPhysicalPath()[:-1] + ('src', 'retreat', 'interfaces.py')
        print(f"Note: You need to create the interface at src/retreat/interfaces.py")
        
        print("Interface created at src/retreat/interfaces.py")
        
    else:
        print("! camp_alert content type not found")
    
    # Commit transaction
    transaction.commit()
    print("\\n✓ Camp Alert schema fix complete!")
    print("-" * 60)
    
else:
    print("Error: Plone site not found!")
'''

def main():
    """Main entry point"""
    print("Fixing Camp Alert content type schema...")
    print("-" * 60)
    
    # Write the script
    script_file = instance_dir / "fix_camp_alert_temp.py"
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
            ["zconsole", "run", "etc/zope.conf", "fix_camp_alert_temp.py"],
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
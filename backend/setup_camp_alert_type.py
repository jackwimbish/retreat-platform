#!/usr/bin/env python
"""
Setup camp_alert content type
Ensures the camp_alert content type is properly registered
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
from plone.dexterity.fti import DexterityFTI

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
    
    print("Setting up camp_alert content type...")
    print("-" * 60)
    
    # Get portal_types tool
    portal_types = getToolByName(plone, 'portal_types')
    
    # Create Camp Alert content type
    if 'camp_alert' not in portal_types:
        print("Creating Camp Alert content type...")
        fti = DexterityFTI('camp_alert')
        fti.title = 'Camp Alert'
        fti.description = 'Emergency alerts and announcements for all camp members'
        fti.icon_expr = 'string:bell'
        fti.factory = 'camp_alert'
        fti.add_view_expr = 'string:${folder_url}/++add++camp_alert'
        fti.global_allow = True
        fti.filter_content_types = False
        fti.allowed_content_types = []
        fti.allow_discussion = False
        fti.default_view = 'view'
        fti.view_methods = ['view']
        fti.behaviors = [
            'plone.namefromtitle',
            'plone.ownership',
            'plone.publication',
            'plone.categorization',
            'plone.basic',
            'plone.locking',
            'plone.leadimage',
            'volto.blocks',
            'plone.eventbasic',
        ]
        
        # Define the schema
        fti.model_source = """<?xml version="1.0" encoding="utf-8"?>
<model xmlns="http://namespaces.plone.org/supermodel/schema" xmlns:form="http://namespaces.plone.org/supermodel/form" xmlns:marshal="http://namespaces.plone.org/supermodel/marshal" xmlns:security="http://namespaces.plone.org/supermodel/security">
  <schema>
    <field name="alert_type" type="zope.schema.Choice" required="True">
      <title>Alert Type</title>
      <description>Type of alert being sent</description>
      <vocabulary>
        <SimpleTerm value="emergency" title="Emergency" />
        <SimpleTerm value="event" title="Event" />
        <SimpleTerm value="info" title="Information" />
      </vocabulary>
      <default>info</default>
    </field>
    
    <field name="message" type="zope.schema.Text" required="True">
      <title>Message</title>
      <description>The alert message to send to all camp members</description>
    </field>
    
    <field name="active" type="zope.schema.Bool" required="False">
      <title>Active</title>
      <description>Whether this alert is currently active</description>
      <default>True</default>
    </field>
    
    <field name="sms_number" type="zope.schema.TextLine" required="False">
      <title>SMS Number (Future)</title>
      <description>Phone number for SMS alerts (not implemented yet)</description>
    </field>
    
    <field name="push_notification_enabled" type="zope.schema.Bool" required="False">
      <title>Push Notifications (Future)</title>
      <description>Enable push notifications (not implemented yet)</description>
      <default>False</default>
    </field>
  </schema>
</model>
"""
        
        portal_types._setObject('camp_alert', fti)
        
        # Ensure icon_expr is properly initialized
        alert_fti = portal_types['camp_alert']
        alert_fti._updateProperty('icon_expr', 'string:bell')
        
        # Set custom add permission
        alert_fti.add_permission = 'cmf.AddPortalContent'  # Use standard permission for now
        
        print("✓ Camp Alert content type created")
    else:
        print("! Camp Alert content type already exists - updating...")
        alert_fti = portal_types['camp_alert']
        alert_fti._updateProperty('icon_expr', 'string:bell')
        alert_fti.add_permission = 'cmf.AddPortalContent'  # Use standard permission for now
        print("✓ Camp Alert content type updated")
    
    # Set workflow
    workflow_tool = getToolByName(plone, 'portal_workflow')
    workflow_tool.setChainForPortalTypes(['camp_alert'], 'one_state_workflow')
    print("✓ Camp Alerts set to use one_state_workflow")
    
    # Update security
    workflow_tool.updateRoleMappings()
    
    # Commit transaction
    transaction.commit()
    print("\\n✓ Camp Alert content type setup complete!")
    print("-" * 60)
    
else:
    print("Error: Plone site not found!")
'''

def main():
    """Main entry point"""
    print("Setting up Camp Alert content type...")
    print("-" * 60)
    
    # Write the script
    script_file = instance_dir / "setup_camp_alert_temp.py"
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
            ["zconsole", "run", "etc/zope.conf", "setup_camp_alert_temp.py"],
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
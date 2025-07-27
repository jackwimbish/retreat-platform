#!/usr/bin/env python
"""
Setup conference room and booking content types
Must be run before creating conference rooms
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
    
    print("Setting up conference room content types...")
    print("-" * 60)
    
    # Get portal_types tool
    portal_types = getToolByName(plone, 'portal_types')
    
    # Create Conference Room content type
    if 'conference_room' not in portal_types:
        print("Creating Conference Room content type...")
        fti = DexterityFTI('conference_room')
        fti.title = 'Conference Room'
        fti.description = 'A bookable conference room'
        fti.icon_expr = 'string:folder'
        fti.factory = 'conference_room'
        fti.add_view_expr = 'string:${folder_url}/++add++conference_room'
        fti.global_allow = True  # Allow it to be created anywhere for now
        fti.filter_content_types = True
        fti.allowed_content_types = []
        fti.allow_discussion = False
        fti.default_view = 'view'
        fti.view_methods = ('view',)
        
        # Enable behaviors
        fti.behaviors = (
            'plone.namefromtitle',
            'plone.basic',
            'plone.ownership',
            'plone.categorization',
            'plone.locking',
        )
        
        # Use Python schema interface
        fti.schema = 'retreat.interfaces.IConferenceRoom'
        
        portal_types._setObject('conference_room', fti)
        room_fti = portal_types['conference_room']
        room_fti._updateProperty('icon_expr', 'string:folder')
        print("✓ Conference Room content type created")
    else:
        print("! Conference Room content type already exists")

    # Create Room Booking content type
    if 'room_booking' not in portal_types:
        print("Creating Room Booking content type...")
        fti = DexterityFTI('room_booking')
        fti.title = 'Room Booking'
        fti.description = 'A conference room booking'
        fti.icon_expr = 'string:event'
        fti.factory = 'room_booking'
        fti.add_view_expr = 'string:${folder_url}/++add++room_booking'
        fti.global_allow = True  # Allow it to be created anywhere for now
        fti.filter_content_types = True
        fti.allowed_content_types = []
        fti.allow_discussion = False
        fti.default_view = 'view'
        fti.view_methods = ('view',)
        
        # Enable behaviors
        fti.behaviors = (
            'plone.namefromtitle',
            'plone.basic',
            'plone.ownership',
            'plone.locking',
        )
        
        # Use Python schema interface
        fti.schema = 'retreat.interfaces.IRoomBooking'
        
        portal_types._setObject('room_booking', fti)
        booking_fti = portal_types['room_booking']
        booking_fti._updateProperty('icon_expr', 'string:event')
        print("✓ Room Booking content type created")
    else:
        print("! Room Booking content type already exists")
    
    # Set workflow
    workflow_tool = getToolByName(plone, 'portal_workflow')
    workflow_tool.setChainForPortalTypes(['conference_room', 'room_booking'], 'one_state_workflow')
    print("✓ Conference Rooms and Bookings set to use one_state_workflow")
    
    # Update security
    workflow_tool.updateRoleMappings()
    
    # Update the Document type to allow conference_room as a child
    if 'Document' in portal_types:
        doc_fti = portal_types['Document']
        allowed = list(doc_fti.allowed_content_types)
        if 'conference_room' not in allowed:
            allowed.append('conference_room')
        if 'room_booking' not in allowed:
            allowed.append('room_booking')
        doc_fti.allowed_content_types = tuple(allowed)
        print("✓ Updated Document to allow conference_room and room_booking")
    
    # Commit transaction
    transaction.commit()
    print("\\n✓ Conference room content types setup complete!")
    print("-" * 60)
    
else:
    print("Error: Plone site not found!")
'''

def main():
    """Main entry point"""
    print("Setting up conference room content types...")
    print("-" * 60)
    
    # Write the script
    script_file = instance_dir / "setup_room_types_temp.py"
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
            ["zconsole", "run", "etc/zope.conf", "setup_room_types_temp.py"],
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
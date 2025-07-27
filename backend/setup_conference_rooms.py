#!/usr/bin/env python
"""
Setup conference rooms for Camp Coordinator
Creates the conference-rooms folder and initial rooms
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
from plone import api

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
    
    print("Setting up conference rooms for Camp Coordinator...")
    print("-" * 60)
    
    # Create /conference-rooms folder if it doesn't exist
    if 'conference-rooms' not in plone.objectIds():
        print("\\nCreating /conference-rooms folder...")
        
        # Create as a Document (standard Plone type)
        plone.invokeFactory(
            'Document',
            id='conference-rooms',
            title='Conference Rooms',
            description='Book conference rooms for meetings and events'
        )
        rooms_folder = plone['conference-rooms']
        
        print(f"✓ Created folder: /conference-rooms")
        
        # Set up permissions for the conference-rooms folder
        print("\\nConfiguring permissions for /conference-rooms folder...")
        
        # Define permissions for the folder
        folder_permissions = [
            # All authenticated users can view
            ('View', ['Manager', 'Editor', 'Member', 'Authenticated']),
            ('Access contents information', ['Manager', 'Editor', 'Member', 'Authenticated']),
            
            # All authenticated users can add bookings
            ('Add portal content', ['Manager', 'Editor', 'Member']),
            
            # Only managers and editors can modify the folder itself
            ('Modify portal content', ['Manager', 'Editor']),
            ('Delete objects', ['Manager', 'Editor']),
        ]
        
        # Apply permissions
        for permission, roles in folder_permissions:
            rooms_folder.manage_permission(permission, roles=roles, acquire=False)
            print(f"  ✓ Set '{permission}' for roles: {', '.join(roles)}")
        
        # Create the initial conference rooms
        print("\\nCreating conference rooms...")
        
        rooms_data = [
            ('downstairs-room-1', 'Downstairs Room 1', 4),
            ('downstairs-room-2', 'Downstairs Room 2', 4),
            ('upstairs-room-1', 'Upstairs Room 1', 4),
            ('upstairs-room-2', 'Upstairs Room 2', 2),
            ('upstairs-room-3', 'Upstairs Room 3', 2),
        ]
        
        for room_id, room_title, capacity in rooms_data:
            if room_id not in rooms_folder.objectIds():
                try:
                    room = api.content.create(
                        container=rooms_folder,
                        type='conference_room',
                        id=room_id,
                        title=room_title,
                        capacity=capacity
                    )
                    print(f"  ✓ Created {room_title} (capacity: {capacity})")
                except Exception as e:
                    print(f"  ! Error creating {room_title}: {e}")
        
        # Create bookings subfolder for storing bookings
        if 'bookings' not in rooms_folder.objectIds():
            rooms_folder.invokeFactory(
                'Document',
                id='bookings',
                title='Bookings',
                description='All room bookings'
            )
            bookings_folder = rooms_folder['bookings']
            
            # Set permissions for bookings folder
            bookings_permissions = [
                ('View', ['Manager', 'Editor', 'Member', 'Authenticated']),
                ('Access contents information', ['Manager', 'Editor', 'Member', 'Authenticated']),
                ('Add portal content', ['Manager', 'Editor', 'Member']),
                ('Modify portal content', ['Manager', 'Editor']),
                ('Delete objects', ['Manager', 'Editor']),
            ]
            
            for permission, roles in bookings_permissions:
                bookings_folder.manage_permission(permission, roles=roles, acquire=False)
            
            print("  ✓ Created bookings subfolder")
        
        # Commit transaction
        transaction.commit()
        print("\\n✓ Conference rooms setup complete!")
        
    else:
        print("\\n! Conference rooms folder already exists")
    
    print("-" * 60)
    print("Done!")
    
else:
    print("Error: Plone site not found!")
'''

def main():
    """Main entry point"""
    print("Setting up Camp Coordinator conference rooms...")
    print("-" * 60)
    
    # Write the script
    script_file = instance_dir / "setup_rooms_temp.py"
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
            ["zconsole", "run", "etc/zope.conf", "setup_rooms_temp.py"],
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
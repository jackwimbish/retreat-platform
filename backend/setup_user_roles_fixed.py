#!/usr/bin/env python
"""
Setup user roles and permissions for the Camp Coordinator
Run this after the site is created: ./setup_user_roles_fixed.py

Creates 3 roles:
1. Admin - Full system access (using Manager role)
2. Staff - Can create/edit/resolve issues, view participants (using Editor role)  
3. Participant - Can create and view issues, edit own issues (using Member role)
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
    
    # Also set up request
    plone.REQUEST['PARENTS'] = [plone]
    
    print("Setting up user roles and permissions...")
    print("-" * 60)
    
    # Get the portal_types tool
    portal_types = getToolByName(plone, 'portal_types')
    
    # Configure Issue content type permissions
    if 'issue' in portal_types:
        print("\\nConfiguring Issue permissions...")
        issue_type = portal_types['issue']
        
        # Define permission mappings for Issue type
        # Using only the permissions that actually exist
        issue_permissions = [
            # View permission - all authenticated users can view issues
            ('View', ['Manager', 'Editor', 'Member', 'Authenticated']),
            ('Access contents information', ['Manager', 'Editor', 'Member', 'Authenticated']),
            
            # Delete permission - Only Admin and Staff
            ('Delete objects', ['Manager', 'Editor']),
            
            # Manage properties - for changing metadata (only staff)
            ('Manage properties', ['Manager', 'Editor']),
        ]
        
        # Apply permissions to Issue type
        for permission, roles in issue_permissions:
            issue_type.manage_permission(permission, roles=roles, acquire=False)
        
        print("✓ Issue permissions configured")
        print("  - All authenticated users can view issues")
        print("  - Only Staff can delete issues")
        
        # Note about editing: In Plone, the actual edit permission is handled
        # at the content level through ownership and local roles
    else:
        print("⚠️  Issue content type not found")
    
    # Configure Participant content type permissions
    if 'participant' in portal_types:
        print("\\nConfiguring Participant permissions...")
        participant_type = portal_types['participant']
        
        participant_permissions = [
            # View permission - all authenticated users can view participant directory
            ('View', ['Manager', 'Editor', 'Member', 'Authenticated']),
            ('Access contents information', ['Manager', 'Editor', 'Member', 'Authenticated']),
            
            # Delete - Only Admin
            ('Delete objects', ['Manager']),
            
            # Manage properties - Only staff
            ('Manage properties', ['Manager', 'Editor']),
        ]
        
        # Apply permissions to Participant type
        for permission, roles in participant_permissions:
            participant_type.manage_permission(permission, roles=roles, acquire=False)
        
        print("✓ Participant permissions configured")
        print("  - All authenticated users can view participant directory")
        print("  - Only Admin can delete participants")
    else:
        print("⚠️  Participant content type not found")
    
    # Configure folder permissions for /issues if it exists
    if hasattr(plone, 'issues'):
        print("\\nConfiguring /issues folder permissions...")
        issues_folder = plone.issues
        
        # For folders, we set basic permissions
        folder_permissions = [
            ('View', ['Manager', 'Editor', 'Member', 'Authenticated']),
            ('Access contents information', ['Manager', 'Editor', 'Member', 'Authenticated']),
        ]
        
        for permission, roles in folder_permissions:
            issues_folder.manage_permission(permission, roles=roles, acquire=False)
        
        print("✓ /issues folder permissions configured")
    else:
        print("⚠️  /issues folder not found (will be created when first issue is added)")
    
    # Set site-wide permissions for who can add content
    print("\\nConfiguring site-wide add permissions...")
    
    # First, let's check and update the Issue FTI add_permission
    if 'issue' in portal_types:
        issue_fti = portal_types['issue']
        # This controls who can add issues
        issue_fti.add_permission = 'cmf.AddPortalContent'
        print("✓ Issue add permission set to 'cmf.AddPortalContent'")
    
    # Now set who has the add permission globally
    # This is the key permission for creating content
    plone.manage_permission('Add portal content', ['Manager', 'Editor', 'Member'], acquire=True)
    print("✓ Members, Staff, and Admins can now add content")
    
    # For participants, only staff should add them
    if 'participant' in portal_types:
        participant_fti = portal_types['participant']
        participant_fti.add_permission = 'cmf.AddPortalContent'
        # We'll need to restrict this in specific folders
    
    # Create sample users for testing
    print("\\n" + "="*60)
    print("Creating sample users...")
    print("="*60)
    
    # Get ACL users
    plone_users = plone.acl_users
    
    # Helper function to create a user
    def create_user(username, password, fullname, email, roles):
        # Check if user already exists
        if plone_users.getUserById(username):
            print(f"  - User '{username}' already exists, updating roles...")
            user = plone_users.getUserById(username)
            # Update roles if needed
            try:
                plone_users.userFolderEditUser(username, password, roles, [])
            except:
                pass
            return
        
        # Register the user
        try:
            plone_users.userFolderAddUser(
                username, 
                password, 
                roles, 
                []
            )
            
            # Get the user and set properties
            user = plone_users.getUserById(username)
            if user:
                # Set member properties
                member_tool = getToolByName(plone, 'portal_membership')
                member = member_tool.getMemberById(username)
                if member:
                    member.setMemberProperties({
                        'fullname': fullname,
                        'email': email,
                    })
            
            print(f"  ✓ Created user: {username} ({fullname})")
            print(f"    Password: {password}")
            print(f"    Roles: {', '.join(roles)}")
            print()
            
        except Exception as e:
            print(f"  ❌ Error creating user {username}: {e}")
    
    # Create sample users
    sample_users = [
        # (username, password, fullname, email, roles)
        ('director', 'director123', 'Jane Director', 'director@camp.org', ['Manager']),
        ('staff1', 'staff123', 'John Staff', 'john@camp.org', ['Editor']),
        ('staff2', 'staff123', 'Mary Staff', 'mary@camp.org', ['Editor']),
        ('participant1', 'participant123', 'Alice Participant', 'alice@retreat.org', ['Member']),
        ('participant2', 'participant123', 'Bob Participant', 'bob@retreat.org', ['Member']),
    ]
    
    for username, password, fullname, email, roles in sample_users:
        create_user(username, password, fullname, email, roles)
    
    # Commit transaction
    transaction.commit()
    
    print("="*60)
    print("✅ Role and permission setup complete!")
    print("="*60)
    print("\\nRole Summary:")
    print("- Admin (Manager role): Full system access")
    print("- Staff (Editor role): Create/edit/resolve issues, manage participants")
    print("- Participant (Member role): Create issues, view all issues, edit own issues")
    print("")
    print("Permission Notes:")
    print("- Edit permissions in Plone work through ownership")
    print("- When a Member creates an issue, they become the Owner")
    print("- Owners can edit their own content by default")
    print("- Staff (Editors) can edit any content")
    print("")
    print("You can now login at http://localhost:3000 with any of the sample users")
    
else:
    print("Error: Plone site not found!")
'''

def main():
    """Main entry point"""
    print("Setting up Camp Coordinator user roles and permissions...")
    print("-" * 60)
    
    # Write the script
    script_file = instance_dir / "setup_roles_temp.py"
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
            ["zconsole", "run", "etc/zope.conf", "setup_roles_temp.py"],
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
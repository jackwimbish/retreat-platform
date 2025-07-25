#!/usr/bin/env python
"""
Create a simple directory view in Plone
"""

import os
import sys
from pathlib import Path

# Add instance directory to Python path
instance_dir = Path(__file__).parent / "instance"
sys.path.insert(0, str(instance_dir))

# Script to run inside Plone
create_script = '''
import transaction
from AccessControl.SecurityManagement import newSecurityManager
from Testing.makerequest import makerequest
from Products.PythonScripts.PythonScript import manage_addPythonScript

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
    
    from zope.component.hooks import setSite
    setSite(plone)
    
    print("=" * 70)
    print("CREATING DIRECTORY VIEW")
    print("=" * 70)
    
    # Create a Python Script that will serve as our directory view
    script_code = """
# Directory view - returns JSON data of all users
from Products.CMFCore.utils import getToolByName
import json

# Check if user is authenticated
mtool = getToolByName(context, 'portal_membership')
if mtool.isAnonymousUser():
    container.REQUEST.RESPONSE.setStatus(401)
    return json.dumps({"error": "Authentication required"})

# Get all users
users_data = []
acl_users = context.acl_users
users = acl_users.searchUsers()

for user_info in users:
    user_id = user_info.get('userid')
    if user_id:
        member = mtool.getMemberById(user_id)
        if member:
            # Get member properties
            fullname = member.getProperty('fullname', '') or user_id
            email = member.getProperty('email', '')
            
            # Get roles (excluding default ones)
            roles = list(member.getRoles())
            filtered_roles = [r for r in roles if r not in ['Member', 'Authenticated']]
            
            # Get portrait URL
            portrait_url = None
            portrait = mtool.getPersonalPortrait(user_id)
            # Check if it's not the default portrait
            if portrait and hasattr(portrait, 'absolute_url'):
                portrait_url = portrait.absolute_url()
                if 'defaultUser.png' in portrait_url:
                    portrait_url = None
                elif portrait_url and '/portal_memberdata/portraits/' in portrait_url:
                    # Convert to API-friendly URL
                    portal_url = context.portal_url()
                    portrait_url = portal_url + '/++api++/@@portrait/' + user_id
            
            user_data = {
                "id": user_id,
                "fullname": fullname,
                "email": email,
                "roles": filtered_roles,
                "portrait": portrait_url
            }
            
            users_data.append(user_data)

# Sort users by fullname
users_data.sort(key=lambda x: x['fullname'].lower())

# Set response headers
container.REQUEST.RESPONSE.setHeader('Content-Type', 'application/json')
container.REQUEST.RESPONSE.setHeader('Cache-Control', 'private, max-age=60')

return json.dumps({
    "users": users_data,
    "@id": context.absolute_url() + '/directory_api'
})
"""
    
    # Create the script
    script_id = 'directory_api'
    
    # Remove existing script if it exists
    if script_id in plone.objectIds():
        plone.manage_delObjects([script_id])
        print(f"✓ Removed existing {script_id} script")
    
    # Add the new script  
    manage_addPythonScript(plone, script_id)
    script = plone[script_id]
    
    # Set the script code
    script.write(script_code)
    
    # Make it accessible to authenticated users
    script.manage_permission('View', roles=['Authenticated'], acquire=0)
    
    print(f"✓ Created {script_id} script")
    
    # Test the script
    try:
        # Get the script and execute it
        result = script()
        import json
        data = json.loads(result)
        print(f"✓ Script works! Found {len(data.get('users', []))} users")
    except Exception as e:
        print(f"✗ Error testing script: {e}")
    
    # Commit changes
    transaction.commit()
    
    print("\\n" + "="*70)
    print("✅ DIRECTORY VIEW CREATED!")
    print("="*70)
    print("\\nThe directory is now accessible at:")
    print("  - http://localhost:8080/Plone/directory_api")
    print("  - From Volto: /++api++/directory_api")
    print("\\nNo restart needed!")
    
else:
    print("Error: Plone site not found!")
'''

def main():
    """Main entry point"""
    print("Creating directory view...")
    print("-" * 60)
    
    # Write the script
    script_file = instance_dir / "create_directory_temp.py"
    script_file.write_text(create_script)
    
    # Run the script
    import subprocess
    
    # Activate virtualenv in the environment
    env = os.environ.copy()
    venv_dir = Path(__file__).parent / "venv"
    env['PATH'] = f"{venv_dir}/bin:{env['PATH']}"
    env['VIRTUAL_ENV'] = str(venv_dir)
    
    try:
        result = subprocess.run(
            ["zconsole", "run", "etc/zope.conf", "create_directory_temp.py"],
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
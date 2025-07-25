#!/usr/bin/env python
"""
Update OIDC redirect URI for Volto
"""

import os
import sys
from pathlib import Path

# Add instance directory to Python path
instance_dir = Path(__file__).parent / "instance"
sys.path.insert(0, str(instance_dir))

# Script to run inside Plone
update_script = '''
import transaction
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
    
    from zope.component.hooks import setSite
    setSite(plone)
    
    print("=" * 70)
    print("UPDATING OIDC REDIRECT URI FOR VOLTO")
    print("=" * 70)
    
    pas = plone.acl_users
    
    if 'oidc' not in pas.objectIds():
        print("✗ OIDC plugin not found!")
        import sys
        sys.exit(1)
        
    oidc = pas.oidc
    
    print("\\n1. CURRENT CONFIGURATION")
    print("-" * 40)
    
    current_uris = getattr(oidc, 'redirect_uris', [])
    print(f"Current redirect URIs: {current_uris}")
    
    print("\\n2. UPDATING REDIRECT URI")
    print("-" * 40)
    
    # For Volto with volto-authomatic, the redirect should go to the frontend
    new_redirect_uri = 'http://localhost:3000/login-oidc/oidc'
    
    # Update the redirect URI
    oidc.redirect_uris = [new_redirect_uri]
    print(f"✓ Updated redirect URI to: {new_redirect_uri}")
    
    print("\\n3. VERIFYING ALL SETTINGS")
    print("-" * 40)
    
    settings_to_check = [
        'client_id',
        'client_secret',
        'redirect_uris',
        'issuer',
        'authorization_endpoint',
        'token_endpoint',
        'userinfo_endpoint',
        'scope',
        'use_session',
        'create_ticket',
        'create_restapi_ticket'
    ]
    
    for setting in settings_to_check:
        if hasattr(oidc, setting):
            value = getattr(oidc, setting)
            if setting == 'client_secret' and value:
                value = '***hidden***'
            print(f"{setting}: {value}")
    
    # Ensure REST API ticket creation is enabled for Volto
    if hasattr(oidc, 'create_restapi_ticket'):
        oidc.create_restapi_ticket = True
        print("\\n✓ Enabled REST API ticket creation for Volto")
    
    # Commit changes
    transaction.commit()
    
    print("\\n" + "="*70)
    print("✅ REDIRECT URI UPDATED!")
    print("="*70)
    
    print("\\nIMPORTANT NEXT STEPS:")
    print("1. Update Google OAuth to use: http://localhost:3000/login-oidc/oidc")
    print("2. Restart both Plone backend and Volto frontend")
    print("3. Clear browser cookies/cache")
    print("4. Try logging in again")
    
    print("\\nThe flow should be:")
    print("1. Click login in Volto (port 3000)")
    print("2. Get redirected to Google")
    print("3. Google redirects back to Volto (port 3000)")
    print("4. Volto handles the callback and logs you in")
    
else:
    print("Error: Plone site not found!")
'''

def main():
    """Main entry point"""
    print("Updating OIDC redirect URI...")
    print("-" * 60)
    
    # Write the script
    script_file = instance_dir / "update_redirect_temp.py"
    script_file.write_text(update_script)
    
    # Run the script
    import subprocess
    
    # Activate virtualenv in the environment
    env = os.environ.copy()
    venv_dir = Path(__file__).parent / "venv"
    env['PATH'] = f"{venv_dir}/bin:{env['PATH']}"
    env['VIRTUAL_ENV'] = str(venv_dir)
    
    try:
        result = subprocess.run(
            ["zconsole", "run", "etc/zope.conf", "update_redirect_temp.py"],
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
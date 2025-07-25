#!/usr/bin/env python
"""
Start Plone with automatic initialization
This script handles the complete setup programmatically
"""

import os
import sys
import subprocess
from pathlib import Path
import time

# Configuration
INSTANCE_DIR = Path(__file__).parent / "instance"
VENV_DIR = Path(__file__).parent / "venv"
BACKEND_DIR = Path(__file__).parent

# Ensure we're in the backend directory
os.chdir(BACKEND_DIR)


def run_command(cmd, env=None):
    """Run a shell command"""
    if env is None:
        env = os.environ.copy()
    
    # Activate virtualenv in the environment
    env['PATH'] = f"{VENV_DIR}/bin:{env['PATH']}"
    env['VIRTUAL_ENV'] = str(VENV_DIR)
    
    # Add src directory to Python path for custom code
    env['PYTHONPATH'] = f"{BACKEND_DIR}/src:{env.get('PYTHONPATH', '')}"
    
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    
    if result.stdout:
        print(result.stdout)
    
    return True


def main():
    """Main entry point"""
    print("Starting Plone with automatic setup...")
    print("-" * 60)
    
    # Check if instance exists, if not create it
    if not (INSTANCE_DIR / "etc" / "zope.conf").exists():
        print("Creating Plone instance...")
        if not run_command(f"cd {INSTANCE_DIR} && mkwsgiinstance -d . -u admin:admin"):
            print("Failed to create instance!")
            sys.exit(1)
    
    # Create necessary directories
    for dir_path in [
        INSTANCE_DIR / "var",
        INSTANCE_DIR / "var" / "filestorage", 
        INSTANCE_DIR / "var" / "blobstorage",
        INSTANCE_DIR / "var" / "log",
        INSTANCE_DIR / "var" / "cache",
    ]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Check if site needs to be created
    data_fs = INSTANCE_DIR / "var" / "filestorage" / "Data.fs"
    if not data_fs.exists() or data_fs.stat().st_size < 1000:  # New database
        print("\nInitializing new Plone site...")
        
        # Temporarily disable retreat package for initialization
        retreat_config = INSTANCE_DIR / "etc" / "package-includes" / "retreat-configure.zcml"
        retreat_disabled = retreat_config.with_suffix('.zcml.disabled')
        if retreat_config.exists():
            print("Temporarily disabling retreat package for initialization...")
            retreat_config.rename(retreat_disabled)
        
        # Create initialization script content
        init_script = '''
import transaction
from AccessControl.SecurityManagement import newSecurityManager
from Testing.makerequest import makerequest
from Products.CMFPlone.factory import addPloneSite

app = globals()['app']
app = makerequest(app)

# Login as admin
acl_users = app.acl_users
user = acl_users.getUserById('admin')
if user is None:
    acl_users._doAddUser('admin', 'admin', ['Manager'], [])
    user = acl_users.getUserById('admin')
newSecurityManager(None, user)

# Create site
if 'Plone' not in app.objectIds():
    print("Creating Plone site...")
    site = addPloneSite(
        app,
        'Plone',
        title='Retreat Platform',
        description='Retreat Experience Platform',
        profile_id='Products.CMFPlone:plone',
        extension_ids=['plone.restapi:default'],
        default_language='en',
        setup_content=False
    )
    transaction.commit()
    print("✓ Site created successfully!")
    
    # Install Volto addon
    print("Installing Volto addon...")
    from Products.CMFCore.utils import getToolByName
    setup_tool = getToolByName(site, 'portal_setup')
    
    # Import the Volto profile
    try:
        from zope.site.hooks import setSite
        setSite(site)
        setup_tool.runAllImportStepsFromProfile('profile-plone.volto:default')
        transaction.commit()
        print("✓ Volto addon installed successfully!")
    except Exception as e:
        print(f"Warning: Could not install Volto automatically: {e}")
        print("You can install it manually through the web interface.")
else:
    print("Site already exists")
'''
        
        # Write temporary init script
        init_file = INSTANCE_DIR / "temp_init.py"
        init_file.write_text(init_script)
        
        # Run initialization
        run_command(f"cd {INSTANCE_DIR} && zconsole run etc/zope.conf temp_init.py")
        
        # Clean up
        init_file.unlink()
        
        # Wait a moment for the site to be fully initialized
        print("\nWaiting for site initialization to complete...")
        time.sleep(2)
        
        # Re-enable retreat package after initialization
        if retreat_disabled.exists():
            print("\nRe-enabling custom retreat package...")
            retreat_disabled.rename(retreat_config)
    
    # Ensure retreat package configuration exists
    retreat_config = INSTANCE_DIR / "etc" / "package-includes" / "retreat-configure.zcml"
    if not retreat_config.exists():
        print("\nCreating retreat package configuration...")
        retreat_config.parent.mkdir(parents=True, exist_ok=True)
        retreat_config.write_text('<include package="retreat" />')
    
    # Set CORS environment variables
    env = os.environ.copy()
    env.update({
        'CORS_ALLOW_ORIGIN': '*',
        'CORS_ALLOW_METHODS': 'DELETE,GET,OPTIONS,PATCH,POST,PUT',
        'CORS_ALLOW_CREDENTIALS': 'true',
        'CORS_ALLOW_HEADERS': 'Accept,Authorization,Content-Type,X-CSRF-TOKEN',
        'CORS_EXPOSE_HEADERS': 'Content-Length,X-My-Header',
        'CORS_MAX_AGE': '3600'
    })
    
    # Add src directory to Python path for custom code
    env['PYTHONPATH'] = f"{BACKEND_DIR}/src:{env.get('PYTHONPATH', '')}"
    
    print("\n" + "=" * 60)
    print("Starting Plone server...")
    print("=" * 60)
    print("\nAccess points:")
    print("- Backend: http://localhost:8080/Plone")
    print("- API: http://localhost:8080/Plone/++api++/")
    print("- Frontend: http://localhost:3000")
    print("- Admin: admin/admin")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60 + "\n")
    
    # Start server
    os.chdir(INSTANCE_DIR)
    os.execvpe(
        f"{VENV_DIR}/bin/runwsgi",
        ["runwsgi", "etc/zope.ini"],
        env
    )


if __name__ == "__main__":
    main()

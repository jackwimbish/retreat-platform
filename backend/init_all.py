#!/usr/bin/env python
"""
Initialize all Plone site configuration for Docker
"""

import os
import sys
import subprocess

def main():
    """Run initialization"""
    print("\n" + "="*60)
    print("🚀 PLONE SITE INITIALIZATION")
    print("="*60)
    
    # Temporarily disable retreat package
    retreat_config = "/app/instance/etc/package-includes/retreat-configure.zcml"
    retreat_disabled = "/app/instance/etc/package-includes/retreat-configure.zcml.disabled"
    retreat_was_disabled = False
    
    if os.path.exists(retreat_config):
        print("\nTemporarily disabling retreat package...")
        os.rename(retreat_config, retreat_disabled)
        retreat_was_disabled = True
    
    # Run the all-in-one initialization script
    print("\nRunning site initialization...")
    env = os.environ.copy()
    env['PYTHONPATH'] = '/app/src:' + env.get('PYTHONPATH', '')
    
    cmd = "cd /app/instance && zconsole run etc/zope.conf /app/docker_init_site.py"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
    
    if result.returncode != 0:
        print("ERROR during initialization:")
        print(result.stderr)
    else:
        print(result.stdout)
    
    # Re-enable retreat package
    if retreat_was_disabled and os.path.exists(retreat_disabled):
        print("\nRe-enabling retreat package...")
        os.rename(retreat_disabled, retreat_config)
    
    print("\n✅ Initialization process completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
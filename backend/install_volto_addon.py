#!/usr/bin/env python
"""Install Volto addon programmatically via REST API"""

import requests
import time
import sys

def install_volto_addon():
    """Install Volto addon through the REST API"""
    base_url = "http://localhost:8080/Plone"
    auth = ("admin", "admin")
    
    print("Installing Volto addon...")
    
    # First, check if site is ready
    try:
        response = requests.get(f"{base_url}/++api++/", auth=auth)
        if response.status_code != 200:
            print(f"Error: Site not ready. Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: Cannot connect to Plone: {e}")
        return False
    
    # Get the site object to check installed products
    try:
        response = requests.get(
            f"{base_url}/++api++/@addons",
            auth=auth,
            headers={"Accept": "application/json"}
        )
        
        if response.status_code == 200:
            addons = response.json()
            
            # Check if Volto is already installed
            for addon in addons.get('items', []):
                if addon.get('id') == 'plone.volto' and addon.get('is_installed'):
                    print("✓ Volto addon is already installed!")
                    return True
            
            # Install Volto
            print("Installing plone.volto...")
            install_response = requests.post(
                f"{base_url}/++api++/@addons",
                json={
                    "id": "plone.volto",
                    "action": "install"
                },
                auth=auth,
                headers={"Accept": "application/json", "Content-Type": "application/json"}
            )
            
            if install_response.status_code in (200, 204):
                print("✓ Volto addon installed successfully!")
                print("\nIMPORTANT: You need to restart Plone for the changes to take effect.")
                return True
            else:
                print(f"✗ Failed to install Volto addon. Status: {install_response.status_code}")
                print(f"Response: {install_response.text}")
                return False
                
    except Exception as e:
        print(f"Error during installation: {e}")
        return False

if __name__ == "__main__":
    success = install_volto_addon()
    sys.exit(0 if success else 1)
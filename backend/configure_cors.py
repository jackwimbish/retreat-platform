#!/usr/bin/env python
"""Configure CORS settings for Volto in Plone"""

import requests
import sys
import time

def configure_cors():
    """Configure CORS settings via REST API"""
    base_url = "http://localhost:8080/Plone"
    auth = ("admin", "admin")
    
    # Wait for Plone to be ready
    print("Waiting for Plone to start...")
    for i in range(30):
        try:
            response = requests.get(f"{base_url}/++api++/", auth=auth)
            print(f"Attempt {i+1}: Status code: {response.status_code}")
            if response.status_code == 200:
                print("Plone is ready!")
                break
        except requests.exceptions.ConnectionError as e:
            print(f"Attempt {i+1}: Connection error - Plone not yet available")
        except Exception as e:
            print(f"Attempt {i+1}: Error: {e}")
        time.sleep(1)
    else:
        print("Plone did not start in time")
        sys.exit(1)
    
    # Get registry endpoint
    registry_url = f"{base_url}/++api++/@registry"
    
    # CORS settings to configure
    cors_settings = {
        "plone.cors_enabled": True,
        "plone.allowed_cors_origins": ["http://localhost:3000"],
        "plone.cors_allow_methods": ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"],
        "plone.cors_allow_credentials": True,
        "plone.cors_allow_headers": ["Accept", "Authorization", "Content-Type"],
        "plone.cors_expose_headers": ["Content-Length", "X-My-Header"],
        "plone.cors_max_age": 3600
    }
    
    # Configure each setting
    for key, value in cors_settings.items():
        print(f"Setting {key}...")
        try:
            response = requests.patch(
                registry_url,
                json={key: {"value": value}},
                auth=auth,
                headers={"Accept": "application/json", "Content-Type": "application/json"}
            )
            if response.status_code in (200, 204):
                print(f"✓ {key} configured")
            else:
                print(f"✗ Failed to set {key}: {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"✗ Error setting {key}: {e}")
    
    print("\nCORS configuration complete!")
    print("Volto can now connect to http://localhost:8080/Plone/++api++/")

if __name__ == "__main__":
    configure_cors()
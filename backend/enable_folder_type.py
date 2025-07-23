#!/usr/bin/env python
"""Enable Folder content type in Plone"""

import requests
import sys

def enable_folder_type():
    """Enable Folder type via REST API"""
    base_url = "http://localhost:8080/Plone"
    auth = ("admin", "admin")
    
    print("Checking Folder type status...")
    
    # Get current types
    response = requests.get(
        f"{base_url}/++api++/@types",
        auth=auth,
        headers={"Accept": "application/json"}
    )
    
    if response.status_code == 200:
        types = response.json()
        folder_type = next((t for t in types if t['@id'].endswith('/Folder')), None)
        
        if folder_type:
            print(f"Folder type found: {folder_type.get('title', 'Folder')}")
            # Check if it's globally addable
            if not folder_type.get('addable', False):
                print("Folder type exists but is not globally addable")
                # You might need to modify this through the Plone UI
            else:
                print("✓ Folder type is already enabled")
        else:
            print("Folder type not found in available types")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    enable_folder_type()
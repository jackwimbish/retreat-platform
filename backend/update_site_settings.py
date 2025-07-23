#!/usr/bin/env python
"""Update Plone site settings for Camp Coordinator"""

import requests
import json

def update_site_settings():
    """Update site title and description via REST API"""
    base_url = "http://localhost:8080/Plone"
    auth = ("admin", "admin")
    
    # Update site properties
    site_data = {
        "title": "Camp Coordinator",
        "description": "Manage Your Retreat with Ease"
    }
    
    print("Updating site settings...")
    
    response = requests.patch(
        f"{base_url}/++api++",
        auth=auth,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        data=json.dumps(site_data)
    )
    
    if response.status_code == 204:
        print("✓ Site settings updated successfully!")
        print(f"  - Title: {site_data['title']}")
        print(f"  - Description: {site_data['description']}")
    else:
        print(f"Error updating site settings: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    update_site_settings()
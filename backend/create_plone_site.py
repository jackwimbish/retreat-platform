#!/usr/bin/env python
"""Create a Plone site in the running instance"""

import requests
import sys
import time

def create_plone_site():
    """Create Plone site via REST API"""
    base_url = "http://localhost:8080"
    auth = ("admin", "admin")
    
    # First check if Zope is running
    print("Checking if Zope is running...")
    try:
        response = requests.get(base_url, auth=auth)
        print(f"Zope status: {response.status_code}")
    except Exception as e:
        print(f"Error: Cannot connect to Zope at {base_url}")
        print(f"Make sure runwsgi is running")
        sys.exit(1)
    
    # Check if Plone site already exists
    try:
        response = requests.get(f"{base_url}/Plone", auth=auth)
        if response.status_code == 200:
            print("Plone site already exists!")
            return
    except:
        pass
    
    # Create Plone site using the @@plone-addsite view
    print("Creating Plone site...")
    
    # Prepare the form data
    form_data = {
        'site_id': 'Plone',
        'title': 'Retreat Platform',
        'description': 'Retreat Experience Platform',
        'profile_id': 'plone.volto:default',
        'extension_ids:list': 'plone.restapi:default',
        'form.submitted': '1',
        'submit': 'Create Plone Site'
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    
    try:
        response = requests.post(
            f"{base_url}/@@plone-addsite",
            data=form_data,
            auth=auth,
            headers=headers,
            allow_redirects=False
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code in (302, 303):  # Redirect means success
            print("✓ Plone site created successfully!")
            print(f"Site URL: {base_url}/Plone")
            print(f"API URL: {base_url}/Plone/++api++/")
        else:
            print(f"Failed to create site. Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"Error creating site: {e}")

if __name__ == "__main__":
    create_plone_site()
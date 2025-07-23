#!/usr/bin/env python
"""
Create content items (Issue and Participant instances) in Plone via REST API.
This script assumes the content types have already been created.
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
PLONE_URL = "http://localhost:8080/Plone"
API_URL = f"{PLONE_URL}/++api++"
USERNAME = "admin"
PASSWORD = "admin"

# Authentication
auth = (USERNAME, PASSWORD)

def create_content(container_path, content_data):
    """Create a content item via the API."""
    url = f"{API_URL}{container_path}"
    
    response = requests.post(
        url,
        auth=auth,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json=content_data
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"✓ Created {content_data['@type']}: {content_data['title']}")
        print(f"  URL: {data.get('@id', 'N/A')}")
        return True
    else:
        print(f"✗ Failed to create {content_data['@type']}: {content_data['title']}")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")
        return False

def main():
    print("Creating sample content for Retreat Platform...\n")
    
    # Create a folder to organize our content
    folder_data = {
        "@type": "Folder",
        "id": "retreat-management",
        "title": "Retreat Management",
        "description": "Container for retreat-related content"
    }
    
    print("Creating container folder...")
    if create_content("", folder_data):
        container = "/retreat-management"
    else:
        container = ""  # Use root if folder creation fails
    
    print("\nCreating sample Issues...")
    
    # Sample issues
    issues = [
        {
            "@type": "issue",
            "title": "Broken AC in Room 12",
            "description": "Air conditioning unit not working",
            "status": "new",
            "priority": "high",
            "location": "Building A, Room 12",
            "issue_description": "The air conditioning unit in Room 12 stopped working this morning. Residents report the room is getting very warm.",
            "resolution_notes": ""
        },
        {
            "@type": "issue",
            "title": "Kitchen Refrigerator Temperature",
            "description": "Main kitchen fridge running warm",
            "status": "in_progress",
            "priority": "high",
            "location": "Main Kitchen",
            "issue_description": "The main refrigerator in the kitchen is not maintaining proper temperature. Food safety concern.",
            "resolution_notes": "Technician scheduled for tomorrow morning."
        },
        {
            "@type": "issue",
            "title": "WiFi Dead Zone in Conference Room",
            "description": "No WiFi signal in west conference room",
            "status": "new",
            "priority": "normal",
            "location": "West Wing Conference Room",
            "issue_description": "Participants report no WiFi connectivity in the west conference room during sessions.",
            "resolution_notes": ""
        }
    ]
    
    for issue in issues:
        create_content(container, issue)
    
    print("\nCreating sample Participants...")
    
    # Sample participants
    today = datetime.now()
    participants = [
        {
            "@type": "participant",
            "title": "Jane Smith",
            "description": "Participant in Summer 2024 Bootcamp",
            "email": "jane.smith@example.com",
            "phone": "+1-555-0101",
            "emergency_contact_name": "John Smith",
            "emergency_contact_phone": "+1-555-0102",
            "dietary_restrictions": "Vegetarian, no nuts",
            "medical_notes": "Allergic to penicillin",
            "arrival_date": today.strftime("%Y-%m-%d"),
            "departure_date": (today + timedelta(days=30)).strftime("%Y-%m-%d")
        },
        {
            "@type": "participant",
            "title": "Bob Johnson",
            "description": "Participant in Summer 2024 Bootcamp",
            "email": "bob.johnson@example.com",
            "phone": "+1-555-0201",
            "emergency_contact_name": "Mary Johnson",
            "emergency_contact_phone": "+1-555-0202",
            "dietary_restrictions": "None",
            "medical_notes": "Type 2 diabetes - insulin dependent",
            "arrival_date": today.strftime("%Y-%m-%d"),
            "departure_date": (today + timedelta(days=30)).strftime("%Y-%m-%d")
        },
        {
            "@type": "participant",
            "title": "Alice Williams",
            "description": "Participant in Summer 2024 Bootcamp",
            "email": "alice.williams@example.com",
            "phone": "+1-555-0301",
            "emergency_contact_name": "Robert Williams",
            "emergency_contact_phone": "+1-555-0302",
            "dietary_restrictions": "Gluten-free",
            "medical_notes": "None",
            "arrival_date": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
            "departure_date": (today + timedelta(days=32)).strftime("%Y-%m-%d")
        }
    ]
    
    for participant in participants:
        create_content(container, participant)
    
    print("\n✓ Content creation complete!")
    print(f"\nView your content at: {PLONE_URL}{container}")

if __name__ == "__main__":
    main()
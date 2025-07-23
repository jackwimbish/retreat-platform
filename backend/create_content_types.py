#!/usr/bin/env python
"""
Create custom content types (Issue and Participant) in Plone via REST API.
"""

import requests
import json

# Configuration
PLONE_URL = "http://localhost:8080/Plone"
API_URL = f"{PLONE_URL}/++api++"
USERNAME = "admin"
PASSWORD = "admin"

# Authentication
auth = (USERNAME, PASSWORD)

def create_content_type(type_id, type_info):
    """Create a content type via the API."""
    response = requests.post(
        f"{API_URL}/@types",
        auth=auth,
        headers={"Content-Type": "application/json"},
        json=type_info
    )
    
    if response.status_code == 201:
        print(f"✓ Successfully created content type: {type_id}")
        return True
    elif response.status_code == 400 and "already exists" in response.text:
        print(f"! Content type {type_id} already exists")
        return True
    else:
        print(f"✗ Failed to create content type {type_id}")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text}")
        return False

def main():
    print("Creating custom content types for Retreat Platform...\n")
    
    # Define Issue content type
    issue_type = {
        "id": "issue",
        "title": "Issue",
        "description": "A maintenance or facility issue that needs attention",
        "filter_content_types": True,
        "allowed_content_types": [],
        "global_allow": True,
        "group": "Content",
        "behaviors": [
            "plone.dublincore",
            "plone.namefromtitle",
            "plone.shortname",
            "plone.ownership",
            "plone.publication",
            "plone.categorization",
            "plone.basic",
            "plone.locking",
            "plone.constraintypes",
            "plone.tableofcontents"
        ],
        "properties": {
            "fields": [
                {
                    "id": "status",
                    "title": "Status",
                    "description": "Current status of the issue",
                    "factory": "Choice",
                    "type": "string",
                    "vocabulary": {
                        "@id": f"{API_URL}/@vocabularies/issue_status"
                    },
                    "default": "new",
                    "required": True
                },
                {
                    "id": "priority",
                    "title": "Priority",
                    "description": "Priority level of the issue",
                    "factory": "Choice",
                    "type": "string",
                    "vocabulary": {
                        "@id": f"{API_URL}/@vocabularies/issue_priority"
                    },
                    "default": "normal",
                    "required": True
                },
                {
                    "id": "location",
                    "title": "Location",
                    "description": "Where is the issue located?",
                    "factory": "Text",
                    "type": "string",
                    "required": True
                },
                {
                    "id": "issue_description",
                    "title": "Issue Description",
                    "description": "Detailed description of the issue",
                    "factory": "Text",
                    "type": "string",
                    "widget": "textarea",
                    "required": True
                },
                {
                    "id": "resolution_notes",
                    "title": "Resolution Notes",
                    "description": "Notes about how the issue was resolved",
                    "factory": "Text",
                    "type": "string",
                    "widget": "textarea",
                    "required": False
                }
            ],
            "fieldsets": [
                {
                    "id": "default",
                    "title": "Default",
                    "fields": ["title", "description"]
                },
                {
                    "id": "issue_details",
                    "title": "Issue Details",
                    "fields": ["status", "priority", "location", "issue_description"]
                },
                {
                    "id": "resolution",
                    "title": "Resolution",
                    "fields": ["resolution_notes"]
                }
            ],
            "required": ["title", "status", "priority", "location", "issue_description"]
        }
    }
    
    # Define Participant content type
    participant_type = {
        "id": "participant",
        "title": "Participant",
        "description": "A participant in a retreat or bootcamp",
        "filter_content_types": True,
        "allowed_content_types": [],
        "global_allow": True,
        "group": "Content",
        "behaviors": [
            "plone.dublincore",
            "plone.namefromtitle",
            "plone.shortname",
            "plone.ownership",
            "plone.publication",
            "plone.categorization",
            "plone.basic",
            "plone.locking",
            "plone.constraintypes",
            "plone.tableofcontents"
        ],
        "properties": {
            "fields": [
                {
                    "id": "email",
                    "title": "Email",
                    "description": "Participant's email address",
                    "factory": "Email",
                    "type": "string",
                    "required": True
                },
                {
                    "id": "phone",
                    "title": "Phone",
                    "description": "Participant's phone number",
                    "factory": "Text",
                    "type": "string",
                    "required": False
                },
                {
                    "id": "emergency_contact_name",
                    "title": "Emergency Contact Name",
                    "description": "Name of emergency contact",
                    "factory": "Text",
                    "type": "string",
                    "required": True
                },
                {
                    "id": "emergency_contact_phone",
                    "title": "Emergency Contact Phone",
                    "description": "Phone number of emergency contact",
                    "factory": "Text",
                    "type": "string",
                    "required": True
                },
                {
                    "id": "dietary_restrictions",
                    "title": "Dietary Restrictions",
                    "description": "Any dietary restrictions or preferences",
                    "factory": "Text",
                    "type": "string",
                    "widget": "textarea",
                    "required": False
                },
                {
                    "id": "medical_notes",
                    "title": "Medical Notes",
                    "description": "Any medical conditions or medications",
                    "factory": "Text",
                    "type": "string",
                    "widget": "textarea",
                    "required": False
                },
                {
                    "id": "arrival_date",
                    "title": "Arrival Date",
                    "description": "Date of arrival",
                    "factory": "Date",
                    "type": "string",
                    "widget": "date",
                    "required": True
                },
                {
                    "id": "departure_date",
                    "title": "Departure Date",
                    "description": "Date of departure",
                    "factory": "Date",
                    "type": "string",
                    "widget": "date",
                    "required": True
                }
            ],
            "fieldsets": [
                {
                    "id": "default",
                    "title": "Default",
                    "fields": ["title", "description"]
                },
                {
                    "id": "contact",
                    "title": "Contact Information",
                    "fields": ["email", "phone"]
                },
                {
                    "id": "emergency",
                    "title": "Emergency Contact",
                    "fields": ["emergency_contact_name", "emergency_contact_phone"]
                },
                {
                    "id": "health",
                    "title": "Health Information",
                    "fields": ["dietary_restrictions", "medical_notes"]
                },
                {
                    "id": "schedule",
                    "title": "Schedule",
                    "fields": ["arrival_date", "departure_date"]
                }
            ],
            "required": ["title", "email", "emergency_contact_name", "emergency_contact_phone", "arrival_date", "departure_date"]
        }
    }
    
    # Create the content types
    success = True
    
    # Note: The REST API for creating content types is limited in Plone 6
    # You may need to create these through the web interface instead
    print("Note: The Plone REST API has limited support for creating content types.")
    print("If this script fails, you'll need to create them through the web interface.")
    print()
    
    # Try to create Issue type
    if not create_content_type("issue", issue_type):
        success = False
    
    # Try to create Participant type
    if not create_content_type("participant", participant_type):
        success = False
    
    if success:
        print("\n✓ All content types created successfully!")
    else:
        print("\n✗ Some content types could not be created via API.")
        print("\nTo create them manually:")
        print("1. Go to http://localhost:8080/Plone/manage")
        print("2. Navigate to Site Setup → Dexterity Content Types")
        print("3. Click 'Add New Content Type'")
        print("4. Use the field definitions from this script")

if __name__ == "__main__":
    main()
# Content Type Definitions for Retreat Platform

## Issue Content Type

**ID:** issue  
**Title:** Issue  
**Description:** A maintenance or facility issue that needs attention

### Fields:

1. **Status** (Choice field)
   - Field name: status
   - Required: Yes
   - Default: new
   - Values: new, in_progress, resolved

2. **Priority** (Choice field)
   - Field name: priority
   - Required: Yes
   - Default: normal
   - Values: low, normal, high, critical

3. **Location** (Text field)
   - Field name: location
   - Required: Yes
   - Description: Where is the issue located?

4. **Issue Description** (Text field, textarea widget)
   - Field name: issue_description
   - Required: Yes
   - Description: Detailed description of the issue

5. **Resolution Notes** (Text field, textarea widget)
   - Field name: resolution_notes
   - Required: No
   - Description: Notes about how the issue was resolved

## Participant Content Type

**ID:** participant  
**Title:** Participant  
**Description:** A participant in a retreat or bootcamp

### Fields:

1. **Email** (Email field)
   - Field name: email
   - Required: Yes
   - Description: Participant's email address

2. **Phone** (Text field)
   - Field name: phone
   - Required: No
   - Description: Participant's phone number

3. **Emergency Contact Name** (Text field)
   - Field name: emergency_contact_name
   - Required: Yes

4. **Emergency Contact Phone** (Text field)
   - Field name: emergency_contact_phone
   - Required: Yes

5. **Dietary Restrictions** (Text field, textarea widget)
   - Field name: dietary_restrictions
   - Required: No

6. **Medical Notes** (Text field, textarea widget)
   - Field name: medical_notes
   - Required: No
   - Description: Any medical conditions or medications

7. **Arrival Date** (Date field)
   - Field name: arrival_date
   - Required: Yes

8. **Departure Date** (Date field)
   - Field name: departure_date
   - Required: Yes

## Manual Creation Steps

1. Log in to Plone admin: http://localhost:8080/Plone/manage
2. Go to Site Setup → Dexterity Content Types
3. Click "Add New Content Type"
4. For each content type:
   - Enter the ID, Title, and Description
   - Save
   - Click on the new type
   - Go to "Fields" tab
   - Add each field with the specifications above
   - Save after adding all fields

Once created, you can use the `create_content_items.py` script to populate sample data.
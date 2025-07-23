#!/usr/bin/env python
"""
Create content types by directly accessing Plone's internal API.
This script should be run inside the Plone instance using:
docker-compose exec backend /app/bin/zconsole run /data/create_types_via_zope.py
"""

from plone.dexterity.fti import DexterityFTI
from Products.CMFCore.utils import getToolByName
import transaction

# Get the Plone site
app = locals().get('app')
if app and hasattr(app, 'Plone'):
    plone = app.Plone
    
    # Get the portal_types tool
    portal_types = getToolByName(plone, 'portal_types')
    
    print("Creating content types...")
    
    # Create Issue type
    if 'issue' not in portal_types:
        fti = DexterityFTI('issue')
        fti.title = 'Issue'
        fti.description = 'A maintenance or facility issue that needs attention'
        fti.factory = 'issue'
        fti.add_view_expr = 'string:${folder_url}/++add++issue'
        fti.link_target = ''
        fti.immediate_view = 'view'
        fti.global_allow = True
        fti.filter_content_types = True
        fti.allowed_content_types = []
        fti.allow_discussion = False
        fti.default_view = 'view'
        fti.view_methods = ('view',)
        fti.default_view_fallback = False
        fti.add_permission = 'cmf.AddPortalContent'
        fti.klass = 'plone.dexterity.content.Container'
        fti.schema = 'retreat.platform.content.issue.IIssue'
        fti.model_source = '''
<model xmlns="http://namespaces.plone.org/supermodel/schema">
  <schema>
    <field name="status" type="zope.schema.Choice">
      <title>Status</title>
      <description>Current status of the issue</description>
      <required>True</required>
      <default>new</default>
      <values>
        <element>new</element>
        <element>in_progress</element>
        <element>resolved</element>
      </values>
    </field>
    <field name="priority" type="zope.schema.Choice">
      <title>Priority</title>
      <description>Priority level of the issue</description>
      <required>True</required>
      <default>normal</default>
      <values>
        <element>low</element>
        <element>normal</element>
        <element>high</element>
        <element>critical</element>
      </values>
    </field>
    <field name="location" type="zope.schema.TextLine">
      <title>Location</title>
      <description>Where is the issue located?</description>
      <required>True</required>
    </field>
    <field name="issue_description" type="zope.schema.Text">
      <title>Issue Description</title>
      <description>Detailed description of the issue</description>
      <required>True</required>
    </field>
    <field name="resolution_notes" type="zope.schema.Text">
      <title>Resolution Notes</title>
      <description>Notes about how the issue was resolved</description>
      <required>False</required>
    </field>
  </schema>
</model>
'''
        portal_types._setObject('issue', fti)
        print("✓ Created Issue content type")
    else:
        print("! Issue type already exists")
    
    # Create Participant type
    if 'participant' not in portal_types:
        fti = DexterityFTI('participant')
        fti.title = 'Participant'
        fti.description = 'A participant in a retreat or bootcamp'
        fti.factory = 'participant'
        fti.add_view_expr = 'string:${folder_url}/++add++participant'
        fti.link_target = ''
        fti.immediate_view = 'view'
        fti.global_allow = True
        fti.filter_content_types = True
        fti.allowed_content_types = []
        fti.allow_discussion = False
        fti.default_view = 'view'
        fti.view_methods = ('view',)
        fti.default_view_fallback = False
        fti.add_permission = 'cmf.AddPortalContent'
        fti.klass = 'plone.dexterity.content.Container'
        fti.schema = 'retreat.platform.content.participant.IParticipant'
        fti.model_source = '''
<model xmlns="http://namespaces.plone.org/supermodel/schema">
  <schema>
    <field name="email" type="zope.schema.TextLine">
      <title>Email</title>
      <description>Participant's email address</description>
      <required>True</required>
    </field>
    <field name="phone" type="zope.schema.TextLine">
      <title>Phone</title>
      <description>Participant's phone number</description>
      <required>False</required>
    </field>
    <field name="emergency_contact_name" type="zope.schema.TextLine">
      <title>Emergency Contact Name</title>
      <description>Name of emergency contact</description>
      <required>True</required>
    </field>
    <field name="emergency_contact_phone" type="zope.schema.TextLine">
      <title>Emergency Contact Phone</title>
      <description>Phone number of emergency contact</description>
      <required>True</required>
    </field>
    <field name="dietary_restrictions" type="zope.schema.Text">
      <title>Dietary Restrictions</title>
      <description>Any dietary restrictions or preferences</description>
      <required>False</required>
    </field>
    <field name="medical_notes" type="zope.schema.Text">
      <title>Medical Notes</title>
      <description>Any medical conditions or medications</description>
      <required>False</required>
    </field>
    <field name="arrival_date" type="zope.schema.Date">
      <title>Arrival Date</title>
      <description>Date of arrival</description>
      <required>True</required>
    </field>
    <field name="departure_date" type="zope.schema.Date">
      <title>Departure Date</title>
      <description>Date of departure</description>
      <required>True</required>
    </field>
  </schema>
</model>
'''
        portal_types._setObject('participant', fti)
        print("✓ Created Participant content type")
    else:
        print("! Participant type already exists")
    
    # Commit the transaction
    transaction.commit()
    print("\n✓ Content types created successfully!")
    
else:
    print("Error: This script must be run inside Plone context")
    print("Use: docker-compose exec backend /app/bin/zconsole run <this_script>")
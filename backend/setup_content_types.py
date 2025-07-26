#!/usr/bin/env python
"""
Setup custom content types for the Retreat Platform
Run this after the site is created via zconsole
"""

# This script is meant to be run directly via zconsole
import transaction
from plone.dexterity.fti import DexterityFTI
from Products.CMFCore.utils import getToolByName
from AccessControl.SecurityManagement import newSecurityManager
from Testing.makerequest import makerequest

# Get the Zope app
app = globals()['app']
app = makerequest(app)

# Login as admin
acl_users = app.acl_users
user = acl_users.getUserById('admin')
if user:
    newSecurityManager(None, user)

# Get Plone site
if 'Plone' in app.objectIds():
    plone = app.Plone
    
    # Set up the site context properly
    from zope.site.hooks import setSite
    setSite(plone)
    
    portal_types = getToolByName(plone, 'portal_types')
    
    print("Setting up custom content types...")
    
    # Create Issue content type
    if 'issue' not in portal_types:
        print("Creating Issue content type...")
        fti = DexterityFTI('issue')
        fti.title = 'Issue'
        fti.description = 'A maintenance or facility issue that needs attention'
        fti.icon_expr = 'string:file-earmark-text'
        fti.factory = 'issue'
        fti.add_view_expr = 'string:${folder_url}/++add++issue'
        fti.global_allow = True
        fti.filter_content_types = False
        fti.allowed_content_types = []
        fti.allow_discussion = False
        fti.default_view = 'view'
        fti.view_methods = ('view',)
        
        # Enable behaviors
        fti.behaviors = (
            'plone.dublin_core',
            'plone.namefromtitle',
            'plone.allowdiscussion',
            'plone.excludefromnavigation',
            'plone.shortname',
            'plone.ownership',
            'plone.publication',
            'plone.categorization',
            'plone.basic',
            'plone.relateditems',
            'plone.versioning',
            'plone.locking',
            'plone.leadimage',
            'volto.blocks',
        )
        
        # Define the schema
        fti.model_source = """
<model xmlns:i18n="http://xml.zope.org/namespaces/i18n"
       xmlns:security="http://namespaces.plone.org/supermodel/security"
       xmlns:form="http://namespaces.plone.org/supermodel/form"
       xmlns:marshal="http://namespaces.plone.org/supermodel/marshal"
       xmlns="http://namespaces.plone.org/supermodel/schema">
  <schema>
    <field name="status" type="zope.schema.Choice">
      <default>new</default>
      <description>Current status of the issue</description>
      <title>Status</title>
      <values>
        <element>new</element>
        <element>in_progress</element>
        <element>resolved</element>
      </values>
    </field>
    <field name="priority" type="zope.schema.Choice">
      <default>normal</default>
      <description>Priority level of the issue</description>
      <title>Priority</title>
      <values>
        <element>low</element>
        <element>normal</element>
        <element>high</element>
        <element>urgent</element>
      </values>
    </field>
    <field name="location" type="zope.schema.TextLine">
      <description>Where is this issue located?</description>
      <required>True</required>
      <title>Location</title>
    </field>
    <field name="issue_description" type="zope.schema.Text">
      <description>Detailed description of the issue</description>
      <required>True</required>
      <title>Issue Description</title>
    </field>
    <field name="resolution_notes" type="zope.schema.Text">
      <description>Notes about how the issue was resolved</description>
      <required>False</required>
      <title>Resolution Notes</title>
    </field>
  </schema>
</model>
"""
        
        portal_types._setObject('issue', fti)
        # Ensure icon_expr is properly initialized
        issue_fti = portal_types['issue']
        issue_fti._updateProperty('icon_expr', 'string:file-earmark-text')
        print("✓ Issue content type created")
    else:
        print("! Issue content type already exists")
        # Update icon_expr for existing type
        issue_fti = portal_types['issue']
        issue_fti._updateProperty('icon_expr', 'string:file-earmark-text')
        print("  ✓ Updated icon expression")
    
    # Create Participant content type
    if 'participant' not in portal_types:
        print("Creating Participant content type...")
        fti = DexterityFTI('participant')
        fti.title = 'Participant'
        fti.description = 'A participant in a retreat or bootcamp'
        fti.icon_expr = 'string:user'
        fti.factory = 'participant'
        fti.add_view_expr = 'string:${folder_url}/++add++participant'
        fti.global_allow = True
        fti.filter_content_types = False
        fti.allowed_content_types = []
        fti.allow_discussion = False
        fti.default_view = 'view'
        fti.view_methods = ('view',)
        
        # Enable behaviors
        fti.behaviors = (
            'plone.dublin_core',
            'plone.namefromtitle',
            'plone.allowdiscussion',
            'plone.excludefromnavigation',
            'plone.shortname',
            'plone.ownership',
            'plone.publication',
            'plone.categorization',
            'plone.basic',
            'plone.relateditems',
            'plone.versioning',
            'plone.locking',
            'plone.leadimage',
            'volto.blocks',
        )
        
        # Define the schema
        fti.model_source = """
<model xmlns:i18n="http://xml.zope.org/namespaces/i18n"
       xmlns:security="http://namespaces.plone.org/supermodel/security"
       xmlns:form="http://namespaces.plone.org/supermodel/form"
       xmlns:marshal="http://namespaces.plone.org/supermodel/marshal"
       xmlns="http://namespaces.plone.org/supermodel/schema">
  <schema>
    <field name="email" type="zope.schema.TextLine">
      <description>Contact email address</description>
      <required>True</required>
      <title>Email</title>
    </field>
    <field name="phone" type="zope.schema.TextLine">
      <description>Contact phone number</description>
      <required>False</required>
      <title>Phone</title>
    </field>
    <field name="emergency_contact" type="zope.schema.Text">
      <description>Emergency contact information</description>
      <required>True</required>
      <title>Emergency Contact</title>
    </field>
    <field name="dietary_restrictions" type="zope.schema.Text">
      <description>Any dietary restrictions or allergies</description>
      <required>False</required>
      <title>Dietary Restrictions</title>
    </field>
    <field name="special_needs" type="zope.schema.Text">
      <description>Any special accommodations needed</description>
      <required>False</required>
      <title>Special Needs</title>
    </field>
    <field name="arrival_date" type="zope.schema.Date">
      <description>Expected arrival date</description>
      <required>True</required>
      <title>Arrival Date</title>
    </field>
    <field name="departure_date" type="zope.schema.Date">
      <description>Expected departure date</description>
      <required>True</required>
      <title>Departure Date</title>
    </field>
  </schema>
</model>
"""
        
        portal_types._setObject('participant', fti)
        # Ensure icon_expr is properly initialized
        participant_fti = portal_types['participant']
        participant_fti._updateProperty('icon_expr', 'string:user')
        print("✓ Participant content type created")
    else:
        print("! Participant content type already exists")
        # Update icon_expr for existing type
        participant_fti = portal_types['participant']
        participant_fti._updateProperty('icon_expr', 'string:user')
        print("  ✓ Updated icon expression")
    
    # Update permissions if needed
    plone.reindexObject()
    
    # Commit transaction
    transaction.commit()
    
    print("\n✓ Content types setup complete!")
    print("\nYou can now create:")
    print("- Issues: for tracking maintenance and facility problems")
    print("- Participants: for managing retreat attendees")
    print("\nAccess them through the Volto UI at http://localhost:3000")
else:
    print("Error: Plone site not found!")
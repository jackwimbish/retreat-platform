#!/usr/bin/env python
"""
All-in-one initialization script for Docker
Run this via zconsole to set up the entire site
"""

import transaction
from plone.dexterity.fti import DexterityFTI
from Products.CMFCore.utils import getToolByName
from AccessControl.SecurityManagement import newSecurityManager
from Testing.makerequest import makerequest
from plone.app.workflow.interfaces import ISharingPageRole
from zope.interface import implementer
from zope.component import adapter, provideAdapter
from Products.CMFPlone.interfaces import INonInstallable

# Get the Zope app
app = globals()['app']
app = makerequest(app)

# Login as admin
acl_users = app.acl_users
user = acl_users.getUserById('admin')
if user:
    newSecurityManager(None, user)

# Get Plone site
if 'Plone' not in app.objectIds():
    print("Error: Plone site not found!")
    import sys
    sys.exit(1)

plone = app.Plone

# Set up the site context properly
from zope.component.hooks import setSite
setSite(plone)

print("\n" + "="*60)
print("🚀 INITIALIZING PLONE SITE")
print("="*60)

# 1. SETUP CONTENT TYPES
print("\n>>> Setting up content types...")
portal_types = getToolByName(plone, 'portal_types')

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
    print("! Issue content type already exists - updating icon")
    issue_fti = portal_types['issue']
    issue_fti._updateProperty('icon_expr', 'string:file-earmark-text')

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
    print("! Participant content type already exists - updating icon")
    participant_fti = portal_types['participant']
    participant_fti._updateProperty('icon_expr', 'string:user')

# Update permissions if needed
plone.reindexObject()
transaction.commit()
print("✓ Content types setup complete!")

# 2. SETUP USER ROLES AND PERMISSIONS
print("\n>>> Setting up user roles and permissions...")

# Configure Issue permissions
if 'issue' in portal_types:
    issue_type = portal_types['issue']
    
    # Use only the permissions that actually exist on FTI
    issue_permissions = [
        # View permission - all authenticated users can view issues
        ('View', ['Manager', 'Editor', 'Member', 'Authenticated']),
        ('Access contents information', ['Manager', 'Editor', 'Member', 'Authenticated']),
        
        # Delete permission - Only Admin and Staff
        ('Delete objects', ['Manager', 'Editor']),
        
        # Manage properties - for changing metadata (only staff)
        ('Manage properties', ['Manager', 'Editor']),
    ]
    
    # Apply permissions to Issue type
    for permission, roles in issue_permissions:
        issue_type.manage_permission(permission, roles=roles, acquire=False)
    
    # Set the add permission property
    issue_type.add_permission = 'cmf.AddPortalContent'
    
    print("✓ Issue permissions configured")

# Configure Participant permissions
if 'participant' in portal_types:
    participant_type = portal_types['participant']
    
    participant_permissions = [
        # View permission - all authenticated users can view participant directory
        ('View', ['Manager', 'Editor', 'Member', 'Authenticated']),
        ('Access contents information', ['Manager', 'Editor', 'Member', 'Authenticated']),
        
        # Delete - Only Admin
        ('Delete objects', ['Manager']),
        
        # Manage properties - Only staff
        ('Manage properties', ['Manager', 'Editor']),
    ]
    
    # Apply permissions to Participant type
    for permission, roles in participant_permissions:
        participant_type.manage_permission(permission, roles=roles, acquire=False)
    
    # Set the add permission property
    participant_type.add_permission = 'cmf.AddPortalContent'
    
    print("✓ Participant permissions configured")

# Set site-wide add permission
plone.manage_permission('Add portal content', ['Manager', 'Editor', 'Member'], acquire=True)
print("✓ Members, Staff, and Admins can now add content site-wide")

transaction.commit()
print("✓ Permissions setup complete!")

# 3. PROTECT HOMEPAGE
print("\n>>> Protecting homepage from anonymous access...")

# Get the default homepage (usually front-page)
if hasattr(plone, 'front-page'):
    homepage = plone['front-page']
    
    # Set view permission to authenticated users only
    homepage.manage_permission('View',
        roles=['Manager', 'Editor', 'Member', 'Authenticated'],
        acquire=False)
    
    # Also set the root site view permission
    plone.manage_permission('View',
        roles=['Manager', 'Editor', 'Member', 'Authenticated'],
        acquire=False)
    
    # Set the login form to be accessible by anonymous
    plone.manage_permission('Access contents information',
        roles=['Manager', 'Editor', 'Member', 'Authenticated', 'Anonymous'],
        acquire=False)
    
    transaction.commit()
    print("✓ Homepage protected - anonymous users will be redirected to login")
else:
    print("! Homepage not found - skipping protection")

# 4. CREATE DEFAULT CONTENT STRUCTURE
print("\n>>> Creating default content structure...")

# Create Issues folder (as Document in Volto)
if 'issues' not in plone.objectIds():
    plone.invokeFactory('Document', 'issues',
                       title='Issues',
                       description='Report and track maintenance issues')
    issues_folder = plone['issues']
    
    # Set permissions for issues folder
    folder_permissions = [
        ('View', ['Manager', 'Editor', 'Member', 'Authenticated']),
        ('Access contents information', ['Manager', 'Editor', 'Member', 'Authenticated']),
    ]
    
    for permission, roles in folder_permissions:
        issues_folder.manage_permission(permission, roles=roles, acquire=False)
    
    print("✓ Issues folder created")
else:
    print("! Issues folder already exists")

# Create Locations folder (as Document in Volto)
if 'locations' not in plone.objectIds():
    plone.invokeFactory('Document', 'locations',
                       title='Locations',
                       description='Different areas and buildings')
    locations_folder = plone['locations']
    
    # Set permissions for locations folder
    folder_permissions = [
        ('View', ['Manager', 'Editor', 'Member', 'Authenticated']),
        ('Access contents information', ['Manager', 'Editor', 'Member', 'Authenticated']),
    ]
    
    for permission, roles in folder_permissions:
        locations_folder.manage_permission(permission, roles=roles, acquire=False)
    
    # Create some default locations
    default_locations = [
        ('main-hall', 'Main Hall', 'Central gathering and dining area'),
        ('dormitory-a', 'Dormitory A', 'Sleeping quarters block A'),
        ('dormitory-b', 'Dormitory B', 'Sleeping quarters block B'),
        ('kitchen', 'Kitchen', 'Food preparation and storage area'),
        ('outdoor-areas', 'Outdoor Areas', 'Grounds, paths, and outdoor facilities'),
    ]
    
    for loc_id, loc_title, loc_desc in default_locations:
        if loc_id not in locations_folder.objectIds():
            locations_folder.invokeFactory('Document', loc_id,
                                         title=loc_title,
                                         description=loc_desc)
            # Set basic permissions for location folders
            location = locations_folder[loc_id]
            for permission, roles in folder_permissions:
                location.manage_permission(permission, roles=roles, acquire=False)
    
    print("✓ Locations folder created with default locations")
else:
    print("! Locations folder already exists")

# Create Participants folder (as Document in Volto)
if 'participants' not in plone.objectIds():
    plone.invokeFactory('Document', 'participants',
                       title='Participants',
                       description='Retreat and bootcamp participants')
    participants_folder = plone['participants']
    
    # Set permissions for participants folder
    folder_permissions = [
        ('View', ['Manager', 'Editor', 'Member', 'Authenticated']),
        ('Access contents information', ['Manager', 'Editor', 'Member', 'Authenticated']),
    ]
    
    for permission, roles in folder_permissions:
        participants_folder.manage_permission(permission, roles=roles, acquire=False)
    
    print("✓ Participants folder created")
else:
    print("! Participants folder already exists")

transaction.commit()
print("✓ Default content structure created!")

# 5. SETUP WORKFLOW
print("\n>>> Setting up simplified workflow...")

# Get workflow tool
wf_tool = getToolByName(plone, 'portal_workflow')

# Set Issue to use simple_publication_workflow
wf_tool.setChainForPortalTypes(['issue'], 'simple_publication_workflow')

# Update workflow so new issues are automatically published
workflow = wf_tool.getWorkflowById('simple_publication_workflow')
if workflow:
    # This is handled in the frontend now, but keeping for reference
    print("✓ Issues set to use simple_publication_workflow")

# Set Participant to use simple_publication_workflow too
wf_tool.setChainForPortalTypes(['participant'], 'simple_publication_workflow')
print("✓ Participants set to use simple_publication_workflow")

# Update security
wf_tool.updateRoleMappings()
transaction.commit()
print("✓ Workflow configuration complete!")

# 6. CREATE SAMPLE USERS
print("\n>>> Creating sample users...")

# Get user management tools
membership_tool = getToolByName(plone, 'portal_membership')
registration_tool = getToolByName(plone, 'portal_registration')

# Sample users to create
sample_users = [
    ('director1', 'director123', 'director1@example.com', 'Camp Director', ['Manager']),
    ('staff1', 'staff123', 'staff1@example.com', 'Staff Member 1', ['Editor']),
    ('staff2', 'staff123', 'staff2@example.com', 'Staff Member 2', ['Editor']),
    ('participant1', 'participant123', 'participant1@example.com', 'John Doe', ['Member']),
    ('participant2', 'participant123', 'participant2@example.com', 'Jane Smith', ['Member']),
    ('participant3', 'participant123', 'participant3@example.com', 'Bob Wilson', ['Member']),
]

for username, password, email, fullname, roles in sample_users:
    if not membership_tool.getMemberById(username):
        registration_tool.addMember(username, password)
        member = membership_tool.getMemberById(username)
        member.setMemberProperties(mapping={
            'email': email,
            'fullname': fullname,
        })
        # Set roles
        plone.acl_users.userFolderEditUser(username, password, roles, [])
        print(f"✓ Created user: {username} ({fullname}) with roles: {', '.join(roles)}")
    else:
        print(f"! User {username} already exists")

transaction.commit()
print("✓ Sample users created!")

# 7. INSTALL VOLTO
print("\n>>> Installing Volto...")
try:
    qi_tool = getToolByName(plone, 'portal_quickinstaller')
    
    # First install plone.volto if not already installed
    installable = [p['id'] for p in qi_tool.listInstallableProducts()]
    
    if 'plone.volto' in installable:
        qi_tool.installProduct('plone.volto')
        print("✓ plone.volto installed successfully!")
        transaction.commit()
    else:
        print("! plone.volto not available or already installed")
    
    # Also try to install plone.restapi if needed
    if 'plone.restapi' in installable:
        qi_tool.installProduct('plone.restapi')
        print("✓ plone.restapi installed successfully!")
        transaction.commit()
    else:
        print("! plone.restapi not available or already installed")
        
except Exception as e:
    print(f"! Error installing Volto: {str(e)}")

# 8. TRY TO INSTALL OIDC PLUGIN
print("\n>>> Attempting to install OIDC plugin...")
try:
    qi_tool = getToolByName(plone, 'portal_quickinstaller')
    
    # Check if pas.plugins.oidc is available
    installable = [p['id'] for p in qi_tool.listInstallableProducts()]
    
    if 'pas.plugins.oidc' in installable:
        qi_tool.installProduct('pas.plugins.oidc')
        print("✓ OIDC plugin installed successfully!")
        
        # Try to get the plugin
        from pas.plugins.oidc.utils import get_plugin
        plugin = get_plugin()
        if plugin:
            print("✓ OIDC plugin is active")
        else:
            print("! OIDC plugin installed but not active")
    else:
        print("! OIDC plugin not available for installation")
        print("  You'll need to install it manually through the web interface")
except Exception as e:
    print(f"! Could not install OIDC plugin: {str(e)}")
    print("  You'll need to install it manually through the web interface")

# Final summary
print("\n" + "="*60)
print("✅ SITE INITIALIZATION COMPLETE!")
print("="*60)
print("\nYour Plone site is now configured with:")
print("- Custom content types (Issue, Participant)")
print("- User roles and permissions")
print("- Protected homepage (login required)")
print("- Default folder structure")
print("- Sample users")
print("\nSample user credentials:")
print("- Admin: admin/admin")
print("- Director: director1/director123")
print("- Staff: staff1/staff123, staff2/staff123")
print("- Participants: participant1/participant123, etc.")
print("\nNext steps:")
print("1. If OIDC wasn't installed, install it manually")
print("2. Configure Google OAuth credentials")
print("3. Access the site at http://localhost:3000")
print("="*60)
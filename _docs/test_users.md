Configuring Issue permissions...
✓ Issue permissions configured
  - All authenticated users can view issues
  - Only Staff can delete issues

Configuring Participant permissions...
✓ Participant permissions configured
  - All authenticated users can view participant directory
  - Only Admin can delete participants

Configuring /issues folder permissions...
✓ /issues folder permissions configured

Configuring site-wide add permissions...
✓ Issue add permission set to 'cmf.AddPortalContent'
✓ Members, Staff, and Admins can now add content

============================================================
Creating sample users...
============================================================
  ✓ Created user: director (Jane Director)
    Password: director123
    Roles: Manager

  ✓ Created user: staff1 (John Staff)
    Password: staff123
    Roles: Editor

  ✓ Created user: staff2 (Mary Staff)
    Password: staff123
    Roles: Editor

  ✓ Created user: participant1 (Alice Participant)
    Password: participant123
    Roles: Member

  ✓ Created user: participant2 (Bob Participant)
    Password: participant123
    Roles: Member

============================================================
✅ Role and permission setup complete!
============================================================

Role Summary:
- Admin (Manager role): Full system access
- Staff (Editor role): Create/edit/resolve issues, manage participants
- Participant (Member role): Create issues, view all issues, edit own issues

Permission Notes:
- Edit permissions in Plone work through ownership
- When a Member creates an issue, they become the Owner
- Owners can edit their own content by default
- Staff (Editors) can edit any content

You can now login at http://localhost:3000 with any of the sample users

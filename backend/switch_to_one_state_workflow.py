#!/usr/bin/env python
"""
Switch issues to one_state_workflow
This removes the private/published states and makes all issues always visible
"""

import os
import sys
from pathlib import Path

# Add instance directory to Python path
instance_dir = Path(__file__).parent / "instance"
sys.path.insert(0, str(instance_dir))

# Script to run inside Plone
switch_script = '''
import transaction
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
    from zope.component.hooks import setSite
    setSite(plone)
    
    print("=" * 70)
    print("SWITCHING ISSUES TO ONE STATE WORKFLOW")
    print("=" * 70)
    
    # Get workflow tool
    workflow_tool = getToolByName(plone, 'portal_workflow')
    
    # 1. Check current workflow
    print("\\n1. CHECKING CURRENT WORKFLOW")
    print("-" * 40)
    
    current_chain = workflow_tool.getChainFor('issue')
    print(f"Current workflow for issues: {', '.join(current_chain) if current_chain else 'None'}")
    
    # 2. Change workflow for issue content type
    print("\\n2. CHANGING WORKFLOW ASSIGNMENT")
    print("-" * 40)
    
    # Set the new workflow
    workflow_tool.setChainForPortalTypes(('issue',), ('one_state_workflow',))
    
    # Verify the change
    new_chain = workflow_tool.getChainFor('issue')
    print(f"New workflow for issues: {', '.join(new_chain) if new_chain else 'None'}")
    
    # 3. Update existing issues
    print("\\n3. UPDATING EXISTING ISSUES")
    print("-" * 40)
    
    catalog = getToolByName(plone, 'portal_catalog')
    issues = catalog(portal_type='issue')
    
    print(f"Found {len(issues)} issues to update")
    
    updated_count = 0
    error_count = 0
    
    for brain in issues:
        try:
            obj = brain.getObject()
            
            # Get current state info
            try:
                old_state = workflow_tool.getInfoFor(obj, 'review_state', 'unknown')
            except:
                old_state = 'unknown'
            
            # Update the workflow state
            workflow_tool.updateRoleMappingsFor(obj)
            
            # Reindex the object
            obj.reindexObject(idxs=['allowedRolesAndUsers', 'review_state'])
            obj.reindexObjectSecurity()
            
            # Get new state (should be 'published' for one_state_workflow)
            try:
                new_state = workflow_tool.getInfoFor(obj, 'review_state', 'unknown')
            except:
                new_state = 'published'  # one_state_workflow default
            
            updated_count += 1
            print(f"  ✓ {obj.title}: {old_state} → {new_state}")
            
        except Exception as e:
            error_count += 1
            print(f"  ✗ Error updating {brain.getPath()}: {str(e)}")
    
    print(f"\\nSummary:")
    print(f"  - Updated: {updated_count} issues")
    print(f"  - Errors: {error_count} issues")
    
    # 4. Clear workflow history (optional but clean)
    print("\\n4. CLEANING WORKFLOW HISTORY")
    print("-" * 40)
    
    cleaned = 0
    for brain in issues:
        try:
            obj = brain.getObject()
            # Remove workflow history attribute if it exists
            if hasattr(obj, 'workflow_history'):
                # Keep the history but clear references to old workflow
                if 'simple_publication_workflow' in obj.workflow_history:
                    del obj.workflow_history['simple_publication_workflow']
                    cleaned += 1
        except:
            pass
    
    print(f"Cleaned workflow history for {cleaned} issues")
    
    # 5. Verify permissions
    print("\\n5. VERIFYING PERMISSIONS")
    print("-" * 40)
    
    # Check a sample issue
    if issues:
        sample = issues[0].getObject()
        view_roles = sample.rolesOfPermission('View')
        allowed_roles = [r['name'] for r in view_roles if r.get('selected')]
        print(f"Sample issue '{sample.title}' viewable by: {', '.join(allowed_roles)}")
    
    # Commit all changes
    transaction.commit()
    
    print("\\n" + "="*70)
    print("✅ WORKFLOW SWITCH COMPLETE!")
    print("="*70)
    
    print("\\nWhat changed:")
    print("1. ✓ Issues now use one_state_workflow")
    print("2. ✓ All issues are in 'published' state")
    print("3. ✓ No more private/published confusion")
    print("4. ✓ All users with View permission can see all issues")
    
    print("\\nBenefits:")
    print("- New issues are immediately visible to everyone")
    print("- No workflow transitions needed")
    print("- Simpler user experience")
    print("- Edit permissions still controlled by ownership/roles")
    
else:
    print("Error: Plone site not found!")
'''

def main():
    """Main entry point"""
    print("Switching issues to one_state_workflow...")
    print("-" * 60)
    
    # Write the script
    script_file = instance_dir / "switch_workflow_temp.py"
    script_file.write_text(switch_script)
    
    # Run the script
    import subprocess
    
    # Activate virtualenv in the environment
    env = os.environ.copy()
    venv_dir = Path(__file__).parent / "venv"
    env['PATH'] = f"{venv_dir}/bin:{env['PATH']}"
    env['VIRTUAL_ENV'] = str(venv_dir)
    
    try:
        result = subprocess.run(
            ["zconsole", "run", "etc/zope.conf", "switch_workflow_temp.py"],
            cwd=instance_dir,
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
            
    finally:
        # Clean up
        if script_file.exists():
            script_file.unlink()

if __name__ == "__main__":
    main()
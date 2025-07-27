"""Browser view to initialize stored values for existing issues."""

from plone import api
from Products.Five import BrowserView
from zope.annotation.interfaces import IAnnotations
import transaction


class InitializeStoredValues(BrowserView):
    """Initialize stored values for activity tracking."""
    
    def __call__(self):
        """Initialize stored values for all issues."""
        # Check permissions
        if not api.user.has_permission('Manage portal'):
            return "Unauthorized: You need Manager permissions to run this."
        
        results = []
        results.append("Initializing stored values for existing issues...\n")
        
        # Search for all issues
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(portal_type='issue')
        
        results.append(f"Found {len(brains)} issues to process\n")
        
        initialized = 0
        skipped = 0
        errors = 0
        
        for brain in brains:
            try:
                issue = brain.getObject()
                
                # Check if stored values already exist
                annotations = IAnnotations(issue)
                if 'retreat.stored_values' in annotations:
                    results.append(f"Skipping {issue.title} - already has stored values")
                    skipped += 1
                    continue
                
                # Get current values
                status = getattr(issue, 'status', 'new')
                if hasattr(status, 'token'):
                    status = status.token
                    
                priority = getattr(issue, 'priority', 'normal')
                if hasattr(priority, 'token'):
                    priority = priority.token
                    
                assigned_to = getattr(issue, 'assigned_to', None)
                if hasattr(assigned_to, 'token'):
                    assigned_to = assigned_to.token
                
                # Store the values
                annotations['retreat.stored_values'] = {
                    'status': status,
                    'priority': priority,
                    'assigned_to': assigned_to
                }
                annotations._p_changed = True
                
                results.append(f"Initialized stored values for: {issue.title}")
                results.append(f"  Status: {status}")
                results.append(f"  Priority: {priority}")
                results.append(f"  Assigned to: {assigned_to}")
                initialized += 1
                
            except Exception as e:
                results.append(f"Error processing issue {brain.getPath()}: {e}")
                errors += 1
        
        # Commit the transaction
        transaction.commit()
        
        results.append(f"\nStored values initialization complete!")
        results.append(f"Initialized: {initialized}")
        results.append(f"Skipped: {skipped}")
        results.append(f"Errors: {errors}")
        
        # Return plain text response
        self.request.response.setHeader('Content-Type', 'text/plain')
        return '\n'.join(results)
"""Activity management for Issues - handles comments and system activities."""

from datetime import datetime
import uuid
from plone import api
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
import transaction


def add_activity(issue, activity_type, data, user=None):
    """Add an activity to an issue's activity log.
    
    Args:
        issue: The issue object
        activity_type: Type of activity ('comment', 'status_change', etc.)
        data: Dict containing activity-specific data
        user: User object or None to use current user
    """
    if user is None:
        user = api.user.get_current()
    
    # Get current activity log or initialize
    activity_log = getattr(issue, 'activity_log', []) or []
    
    # Create new activity
    activity = {
        'id': str(uuid.uuid4()),
        'type': activity_type,
        'timestamp': datetime.now().isoformat() + 'Z',
        'user_id': user.getId(),
        'user_fullname': user.getProperty('fullname', user.getId()),
        'data': data
    }
    
    # Add soft-delete flag for comments
    if activity_type == 'comment':
        activity['deleted'] = False
    
    # Append to log
    activity_log.append(activity)
    
    # Update issue with retry logic for concurrent updates
    _update_activity_log_with_retry(issue, activity_log)
    
    return activity


def update_comment(issue, comment_id, new_text, user=None):
    """Update an existing comment.
    
    Args:
        issue: The issue object
        comment_id: ID of the comment to update
        new_text: New comment text
        user: User object or None to use current user
    
    Returns:
        True if updated, False if not found or not authorized
    """
    if user is None:
        user = api.user.get_current()
    
    activity_log = getattr(issue, 'activity_log', []) or []
    
    for activity in activity_log:
        if (activity.get('id') == comment_id and 
            activity.get('type') == 'comment' and
            activity.get('user_id') == user.getId() and
            not activity.get('deleted', False)):
            
            # Update the comment
            activity['data']['text'] = new_text
            activity['edited'] = True
            activity['edited_timestamp'] = datetime.now().isoformat() + 'Z'
            
            _update_activity_log_with_retry(issue, activity_log)
            return True
    
    return False


def delete_comment(issue, comment_id, user=None):
    """Soft delete a comment.
    
    Args:
        issue: The issue object
        comment_id: ID of the comment to delete
        user: User object or None to use current user
    
    Returns:
        True if deleted, False if not found or not authorized
    """
    if user is None:
        user = api.user.get_current()
    
    activity_log = getattr(issue, 'activity_log', []) or []
    
    for activity in activity_log:
        if (activity.get('id') == comment_id and 
            activity.get('type') == 'comment' and
            activity.get('user_id') == user.getId() and
            not activity.get('deleted', False)):
            
            # Soft delete
            activity['deleted'] = True
            activity['deleted_timestamp'] = datetime.now().isoformat() + 'Z'
            
            _update_activity_log_with_retry(issue, activity_log)
            return True
    
    return False


def _update_activity_log_with_retry(issue, activity_log, max_retries=3):
    """Update activity log with retry logic for concurrent updates."""
    for attempt in range(max_retries):
        try:
            # Create a savepoint
            savepoint = transaction.savepoint()
            
            # Update the field
            issue.activity_log = activity_log
            issue.reindexObject(idxs=['modified'])
            
            # Try to commit the transaction
            transaction.commit()
            return
            
        except Exception as e:
            # Rollback to savepoint and retry
            savepoint.rollback()
            if attempt == max_retries - 1:
                raise
            # Refresh the object and its activity log
            issue._p_jar.sync()
            activity_log = getattr(issue, 'activity_log', []) or []


def log_issue_changes(event):
    """Event subscriber to automatically log issue changes."""
    try:
        issue = event.object
        
        # Only process Issue content type
        if getattr(issue, 'portal_type', None) != 'issue':
            return
        
        # Skip if this is a new object (will be handled by object added event)
        descriptions = getattr(event, 'descriptions', None)
        if not descriptions:
            return
        
        # Skip if activity_log field doesn't exist yet (old issues)
        if not hasattr(issue, 'activity_log'):
            return
            
        current_user = api.user.get_current()
        
        for desc in descriptions:
            if not hasattr(desc, 'attributes'):
                continue
                
            # Get the old values
            old_values = getattr(desc, 'oldValue', {})
            if not isinstance(old_values, dict):
                continue
                
            # Check if specific fields changed
            for attr in desc.attributes:
                old_value = old_values.get(attr)
                new_value = getattr(issue, attr, None)
                
                # Log status changes
                if attr == 'status' and old_value != new_value:
                    add_activity(issue, 'status_change', {
                        'from': old_value,
                        'to': new_value
                    }, current_user)
                
                # Log priority changes
                elif attr == 'priority' and old_value != new_value:
                    add_activity(issue, 'priority_change', {
                        'from': old_value,
                        'to': new_value
                    }, current_user)
                
                # Log assignment changes
                elif attr == 'assigned_to' and old_value != new_value:
                    add_activity(issue, 'assignment', {
                        'from': old_value,
                        'to': new_value
                    }, current_user)
    except Exception:
        # Silently fail to not break the modification process
        pass
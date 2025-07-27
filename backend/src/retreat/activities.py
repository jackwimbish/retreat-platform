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
    import logging
    logger = logging.getLogger('retreat.activities')
    
    try:
        issue = event.object
        
        # Only process Issue content type
        if getattr(issue, 'portal_type', None) != 'issue':
            return
        
        # Skip if activity_log field doesn't exist yet (old issues)
        if not hasattr(issue, 'activity_log'):
            return
            
        current_user = api.user.get_current()
        
        # Log for debugging
        logger.info(f"Processing issue modification for: {issue.title}")
        
        # Get descriptions from event
        descriptions = getattr(event, 'descriptions', [])
        if not descriptions:
            # Sometimes changes come without descriptions, so let's check the object itself
            # Store the current values to compare on next change
            logger.info("No descriptions in event, checking stored values")
            
            # Get stored values from annotations
            from zope.annotation.interfaces import IAnnotations
            annotations = IAnnotations(issue)
            stored_key = 'retreat.stored_values'
            stored = annotations.get(stored_key, {})
            
            # Check for changes
            current_status = getattr(issue, 'status', None)
            current_priority = getattr(issue, 'priority', None)
            current_assigned = getattr(issue, 'assigned_to', None)
            
            # Convert token values to strings for comparison
            if hasattr(current_status, 'token'):
                current_status = current_status.token
            if hasattr(current_priority, 'token'):
                current_priority = current_priority.token
                
            changes_made = False
            
            # Check status
            if stored.get('status') != current_status and stored.get('status') is not None:
                logger.info(f"Status changed from {stored.get('status')} to {current_status}")
                add_activity(issue, 'status_change', {
                    'from': stored.get('status'),
                    'to': current_status
                }, current_user)
                changes_made = True
                
            # Check priority  
            if stored.get('priority') != current_priority and stored.get('priority') is not None:
                logger.info(f"Priority changed from {stored.get('priority')} to {current_priority}")
                add_activity(issue, 'priority_change', {
                    'from': stored.get('priority'),
                    'to': current_priority
                }, current_user)
                changes_made = True
                
            # Check assignment
            if stored.get('assigned_to') != current_assigned and stored.get('assigned_to') is not None:
                logger.info(f"Assignment changed from {stored.get('assigned_to')} to {current_assigned}")
                add_activity(issue, 'assignment', {
                    'from': stored.get('assigned_to'),
                    'to': current_assigned
                }, current_user)
                changes_made = True
            
            # Update stored values for next comparison
            annotations[stored_key] = {
                'status': current_status,
                'priority': current_priority,
                'assigned_to': current_assigned
            }
            # Force the annotations to persist
            annotations._p_changed = True
            
            if changes_made:
                logger.info("Changes logged successfully")
            
        else:
            # Process descriptions if available
            logger.info(f"Processing {len(descriptions)} descriptions")
            for i, desc in enumerate(descriptions):
                logger.info(f"Description {i}: {desc}")
                logger.info(f"Has attributes: {hasattr(desc, 'attributes')}")
                
                if not hasattr(desc, 'attributes'):
                    logger.info(f"Description {i} has no attributes")
                    continue
                    
                logger.info(f"Attributes: {desc.attributes}")
                    
                # Get the old values
                old_values = getattr(desc, 'oldValue', {})
                logger.info(f"Old values type: {type(old_values)}, content: {old_values}")
                
                if not isinstance(old_values, dict):
                    logger.info(f"Old values is not a dict, skipping")
                    continue
                    
                # Check if specific fields changed
                for attr in desc.attributes:
                    # Extract the actual attribute name from the fully qualified name
                    # e.g., 'Plone_5_1753631178_2_552559_0_issue.priority' -> 'priority'
                    if '.' in attr:
                        simple_attr = attr.split('.')[-1]
                    else:
                        simple_attr = attr
                    
                    logger.info(f"Extracted attribute name: {simple_attr} from {attr}")
                    
                    # Skip non-relevant attributes
                    if simple_attr not in ['status', 'priority', 'assigned_to']:
                        continue
                    
                    # Get current value
                    new_value = getattr(issue, simple_attr, None)
                    
                    # Get stored value from annotations
                    from zope.annotation.interfaces import IAnnotations
                    annotations = IAnnotations(issue)
                    stored_values = annotations.get('retreat.stored_values', {})
                    old_value = stored_values.get(simple_attr)
                    
                    logger.info(f"Checking attribute '{simple_attr}': old={old_value}, new={new_value}")
                    
                    # Handle token values
                    if hasattr(new_value, 'token'):
                        new_value = new_value.token
                        logger.info(f"Converted new token value to: {new_value}")
                    
                    # Check if value actually changed
                    if old_value == new_value:
                        logger.info(f"No change detected for {simple_attr}")
                        continue
                    
                    # Log status changes
                    if simple_attr == 'status':
                        logger.info(f"Status changed from {old_value} to {new_value}")
                        add_activity(issue, 'status_change', {
                            'from': old_value,
                            'to': new_value
                        }, current_user)
                    
                    # Log priority changes
                    elif simple_attr == 'priority':
                        logger.info(f"Priority changed from {old_value} to {new_value}")
                        add_activity(issue, 'priority_change', {
                            'from': old_value,
                            'to': new_value
                        }, current_user)
                    
                    # Log assignment changes
                    elif simple_attr == 'assigned_to':
                        logger.info(f"Assignment changed from {old_value} to {new_value}")
                        add_activity(issue, 'assignment', {
                            'from': old_value,
                            'to': new_value
                        }, current_user)
                        
            # After processing all descriptions, update stored values
            current_status = getattr(issue, 'status', None)
            current_priority = getattr(issue, 'priority', None) 
            current_assigned = getattr(issue, 'assigned_to', None)
            
            # Convert token values
            if hasattr(current_status, 'token'):
                current_status = current_status.token
            if hasattr(current_priority, 'token'):
                current_priority = current_priority.token
            if hasattr(current_assigned, 'token'):
                current_assigned = current_assigned.token
                
            # Update stored values for next comparison
            from zope.annotation.interfaces import IAnnotations
            annotations = IAnnotations(issue)
            annotations['retreat.stored_values'] = {
                'status': current_status,
                'priority': current_priority,
                'assigned_to': current_assigned
            }
            annotations._p_changed = True
            logger.info(f"Updated stored values: status={current_status}, priority={current_priority}, assigned_to={current_assigned}")
                        
    except Exception as e:
        logger.error(f"Error in log_issue_changes: {e}")
        import traceback
        logger.error(traceback.format_exc())
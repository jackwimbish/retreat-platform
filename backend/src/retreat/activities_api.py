"""REST API endpoints for Issue activities and comments."""

from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from plone import api
from plone.restapi.serializer.converters import json_compatible
from . import activities
import json


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Activities:
    """Expandable element to include activities in issue serialization."""
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'activities': {
                '@id': f'{self.context.absolute_url()}/@activities',
            },
        }
        if not expand or getattr(self.context, 'portal_type', None) != 'issue':
            return result

        # Get activity log
        activity_log = getattr(self.context, 'activity_log', []) or []
        
        # Filter out soft-deleted comments for non-owners
        current_user = api.user.get_current()
        filtered_activities = []
        
        for activity in activity_log:
            if activity.get('type') == 'comment' and activity.get('deleted', False):
                # Only show deleted comments to their authors
                if activity.get('user_id') == current_user.getId():
                    filtered_activities.append(activity)
            else:
                filtered_activities.append(activity)
        
        result['activities']['items'] = filtered_activities
        result['activities']['items_total'] = len(filtered_activities)
        
        return result


class ActivitiesGet(Service):
    """Get activities for an issue."""

    def reply(self):
        # Check if this is an issue
        if getattr(self.context, 'portal_type', None) != 'issue':
            self.request.response.setStatus(400)
            return {'error': 'This endpoint is only available for issues'}
        
        # Get activity log
        activity_log = getattr(self.context, 'activity_log', []) or []
        
        # Filter out soft-deleted comments for non-owners
        current_user = api.user.get_current()
        filtered_activities = []
        
        for activity in activity_log:
            if activity.get('type') == 'comment' and activity.get('deleted', False):
                # Only show deleted comments to their authors
                if activity.get('user_id') == current_user.getId():
                    filtered_activities.append(activity)
            else:
                filtered_activities.append(activity)
        
        return {
            '@id': f'{self.context.absolute_url()}/@activities',
            'items': json_compatible(filtered_activities),
            'items_total': len(filtered_activities)
        }


class ActivitiesPost(Service):
    """Add a new comment to an issue."""

    def reply(self):
        # Check if this is an issue
        if getattr(self.context, 'portal_type', None) != 'issue':
            self.request.response.setStatus(400)
            return {'error': 'This endpoint is only available for issues'}
        
        # Check permissions - all authenticated users can comment
        if api.user.is_anonymous():
            self.request.response.setStatus(401)
            return {'error': 'Authentication required'}
        
        # Get comment text from request
        data = json.loads(self.request.get('BODY', '{}'))
        comment_text = data.get('text', '').strip()
        
        if not comment_text:
            self.request.response.setStatus(400)
            return {'error': 'Comment text is required'}
        
        # Add the comment
        activity = activities.add_activity(
            self.context,
            'comment',
            {'text': comment_text}
        )
        
        self.request.response.setStatus(201)
        return json_compatible(activity)


class ActivityPatch(Service):
    """Update an existing comment."""

    def reply(self):
        # Extract activity ID from URL
        activity_id = self.request.get('activity_id')
        if not activity_id:
            self.request.response.setStatus(400)
            return {'error': 'Activity ID is required'}
        
        # Check if this is an issue
        if getattr(self.context, 'portal_type', None) != 'issue':
            self.request.response.setStatus(400)
            return {'error': 'This endpoint is only available for issues'}
        
        # Get new text from request
        data = json.loads(self.request.get('BODY', '{}'))
        new_text = data.get('text', '').strip()
        
        if not new_text:
            self.request.response.setStatus(400)
            return {'error': 'Comment text is required'}
        
        # Try to update the comment
        success = activities.update_comment(self.context, activity_id, new_text)
        
        if success:
            return {'message': 'Comment updated successfully'}
        else:
            self.request.response.setStatus(404)
            return {'error': 'Comment not found or you do not have permission to edit it'}


class ActivityDelete(Service):
    """Soft delete a comment."""

    def reply(self):
        # Extract activity ID from URL
        activity_id = self.request.get('activity_id')
        if not activity_id:
            self.request.response.setStatus(400)
            return {'error': 'Activity ID is required'}
        
        # Check if this is an issue
        if getattr(self.context, 'portal_type', None) != 'issue':
            self.request.response.setStatus(400)
            return {'error': 'This endpoint is only available for issues'}
        
        # Try to delete the comment
        success = activities.delete_comment(self.context, activity_id)
        
        if success:
            return {'message': 'Comment deleted successfully'}
        else:
            self.request.response.setStatus(404)
            return {'error': 'Comment not found or you do not have permission to delete it'}
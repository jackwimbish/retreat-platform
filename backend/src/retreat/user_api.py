"""Public API endpoint for user display names"""

from plone import api
from plone.restapi.services import Service
import json


class UserDisplayName(Service):
    """Get display name for a user - public endpoint"""

    def reply(self):
        user_id = self.request.get('user_id')
        if not user_id:
            self.request.response.setStatus(400)
            return {'error': 'user_id parameter is required'}
        
        # Get the user
        user = api.user.get(userid=user_id)
        if not user:
            return {'display_name': user_id}  # Return the ID if user not found
        
        # Get display name (fullname or username)
        fullname = user.getProperty('fullname', '')
        display_name = fullname if fullname else user.getId()
        
        return {
            'user_id': user_id,
            'display_name': display_name
        }
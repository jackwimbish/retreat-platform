# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone import api
import json


class DirectoryView(BrowserView):
    """
    Browser view to provide directory data for all authenticated users
    """

    def __call__(self):
        """Return JSON data with all users and their basic information"""
        
        # Check if user is authenticated
        if api.user.is_anonymous():
            self.request.response.setStatus(401)
            return json.dumps({"error": "Authentication required"})
        
        # Get portal membership tool
        mtool = getToolByName(self.context, 'portal_membership')
        
        # Get all users
        users_data = []
        
        # Get all user ids
        acl_users = api.portal.get_tool('acl_users')
        users = acl_users.searchUsers()
        
        for user_info in users:
            user_id = user_info.get('userid')
            if user_id:
                member = mtool.getMemberById(user_id)
                if member:
                    # Get member properties
                    fullname = member.getProperty('fullname', '') or user_id
                    email = member.getProperty('email', '')
                    
                    # Get roles (excluding default ones)
                    roles = list(member.getRoles())
                    # Filter out default Plone roles
                    filtered_roles = [r for r in roles if r not in ['Member', 'Authenticated']]
                    
                    # Get portrait URL
                    portrait_url = None
                    portrait = mtool.getPersonalPortrait(user_id)
                    if portrait and portrait.getId() != 'defaultUser.png':
                        portrait_url = f"{api.portal.get().absolute_url()}/++api++/Members/{user_id}/@@images/portrait"
                    
                    user_data = {
                        "id": user_id,
                        "fullname": fullname,
                        "email": email,
                        "roles": filtered_roles,
                        "portrait": portrait_url
                    }
                    
                    users_data.append(user_data)
        
        # Sort users by fullname
        users_data.sort(key=lambda x: x['fullname'].lower())
        
        # Set response headers
        self.request.response.setHeader('Content-Type', 'application/json')
        self.request.response.setHeader('Cache-Control', 'private, max-age=60')
        
        return json.dumps({
            "users": users_data,
            "@id": self.context.absolute_url() + '/@@directory'
        })
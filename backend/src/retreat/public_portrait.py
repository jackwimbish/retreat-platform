from plone import api
from Products.Five import BrowserView
from zope.publisher.interfaces import NotFound
import logging

logger = logging.getLogger(__name__)


class PublicPortraitView(BrowserView):
    """Serves user portraits without authentication requirement"""
    
    def __call__(self):
        username = self.request.get('username')
        if not username:
            raise NotFound(self, 'username', self.request)
        
        # Get the portal
        portal = api.portal.get()
        
        # Get the membership tool
        membership_tool = api.portal.get_tool('portal_membership')
        
        # Get member by username
        member = membership_tool.getMemberById(username)
        if not member:
            logger.info(f"Member not found: {username}")
            raise NotFound(self, username, self.request)
        
        # Get the portrait
        portrait = membership_tool.getPersonalPortrait(username)
        
        # Check if it's the default portrait
        default_portrait = membership_tool.getPersonalPortrait()
        
        if portrait and portrait.absolute_url() != default_portrait.absolute_url():
            # We have a custom portrait
            # Get the actual image data
            if hasattr(portrait, 'data'):
                # It's a file-like object
                data = portrait.data
                if hasattr(data, 'data'):
                    # It might be wrapped
                    data = data.data
            elif hasattr(portrait, '_data'):
                data = portrait._data
            else:
                # Try to get the image through the portal_memberdata tool
                memberdata_tool = api.portal.get_tool('portal_memberdata')
                portraits = getattr(memberdata_tool, 'portraits', None)
                if portraits and hasattr(portraits, username):
                    portrait_obj = getattr(portraits, username)
                    if hasattr(portrait_obj, 'data'):
                        data = portrait_obj.data
                    else:
                        data = portrait_obj
                else:
                    logger.info(f"No portrait data found for: {username}")
                    raise NotFound(self, username, self.request)
            
            # Set headers and return data
            self.request.response.setHeader('Content-Type', 'image/jpeg')
            self.request.response.setHeader('Cache-Control', 'public, max-age=3600')
            
            return data
        
        # No custom portrait found
        logger.info(f"No custom portrait for: {username}")
        raise NotFound(self, username, self.request)
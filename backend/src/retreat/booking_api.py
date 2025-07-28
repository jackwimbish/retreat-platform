"""Custom API endpoints for booking management"""

from plone import api
from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
import logging

logger = logging.getLogger(__name__)


@implementer(IPublishTraverse)
class CancelBooking(Service):
    """Custom endpoint to cancel bookings that handles OAuth users properly"""
    
    def __init__(self, context, request):
        super(CancelBooking, self).__init__(context, request)
        self.params = []
    
    def publishTraverse(self, request, name):
        self.params.append(name)
        return self
    
    def reply(self):
        """Cancel a booking - works for OAuth users"""
        if not self.params:
            self.request.response.setStatus(400)
            return {"error": "No booking ID provided"}
        
        booking_id = self.params[0]
        current_user = api.user.get_current()
        
        if not current_user or current_user.getId() == 'Anonymous User':
            self.request.response.setStatus(401)
            return {"error": "Authentication required"}
        
        # Try to find the booking
        catalog = api.portal.get_tool('portal_catalog')
        results = catalog(id=booking_id, portal_type='room_booking')
        
        if not results:
            self.request.response.setStatus(404)
            return {"error": "Booking not found"}
        
        booking = results[0].getObject()
        
        # Check ownership - handle OAuth users
        user_id = current_user.getId()
        user_email = current_user.getProperty('email', '')
        user_fullname = current_user.getProperty('fullname', '')
        
        # Get creator info
        creator_id = booking.creators[0] if booking.creators else booking.Creator()
        
        # Enhanced ownership check for OAuth users
        is_owner = False
        
        # Direct ID match
        if creator_id == user_id:
            is_owner = True
        # OAuth numeric ID match (Google OAuth IDs are numeric)
        elif creator_id.isdigit() and user_id.endswith(creator_id):
            is_owner = True
        # Email match
        elif user_email and creator_id == user_email:
            is_owner = True
        # Check if booking title contains user's name (common pattern)
        elif user_fullname and user_fullname in booking.title:
            is_owner = True
        # Check if user ID contains creator ID (OAuth pattern)
        elif creator_id in user_id:
            is_owner = True
        
        # Also allow managers
        if api.user.has_permission('Manage portal', user=current_user, obj=booking):
            is_owner = True
        
        logger.info(f"Cancel booking check - User: {user_id}, Creator: {creator_id}, "
                   f"Email: {user_email}, Fullname: {user_fullname}, "
                   f"Is Owner: {is_owner}")
        
        if not is_owner:
            self.request.response.setStatus(403)
            return {"error": "You can only cancel your own bookings"}
        
        # Delete the booking using privileged execution
        try:
            from plone.protect.interfaces import IDisableCSRFProtection
            from zope.interface import alsoProvides
            
            # Disable CSRF protection for this request
            alsoProvides(self.request, IDisableCSRFProtection)
            
            # Use api.content.delete which handles permissions better
            with api.env.adopt_roles(['Manager']):
                api.content.delete(obj=booking)
            
            logger.info(f"Booking {booking_id} cancelled by {user_id}")
            return {"success": True, "message": "Booking cancelled successfully"}
            
        except Exception as e:
            logger.error(f"Error cancelling booking: {str(e)}")
            self.request.response.setStatus(500)
            return {"error": "Failed to cancel booking"}


@implementer(IPublishTraverse)
class MyBookings(Service):
    """Get current user's bookings - handles OAuth users"""
    
    def reply(self):
        current_user = api.user.get_current()
        
        if not current_user or current_user.getId() == 'Anonymous User':
            self.request.response.setStatus(401)
            return {"error": "Authentication required"}
        
        user_id = current_user.getId()
        user_email = current_user.getProperty('email', '')
        user_fullname = current_user.getProperty('fullname', '')
        
        # Search for bookings
        catalog = api.portal.get_tool('portal_catalog')
        all_bookings = catalog(portal_type='room_booking')
        
        my_bookings = []
        
        for brain in all_bookings:
            booking = brain.getObject()
            creator_id = booking.creators[0] if booking.creators else booking.Creator()
            
            # Check if this is user's booking (same logic as cancel)
            is_mine = False
            
            if creator_id == user_id:
                is_mine = True
            elif creator_id.isdigit() and user_id.endswith(creator_id):
                is_mine = True
            elif user_email and creator_id == user_email:
                is_mine = True
            elif user_fullname and user_fullname in booking.title:
                is_mine = True
            elif creator_id in user_id:
                is_mine = True
            
            if is_mine:
                my_bookings.append({
                    'id': booking.getId(),
                    'uid': booking.UID(),
                    'title': booking.title,
                    'start_datetime': booking.start_datetime.isoformat(),
                    'end_datetime': booking.end_datetime.isoformat(),
                    'room': booking.room.to_object.title if booking.room else 'Unknown',
                    'purpose': booking.purpose or '',
                    'url': booking.absolute_url()
                })
        
        return {
            'bookings': my_bookings,
            'count': len(my_bookings)
        }
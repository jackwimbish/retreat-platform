"""Utilities for room booking system"""

from datetime import datetime, timedelta
from plone import api
import logging

logger = logging.getLogger(__name__)


def round_to_half_hour(dt):
    """Round datetime to nearest half hour"""
    minute = dt.minute
    if minute < 15:
        minute = 0
    elif minute < 45:
        minute = 30
    else:
        minute = 0
        dt = dt + timedelta(hours=1)
    
    return dt.replace(minute=minute, second=0, microsecond=0)


def validate_booking_times(start_dt, end_dt):
    """Validate booking times"""
    errors = []
    
    # Ensure times are on half-hour boundaries
    if start_dt.minute not in [0, 30] or start_dt.second != 0:
        errors.append("Start time must be on the hour or half-hour")
    
    if end_dt.minute not in [0, 30] or end_dt.second != 0:
        errors.append("End time must be on the hour or half-hour")
    
    # Ensure end is after start
    if end_dt <= start_dt:
        errors.append("End time must be after start time")
    
    # Check maximum duration (5 hours)
    duration = end_dt - start_dt
    if duration > timedelta(hours=5):
        errors.append("Bookings cannot exceed 5 hours")
    
    # Check minimum duration (30 minutes)
    if duration < timedelta(minutes=30):
        errors.append("Bookings must be at least 30 minutes")
    
    return errors


def check_booking_conflicts(room_uid, start_dt, end_dt, exclude_booking_uid=None):
    """Check if there are any booking conflicts for a room"""
    catalog = api.portal.get_tool('portal_catalog')
    
    # Search for bookings of this room
    query = {
        'portal_type': 'room_booking',
        'path': '/'.join(api.portal.get().getPhysicalPath()) + '/conference-rooms/bookings'
    }
    
    bookings = catalog(query)
    conflicts = []
    
    for brain in bookings:
        booking = brain.getObject()
        
        # Skip if this is the booking we're editing
        if exclude_booking_uid and booking.UID() == exclude_booking_uid:
            continue
        
        # Skip if it's a different room
        if not booking.room or booking.room.to_object.UID() != room_uid:
            continue
        
        # Check for time overlap
        booking_start = booking.start_datetime
        booking_end = booking.end_datetime
        
        # Overlap occurs if:
        # 1. New booking starts during existing booking
        # 2. New booking ends during existing booking  
        # 3. New booking completely contains existing booking
        # 4. Existing booking completely contains new booking
        
        if (start_dt < booking_end and end_dt > booking_start):
            conflicts.append({
                'booking': booking,
                'start': booking_start,
                'end': booking_end,
                'title': booking.title,
                'user': booking.Creator()
            })
    
    return conflicts


def get_user_bookings(username=None):
    """Get all bookings for a user"""
    if not username:
        username = api.user.get_current().getId()
    
    catalog = api.portal.get_tool('portal_catalog')
    
    query = {
        'portal_type': 'room_booking',
        'Creator': username,
        'sort_on': 'start_datetime',
        'sort_order': 'ascending'
    }
    
    return catalog(query)


def get_room_bookings(room_uid, start_date=None, end_date=None):
    """Get all bookings for a specific room within a date range"""
    catalog = api.portal.get_tool('portal_catalog')
    
    query = {
        'portal_type': 'room_booking',
        'sort_on': 'start_datetime',
        'sort_order': 'ascending'
    }
    
    # Note: We'll need to filter by room relation and date range in the results
    # since catalog queries don't easily support relation filtering
    
    bookings = catalog(query)
    filtered = []
    
    for brain in bookings:
        booking = brain.getObject()
        
        # Check if it's for this room
        if not booking.room or booking.room.to_object.UID() != room_uid:
            continue
        
        # Check date range if provided
        if start_date and booking.end_datetime < start_date:
            continue
        if end_date and booking.start_datetime > end_date:
            continue
            
        filtered.append(booking)
    
    return filtered


def can_user_cancel_booking(booking, user=None):
    """Check if user can cancel a booking"""
    if not user:
        user = api.user.get_current()
    
    # Users can cancel their own bookings
    if booking.Creator() == user.getId():
        return True
    
    # Managers can cancel any booking
    if api.user.has_permission('Manage portal', user=user, obj=booking):
        return True
    
    return False
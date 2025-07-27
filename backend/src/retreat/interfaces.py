"""Interfaces for retreat package"""

from zope import schema
from zope.interface import Interface
from z3c.relationfield.schema import RelationChoice
from plone.app.vocabularies.catalog import CatalogSource


class ICampAlert(Interface):
    """Camp Alert schema"""
    
    alert_type = schema.Choice(
        title=u"Alert Type",
        description=u"Type of alert being sent",
        values=['emergency', 'event', 'info'],
        required=True,
        default='info'
    )
    
    message = schema.Text(
        title=u"Message",
        description=u"The alert message to send to all camp members",
        required=True
    )
    
    active = schema.Bool(
        title=u"Active",
        description=u"Whether this alert is currently active",
        required=False,
        default=True
    )


class IConferenceRoom(Interface):
    """Conference Room schema"""
    
    capacity = schema.Int(
        title=u"Capacity",
        description=u"Maximum number of people this room can accommodate",
        required=True,
        min=1,
        max=100
    )


class IRoomBooking(Interface):
    """Room Booking schema"""
    
    room = RelationChoice(
        title=u"Room",
        description=u"Conference room being booked",
        source=CatalogSource(portal_type='conference_room'),
        required=True
    )
    
    start_datetime = schema.Datetime(
        title=u"Start Date/Time",
        description=u"When the booking starts",
        required=True
    )
    
    end_datetime = schema.Datetime(
        title=u"End Date/Time", 
        description=u"When the booking ends",
        required=True
    )
    
    purpose = schema.Text(
        title=u"Purpose",
        description=u"Purpose of this booking (optional)",
        required=False
    )
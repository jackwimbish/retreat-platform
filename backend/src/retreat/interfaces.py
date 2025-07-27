"""Interfaces for retreat package"""

from zope import schema
from zope.interface import Interface


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
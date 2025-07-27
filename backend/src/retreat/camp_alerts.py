"""Email notifications for camp alerts"""
import os
import logging
from plone import api

logger = logging.getLogger('retreat.camp_alerts')


def send_camp_alert(obj, event):
    """Send email notification when a new camp alert is created"""
    
    # Only process camp_alert content type
    if obj.portal_type != 'camp_alert':
        return
    
    # Only send on creation, not edits
    if event.__class__.__name__ != 'ObjectAddedEvent':
        return
    
    # Check if the alert should send immediately
    if not getattr(obj, 'send_immediately', True):
        return
        
    # Check if notifications are enabled
    if os.environ.get('ENABLE_ISSUE_NOTIFICATIONS', 'false').lower() != 'true':
        logger.info("Camp alert notifications are disabled")
        return
    
    # Check for test mode
    test_mode = os.environ.get('RESEND_TEST_MODE', 'false').lower() == 'true'
    
    try:
        # Import resend here to avoid import errors if not installed
        import resend
        
        # Initialize Resend API
        resend.api_key = os.environ.get('RESEND_API_KEY')
        
        if not resend.api_key:
            logger.error("RESEND_API_KEY not found in environment variables")
            return
        
        # Get all users to notify
        recipients = []
        
        for user in api.user.get_users():
            email = user.getProperty('email')
            if email:
                recipients.append({
                    'email': email,
                    'fullname': user.getProperty('fullname', user.getId())
                })
        
        if not recipients:
            logger.info("No recipients found for camp alert notification")
            return
        
        # Get alert details
        alert_type = getattr(obj, 'alert_type', 'info')
        message = getattr(obj, 'message', '')
        
        # Get sender info
        sender = api.user.get_current()
        sender_name = sender.getProperty('fullname', sender.getId()) if sender else 'System'
        
        # Format alert type for display
        alert_type_map = {
            'emergency': {
                'title': 'EMERGENCY ALERT',
                'color': '#dc3545',
                'emoji': '🚨'
            },
            'event': {
                'title': 'Event Announcement',
                'color': '#28a745',
                'emoji': '📅'
            },
            'info': {
                'title': 'Information',
                'color': '#17a2b8',
                'emoji': 'ℹ️'
            }
        }
        
        alert_config = alert_type_map.get(alert_type, alert_type_map['info'])
        
        # Create email content
        email_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: {alert_config['color']}; color: white; padding: 20px; text-align: center;">
                <h1 style="margin: 0; font-size: 24px;">
                    {alert_config['emoji']} {alert_config['title']}
                </h1>
            </div>
            
            <div style="padding: 30px; background-color: #f8f9fa;">
                <h2 style="color: #333; margin-top: 0;">{obj.title}</h2>
                
                <div style="background-color: white; padding: 20px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0; line-height: 1.6; white-space: pre-wrap;">{message}</p>
                </div>
                
                <div style="color: #666; font-size: 14px; margin-top: 20px;">
                    <p>Sent by: {sender_name}</p>
                </div>
            </div>
            
            <div style="background-color: #e9ecef; padding: 20px; text-align: center; font-size: 12px; color: #666;">
                <p>This is an automated message from the Camp Coordinator system.</p>
                <p>You are receiving this because you are registered at the camp.</p>
            </div>
        </div>
        """
        
        # Prepare email data
        email_data = {
            "from": "Camp Coordinator <noreply@coolapps.jackwimbish.com>",
            "to": [r['email'] for r in recipients],
            "subject": f"{alert_config['emoji']} {obj.title}",
            "html": email_html
        }
        
        if test_mode:
            # Test mode - just log the email details
            logger.info("=== TEST MODE - Camp Alert Email would be sent ===")
            logger.info(f"Alert Type: {alert_type}")
            logger.info(f"From: {email_data['from']}")
            logger.info(f"To: {len(recipients)} recipients")
            logger.info(f"Subject: {email_data['subject']}")
            logger.info(f"Message: {message[:100]}{'...' if len(message) > 100 else ''}")
            logger.info(f"Recipients: {[r['fullname'] + ' <' + r['email'] + '>' for r in recipients[:3]]}... and {len(recipients)-3} more")
            logger.info("=== End of test email ===")
        else:
            # Production mode - send the email
            result = resend.Emails.send(email_data)
            logger.info(f"Camp alert email sent successfully. Resend ID: {result.get('id', 'unknown')}")
            logger.info(f"Alert type: {alert_type}, Sent to {len(recipients)} recipients")
    
    except ImportError:
        logger.error("resend package not installed. Run: pip install resend")
    except Exception as e:
        # Log error but don't block alert creation
        logger.error(f"Failed to send camp alert email: {str(e)}", exc_info=True)
        
        
def set_camp_alert_permissions():
    """Set up permissions for camp alerts - only Directors and Staff can add"""
    try:
        portal = api.portal.get()
        
        # Set permissions so only Manager and Editor roles can add camp alerts
        portal.manage_permission(
            'retreat: Add Camp Alert',
            roles=['Manager', 'Editor'],
            acquire=False
        )
        
        logger.info("Camp alert permissions configured successfully")
    except Exception as e:
        logger.error(f"Failed to set camp alert permissions: {e}")
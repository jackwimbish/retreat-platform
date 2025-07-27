"""Email notifications for new issues"""
import os
import logging
from plone import api
from . import activities

logger = logging.getLogger('retreat.notifications')


def notify_new_issue(obj, event):
    """Send email notification when a new issue is created"""
    
    # Only process issue content type
    if obj.portal_type != 'issue':
        return
    
    # Add initial activity log entry for issue creation
    try:
        if hasattr(obj, 'activity_log'):
            # Get the values, handling token objects
            status = getattr(obj, 'status', 'new')
            if hasattr(status, 'token'):
                status = status.token
            priority = getattr(obj, 'priority', 'normal')
            if hasattr(priority, 'token'):
                priority = priority.token
                
            activities.add_activity(obj, 'issue_created', {
                'title': obj.title,
                'description': getattr(obj, 'issue_description', ''),
                'location': getattr(obj, 'location', ''),
                'priority': priority,
                'status': status
            })
            
            # Store initial values for future comparison
            from zope.annotation.interfaces import IAnnotations
            annotations = IAnnotations(obj)
            
            # Get assigned_to value, handling token objects
            assigned_to = getattr(obj, 'assigned_to', None)
            if hasattr(assigned_to, 'token'):
                assigned_to = assigned_to.token
                
            annotations['retreat.stored_values'] = {
                'status': status,
                'priority': priority,
                'assigned_to': assigned_to
            }
            # Force the annotations to persist
            annotations._p_changed = True
    except Exception as e:
        logger.error(f"Failed to add creation activity: {e}")
    
    # Check if notifications are enabled
    if os.environ.get('ENABLE_ISSUE_NOTIFICATIONS', 'false').lower() != 'true':
        logger.info("Issue notifications are disabled")
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
        
        # Get users to notify (Staff and Directors)
        recipients = []
        
        for user in api.user.get_users():
            user_roles = api.user.get_roles(user=user)
            
            # Check if user is Staff (Editor) or Director (Manager)
            if 'Manager' in user_roles or 'Editor' in user_roles:
                email = user.getProperty('email')
                if email:
                    recipients.append({
                        'email': email,
                        'fullname': user.getProperty('fullname', user.getId())
                    })
        
        if not recipients:
            logger.info("No recipients found for issue notification")
            return
        
        # Get issue details
        creator = api.user.get(userid=obj.Creator())
        creator_name = creator.getProperty('fullname', obj.Creator()) if creator else obj.Creator()
        
        # Build issue URL
        portal_url = api.portal.get().absolute_url()
        issue_path = '/'.join(obj.getPhysicalPath()[2:])  # Skip /Plone prefix
        issue_url = f"{portal_url}/{issue_path}"
        
        # Format priority for display
        priority_map = {
            'low': 'Low',
            'medium': 'Medium',
            'high': 'High',
            'urgent': 'Urgent'
        }
        priority_display = priority_map.get(obj.priority, obj.priority)
        
        # Create email content
        email_html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">New Issue Reported</h2>
            
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">
                        <strong>Title:</strong>
                    </td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">
                        {obj.title}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">
                        <strong>Location:</strong>
                    </td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">
                        {obj.location}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">
                        <strong>Priority:</strong>
                    </td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">
                        {priority_display}
                    </td>
                </tr>
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">
                        <strong>Submitted by:</strong>
                    </td>
                    <td style="padding: 8px 0; border-bottom: 1px solid #eee;">
                        {creator_name}
                    </td>
                </tr>
            </table>
            
            <div style="margin-top: 20px;">
                <strong>Description:</strong>
                <p style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
                    {obj.issue_description or 'No description provided'}
                </p>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                <a href="{issue_url}" 
                   style="display: inline-block; padding: 10px 20px; background-color: #007bff; 
                          color: white; text-decoration: none; border-radius: 5px;">
                    View Issue
                </a>
            </div>
            
            <div style="margin-top: 30px; font-size: 12px; color: #666;">
                <p>You are receiving this email because you are a staff member or director.</p>
            </div>
        </div>
        """
        
        # Prepare email data
        email_data = {
            "from": "Camp Coordinator <noreply@coolapps.jackwimbish.com>",
            "to": [r['email'] for r in recipients],
            "subject": f"New Issue: {obj.title}",
            "html": email_html
        }
        
        if test_mode:
            # Test mode - just log the email details
            logger.info("=== TEST MODE - Email would be sent ===")
            logger.info(f"From: {email_data['from']}")
            logger.info(f"To: {email_data['to']}")
            logger.info(f"Subject: {email_data['subject']}")
            logger.info(f"Recipients: {[r['fullname'] + ' <' + r['email'] + '>' for r in recipients]}")
            logger.info("=== Email HTML Preview ===")
            logger.info(email_html)
            logger.info("=== End of test email ===")
        else:
            # Production mode - send the email
            result = resend.Emails.send(email_data)
            logger.info(f"Email sent successfully. Resend ID: {result.get('id', 'unknown')}")
            logger.info(f"Sent to {len(recipients)} recipients")
    
    except ImportError:
        logger.error("resend package not installed. Run: pip install resend")
    except Exception as e:
        # Log error but don't block issue creation
        logger.error(f"Failed to send issue notification email: {str(e)}", exc_info=True)
/**
 * Camp Alert View component.
 * Displays a single camp alert with appropriate styling
 */

import React from 'react';
import { 
  Container, 
  Segment, 
  Label, 
  Icon, 
  Header, 
  Message,
  Button
} from 'semantic-ui-react';
import { Link } from 'react-router-dom';
import { FormattedDate } from '@plone/volto/components';
import { flattenToAppURL } from '@plone/volto/helpers';
import './CampAlertView.css';

const CampAlertView = (props) => {
  const { content } = props;
  
  // Extract alert type
  const alertType = content.alert_type?.token || content.alert_type || 'info';
  
  // Alert type configuration
  const alertConfig = {
    emergency: { 
      color: 'red', 
      icon: 'warning sign', 
      label: 'EMERGENCY ALERT',
      messageColor: 'red'
    },
    event: { 
      color: 'green', 
      icon: 'calendar alternate', 
      label: 'Event Announcement',
      messageColor: 'green'
    },
    info: { 
      color: 'blue', 
      icon: 'info circle', 
      label: 'Information',
      messageColor: 'blue'
    }
  };

  const config = alertConfig[alertType] || alertConfig.info;
  const isActive = content.active !== false;

  return (
    <Container className="camp-alert-view">
      {/* Alert Header */}
      <Segment className={`alert-header ${alertType}`}>
        <div className="alert-header-content">
          <Icon name={config.icon} size="huge" />
          <div>
            <Header as="h1" inverted>
              {content.title}
            </Header>
            <Label size="large" inverted>
              {config.label}
            </Label>
          </div>
        </div>
      </Segment>

      {/* Alert Status */}
      {!isActive && (
        <Message warning>
          <Icon name="archive" />
          This alert has been archived and is no longer active.
        </Message>
      )}

      {/* Alert Content */}
      <Segment size="large" className="alert-content">
        <Message color={config.messageColor} size="large">
          <Message.Content>
            <div className="alert-message-text">
              {content.message}
            </div>
          </Message.Content>
        </Message>

        {/* Metadata */}
        <div className="alert-metadata">
          <div>
            <Icon name="user" />
            <strong>Sent by:</strong> {content.creators?.[0] || 'System'}
          </div>
          <div>
            <Icon name="clock" />
            <strong>Sent on:</strong> <FormattedDate date={content.created} includeTime />
          </div>
        </div>
      </Segment>

      {/* Action Buttons */}
      <Segment basic textAlign="center">
        <Button 
          primary 
          as={Link} 
          to={flattenToAppURL(content['@id']) + '/edit'}
        >
          <Icon name="edit" />
          Edit Alert
        </Button>
        <Button as={Link} to="/alerts">
          <Icon name="list" />
          View All Alerts
        </Button>
      </Segment>
    </Container>
  );
};

export default CampAlertView;
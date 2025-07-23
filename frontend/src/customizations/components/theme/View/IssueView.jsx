/**
 * Issue View component.
 * Custom view for Issue content type
 */

import React from 'react';
import { Container, Segment, Grid, Label, Header, Icon, Message } from 'semantic-ui-react';
import { DefaultView } from '@plone/volto/components';
import { FormattedDate } from '@plone/volto/components';
import '../../../../theme/IssueView.css';

const IssueView = (props) => {
  const { content } = props;
  
  // Status configuration
  const statusConfig = {
    new: { color: 'red', icon: 'exclamation circle' },
    in_progress: { color: 'yellow', icon: 'clock' },
    resolved: { color: 'green', icon: 'check circle' }
  };

  // Priority configuration  
  const priorityConfig = {
    low: { color: 'grey', icon: 'angle down' },
    normal: { color: 'blue', icon: 'minus' },
    high: { color: 'orange', icon: 'angle up' },
    critical: { color: 'red', icon: 'angle double up' }
  };

  // Extract the token from status and priority objects
  const statusValue = content.status?.token || content.status || 'new';
  const priorityValue = content.priority?.token || content.priority || 'normal';
  
  const currentStatus = statusConfig[statusValue] || statusConfig.new;
  const currentPriority = priorityConfig[priorityValue] || priorityConfig.normal;

  return (
    <Container className="issue-view">
      <Segment raised>
        <Grid>
          <Grid.Row>
            <Grid.Column width={12}>
              <Header as="h1">
                <Icon name="file alternate outline" />
                {content.title}
              </Header>
            </Grid.Column>
            <Grid.Column width={4} textAlign="right">
              <Label color={currentStatus.color} size="large">
                <Icon name={currentStatus.icon} />
                {content.status?.title?.toUpperCase() || statusValue.replace('_', ' ').toUpperCase()}
              </Label>
            </Grid.Column>
          </Grid.Row>
          
          <Grid.Row>
            <Grid.Column width={16}>
              <Label.Group>
                <Label>
                  <Icon name="map marker alternate" />
                  Location: {content.location || 'Not specified'}
                </Label>
                <Label color={currentPriority.color}>
                  <Icon name={currentPriority.icon} />
                  Priority: {content.priority?.title?.toUpperCase() || priorityValue.toUpperCase()}
                </Label>
                <Label>
                  <Icon name="calendar" />
                  Created: <FormattedDate date={content.created} includeTime />
                </Label>
              </Label.Group>
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Segment>

      <Segment>
        <Header as="h3">
          <Icon name="info circle" />
          Issue Description
        </Header>
        <p style={{ fontSize: '1.1em', lineHeight: '1.6' }}>
          {content.issue_description || 'No description provided.'}
        </p>
      </Segment>

      {content.resolution_notes && (
        <Message positive>
          <Message.Header>
            <Icon name="check" />
            Resolution Notes
          </Message.Header>
          <p>{content.resolution_notes}</p>
        </Message>
      )}

      {statusValue !== 'resolved' && (
        <Message info>
          <Message.Header>Issue Status</Message.Header>
          <p>This issue is currently {content.status?.title || statusValue.replace('_', ' ')} and requires attention.</p>
        </Message>
      )}

      {/* Include any blocks if they exist */}
      {content.blocks && <DefaultView {...props} />}
    </Container>
  );
};

export default IssueView;
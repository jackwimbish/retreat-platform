/**
 * Issue View component.
 * Displays a single issue with its details in a professional layout
 */

import React from 'react';
import { 
  Container, 
  Segment, 
  Label, 
  Icon, 
  Header, 
  Grid, 
  Button,
  Card,
  Divider,
  List,
  Message
} from 'semantic-ui-react';
import { FormattedDate } from '@plone/volto/components';
import { Link } from 'react-router-dom';
import { flattenToAppURL } from '@plone/volto/helpers';
import IssueActivities from '../../../../components/IssueActivities/IssueActivities';
import '../../../../theme/IssueView.css';

const IssueView = (props) => {
  const { content } = props;
  const [creatorName, setCreatorName] = React.useState('');
  
  // Extract status and priority values
  const statusValue = content.status?.token || content.status || 'new';
  const priorityValue = content.priority?.token || content.priority || 'normal';
  
  // Fetch creator's full name
  React.useEffect(() => {
    const fetchCreatorName = async () => {
      if (content.creators && content.creators.length > 0) {
        const creatorId = content.creators[0];
        try {
          // Use the public endpoint to get display name
          const contentPath = content['@id'].replace(/^.*\/\/[^\/]+/, '');
          const response = await fetch(`/++api++${contentPath}/@user-display-name?user_id=${creatorId}`, {
            headers: {
              'Accept': 'application/json',
            }
          });
          if (response.ok) {
            const data = await response.json();
            setCreatorName(data.display_name || creatorId);
          } else {
            setCreatorName(creatorId);
          }
        } catch (error) {
          console.error('Failed to fetch creator info:', error);
          setCreatorName(creatorId);
        }
      }
    };
    
    fetchCreatorName();
  }, [content.creators, content['@id']]);
  
  // Status configuration
  const statusConfig = {
    new: { color: 'red', icon: 'exclamation circle', label: 'New' },
    in_progress: { color: 'yellow', icon: 'clock', label: 'In Progress' },
    resolved: { color: 'green', icon: 'check circle', label: 'Resolved' }
  };

  const status = statusConfig[statusValue] || statusConfig.new;

  // Priority configuration
  const priorityConfig = {
    low: { color: 'grey', icon: 'angle down', label: 'Low' },
    normal: { color: 'blue', icon: 'minus', label: 'Normal' },
    high: { color: 'orange', icon: 'angle up', label: 'High' },
    critical: { color: 'red', icon: 'angle double up', label: 'Critical' }
  };

  const priority = priorityConfig[priorityValue] || priorityConfig.normal;

  // Get parent folder path
  const parentPath = content['@id'].substring(0, content['@id'].lastIndexOf('/'));

  return (
    <Container className="issue-view-professional">
      {/* Header Section */}
      <div className="issue-header">
        <div className="header-content">
          <Header as="h1" className="issue-title">
            <Icon name="clipboard outline" />
            {content.title}
          </Header>
          <Label color={status.color} size="large" className="status-badge">
            <Icon name={status.icon} />
            {content.status?.title || status.label}
          </Label>
        </div>
        
        {/* Action Buttons */}
        <div className="action-buttons">
          <Button primary as={Link} to={`${flattenToAppURL(content['@id'])}/edit`}>
            <Icon name="edit" />
            Edit Issue
          </Button>
        </div>
      </div>

      <Divider />

      <Grid stackable>
        <Grid.Row>
          {/* Main Content Column */}
          <Grid.Column width={11}>
            {/* Issue Details Card */}
            <Card fluid>
              <Card.Content>
                <Card.Header>
                  <Icon name="info circle" />
                  Issue Details
                </Card.Header>
                <Card.Description>
                  <Grid columns={2} divided>
                    <Grid.Row>
                      <Grid.Column>
                        <List>
                          <List.Item>
                            <List.Icon name="map marker alternate" />
                            <List.Content>
                              <List.Header>Location</List.Header>
                              <List.Description>
                                {content.location || 'Not specified'}
                              </List.Description>
                            </List.Content>
                          </List.Item>
                          <List.Item>
                            <List.Icon name="flag" />
                            <List.Content>
                              <List.Header>Priority</List.Header>
                              <List.Description>
                                <Label color={priority.color} size="small">
                                  <Icon name={priority.icon} />
                                  {content.priority?.title || priority.label}
                                </Label>
                              </List.Description>
                            </List.Content>
                          </List.Item>
                        </List>
                      </Grid.Column>
                      <Grid.Column>
                        <List>
                          <List.Item>
                            <List.Icon name="user outline" />
                            <List.Content>
                              <List.Header>Submitted By</List.Header>
                              <List.Description>
                                {creatorName || 'Unknown'}
                              </List.Description>
                            </List.Content>
                          </List.Item>
                          <List.Item>
                            <List.Icon name="calendar plus" />
                            <List.Content>
                              <List.Header>Created</List.Header>
                              <List.Description>
                                <FormattedDate date={content.created} includeTime />
                              </List.Description>
                            </List.Content>
                          </List.Item>
                          <List.Item>
                            <List.Icon name="calendar check" />
                            <List.Content>
                              <List.Header>Last Modified</List.Header>
                              <List.Description>
                                <FormattedDate date={content.modified} includeTime />
                              </List.Description>
                            </List.Content>
                          </List.Item>
                        </List>
                      </Grid.Column>
                    </Grid.Row>
                  </Grid>
                </Card.Description>
              </Card.Content>
            </Card>

            {/* Description Section */}
            <Segment>
              <Header as="h3">
                <Icon name="align left" />
                Description
              </Header>
              <div className="issue-description">
                {content.issue_description || content.description ? (
                  <p>{content.issue_description || content.description}</p>
                ) : (
                  <em className="no-description">No description provided.</em>
                )}
              </div>
            </Segment>

            {/* Resolution Notes (if resolved) */}
            {content.resolution_notes && (
              <Message positive>
                <Message.Header>
                  <Icon name="check" />
                  Resolution Notes
                </Message.Header>
                <p>{content.resolution_notes}</p>
              </Message>
            )}

            {/* Activity/Comments Section */}
            <IssueActivities content={content} />
          </Grid.Column>

          {/* Sidebar */}
          <Grid.Column width={5}>
            {/* Assignment Information */}
            {content.assigned_to && (
              <Segment>
                <Header as="h4">
                  <Icon name="user" />
                  Assigned To
                </Header>
                <p>{content.assigned_to.title || content.assigned_to.token || content.assigned_to}</p>
              </Segment>
            )}
            
            {/* Status Information */}
            {statusValue !== 'resolved' && (
              <Message info>
                <Message.Header>Current Status</Message.Header>
                <p>This issue is {status.label.toLowerCase()} and requires attention.</p>
              </Message>
            )}


          </Grid.Column>
        </Grid.Row>
      </Grid>
    </Container>
  );
};

export default IssueView;
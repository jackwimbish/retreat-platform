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
import '../../../../theme/IssueView.css';

const IssueView = (props) => {
  const { content } = props;
  
  // Extract status and priority values
  const statusValue = content.status?.token || content.status || 'new';
  const priorityValue = content.priority?.token || content.priority || 'normal';
  
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
          {statusValue !== 'resolved' && (
            <Button positive>
              <Icon name="check" />
              Mark as Resolved
            </Button>
          )}
          <Button basic>
            <Icon name="print" />
            Print
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

            {/* Activity/Comments Section (placeholder for future) */}
            <Segment>
              <Header as="h3">
                <Icon name="comments" />
                Activity & Comments
              </Header>
              <div className="activity-placeholder">
                <Icon name="comment outline" size="large" disabled />
                <p>Comments and activity tracking coming soon...</p>
              </div>
            </Segment>
          </Grid.Column>

          {/* Sidebar */}
          <Grid.Column width={5}>
            {/* Status Information */}
            {statusValue !== 'resolved' && (
              <Message info>
                <Message.Header>Current Status</Message.Header>
                <p>This issue is {status.label.toLowerCase()} and requires attention.</p>
              </Message>
            )}

            {/* Quick Actions Card */}
            <Card fluid>
              <Card.Content>
                <Card.Header>
                  <Icon name="lightning" />
                  Quick Actions
                </Card.Header>
                <Card.Description>
                  <Button.Group vertical fluid>
                    <Button basic>
                      <Icon name="user plus" />
                      Assign to Staff
                    </Button>
                    <Button basic>
                      <Icon name="copy" />
                      Duplicate Issue
                    </Button>
                    <Button basic>
                      <Icon name="archive" />
                      Archive Issue
                    </Button>
                    <Button basic color="red">
                      <Icon name="trash" />
                      Delete Issue
                    </Button>
                  </Button.Group>
                </Card.Description>
              </Card.Content>
            </Card>

            {/* Related Information */}
            <Card fluid>
              <Card.Content>
                <Card.Header>
                  <Icon name="linkify" />
                  Related Information
                </Card.Header>
                <Card.Description>
                  <List>
                    <List.Item>
                      <List.Icon name="folder" />
                      <List.Content>
                        <Link to={flattenToAppURL(parentPath)}>
                          Back to Issues List
                        </Link>
                      </List.Content>
                    </List.Item>
                    <List.Item>
                      <List.Icon name="filter" />
                      <List.Content>
                        <Link to={`${flattenToAppURL(parentPath)}?location=${encodeURIComponent(content.location || '')}`}>
                          Issues in {content.location || 'this location'}
                        </Link>
                      </List.Content>
                    </List.Item>
                  </List>
                </Card.Description>
              </Card.Content>
            </Card>

            {/* Metadata Card */}
            <Card fluid>
              <Card.Content>
                <Card.Header>
                  <Icon name="database" />
                  Metadata
                </Card.Header>
                <Card.Description>
                  <List size="small">
                    <List.Item>
                      <strong>ID:</strong> {content['@id'].split('/').pop()}
                    </List.Item>
                    <List.Item>
                      <strong>Type:</strong> {content['@type']}
                    </List.Item>
                    <List.Item>
                      <strong>State:</strong> {content.review_state}
                    </List.Item>
                  </List>
                </Card.Description>
              </Card.Content>
            </Card>
          </Grid.Column>
        </Grid.Row>
      </Grid>
    </Container>
  );
};

export default IssueView;
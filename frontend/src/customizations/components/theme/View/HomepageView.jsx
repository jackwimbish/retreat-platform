/**
 * Homepage View component.
 * Custom dashboard-style homepage for Camp Coordinator
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import {
  Container,
  Grid,
  Card,
  Icon,
  Header,
  Segment,
  Button,
  Statistic,
  List,
  Label,
  Divider
} from 'semantic-ui-react';
import { FormattedDate } from '@plone/volto/components';
import { flattenToAppURL } from '@plone/volto/helpers';
import '../../../../theme/HomepageView.css';

const HomepageView = (props) => {
  const { content } = props;
  const currentUser = useSelector((state) => state.users?.user);
  const token = useSelector((state) => state.userSession?.token);
  const [recentIssues, setRecentIssues] = useState([]);
  const [activeAlerts, setActiveAlerts] = useState([]);
  const [issueStats, setIssueStats] = useState({
    total: 0,
    new: 0,
    inProgress: 0,
    critical: 0,
    high: 0,
  });
  const [loading, setLoading] = useState(true);

  // Fetch issues data
  useEffect(() => {
    const fetchIssuesData = async () => {
      try {
        // Fetch recent issues
        const headers = {
          'Accept': 'application/json',
        };
        
        // Add auth token if available
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }
        
        const recentResponse = await fetch('/++api++/@search?portal_type=issue&metadata_fields=created&metadata_fields=modified&metadata_fields=status&metadata_fields=priority&metadata_fields=location&sort_on=created&sort_order=descending&b_size=5', {
          headers,
          credentials: 'same-origin',
        });
        
        if (recentResponse.ok) {
          const recentData = await recentResponse.json();
          setRecentIssues(recentData.items || []);
        }

        // Fetch all issues for statistics (lightweight, no full objects)
        const statsResponse = await fetch('/++api++/@search?portal_type=issue&metadata_fields=status&metadata_fields=priority&b_size=1000', {
          headers,
          credentials: 'same-origin',
        });
        
        if (statsResponse.ok) {
          const statsData = await statsResponse.json();
          const allIssues = statsData.items || [];
          
          // Calculate statistics
          const stats = {
            total: allIssues.length,
            new: allIssues.filter(i => (i.status?.token || i.status) === 'new').length,
            inProgress: allIssues.filter(i => (i.status?.token || i.status) === 'in_progress').length,
            critical: allIssues.filter(i => (i.priority?.token || i.priority) === 'critical').length,
            high: allIssues.filter(i => (i.priority?.token || i.priority) === 'high').length,
          };
          setIssueStats(stats);
        }
        
        // Fetch active alerts
        const alertsResponse = await fetch('/++api++/@search?portal_type=camp_alert&active=True&metadata_fields=alert_type&metadata_fields=message&metadata_fields=created&sort_on=created&sort_order=descending&b_size=5&fullobjects=true', {
          headers,
          credentials: 'same-origin',
        });
        
        if (alertsResponse.ok) {
          const alertsData = await alertsResponse.json();
          const alerts = alertsData.items || [];
          // Filter only active alerts
          const activeAlertsFiltered = alerts.filter(alert => alert.active !== false);
          setActiveAlerts(activeAlertsFiltered);
        }
      } catch (error) {
        console.error('Error fetching issues data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchIssuesData();
  }, []);

  const today = new Date();

  return (
    <Container className="homepage-dashboard">
      {/* Date Section */}
      <Segment basic className="welcome-section">
        <p className="date-display">
          <Icon name="calendar" />
          <FormattedDate date={today} format={{
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            weekday: 'long'
          }} />
        </p>
      </Segment>

      {/* Active Alerts */}
      {activeAlerts.length > 0 && (
        <div className="active-alerts-section">
          {activeAlerts.map((alert) => {
            const alertType = alert.alert_type?.token || alert.alert_type || 'info';
            const alertClass = alertType === 'emergency' ? 'emergency' : 
                              alertType === 'event' ? 'event' : 'info';
            
            return (
              <Segment 
                key={alert['@id']} 
                className={`active-alert ${alertClass}`}
                as={Link}
                to={flattenToAppURL(alert['@id'])}
              >
                <div className="alert-content">
                  <div className="alert-icon">
                    <Icon 
                      name={alertType === 'emergency' ? 'warning sign' : 
                            alertType === 'event' ? 'calendar alternate' : 'info circle'} 
                    />
                  </div>
                  <div className="alert-details">
                    <div className="alert-header">
                      <h3 className="alert-title">{alert.title}</h3>
                      <Label className={alertClass}>
                        {alertType}
                      </Label>
                    </div>
                    <div className="alert-message">{alert.message}</div>
                    <div className="alert-meta">
                      <Icon name="clock outline" />
                      <FormattedDate date={alert.created} includeTime />
                    </div>
                  </div>
                </div>
              </Segment>
            );
          })}
        </div>
      )}

      {/* Quick Stats */}
      <Grid stackable columns={4} className="stats-grid">
        <Grid.Column>
          <Card fluid className="stat-card">
            <Card.Content>
              <Statistic size="small">
                <Statistic.Value>
                  <Icon name="clipboard list" />
                  {issueStats.total}
                </Statistic.Value>
                <Statistic.Label>Total Issues</Statistic.Label>
              </Statistic>
            </Card.Content>
          </Card>
        </Grid.Column>
        <Grid.Column>
          <Card fluid className="stat-card new">
            <Card.Content>
              <Statistic size="small" color="red">
                <Statistic.Value>{issueStats.new}</Statistic.Value>
                <Statistic.Label>New Issues</Statistic.Label>
              </Statistic>
            </Card.Content>
          </Card>
        </Grid.Column>
        <Grid.Column>
          <Card fluid className="stat-card progress">
            <Card.Content>
              <Statistic size="small" color="yellow">
                <Statistic.Value>{issueStats.inProgress}</Statistic.Value>
                <Statistic.Label>In Progress</Statistic.Label>
              </Statistic>
            </Card.Content>
          </Card>
        </Grid.Column>
        <Grid.Column>
          <Card fluid className="stat-card alerts">
            <Card.Content>
              <Statistic size="small" color="orange">
                <Statistic.Value>{issueStats.critical + issueStats.high}</Statistic.Value>
                <Statistic.Label>High Priority</Statistic.Label>
              </Statistic>
            </Card.Content>
          </Card>
        </Grid.Column>
      </Grid>

      {/* Quick Links */}
      <Segment className="quick-links-section">
        <Header as="h2">
          <Icon name="lightning" />
          Quick Actions
        </Header>
        <Grid stackable columns={3}>
          <Grid.Column>
            <Card fluid as={Link} to="/issues" className="action-card">
              <Card.Content textAlign="center">
                <Icon name="clipboard list" size="huge" color="blue" />
                <Card.Header>Issues Dashboard</Card.Header>
                <Card.Description>
                  View and manage all maintenance issues
                </Card.Description>
              </Card.Content>
            </Card>
          </Grid.Column>
          <Grid.Column>
            <Card fluid as={Link} to="/directory" className="action-card">
              <Card.Content textAlign="center">
                <Icon name="users" size="huge" color="green" />
                <Card.Header>Camp Directory</Card.Header>
                <Card.Description>
                  View all participants, staff, and directors
                </Card.Description>
              </Card.Content>
            </Card>
          </Grid.Column>
          <Grid.Column>
            <Card fluid as={Link} to="/conference-rooms" className="action-card">
              <Card.Content textAlign="center">
                <Icon name="calendar alternate" size="huge" color="teal" />
                <Card.Header>Book a Room</Card.Header>
                <Card.Description>
                  Reserve conference rooms for meetings
                </Card.Description>
              </Card.Content>
            </Card>
          </Grid.Column>
        </Grid>
      </Segment>

      {/* Admin Tools Section - Visible to managers and editors (staff) */}
      {(currentUser?.roles?.includes('Manager') || currentUser?.roles?.includes('Editor') || currentUser?.id === 'admin') && (
        <Segment className="admin-tools-section">
          <Header as="h2">
            <Icon name="cog" />
            Admin Tools
          </Header>
          <Grid stackable columns={3}>
            <Grid.Column>
              <Card fluid as={Link} to="/manage-users" className="action-card">
                <Card.Content textAlign="center">
                  <Icon name="users" size="huge" color="purple" />
                  <Card.Header>Manage Users</Card.Header>
                  <Card.Description>
                    Assign camp roles to users
                  </Card.Description>
                </Card.Content>
              </Card>
            </Grid.Column>
            <Grid.Column>
              <Card fluid as={Link} to="/directory-generator" className="action-card">
                <Card.Content textAlign="center">
                  <Icon name="sync" size="huge" color="orange" />
                  <Card.Header>Update Directory</Card.Header>
                  <Card.Description>
                    Regenerate the camp directory
                  </Card.Description>
                </Card.Content>
              </Card>
            </Grid.Column>
            <Grid.Column>
              <Card fluid as={Link} to="/alerts" className="action-card">
                <Card.Content textAlign="center">
                  <Icon name="bell" size="huge" color="red" />
                  <Card.Header>Camp Alerts</Card.Header>
                  <Card.Description>
                    Send emergency alerts and announcements
                  </Card.Description>
                </Card.Content>
              </Card>
            </Grid.Column>
          </Grid>
        </Segment>
      )}

      <Grid stackable>
        <Grid.Row>
          {/* Recent Issues */}
          <Grid.Column width={10}>
            <Segment className="recent-issues">
              <Header as="h2">
                <Icon name="history" />
                Recent Issues
              </Header>
              {loading ? (
                <p>Loading recent issues...</p>
              ) : recentIssues.length > 0 ? (
                <List divided relaxed>
                  {recentIssues.map((issue) => {
                    const statusValue = issue.status?.token || issue.status || 'new';
                    const priorityValue = issue.priority?.token || issue.priority || 'normal';
                    const statusColor = {
                      new: 'red',
                      in_progress: 'yellow',
                      resolved: 'green'
                    }[statusValue] || 'grey';
                    const priorityColor = {
                      critical: 'red',
                      high: 'orange',
                      normal: 'blue',
                      low: 'grey'
                    }[priorityValue] || 'grey';

                    return (
                      <List.Item key={issue['@id']}>
                        <List.Content floated="right">
                          <Label color={statusColor} size="small">
                            {issue.status?.title || statusValue}
                          </Label>
                        </List.Content>
                        <List.Icon name="clipboard outline" size="large" verticalAlign="middle" />
                        <List.Content>
                          <List.Header as={Link} to={flattenToAppURL(issue['@id'])}>
                            {issue.title}
                          </List.Header>
                          <List.Description>
                            <Label color={priorityColor} size="tiny">
                              {issue.priority?.title || priorityValue}
                            </Label>
                            {issue.location && (
                              <>
                                <Icon name="map marker alternate" />
                                {issue.location}
                              </>
                            )}
                            {issue.created && (
                              <span className="issue-date">
                                <FormattedDate date={issue.created} />
                              </span>
                            )}
                          </List.Description>
                        </List.Content>
                      </List.Item>
                    );
                  })}
                </List>
              ) : (
                <p>No issues found.</p>
              )}
              <Divider />
              <Button as={Link} to="/issues" fluid basic primary>
                View All Issues
                <Icon name="arrow right" />
              </Button>
            </Segment>
          </Grid.Column>

          {/* Coming Soon Sidebar */}
          <Grid.Column width={6}>
            <Segment className="upcoming-features">
              <Header as="h3">
                <Icon name="rocket" />
                Coming Soon
              </Header>
              <List>
                <List.Item>
                  <List.Icon name="users" />
                  <List.Content>Guest Management</List.Content>
                </List.Item>
                <List.Item>
                  <List.Icon name="calendar alternate" />
                  <List.Content>Booking Calendar</List.Content>
                </List.Item>
                <List.Item>
                  <List.Icon name="chart bar" />
                  <List.Content>Analytics & Reports</List.Content>
                </List.Item>
                <List.Item>
                  <List.Icon name="bell" />
                  <List.Content>Email Notifications</List.Content>
                </List.Item>
              </List>
            </Segment>
          </Grid.Column>
        </Grid.Row>
      </Grid>
    </Container>
  );
};

export default HomepageView;
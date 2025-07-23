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
  const [recentIssues, setRecentIssues] = useState([]);
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
        const recentResponse = await fetch('/++api++/@search?portal_type=issue&metadata_fields=created&metadata_fields=modified&sort_on=created&sort_order=descending&b_size=5', {
          headers: {
            'Accept': 'application/json',
          },
          credentials: 'same-origin',
        });
        
        if (recentResponse.ok) {
          const recentData = await recentResponse.json();
          setRecentIssues(recentData.items || []);
        }

        // Fetch all issues for statistics (lightweight, no full objects)
        const statsResponse = await fetch('/++api++/@search?portal_type=issue&metadata_fields=status&metadata_fields=priority&b_size=1000', {
          headers: {
            'Accept': 'application/json',
          },
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
      } catch (error) {
        console.error('Error fetching issues data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchIssuesData();
  }, []);

  const today = new Date();
  const greeting = currentUser?.fullname || currentUser?.username || 'Camp Administrator';

  return (
    <Container className="homepage-dashboard">
      {/* Welcome Section */}
      <Segment basic className="welcome-section">
        <Header as="h1">
          <Icon name="sun" />
          Welcome back, {greeting}!
        </Header>
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
            <Card fluid as={Link} to="/++add++issue" className="action-card">
              <Card.Content textAlign="center">
                <Icon name="plus circle" size="huge" color="green" />
                <Card.Header>Create New Issue</Card.Header>
                <Card.Description>
                  Report a new maintenance issue
                </Card.Description>
              </Card.Content>
            </Card>
          </Grid.Column>
          <Grid.Column>
            <Card fluid className="action-card disabled">
              <Card.Content textAlign="center">
                <Icon name="bed" size="huge" color="grey" />
                <Card.Header>Room Management</Card.Header>
                <Card.Description>
                  Coming soon...
                </Card.Description>
              </Card.Content>
            </Card>
          </Grid.Column>
        </Grid>
      </Segment>

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

          {/* Quick Actions Sidebar */}
          <Grid.Column width={6}>
            <Segment className="quick-actions">
              <Header as="h3">
                <Icon name="tasks" />
                Quick Tasks
              </Header>
              <Button.Group vertical fluid>
                <Button basic as={Link} to="/issues?status=new">
                  <Icon name="exclamation circle" color="red" />
                  View New Issues ({issueStats.new})
                </Button>
                <Button basic as={Link} to="/issues?priority=critical">
                  <Icon name="warning sign" color="red" />
                  Critical Issues ({issueStats.critical})
                </Button>
                <Button basic as={Link} to="/issues?priority=high">
                  <Icon name="exclamation triangle" color="orange" />
                  High Priority ({issueStats.high})
                </Button>
              </Button.Group>
            </Segment>

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
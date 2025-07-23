/**
 * Issues Folder View component.
 * Custom folder view for displaying issues in a dashboard format
 */

import React, { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { 
  Container, 
  Segment, 
  Table, 
  Label, 
  Icon, 
  Header, 
  Dropdown,
  Grid,
  Statistic,
  Card,
  Button
} from 'semantic-ui-react';
import { FormattedDate } from '@plone/volto/components';
import { flattenToAppURL } from '@plone/volto/helpers';
import '../../../../theme/IssuesFolderView.css';

const IssuesFolderView = (props) => {
  const { content } = props;
  
  // Filter states
  const [statusFilter, setStatusFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [sortBy, setSortBy] = useState('created');
  
  // Configuration
  const statusConfig = {
    new: { color: 'red', icon: 'exclamation circle', label: 'New' },
    in_progress: { color: 'yellow', icon: 'clock', label: 'In Progress' },
    resolved: { color: 'green', icon: 'check circle', label: 'Resolved' }
  };

  const priorityConfig = {
    low: { color: 'grey', icon: 'angle down', label: 'Low' },
    normal: { color: 'blue', icon: 'minus', label: 'Normal' },
    high: { color: 'orange', icon: 'angle up', label: 'High' },
    critical: { color: 'red', icon: 'angle double up', label: 'Critical' }
  };

  // Filter options
  const statusOptions = [
    { key: 'all', text: 'All Statuses', value: 'all' },
    { key: 'new', text: 'New', value: 'new' },
    { key: 'in_progress', text: 'In Progress', value: 'in_progress' },
    { key: 'resolved', text: 'Resolved', value: 'resolved' }
  ];

  const priorityOptions = [
    { key: 'all', text: 'All Priorities', value: 'all' },
    { key: 'critical', text: 'Critical', value: 'critical' },
    { key: 'high', text: 'High', value: 'high' },
    { key: 'normal', text: 'Normal', value: 'normal' },
    { key: 'low', text: 'Low', value: 'low' }
  ];

  const sortOptions = [
    { key: 'created', text: 'Date Created', value: 'created' },
    { key: 'priority', text: 'Priority', value: 'priority' },
    { key: 'status', text: 'Status', value: 'status' }
  ];

  // Get only Issue items
  const issues = useMemo(() => {
    return (content.items || []).filter(item => item['@type'] === 'issue');
  }, [content.items]);

  // Apply filters and sorting
  const filteredAndSortedIssues = useMemo(() => {
    let filtered = issues;

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(issue => 
        (issue.status?.token || issue.status) === statusFilter
      );
    }

    // Priority filter
    if (priorityFilter !== 'all') {
      filtered = filtered.filter(issue => 
        (issue.priority?.token || issue.priority) === priorityFilter
      );
    }

    // Sorting
    const sorted = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'priority':
          const priorityOrder = { critical: 0, high: 1, normal: 2, low: 3 };
          const aPriority = priorityOrder[a.priority?.token || a.priority] || 2;
          const bPriority = priorityOrder[b.priority?.token || b.priority] || 2;
          return aPriority - bPriority;
        case 'status':
          const statusOrder = { new: 0, in_progress: 1, resolved: 2 };
          const aStatus = statusOrder[a.status?.token || a.status] || 0;
          const bStatus = statusOrder[b.status?.token || b.status] || 0;
          return aStatus - bStatus;
        case 'created':
        default:
          // Handle missing dates
          const aDate = a.created ? new Date(a.created) : new Date(0);
          const bDate = b.created ? new Date(b.created) : new Date(0);
          return bDate - aDate;
      }
    });

    return sorted;
  }, [issues, statusFilter, priorityFilter, sortBy]);

  // Calculate statistics
  const stats = useMemo(() => {
    const counts = {
      total: issues.length,
      new: 0,
      in_progress: 0,
      resolved: 0,
      critical: 0,
      high: 0
    };

    issues.forEach(issue => {
      const status = issue.status?.token || issue.status;
      const priority = issue.priority?.token || issue.priority;
      
      if (status === 'new') counts.new++;
      if (status === 'in_progress') counts.in_progress++;
      if (status === 'resolved') counts.resolved++;
      if (priority === 'critical') counts.critical++;
      if (priority === 'high') counts.high++;
    });

    return counts;
  }, [issues]);

  // Render issue row for table
  const renderIssueRow = (issue) => {
    const statusValue = issue.status?.token || issue.status || 'new';
    const priorityValue = issue.priority?.token || issue.priority || 'normal';
    const status = statusConfig[statusValue] || statusConfig.new;
    const priority = priorityConfig[priorityValue] || priorityConfig.normal;
    
    return (
      <Table.Row key={issue['@id']}>
        <Table.Cell>
          <Link to={flattenToAppURL(issue['@id'])}>
            <strong>{issue.title}</strong>
          </Link>
        </Table.Cell>
        <Table.Cell>
          <Label color={status.color} size="small">
            <Icon name={status.icon} />
            {issue.status?.title || status.label}
          </Label>
        </Table.Cell>
        <Table.Cell>
          <Label color={priority.color} size="small">
            <Icon name={priority.icon} />
            {issue.priority?.title || priority.label}
          </Label>
        </Table.Cell>
        <Table.Cell>{issue.location || 'Not specified'}</Table.Cell>
        <Table.Cell>
          {issue.created ? (
            <FormattedDate date={issue.created} />
          ) : (
            <span>-</span>
          )}
        </Table.Cell>
      </Table.Row>
    );
  };

  // Render issue card for mobile
  const renderIssueCard = (issue) => {
    const statusValue = issue.status?.token || issue.status || 'new';
    const priorityValue = issue.priority?.token || issue.priority || 'normal';
    const status = statusConfig[statusValue] || statusConfig.new;
    const priority = priorityConfig[priorityValue] || priorityConfig.normal;
    
    return (
      <Card key={issue['@id']} as={Link} to={flattenToAppURL(issue['@id'])}>
        <Card.Content>
          <Card.Header>{issue.title}</Card.Header>
          <Card.Meta>
            <Icon name="map marker alternate" />
            {issue.location || 'Not specified'}
          </Card.Meta>
          <Card.Description>
            {issue.description}
          </Card.Description>
        </Card.Content>
        <Card.Content extra>
          <Label color={status.color} size="small">
            <Icon name={status.icon} />
            {issue.status?.title || status.label}
          </Label>
          <Label color={priority.color} size="small">
            <Icon name={priority.icon} />
            {issue.priority?.title || priority.label}
          </Label>
          {issue.created && (
            <span style={{ float: 'right', fontSize: '0.9em', color: '#999' }}>
              <FormattedDate date={issue.created} />
            </span>
          )}
        </Card.Content>
      </Card>
    );
  };

  return (
    <Container className="issues-folder-view">
      <Segment>
        <Header as="h1">
          <Icon name="clipboard list" />
          {content.title}
        </Header>
        
        {/* Statistics */}
        <Segment>
          <Grid>
            <Grid.Row>
              <Grid.Column mobile={8} tablet={3} computer={3}>
                <Statistic size="small">
                  <Statistic.Value>{stats.total}</Statistic.Value>
                  <Statistic.Label>Total Issues</Statistic.Label>
                </Statistic>
              </Grid.Column>
              <Grid.Column mobile={8} tablet={3} computer={3}>
                <Statistic size="small" color="red">
                  <Statistic.Value>{stats.new}</Statistic.Value>
                  <Statistic.Label>New</Statistic.Label>
                </Statistic>
              </Grid.Column>
              <Grid.Column mobile={8} tablet={3} computer={3}>
                <Statistic size="small" color="yellow">
                  <Statistic.Value>{stats.in_progress}</Statistic.Value>
                  <Statistic.Label>In Progress</Statistic.Label>
                </Statistic>
              </Grid.Column>
              <Grid.Column mobile={8} tablet={3} computer={3}>
                <Statistic size="small" color="green">
                  <Statistic.Value>{stats.resolved}</Statistic.Value>
                  <Statistic.Label>Resolved</Statistic.Label>
                </Statistic>
              </Grid.Column>
            </Grid.Row>
            {(stats.critical > 0 || stats.high > 0) && (
              <Grid.Row>
                <Grid.Column width={16}>
                  {stats.critical > 0 && (
                    <Label color="red" size="large">
                      <Icon name="warning sign" />
                      {stats.critical} Critical Issue{stats.critical !== 1 ? 's' : ''}
                    </Label>
                  )}
                  {stats.high > 0 && (
                    <Label color="orange" size="large">
                      <Icon name="exclamation triangle" />
                      {stats.high} High Priority Issue{stats.high !== 1 ? 's' : ''}
                    </Label>
                  )}
                </Grid.Column>
              </Grid.Row>
            )}
          </Grid>
        </Segment>

        {/* Filters */}
        <Segment>
          <Grid>
            <Grid.Row>
              <Grid.Column mobile={16} tablet={5} computer={5}>
                <Dropdown
                  placeholder="Filter by Status"
                  fluid
                  selection
                  options={statusOptions}
                  value={statusFilter}
                  onChange={(e, { value }) => setStatusFilter(value)}
                />
              </Grid.Column>
              <Grid.Column mobile={16} tablet={5} computer={5}>
                <Dropdown
                  placeholder="Filter by Priority"
                  fluid
                  selection
                  options={priorityOptions}
                  value={priorityFilter}
                  onChange={(e, { value }) => setPriorityFilter(value)}
                />
              </Grid.Column>
              <Grid.Column mobile={16} tablet={6} computer={6}>
                <Dropdown
                  placeholder="Sort by"
                  fluid
                  selection
                  options={sortOptions}
                  value={sortBy}
                  onChange={(e, { value }) => setSortBy(value)}
                  icon="sort"
                />
              </Grid.Column>
            </Grid.Row>
          </Grid>
        </Segment>

        {/* Issues List */}
        {filteredAndSortedIssues.length === 0 ? (
          <Segment placeholder>
            <Header icon>
              <Icon name="search" />
              No issues found matching your filters.
            </Header>
          </Segment>
        ) : (
          <>
            {/* Desktop Table View */}
            <div className="desktop-only">
              <Table celled selectable>
                <Table.Header>
                  <Table.Row>
                    <Table.HeaderCell>Issue</Table.HeaderCell>
                    <Table.HeaderCell width={2}>Status</Table.HeaderCell>
                    <Table.HeaderCell width={2}>Priority</Table.HeaderCell>
                    <Table.HeaderCell width={3}>Location</Table.HeaderCell>
                    <Table.HeaderCell width={2}>Created</Table.HeaderCell>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {filteredAndSortedIssues.map(renderIssueRow)}
                </Table.Body>
              </Table>
            </div>

            {/* Mobile Card View */}
            <div className="mobile-only">
              <Card.Group itemsPerRow={1}>
                {filteredAndSortedIssues.map(renderIssueCard)}
              </Card.Group>
            </div>
          </>
        )}
      </Segment>
    </Container>
  );
};

export default IssuesFolderView;
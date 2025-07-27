/**
 * Alerts Folder View component.
 * Custom folder view for displaying camp alerts
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { 
  Container, 
  Segment, 
  Table, 
  Label, 
  Icon, 
  Header, 
  Button,
  Dropdown,
  Grid,
  Card,
  Message,
  Loader,
  Checkbox
} from 'semantic-ui-react';
import { FormattedDate } from '@plone/volto/components';
import { flattenToAppURL } from '@plone/volto/helpers';
import { userHasRoles } from '@plone/volto/helpers';
import './AlertsFolderView.css';

const AlertsFolderView = (props) => {
  const { content } = props;
  const token = useSelector((state) => state.userSession?.token);
  const user = useSelector((state) => state.users?.user);
  
  // State
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showArchived, setShowArchived] = useState(false);
  const [filterType, setFilterType] = useState('all');
  
  // Check if user can create alerts
  const canCreateAlerts = userHasRoles(user, ['Manager', 'Editor']);
  
  // Alert type configuration
  const alertConfig = {
    emergency: { 
      color: 'red', 
      icon: 'warning sign', 
      label: 'Emergency'
    },
    event: { 
      color: 'green', 
      icon: 'calendar alternate', 
      label: 'Event'
    },
    info: { 
      color: 'blue', 
      icon: 'info circle', 
      label: 'Information'
    }
  };

  // Filter options
  const typeOptions = [
    { key: 'all', text: 'All Types', value: 'all' },
    { key: 'emergency', text: 'Emergency', value: 'emergency' },
    { key: 'event', text: 'Event', value: 'event' },
    { key: 'info', text: 'Information', value: 'info' }
  ];

  // Fetch alerts
  useEffect(() => {
    const fetchAlerts = async () => {
      setLoading(true);
      try {
        const headers = {
          'Accept': 'application/json',
        };
        
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }
        
        // Search for all camp alerts
        const searchResponse = await fetch(
          '/++api++/@search?portal_type=camp_alert&metadata_fields=created&metadata_fields=modified&metadata_fields=alert_type&metadata_fields=active&metadata_fields=message&metadata_fields=Creator&b_size=1000&sort_on=created&sort_order=descending&fullobjects=true',
          {
            headers,
            credentials: 'same-origin',
          }
        );
        
        if (searchResponse.ok) {
          const searchData = await searchResponse.json();
          setAlerts(searchData.items || []);
        }
      } catch (error) {
        console.error('Error fetching alerts:', error);
        setAlerts([]);
      } finally {
        setLoading(false);
      }
    };

    fetchAlerts();
  }, [token]);

  // Filter alerts
  const filteredAlerts = alerts.filter(alert => {
    // Filter by active/archived
    const isActive = alert.active !== false;
    if (!showArchived && !isActive) return false;
    
    // Filter by type
    if (filterType !== 'all') {
      const alertType = alert.alert_type?.token || alert.alert_type || 'info';
      if (alertType !== filterType) return false;
    }
    
    return true;
  });

  // Archive alert
  const archiveAlert = async (alertPath) => {
    try {
      // Convert the full URL to just the path part
      const pathOnly = alertPath.replace(/^https?:\/\/[^\/]+/, '');
      const response = await fetch(`/++api++${pathOnly}`, {
        method: 'PATCH',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ active: false })
      });
      
      if (response.ok) {
        // Update local state
        setAlerts(alerts.map(alert => 
          alert['@id'] === alertPath 
            ? { ...alert, active: false }
            : alert
        ));
      }
    } catch (error) {
      console.error('Failed to archive alert:', error);
    }
  };

  // Render alert row
  const renderAlertRow = (alert) => {
    const alertType = alert.alert_type?.token || alert.alert_type || 'info';
    const config = alertConfig[alertType] || alertConfig.info;
    const isActive = alert.active !== false;
    
    return (
      <Table.Row key={alert['@id']} className={!isActive ? 'archived' : ''}>
        <Table.Cell>
          <Link to={flattenToAppURL(alert['@id'])}>
            <strong>{alert.title}</strong>
          </Link>
          {alertType === 'emergency' && (
            <Label color="red" size="tiny" style={{ marginLeft: '0.5rem' }}>
              EMERGENCY
            </Label>
          )}
        </Table.Cell>
        <Table.Cell>
          <Label color={config.color} size="small">
            <Icon name={config.icon} />
            {config.label}
          </Label>
        </Table.Cell>
        <Table.Cell>
          {isActive ? (
            <Label color="green" size="small">
              <Icon name="check circle" />
              Active
            </Label>
          ) : (
            <Label size="small">
              <Icon name="archive" />
              Archived
            </Label>
          )}
        </Table.Cell>
        <Table.Cell>
          <FormattedDate date={alert.created} />
        </Table.Cell>
        <Table.Cell>
          <Button.Group size="small">
            <Button as={Link} to={flattenToAppURL(alert['@id'])}>
              <Icon name="eye" />
              View
            </Button>
            {isActive && canCreateAlerts && (
              <Button onClick={() => archiveAlert(alert['@id'])}>
                <Icon name="archive" />
                Archive
              </Button>
            )}
          </Button.Group>
        </Table.Cell>
      </Table.Row>
    );
  };

  return (
    <Container className="alerts-folder-view">
      <Segment>
        <Grid>
          <Grid.Row>
            <Grid.Column width={12}>
              <Header as="h1">
                <Icon name="bell" />
                Camp Alerts Management
              </Header>
            </Grid.Column>
            <Grid.Column width={4} textAlign="right">
              {canCreateAlerts && (
                <Button 
                  primary 
                  as={Link} 
                  to="/alerts/add?type=camp_alert"
                  size="large"
                >
                  <Icon name="plus" />
                  Send New Alert
                </Button>
              )}
            </Grid.Column>
          </Grid.Row>
        </Grid>

        {loading ? (
          <Segment basic textAlign="center">
            <Loader active inline="centered">Loading alerts...</Loader>
          </Segment>
        ) : (
          <>
            {/* Filters */}
            <Segment>
              <Grid>
                <Grid.Row>
                  <Grid.Column width={6}>
                    <Dropdown
                      placeholder="Filter by Type"
                      fluid
                      selection
                      options={typeOptions}
                      value={filterType}
                      onChange={(e, { value }) => setFilterType(value)}
                    />
                  </Grid.Column>
                  <Grid.Column width={6}>
                    <Checkbox
                      label="Show archived alerts"
                      checked={showArchived}
                      onChange={(e, { checked }) => setShowArchived(checked)}
                      style={{ marginTop: '0.5rem' }}
                    />
                  </Grid.Column>
                </Grid.Row>
              </Grid>
            </Segment>

            {/* Alerts List */}
            {filteredAlerts.length === 0 ? (
              <Message info>
                <Icon name="info circle" />
                No alerts found matching your filters.
              </Message>
            ) : (
              <Table celled selectable>
                <Table.Header>
                  <Table.Row>
                    <Table.HeaderCell>Alert Title</Table.HeaderCell>
                    <Table.HeaderCell width={2}>Type</Table.HeaderCell>
                    <Table.HeaderCell width={2}>Status</Table.HeaderCell>
                    <Table.HeaderCell width={2}>Created</Table.HeaderCell>
                    <Table.HeaderCell width={3}>Actions</Table.HeaderCell>
                  </Table.Row>
                </Table.Header>
                <Table.Body>
                  {filteredAlerts.map(renderAlertRow)}
                </Table.Body>
              </Table>
            )}
          </>
        )}
      </Segment>
    </Container>
  );
};

export default AlertsFolderView;
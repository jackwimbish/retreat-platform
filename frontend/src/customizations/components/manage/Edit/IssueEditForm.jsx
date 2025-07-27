/**
 * Custom Edit Form for Issue content type.
 */

import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Container, Segment, Form, Button, Header, Grid, Label, Icon, Confirm } from 'semantic-ui-react';
import { TextWidget, SelectWidget, TextareaWidget } from '@plone/volto/components';
import { FormattedDate } from '@plone/volto/components';
import { withRouter } from 'react-router-dom';
import { compose } from 'redux';
import { connect } from 'react-redux';
import { getUser } from '@plone/volto/actions';
import { getBaseUrl, userHasRoles } from '@plone/volto/helpers';
import jwtDecode from 'jwt-decode';
import './IssueEditForm.css';

class IssueEditForm extends Component {
  static propTypes = {
    schema: PropTypes.object.isRequired,
    formData: PropTypes.object.isRequired,
    onSubmit: PropTypes.func.isRequired,
    onCancel: PropTypes.func.isRequired,
    pathname: PropTypes.string.isRequired,
    loading: PropTypes.bool,
    intl: PropTypes.object.isRequired,
    getUser: PropTypes.func.isRequired,
    history: PropTypes.object.isRequired,
    user: PropTypes.object,
    token: PropTypes.string,
  };

  constructor(props) {
    super(props);
    this.state = {
      formData: { ...(props.formData || {}) },
      errors: {},
      showDeleteConfirm: false,
      deleteLoading: false,
    };
  }

  componentDidMount() {
    // Fetch user data if we have a token
    if (this.props.token) {
      const userId = jwtDecode(this.props.token).sub;
      this.props.getUser(userId);
    }
  }

  handleFieldChange = (id, value) => {
    this.setState(prevState => ({
      formData: {
        ...prevState.formData,
        [id]: value,
      },
      errors: {
        ...prevState.errors,
        [id]: null,
      }
    }));
  };

  handleQuickAction = (action) => {
    let updates = {};
    
    switch (action) {
      case 'resolve':
        updates = {
          status: { token: 'resolved', title: 'Resolved' },
        };
        // Focus on resolution notes after a short delay
        setTimeout(() => {
          const resolutionField = document.getElementById('field-resolution_notes');
          if (resolutionField) {
            resolutionField.scrollIntoView({ behavior: 'smooth', block: 'center' });
            const textarea = resolutionField.querySelector('textarea');
            if (textarea) textarea.focus();
          }
        }, 100);
        break;
      
      case 'in_progress':
        updates = {
          status: { token: 'in_progress', title: 'In Progress' },
        };
        break;
      
      case 'critical':
        updates = {
          priority: { token: 'critical', title: 'Critical' },
        };
        break;
      
      default:
        break;
    }

    this.setState(prevState => ({
      formData: {
        ...prevState.formData,
        ...updates,
      }
    }));
  };

  validateForm = () => {
    const errors = {};
    const { formData } = this.state;

    if (!formData.title || !formData.title.trim()) {
      errors.title = 'Title is required';
    }

    this.setState({ errors });
    return Object.keys(errors).length === 0;
  };

  onSubmit = () => {
    if (this.validateForm()) {
      this.props.onSubmit(this.state.formData);
    }
  };

  handleDeleteClick = () => {
    this.setState({ showDeleteConfirm: true });
  };

  handleDeleteCancel = () => {
    this.setState({ showDeleteConfirm: false });
  };

  handleDeleteConfirm = async () => {
    this.setState({ deleteLoading: true });
    
    // Get the URL for deletion
    const deleteUrl = getBaseUrl(this.props.pathname);
    const headers = {
      'Accept': 'application/json',
      'Authorization': `Bearer ${this.props.token}`,
    };
    
    try {
      // First, try to unlock the content (it's locked because we're in edit mode)
      // We don't await or check the response - if it fails, that's OK
      fetch(`/++api++${deleteUrl}/@lock`, {
        method: 'DELETE',
        headers,
      }).catch(() => {
        // Ignore unlock errors - the content might not be locked
      });
      
      // Now try to delete
      const deleteResponse = await fetch(`/++api++${deleteUrl}`, {
        method: 'DELETE',
        headers,
      });
      
      if (deleteResponse.ok || deleteResponse.status === 204) {
        // Successfully deleted, redirect to issues folder
        this.props.history.push('/issues');
      } else if (deleteResponse.status === 423) {
        // Still locked, user should cancel edit first
        alert('Please cancel editing before deleting the issue.');
        this.setState({ deleteLoading: false, showDeleteConfirm: false });
      } else {
        throw new Error(`Delete failed with status: ${deleteResponse.status}`);
      }
    } catch (error) {
      console.error('Error deleting issue:', error);
      this.setState({ deleteLoading: false, showDeleteConfirm: false });
      alert('Error deleting issue. Please try again.');
    }
  };

  getStatusColor = (status) => {
    const colors = {
      new: 'blue',
      in_progress: 'yellow',
      resolved: 'green',
    };
    return colors[status] || 'grey';
  };

  getPriorityColor = (priority) => {
    const colors = {
      low: 'green',
      normal: 'blue',
      high: 'orange',
      critical: 'red',
    };
    return colors[priority] || 'grey';
  };

  render() {
    const { schema, loading, intl } = this.props;
    const { formData, errors } = this.state;

    const statusChoices = schema.properties.status?.choices || [];
    const priorityChoices = schema.properties.priority?.choices || [];
    const currentStatus = formData.status?.token || formData.status || 'new';
    const currentPriority = formData.priority?.token || formData.priority || 'normal';

    return (
      <Container className="issue-edit-form">
        <Segment basic>
          <Header as="h1">
            <Icon name="edit" />
            Edit Issue: {formData.title}
          </Header>

          {/* Quick Actions Bar */}
          <Segment className="quick-actions-bar">
            <Button.Group>
              <Button
                color="green"
                onClick={() => this.handleQuickAction('resolve')}
                disabled={currentStatus === 'resolved'}
                icon
                labelPosition="left"
              >
                <Icon name="check circle" />
                Mark as Resolved
              </Button>
              <Button
                color="yellow"
                onClick={() => this.handleQuickAction('in_progress')}
                disabled={currentStatus === 'in_progress'}
                icon
                labelPosition="left"
              >
                <Icon name="play" />
                Start Progress
              </Button>
              <Button
                color="red"
                onClick={() => this.handleQuickAction('critical')}
                disabled={currentPriority === 'critical'}
                icon
                labelPosition="left"
              >
                <Icon name="exclamation triangle" />
                Mark as Critical
              </Button>
            </Button.Group>
          </Segment>

          <Form loading={loading}>
            {/* Issue Details Section */}
            <Segment className="form-section">
              <Header as="h3">
                <Icon name="info circle" />
                Issue Details
              </Header>
              
              <Form.Field required error={!!errors.title}>
                <label>Title</label>
                <TextWidget
                  id="title"
                  title="Title"
                  value={formData.title || ''}
                  onChange={this.handleFieldChange}
                />
                {errors.title && <div className="ui pointing red basic label">{errors.title}</div>}
              </Form.Field>

              <Form.Group widths="equal">
                <Form.Field>
                  <label>
                    Status
                    <Label 
                      size="tiny" 
                      color={this.getStatusColor(currentStatus)}
                      className="status-indicator"
                    >
                      {formData.status?.title || currentStatus}
                    </Label>
                  </label>
                  <SelectWidget
                    id="status"
                    title="Status"
                    value={formData.status || { token: 'new', title: 'New' }}
                    choices={statusChoices}
                    onChange={this.handleFieldChange}
                  />
                </Form.Field>

                <Form.Field>
                  <label>
                    Priority
                    <Label 
                      size="tiny" 
                      color={this.getPriorityColor(currentPriority)}
                      className="priority-indicator"
                    >
                      {formData.priority?.title || currentPriority}
                    </Label>
                  </label>
                  <SelectWidget
                    id="priority"
                    title="Priority"
                    value={formData.priority || { token: 'normal', title: 'Normal' }}
                    choices={priorityChoices}
                    onChange={this.handleFieldChange}
                  />
                </Form.Field>
              </Form.Group>

              <Form.Field>
                <label>Location</label>
                <TextWidget
                  id="location"
                  title="Location"
                  value={formData.location || ''}
                  onChange={this.handleFieldChange}
                />
              </Form.Field>
            </Segment>

            {/* Description Section */}
            <Segment className="form-section">
              <Header as="h3">
                <Icon name="file text outline" />
                Description
              </Header>
              
              <Form.Field>
                <TextareaWidget
                  id="issue_description"
                  title="Issue Description"
                  value={formData.issue_description || ''}
                  onChange={this.handleFieldChange}
                  rows={6}
                />
              </Form.Field>
            </Segment>

            {/* Resolution Section */}
            <Segment className="form-section" id="field-resolution_notes">
              <Header as="h3">
                <Icon name="clipboard check" />
                Resolution
              </Header>
              
              <Form.Field>
                <TextareaWidget
                  id="resolution_notes"
                  title="Resolution Notes"
                  value={formData.resolution_notes || ''}
                  onChange={this.handleFieldChange}
                  rows={4}
                  placeholder="Describe how this issue was resolved..."
                />
              </Form.Field>
            </Segment>

            {/* Information Section (Read-only) */}
            <Segment className="form-section info-section">
              <Header as="h3">
                <Icon name="info" />
                Information
              </Header>
              
              <Grid columns={2} stackable>
                <Grid.Column>
                  <div className="info-field">
                    <strong>Created:</strong>{' '}
                    {formData.created && <FormattedDate date={formData.created} />}
                  </div>
                </Grid.Column>
                <Grid.Column>
                  <div className="info-field">
                    <strong>Last Modified:</strong>{' '}
                    {formData.modified && <FormattedDate date={formData.modified} />}
                  </div>
                </Grid.Column>
                <Grid.Column>
                  <div className="info-field">
                    <strong>Issue ID:</strong> {formData.id || 'N/A'}
                  </div>
                </Grid.Column>
                <Grid.Column>
                  <div className="info-field">
                    <strong>Creator:</strong> {formData.creators?.join(', ') || 'Unknown'}
                  </div>
                </Grid.Column>
              </Grid>
            </Segment>

            {/* Form Actions */}
            <Segment basic textAlign="center" className="form-actions">
              <Button
                primary
                size="large"
                onClick={this.onSubmit}
                loading={loading}
                disabled={loading}
              >
                <Icon name="save" />
                Save Changes
              </Button>
              <Button
                size="large"
                onClick={this.props.onCancel}
                disabled={loading}
              >
                <Icon name="cancel" />
                Cancel
              </Button>
              
              {/* Delete button - only show for users with Manager role */}
              {userHasRoles(this.props.user, ['Manager', 'Site Administrator']) && (
                <Button
                  color="red"
                  size="large"
                  onClick={this.handleDeleteClick}
                  disabled={loading || this.state.deleteLoading}
                  floated="right"
                >
                  <Icon name="trash" />
                  Delete Issue
                </Button>
              )}
            </Segment>
          </Form>
        </Segment>
        
        {/* Delete Confirmation Dialog */}
        <Confirm
          open={this.state.showDeleteConfirm}
          onCancel={this.handleDeleteCancel}
          onConfirm={this.handleDeleteConfirm}
          header="Delete Issue"
          content={`Are you sure you want to delete "${formData.title}"? This action cannot be undone.`}
          confirmButton="Delete"
          size="small"
        />
      </Container>
    );
  }
}

export default compose(
  withRouter,
  connect(
    (state) => ({
      user: state.users.user,
      token: state.userSession.token,
    }),
    { getUser }
  )
)(IssueEditForm);
/**
 * Custom Edit Form for Camp Alert content type.
 */

import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Container, Segment, Form, Button, Header, Icon, Message } from 'semantic-ui-react';
import { TextWidget, SelectWidget, TextareaWidget } from '@plone/volto/components';
import { withRouter } from 'react-router-dom';
import { compose } from 'redux';
import { connect } from 'react-redux';
import { getBaseUrl } from '@plone/volto/helpers';
import './CampAlertEditForm.css';

class CampAlertEditForm extends Component {
  static propTypes = {
    schema: PropTypes.object.isRequired,
    formData: PropTypes.object.isRequired,
    onSubmit: PropTypes.func.isRequired,
    onCancel: PropTypes.func.isRequired,
    pathname: PropTypes.string.isRequired,
    loading: PropTypes.bool,
    intl: PropTypes.object.isRequired,
    history: PropTypes.object.isRequired,
    token: PropTypes.string,
  };

  constructor(props) {
    super(props);
    this.state = {
      formData: { ...(props.formData || {}) },
      errors: {},
    };
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

  validateForm = () => {
    const errors = {};
    const { formData } = this.state;

    if (!formData.title || !formData.title.trim()) {
      errors.title = 'Title is required';
    }

    if (!formData.message || !formData.message.trim()) {
      errors.message = 'Message is required';
    }

    this.setState({ errors });
    return Object.keys(errors).length === 0;
  };

  onSubmit = () => {
    if (this.validateForm()) {
      this.props.onSubmit(this.state.formData);
    }
  };

  render() {
    const { schema, loading, intl } = this.props;
    const { formData, errors } = this.state;

    const alertTypeChoices = schema.properties.alert_type?.choices || [
      { token: 'emergency', title: 'Emergency' },
      { token: 'event', title: 'Event' },
      { token: 'info', title: 'Information' }
    ];
    
    const currentAlertType = formData.alert_type?.token || formData.alert_type || 'info';
    
    // Alert type styling
    const alertStyles = {
      emergency: { color: 'red', icon: 'warning sign' },
      event: { color: 'green', icon: 'calendar alternate' },
      info: { color: 'blue', icon: 'info circle' }
    };
    
    const style = alertStyles[currentAlertType] || alertStyles.info;

    return (
      <Container className="camp-alert-edit-form">
        <Segment basic>
          <Header as="h1">
            <Icon name="edit" />
            Edit Camp Alert
          </Header>

          {/* Alert Type Indicator */}
          <Message color={style.color}>
            <Icon name={style.icon} />
            This is {currentAlertType === 'emergency' ? 'an' : 'a'} <strong>{currentAlertType.toUpperCase()}</strong> alert
          </Message>

          <Form loading={loading}>
            {/* Alert Details Section */}
            <Segment className="form-section">
              <Header as="h3">
                <Icon name="bell" />
                Alert Details
              </Header>
              
              <Form.Field required error={!!errors.title}>
                <label>Alert Title</label>
                <TextWidget
                  id="title"
                  title="Title"
                  value={formData.title || ''}
                  onChange={this.handleFieldChange}
                  placeholder="Brief, clear title for the alert"
                />
                {errors.title && <div className="ui pointing red basic label">{errors.title}</div>}
              </Form.Field>

              <Form.Field>
                <label>Alert Type</label>
                <SelectWidget
                  id="alert_type"
                  title="Alert Type"
                  value={formData.alert_type || { token: 'info', title: 'Information' }}
                  choices={alertTypeChoices}
                  onChange={this.handleFieldChange}
                />
                <div className="field-help">
                  <ul>
                    <li><strong>Emergency:</strong> Urgent safety or security issues requiring immediate attention</li>
                    <li><strong>Event:</strong> Announcements about camp activities or schedule changes</li>
                    <li><strong>Information:</strong> General updates and non-urgent information</li>
                  </ul>
                </div>
              </Form.Field>
            </Segment>

            {/* Message Section */}
            <Segment className="form-section">
              <Header as="h3">
                <Icon name="file text outline" />
                Alert Message
              </Header>
              
              <Form.Field required error={!!errors.message}>
                <TextareaWidget
                  id="message"
                  title="Message"
                  value={formData.message || ''}
                  onChange={this.handleFieldChange}
                  rows={8}
                  placeholder="Enter the full alert message here. Be clear and concise."
                />
                {errors.message && <div className="ui pointing red basic label">{errors.message}</div>}
              </Form.Field>
            </Segment>

            {/* Status Section */}
            <Segment className="form-section">
              <Header as="h3">
                <Icon name="settings" />
                Alert Status
              </Header>
              
              <Form.Field>
                <label>Active Status</label>
                <Form.Checkbox
                  label="This alert is currently active"
                  checked={formData.active !== false}
                  onChange={(e, { checked }) => this.handleFieldChange('active', checked)}
                />
                <div className="field-help">
                  Inactive alerts will not appear on the homepage but remain in the alerts archive.
                </div>
              </Form.Field>
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
                Save Alert
              </Button>
              <Button
                size="large"
                onClick={this.props.onCancel}
                disabled={loading}
              >
                <Icon name="cancel" />
                Cancel
              </Button>
            </Segment>
          </Form>
        </Segment>
      </Container>
    );
  }
}

export default compose(
  withRouter,
  connect(
    (state) => ({
      token: state.userSession.token,
    })
  )
)(CampAlertEditForm);
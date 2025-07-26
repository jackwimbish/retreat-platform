/**
 * Quick Issue Modal component.
 * Provides a streamlined interface for quickly creating new issues from anywhere in the site.
 */

import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import {
  Modal,
  Button,
  Form,
  Message,
  Icon,
  Dropdown,
  TextArea,
  Loader,
  Dimmer
} from 'semantic-ui-react';
import { createContent } from '@plone/volto/actions';
import { flattenToAppURL } from '@plone/volto/helpers';
import { toast } from 'react-toastify';
import './QuickIssueModal.css';

const QuickIssueModal = ({ headerMode = false }) => {
  const dispatch = useDispatch();
  const history = useHistory();
  const token = useSelector((state) => state.userSession?.token);
  
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    location: '',
    priority: 'normal',
    issue_description: ''
  });
  const [errors, setErrors] = useState({});

  // Common camp locations for the dropdown
  const commonLocations = [
    { key: 'kitchen', text: 'Kitchen', value: 'Kitchen' },
    { key: 'dining-hall', text: 'Dining Hall', value: 'Dining Hall' },
    { key: 'bathrooms', text: 'Bathrooms', value: 'Bathrooms' },
    { key: 'bedrooms', text: 'Bedrooms', value: 'Bedrooms' },
    { key: 'office', text: 'Office', value: 'Office' },
    { key: 'grounds', text: 'Grounds', value: 'Grounds' },
    { key: 'pool-area', text: 'Pool Area', value: 'Pool Area' },
    { key: 'rec-areas', text: 'Recreational Areas', value: 'Recreational Areas' },
  ];

  const priorityOptions = [
    { key: 'low', text: 'Low', value: 'low', icon: 'angle down' },
    { key: 'normal', text: 'Normal', value: 'normal', icon: 'minus' },
    { key: 'high', text: 'High', value: 'high', icon: 'angle up', label: { color: 'orange', empty: true, circular: true } },
    { key: 'critical', text: 'Critical', value: 'critical', icon: 'angle double up', label: { color: 'red', empty: true, circular: true } },
  ];

  const handleOpen = () => {
    setOpen(true);
    setFormData({
      title: '',
      location: '',
      priority: 'normal',
      issue_description: ''
    });
    setErrors({});
  };

  const handleClose = () => {
    if (!loading) {
      setOpen(false);
    }
  };

  const handleInputChange = (e, { name, value }) => {
    setFormData({ ...formData, [name]: value });
    // Clear error for this field
    if (errors[name]) {
      setErrors({ ...errors, [name]: null });
    }
  };

  const handleLocationChange = (e, { value }) => {
    setFormData({ ...formData, location: value });
    if (errors.location) {
      setErrors({ ...errors, location: null });
    }
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    if (!formData.location.trim()) {
      newErrors.location = 'Location is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    
    try {
      // Build headers with auth token if available
      const headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch('/++api++/issues', {
        method: 'POST',
        headers: headers,
        credentials: 'same-origin',
        body: JSON.stringify({
          '@type': 'issue',
          title: formData.title,
          location: formData.location,
          priority: formData.priority,
          issue_description: formData.issue_description,
          status: 'new'
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        toast.success('Issue created successfully!');
        setOpen(false);
        // Redirect to the new issue
        history.push(flattenToAppURL(data['@id']));
      } else {
        const errorData = await response.json();
        toast.error(errorData.message || 'Failed to create issue');
      }
    } catch (error) {
      console.error('Error creating issue:', error);
      toast.error('An error occurred while creating the issue');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Button - either FAB or header button based on mode */}
      {headerMode ? (
        <Button
          color="blue"
          icon="clipboard outline"
          content="Report Issue"
          onClick={handleOpen}
          className="header-report-button"
        />
      ) : (
        <Button
          circular
          size="huge"
          color="blue"
          icon="plus"
          className="fab-button"
          onClick={handleOpen}
          title="Report New Issue"
        />
      )}

      {/* Quick Issue Modal */}
      <Modal
        open={open}
        onClose={handleClose}
        size="small"
        closeOnDimmerClick={!loading}
        closeOnEscape={!loading}
      >
        <Modal.Header>
          <Icon name="clipboard outline" />
          Report New Issue
        </Modal.Header>
        
        <Modal.Content>
          <Form>
            <Form.Input
              label="Issue Title"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              placeholder="Brief description of the issue"
              required
              error={errors.title}
              disabled={loading}
              autoFocus
            />

            <Form.Field required error={errors.location}>
              <label>Location</label>
              <Dropdown
                placeholder="Where is the issue located?"
                search
                selection
                allowAdditions
                clearable
                options={commonLocations}
                value={formData.location}
                onChange={handleLocationChange}
                disabled={loading}
                onAddItem={(e, { value }) => {
                  // Allow custom locations
                  handleLocationChange(e, { value });
                }}
              />
            </Form.Field>

            <Form.Field>
              <label>Priority</label>
              <Dropdown
                selection
                options={priorityOptions}
                value={formData.priority}
                onChange={(e, { value }) => handleInputChange(e, { name: 'priority', value })}
                disabled={loading}
              />
            </Form.Field>

            <Form.Field>
              <label>Description</label>
              <TextArea
                name="issue_description"
                value={formData.issue_description}
                onChange={handleInputChange}
                placeholder="Provide additional details about the issue..."
                rows={4}
                disabled={loading}
              />
            </Form.Field>
          </Form>

          {errors.form && (
            <Message negative>
              <Message.Header>Error</Message.Header>
              <p>{errors.form}</p>
            </Message>
          )}
        </Modal.Content>

        <Modal.Actions>
          <Button
            onClick={handleClose}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            primary
            onClick={handleSubmit}
            disabled={loading}
          >
            <Icon name="check" />
            Create Issue
          </Button>
        </Modal.Actions>

        {loading && (
          <Dimmer active inverted>
            <Loader>Creating issue...</Loader>
          </Dimmer>
        )}
      </Modal>
    </>
  );
};

export default QuickIssueModal;
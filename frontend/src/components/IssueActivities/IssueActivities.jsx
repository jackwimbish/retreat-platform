/**
 * Issue Activities component.
 * Displays and manages activities and comments for an issue.
 */

import React, { useState, useEffect } from 'react';
import {
  Segment,
  Header,
  Icon,
  Comment,
  Form,
  Button,
  Label,
  Divider,
  Message,
  TextArea
} from 'semantic-ui-react';
import { FormattedRelativeDate } from '@plone/volto/components';
import { useSelector } from 'react-redux';
import { toast } from 'react-toastify';
import { getBaseUrl, flattenToAppURL } from '@plone/volto/helpers';
import './IssueActivities.css';

const IssueActivities = ({ content }) => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [commenting, setCommenting] = useState(false);
  const [comment, setComment] = useState('');
  
  const token = useSelector((state) => state.userSession.token);
  const currentUser = useSelector((state) => state.users.user);

  // Fetch activities
  const fetchActivities = async () => {
    try {
      // Get the path from the content ID and prepend the API prefix
      const contentPath = content['@id'].replace(/^.*\/\/[^\/]+/, ''); // Remove protocol and host
      const apiUrl = `/++api++${contentPath}/@activities`;
      
      const response = await fetch(apiUrl, {
        headers: {
          'Accept': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setActivities(data.items || []);
      } else {
        console.error('Failed to fetch activities:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('Failed to fetch activities:', error);
      toast.error('Failed to load activities');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActivities();
  }, [content['@id'], token]);

  // Add comment
  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!comment.trim()) return;
    
    setCommenting(true);
    try {
      const contentPath = content['@id'].replace(/^.*\/\/[^\/]+/, '');
      const apiUrl = `/++api++${contentPath}/@activities`;
      
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ text: comment })
      });
      
      if (response.ok) {
        setComment('');
        await fetchActivities();
        toast.success('Comment added successfully');
      } else {
        console.error('Failed to add comment:', response.status, response.statusText);
        toast.error('Failed to add comment');
      }
    } catch (error) {
      console.error('Failed to add comment:', error);
      toast.error('Failed to add comment');
    } finally {
      setCommenting(false);
    }
  };


  // Format activity message
  const formatActivityMessage = (activity) => {
    switch (activity.type) {
      case 'issue_created':
        return (
          <>
            created this issue with priority <Label size="tiny" basic>{activity.data.priority}</Label>
            {activity.data.location && <> at location: {activity.data.location}</>}
          </>
        );
      case 'status_change':
        return (
          <>
            changed status from <Label size="tiny" basic>{activity.data.from}</Label> to{' '}
            <Label size="tiny" basic>{activity.data.to}</Label>
          </>
        );
      case 'priority_change':
        return (
          <>
            changed priority from <Label size="tiny" basic>{activity.data.from}</Label> to{' '}
            <Label size="tiny" basic>{activity.data.to}</Label>
          </>
        );
      case 'assignment':
        if (activity.data.from && activity.data.to) {
          return <>reassigned from {activity.data.from} to {activity.data.to}</>;
        } else if (activity.data.to) {
          return <>assigned to {activity.data.to}</>;
        } else {
          return <>removed assignment</>;
        }
      default:
        return null;
    }
  };

  // Get activity icon
  const getActivityIcon = (type) => {
    switch (type) {
      case 'comment':
        return 'comment';
      case 'issue_created':
        return 'plus circle';
      case 'status_change':
        return 'exchange';
      case 'priority_change':
        return 'flag';
      case 'assignment':
        return 'user';
      default:
        return 'info';
    }
  };

  // Parse ISO timestamp
  const parseTimestamp = (timestamp) => {
    return new Date(timestamp.replace('Z', ''));
  };

  if (loading) {
    return (
      <Segment>
        <Header as="h3">
          <Icon name="comments" />
          Activity & Comments
        </Header>
        <Message>
          <Icon name="circle notched" loading />
          Loading activities...
        </Message>
      </Segment>
    );
  }

  return (
    <Segment>
      <Header as="h3">
        <Icon name="comments" />
        Activity & Comments
        {activities.length > 0 && (
          <Label circular size="small" style={{ marginLeft: '10px' }}>
            {activities.length}
          </Label>
        )}
      </Header>
      
      <Comment.Group>
        {activities.length === 0 ? (
          <Message info>
            <Icon name="info circle" />
            No activity yet. Be the first to comment!
          </Message>
        ) : (
          activities.map((activity) => {
            const isComment = activity.type === 'comment';
            const timestamp = parseTimestamp(activity.timestamp);
            
            return (
              <Comment key={activity.id} className={`activity-item ${!isComment ? 'system-activity' : ''}`}>
                <Comment.Avatar>
                  <Icon name={getActivityIcon(activity.type)} circular inverted />
                </Comment.Avatar>
                <Comment.Content>
                  <Comment.Author as="span">{activity.user_fullname}</Comment.Author>
                  <Comment.Metadata>
                    <FormattedRelativeDate date={timestamp} />
                    {activity.edited && ' (edited)'}
                  </Comment.Metadata>
                  <Comment.Text>
                    {isComment ? (
                      activity.data.text
                    ) : (
                      <em>{formatActivityMessage(activity)}</em>
                    )}
                  </Comment.Text>
                </Comment.Content>
              </Comment>
            );
          })
        )}
      </Comment.Group>

      <Divider />

      {/* Add Comment Form */}
      {token ? (
        <Form reply onSubmit={handleAddComment}>
          <TextArea
            placeholder="Add a comment..."
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={3}
          />
          <Button
            primary
            type="submit"
            disabled={commenting || !comment.trim()}
            loading={commenting}
            style={{ marginTop: '10px' }}
          >
            <Icon name="comment" />
            Add Comment
          </Button>
        </Form>
      ) : (
        <Message info>
          <Icon name="lock" />
          Please log in to add comments
        </Message>
      )}

    </Segment>
  );
};

export default IssueActivities;
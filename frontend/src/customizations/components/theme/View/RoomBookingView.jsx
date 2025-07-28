/**
 * Room Booking View component.
 * Displays individual room booking details with cancel functionality
 */

import React, { useState } from 'react';
import { Link, useHistory } from 'react-router-dom';
import { useSelector } from 'react-redux';
import {
  Container,
  Segment,
  Header,
  Icon,
  Button,
  Grid,
  Label,
  Message,
  Confirm
} from 'semantic-ui-react';
import { FormattedDate } from '@plone/volto/components';
import { flattenToAppURL } from '@plone/volto/helpers';

const RoomBookingView = (props) => {
  const { content } = props;
  const history = useHistory();
  const token = useSelector((state) => state.userSession?.token);
  const currentUser = useSelector((state) => state.users?.user);
  
  const [showConfirm, setShowConfirm] = useState(false);
  const [cancelling, setCancelling] = useState(false);
  const [error, setError] = useState(null);
  
  // Check if current user owns this booking
  const isOwner = content.creators?.[0] === currentUser?.id || 
                  content.Creator === currentUser?.id || 
                  content.Creator === currentUser?.username;
  
  // Parse datetime for display
  const parseLocalDateTime = (dateTimeStr) => {
    if (!dateTimeStr.includes('Z') && !dateTimeStr.includes('+') && !dateTimeStr.includes('-', 10)) {
      return new Date(dateTimeStr + 'Z');
    }
    return new Date(dateTimeStr);
  };
  
  const startDate = parseLocalDateTime(content.start_datetime);
  const endDate = parseLocalDateTime(content.end_datetime);
  
  // Calculate duration
  const durationMinutes = (endDate - startDate) / (1000 * 60);
  const durationHours = Math.floor(durationMinutes / 60);
  const remainingMinutes = durationMinutes % 60;
  const durationText = durationHours > 0 
    ? `${durationHours} hour${durationHours > 1 ? 's' : ''}${remainingMinutes > 0 ? ` ${remainingMinutes} minutes` : ''}`
    : `${remainingMinutes} minutes`;
  
  // Handle booking cancellation
  const handleCancelBooking = async () => {
    setCancelling(true);
    setError(null);
    
    try {
      // Extract booking ID from content
      const bookingId = content.id || content['@id'].split('/').pop();
      
      // Use custom cancel endpoint for OAuth compatibility
      const response = await fetch(`/++api++/@cancel-booking/${bookingId}`, {
        method: 'DELETE',
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();
      
      if (response.ok) {
        // Redirect to conference rooms page after successful cancellation
        history.push('/conference-rooms');
      } else {
        console.error('Failed to cancel booking:', response.status, data);
        setError(data.error || 'Failed to cancel booking. Please try again.');
      }
    } catch (error) {
      console.error('Error cancelling booking:', error);
      setError('Failed to cancel booking. Please try again.');
    } finally {
      setCancelling(false);
      setShowConfirm(false);
    }
  };
  
  return (
    <Container className="room-booking-view">
      <Segment>
        <Link to="/conference-rooms">
          <Button basic size="small">
            <Icon name="arrow left" />
            Back to Calendar
          </Button>
        </Link>
        
        <Header as="h1">
          <Icon name="calendar check" />
          {content.title}
        </Header>
        
        {error && (
          <Message negative>
            <Message.Header>Error</Message.Header>
            <p>{error}</p>
          </Message>
        )}
        
        <Grid>
          <Grid.Row>
            <Grid.Column width={10}>
              <Segment>
                <Header as="h3">Booking Details</Header>
                
                <div style={{ marginBottom: '1rem' }}>
                  <Label>
                    <Icon name="building" />
                    Room
                  </Label>
                  {content.room && (
                    <Link to={flattenToAppURL(content.room['@id'])}>
                      {content.room.title}
                    </Link>
                  )}
                </div>
                
                <div style={{ marginBottom: '1rem' }}>
                  <Label>
                    <Icon name="calendar" />
                    Date
                  </Label>
                  {startDate.toLocaleDateString('en-US', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </div>
                
                <div style={{ marginBottom: '1rem' }}>
                  <Label>
                    <Icon name="clock" />
                    Time
                  </Label>
                  {startDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - 
                  {endDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  <span style={{ color: '#666', marginLeft: '0.5rem' }}>
                    ({durationText})
                  </span>
                </div>
                
                {content.purpose && (
                  <div style={{ marginBottom: '1rem' }}>
                    <Label>
                      <Icon name="info circle" />
                      Purpose
                    </Label>
                    <p style={{ marginTop: '0.5rem' }}>{content.purpose}</p>
                  </div>
                )}
                
                <div style={{ marginBottom: '1rem' }}>
                  <Label>
                    <Icon name="user" />
                    Booked by
                  </Label>
                  <span style={{ marginLeft: '0.5rem' }}>
                    {(() => {
                      // Extract username from booking title if available
                      const titleMatch = content.title?.match(/- ([^-]+)$/);
                      if (titleMatch && titleMatch[1]) {
                        return titleMatch[1].trim();
                      }
                      // Fall back to creator info
                      const creator = content.creators?.[0] || content.Creator;
                      // If creator looks like an email or complex ID, try to extract username
                      if (creator && creator.includes('@')) {
                        return creator.split('@')[0];
                      }
                      return creator || 'Unknown';
                    })()}
                  </span>
                </div>
                
                <div style={{ marginBottom: '1rem' }}>
                  <Label>
                    <Icon name="clock outline" />
                    Created
                  </Label>
                  <FormattedDate date={content.created} includeTime />
                </div>
              </Segment>
            </Grid.Column>
            
            <Grid.Column width={6}>
              <Segment>
                <Header as="h4">Actions</Header>
                
                {isOwner ? (
                  <>
                    <Button 
                      negative 
                      fluid
                      onClick={() => setShowConfirm(true)}
                      loading={cancelling}
                      disabled={cancelling}
                    >
                      <Icon name="cancel" />
                      Cancel Booking
                    </Button>
                    <p style={{ marginTop: '0.5rem', fontSize: '0.9rem', color: '#666' }}>
                      You can cancel this booking since you created it.
                    </p>
                  </>
                ) : (
                  <Message info>
                    <Message.Header>Not your booking</Message.Header>
                    <p>Only the person who created this booking can cancel it.</p>
                  </Message>
                )}
              </Segment>
              
              {/* Future Enhancement Ideas */}
              <Segment>
                <Header as="h4">Room Information</Header>
                {content.room && (
                  <>
                    <p><strong>Capacity:</strong> {content.room.capacity || 'Unknown'}</p>
                    <Button 
                      as={Link} 
                      to={flattenToAppURL(content.room['@id'])}
                      basic
                      fluid
                      size="small"
                    >
                      View Room Details
                    </Button>
                  </>
                )}
              </Segment>
            </Grid.Column>
          </Grid.Row>
        </Grid>
      </Segment>
      
      <Confirm
        open={showConfirm}
        header="Cancel Booking"
        content={`Are you sure you want to cancel this booking? This action cannot be undone.`}
        onCancel={() => setShowConfirm(false)}
        onConfirm={handleCancelBooking}
        confirmButton="Yes, Cancel Booking"
        cancelButton="Keep Booking"
      />
    </Container>
  );
};

export default RoomBookingView;
/**
 * Conference Rooms View component.
 * Calendar view for booking conference rooms
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import {
  Container,
  Segment,
  Header,
  Icon,
  Button,
  Grid,
  Label,
  Loader,
  Message,
  Popup,
  Modal,
  Form,
  Dropdown
} from 'semantic-ui-react';
import { FormattedDate } from '@plone/volto/components';
import { flattenToAppURL } from '@plone/volto/helpers';
import './ConferenceRoomsView.css';

const ConferenceRoomsView = (props) => {
  const { content } = props;
  const token = useSelector((state) => state.userSession?.token);
  const currentUser = useSelector((state) => state.users?.user);
  
  // State
  const [rooms, setRooms] = useState([]);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentWeek, setCurrentWeek] = useState(new Date());
  const [showBookingModal, setShowBookingModal] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [bookingForm, setBookingForm] = useState({
    room: '',
    start_datetime: null,
    end_datetime: null,
    purpose: '',
    duration: 60 // minutes
  });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [cancellingBooking, setCancellingBooking] = useState(null);

  // Time slot configuration (8 AM to 8 PM, 30-minute slots)
  const startHour = 8;
  const endHour = 20;
  const slotDuration = 30; // minutes
  const timeSlots = [];
  
  for (let hour = startHour; hour < endHour; hour++) {
    timeSlots.push({
      hour: hour,
      minute: 0,
      label: `${hour}:00`
    });
    timeSlots.push({
      hour: hour,
      minute: 30,
      label: `${hour}:30`
    });
  }

  // Duration options for booking
  const durationOptions = [
    { key: 30, text: '30 minutes', value: 30 },
    { key: 60, text: '1 hour', value: 60 },
    { key: 90, text: '1.5 hours', value: 90 },
    { key: 120, text: '2 hours', value: 120 },
    { key: 150, text: '2.5 hours', value: 150 },
    { key: 180, text: '3 hours', value: 180 },
    { key: 210, text: '3.5 hours', value: 210 },
    { key: 240, text: '4 hours', value: 240 },
    { key: 270, text: '4.5 hours', value: 270 },
    { key: 300, text: '5 hours', value: 300 }
  ];

  // Get week dates
  const getWeekDates = (date) => {
    const week = [];
    const startOfWeek = new Date(date);
    const day = startOfWeek.getDay();
    const diff = startOfWeek.getDate() - day + (day === 0 ? -6 : 1); // Monday start
    startOfWeek.setDate(diff);
    
    for (let i = 0; i < 7; i++) {
      const day = new Date(startOfWeek);
      day.setDate(startOfWeek.getDate() + i);
      week.push(day);
    }
    return week;
  };

  const weekDates = getWeekDates(currentWeek);

  // Parse datetime string - Plone stores as UTC without 'Z' suffix
  const parseLocalDateTime = (dateTimeStr) => {
    // Plone returns UTC times without 'Z' suffix, so we need to treat them as UTC
    if (!dateTimeStr.includes('Z') && !dateTimeStr.includes('+') && !dateTimeStr.includes('-', 10)) {
      // Add 'Z' to indicate UTC
      return new Date(dateTimeStr + 'Z');
    }
    return new Date(dateTimeStr);
  };

  // Fetch data
  useEffect(() => {
    fetchRooms();
  }, [token]);

  useEffect(() => {
    if (selectedRoom) {
      fetchBookings();
    }
  }, [currentWeek, selectedRoom, token]);

  const fetchRooms = async () => {
    try {
      const headers = {
        'Accept': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      // Fetch conference rooms
      const roomsResponse = await fetch(
        '/++api++/@search?portal_type=conference_room&fullobjects=true&b_size=100',
        {
          headers,
          credentials: 'same-origin',
        }
      );
      
      if (roomsResponse.ok) {
        const roomsData = await roomsResponse.json();
        const roomsList = roomsData.items || [];
        setRooms(roomsList);
        
        // Select first room by default
        if (roomsList.length > 0 && !selectedRoom) {
          setSelectedRoom(roomsList[0]);
        }
      }
    } catch (error) {
      console.error('Error fetching rooms:', error);
      setError('Failed to load rooms');
    }
  };

  const fetchBookings = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const headers = {
        'Accept': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      // Fetch bookings for the current week
      const weekStart = weekDates[0].toISOString();
      const weekEnd = new Date(weekDates[6]);
      weekEnd.setHours(23, 59, 59, 999);
      
      const bookingsResponse = await fetch(
        '/++api++/@search?portal_type=room_booking&fullobjects=true&b_size=1000',
        {
          headers,
          credentials: 'same-origin',
        }
      );
      
      if (bookingsResponse.ok) {
        const bookingsData = await bookingsResponse.json();
        console.log('All bookings fetched:', bookingsData.items?.length || 0);
        console.log('Selected room ID:', selectedRoom['@id']);
        
        // Filter bookings for current week and selected room
        const weekBookings = (bookingsData.items || []).filter(booking => {
          const bookingStart = parseLocalDateTime(booking.start_datetime);
          const bookingEnd = parseLocalDateTime(booking.end_datetime);
          const isInWeek = bookingStart <= weekEnd && bookingEnd >= new Date(weekStart);
          
          // Handle different room data structures
          let roomId = null;
          if (booking.room) {
            if (typeof booking.room === 'string') {
              roomId = booking.room;
            } else if (booking.room['@id']) {
              roomId = booking.room['@id'];
            } else if (booking.room.to_object) {
              roomId = booking.room.to_object;
            }
          }
          
          const isForRoom = roomId === selectedRoom['@id'];
          
          console.log('Booking:', booking.title, 'Room ID:', roomId, 'Is for selected room:', isForRoom, 'Is in week:', isInWeek);
          
          return isInWeek && isForRoom;
        });
        
        console.log('Filtered bookings for this room/week:', weekBookings.length);
        weekBookings.forEach(b => {
          console.log('Booking details:', {
            title: b.title,
            start: b.start_datetime,
            end: b.end_datetime,
            startDate: new Date(b.start_datetime).toString(),
            endDate: new Date(b.end_datetime).toString()
          });
        });
        setBookings(weekBookings);
      }
    } catch (error) {
      console.error('Error fetching bookings:', error);
      setError('Failed to load calendar data');
    } finally {
      setLoading(false);
    }
  };

  // Navigate weeks
  const goToPreviousWeek = () => {
    const newWeek = new Date(currentWeek);
    newWeek.setDate(newWeek.getDate() - 7);
    setCurrentWeek(newWeek);
  };

  const goToNextWeek = () => {
    const newWeek = new Date(currentWeek);
    newWeek.setDate(newWeek.getDate() + 7);
    setCurrentWeek(newWeek);
  };

  const goToToday = () => {
    setCurrentWeek(new Date());
  };

  // Check if a slot is booked
  const isSlotBooked = (date, timeSlot) => {
    const slotStart = new Date(date);
    slotStart.setHours(timeSlot.hour, timeSlot.minute, 0, 0);
    const slotEnd = new Date(slotStart);
    slotEnd.setMinutes(slotEnd.getMinutes() + slotDuration);

    return bookings.find(booking => {
      const bookingStart = parseLocalDateTime(booking.start_datetime);
      const bookingEnd = parseLocalDateTime(booking.end_datetime);
      
      return bookingStart < slotEnd && bookingEnd > slotStart;
    });
  };

  // Get booking for a slot
  const getSlotBooking = (date, timeSlot) => {
    const slotStart = new Date(date);
    slotStart.setHours(timeSlot.hour, timeSlot.minute, 0, 0);
    slotStart.setMilliseconds(0);

    return bookings.find(booking => {
      const bookingStart = parseLocalDateTime(booking.start_datetime);
      
      // Debug logging for any Sunday slot
      if (date.getDay() === 0) {
        const matches = Math.abs(bookingStart.getTime() - slotStart.getTime()) < 1000;
        if (matches || timeSlot.hour === 17) {
          console.log(`Checking Sunday ${timeSlot.label}:`, {
            slotStart: slotStart.toString(),
            bookingStart: bookingStart.toString(),
            bookingTitle: booking.title,
            matches: matches,
            slotTime: slotStart.getTime(),
            bookingTime: bookingStart.getTime(),
            diff: Math.abs(bookingStart.getTime() - slotStart.getTime())
          });
        }
      }
      
      // Check if this is the start of the booking (within 1 second tolerance)
      return Math.abs(bookingStart.getTime() - slotStart.getTime()) < 1000;
    });
  };

  // Calculate booking span in number of time slots
  const getBookingSpan = (booking) => {
    const start = parseLocalDateTime(booking.start_datetime);
    const end = parseLocalDateTime(booking.end_datetime);
    const durationMinutes = (end - start) / (1000 * 60);
    return Math.ceil(durationMinutes / slotDuration);
  };

  // Handle slot click
  const handleSlotClick = (date, timeSlot) => {
    const startDateTime = new Date(date);
    startDateTime.setHours(timeSlot.hour, timeSlot.minute, 0, 0);
    
    const endDateTime = new Date(startDateTime);
    endDateTime.setMinutes(endDateTime.getMinutes() + bookingForm.duration);

    setSelectedSlot({ date, timeSlot });
    setBookingForm({
      ...bookingForm,
      room: selectedRoom['@id'],
      start_datetime: startDateTime,
      end_datetime: endDateTime
    });
    setShowBookingModal(true);
  };

  // Handle duration change
  const handleDurationChange = (e, { value }) => {
    setBookingForm(prev => {
      const newEnd = new Date(prev.start_datetime);
      newEnd.setMinutes(newEnd.getMinutes() + value);
      return {
        ...prev,
        duration: value,
        end_datetime: newEnd
      };
    });
  };

  // Handle room selection change
  const handleRoomChange = (e, { value }) => {
    const room = rooms.find(r => r['@id'] === value);
    setSelectedRoom(room);
  };

  // Cancel booking
  const handleCancelBooking = async (bookingId, bookingTitle) => {
    if (!window.confirm(`Are you sure you want to cancel "${bookingTitle}"?`)) {
      return;
    }

    setCancellingBooking(bookingId);
    
    try {
      const response = await fetch(`/++api++${bookingId.replace(window.location.origin, '')}`, {
        method: 'DELETE',
        headers: {
          'Accept': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok || response.status === 204) {
        console.log('Booking cancelled successfully');
        // Refresh bookings
        fetchBookings();
      } else {
        const errorText = await response.text();
        console.error('Failed to cancel booking:', response.status, errorText);
        alert('Failed to cancel booking. Please try again.');
      }
    } catch (error) {
      console.error('Error cancelling booking:', error);
      alert('Failed to cancel booking. Please try again.');
    } finally {
      setCancellingBooking(null);
    }
  };

  // Submit booking
  const handleBookingSubmit = async () => {
    console.log('=== Starting booking submission ===');
    console.log('Selected Room:', selectedRoom);
    console.log('Booking Form:', bookingForm);
    console.log('Current User:', currentUser);
    console.log('Token exists:', !!token);
    
    setSubmitting(true);
    setError(null);

    try {
      // Create booking object
      // Convert local time to UTC and format without 'Z' (as Plone expects)
      const formatAsUTC = (date) => {
        const utcDate = new Date(date.toISOString());
        const year = utcDate.getUTCFullYear();
        const month = String(utcDate.getUTCMonth() + 1).padStart(2, '0');
        const day = String(utcDate.getUTCDate()).padStart(2, '0');
        const hours = String(utcDate.getUTCHours()).padStart(2, '0');
        const minutes = String(utcDate.getUTCMinutes()).padStart(2, '0');
        const seconds = String(utcDate.getUTCSeconds()).padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${minutes}:${seconds}`;
      };
      
      const bookingData = {
        '@type': 'room_booking',
        title: `Booking: ${selectedRoom.title} - ${currentUser?.username || 'User'}`,
        room: selectedRoom['@id'],
        start_datetime: formatAsUTC(bookingForm.start_datetime),
        end_datetime: formatAsUTC(bookingForm.end_datetime),
        purpose: bookingForm.purpose || ''
      };

      console.log('Booking data to send:', bookingData);
      console.log('API URL:', '/++api++/conference-rooms/bookings');

      const response = await fetch('/++api++/conference-rooms/bookings', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(bookingData)
      });

      console.log('Response status:', response.status);
      console.log('Response ok:', response.ok);
      
      const responseText = await response.text();
      console.log('Response text:', responseText);
      
      let responseData;
      try {
        responseData = JSON.parse(responseText);
      } catch (e) {
        console.error('Failed to parse response as JSON:', e);
        responseData = { message: responseText };
      }

      if (response.ok) {
        console.log('Booking created successfully!', responseData);
        setShowBookingModal(false);
        setBookingForm({
          room: '',
          start_datetime: null,
          end_datetime: null,
          purpose: '',
          duration: 60
        });
        fetchBookings(); // Refresh the calendar
      } else {
        console.error('Booking failed with status:', response.status);
        console.error('Error response:', responseData);
        setError(responseData.message || responseData.error || `Failed to create booking (${response.status})`);
      }
    } catch (error) {
      console.error('Error creating booking:', error);
      console.error('Error details:', error.message, error.stack);
      setError('Failed to create booking. Please try again.');
    } finally {
      setSubmitting(false);
      console.log('=== Booking submission complete ===');
    }
  };

  // Render booking cell
  const renderBookingCell = (date, timeSlot, slotIndex) => {
    const booking = getSlotBooking(date, timeSlot);
    const isBooked = isSlotBooked(date, timeSlot);
    
    if (booking) {
      // This is the start of a booking
      const span = getBookingSpan(booking);
      const isOwner = booking.creators?.[0] === currentUser?.id || 
                      booking.Creator === currentUser?.id || 
                      booking.Creator === currentUser?.username;
      console.log('Rendering booking cell:', booking.title, 'at', date.toDateString(), timeSlot.label);
      console.log('Ownership check:', {
        bookingCreator: booking.Creator,
        bookingCreators: booking.creators,
        currentUserId: currentUser?.id,
        currentUsername: currentUser?.username,
        isOwner: isOwner
      });
      
      return {
        element: (
          <td
            key={`${date}-${timeSlot.label}`}
            className="booking-cell booked"
            rowSpan={span}
          >
            <Popup
              trigger={
                <div className={`booking-block ${isOwner ? 'own-booking' : ''}`}>
                  <div className="booking-header">
                    <div className="booking-title">{booking.title}</div>
                    {isOwner && (
                      <Icon 
                        name="close" 
                        className="cancel-icon"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleCancelBooking(booking['@id'], booking.title);
                        }}
                        style={{ 
                          opacity: cancellingBooking === booking['@id'] ? 0.5 : 1,
                          cursor: cancellingBooking === booking['@id'] ? 'wait' : 'pointer'
                        }}
                      />
                    )}
                  </div>
                  {booking.purpose && (
                    <div className="booking-purpose">{booking.purpose}</div>
                  )}
                  <div className="booking-time">
                    {parseLocalDateTime(booking.start_datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - 
                    {parseLocalDateTime(booking.end_datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              }
              content={
                <div>
                  <p><strong>Booked by:</strong> {booking.Creator}</p>
                  <p><strong>Duration:</strong> {span * 30} minutes</p>
                  {booking.purpose && <p><strong>Purpose:</strong> {booking.purpose}</p>}
                  {isOwner && (
                    <Button 
                      size="tiny" 
                      negative
                      as={Link}
                      to={flattenToAppURL(booking['@id'])}
                    >
                      View/Cancel Booking
                    </Button>
                  )}
                </div>
              }
              position="top center"
              on="hover"
            />
          </td>
        ),
        span: span
      };
    } else if (isBooked) {
      // This slot is part of a booking but not the start
      return { element: null, span: 0 };
    } else {
      // Empty slot - can be booked
      const isPast = new Date(date.getFullYear(), date.getMonth(), date.getDate(), 
        timeSlot.hour, timeSlot.minute) < new Date();
      
      return {
        element: (
          <td
            key={`${date}-${timeSlot.label}`}
            className={`booking-cell empty ${isPast ? 'past' : 'available'}`}
            onClick={() => !isPast && handleSlotClick(date, timeSlot)}
          >
            {!isPast && <Icon name="plus" className="add-booking-icon" />}
          </td>
        ),
        span: 1
      };
    }
  };

  // Prepare room options for dropdown
  const roomOptions = rooms.map(room => ({
    key: room['@id'],
    text: `${room.title} (Capacity: ${room.capacity})`,
    value: room['@id']
  }));

  if (!selectedRoom && rooms.length === 0) {
    return (
      <Container className="conference-rooms-view">
        <Segment basic textAlign="center">
          <Loader active inline="centered">Loading rooms...</Loader>
        </Segment>
      </Container>
    );
  }

  if (error && !selectedRoom) {
    return (
      <Container className="conference-rooms-view">
        <Message negative>
          <Message.Header>Error</Message.Header>
          <p>{error}</p>
        </Message>
      </Container>
    );
  }

  return (
    <Container className="conference-rooms-view">
      <Segment>
        <Grid>
          <Grid.Row>
            <Grid.Column width={8}>
              <Header as="h1">
                <Icon name="calendar alternate" />
                Conference Room Bookings
              </Header>
            </Grid.Column>
            <Grid.Column width={8} textAlign="right">
              <Button.Group>
                <Button icon onClick={goToPreviousWeek}>
                  <Icon name="chevron left" />
                </Button>
                <Button onClick={goToToday}>Today</Button>
                <Button icon onClick={goToNextWeek}>
                  <Icon name="chevron right" />
                </Button>
              </Button.Group>
            </Grid.Column>
          </Grid.Row>
        </Grid>

        {/* Room Selector */}
        <Segment>
          <Grid>
            <Grid.Row>
              <Grid.Column width={8}>
                <Form.Field>
                  <label>Select Room:</label>
                  <Dropdown
                    placeholder="Select a conference room"
                    fluid
                    selection
                    options={roomOptions}
                    value={selectedRoom?.['@id']}
                    onChange={handleRoomChange}
                  />
                </Form.Field>
              </Grid.Column>
              <Grid.Column width={8}>
                <Header as="h3" textAlign="center">
                  Week of {weekDates[0].toLocaleDateString()} - {weekDates[6].toLocaleDateString()}
                </Header>
              </Grid.Column>
            </Grid.Row>
          </Grid>
        </Segment>

        {loading ? (
          <Segment basic textAlign="center">
            <Loader active inline="centered">Loading calendar...</Loader>
          </Segment>
        ) : (
          <>
            <div className="calendar-container">
              <table className="booking-calendar">
                <thead>
                  <tr>
                    <th className="time-header-column">Time</th>
                    {weekDates.map((date, index) => (
                      <th key={index} className="day-header">
                        <div className="day-name">
                          {date.toLocaleDateString('en-US', { weekday: 'short' })}
                        </div>
                        <div className="day-date">
                          {date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {timeSlots.map((timeSlot, slotIndex) => {
                    const skipSlots = {};
                    
                    return (
                      <tr key={timeSlot.label}>
                        <td className="time-label-cell">{timeSlot.label}</td>
                        {weekDates.map((date, dateIndex) => {
                          const cellKey = `${dateIndex}-${slotIndex}`;
                          if (skipSlots[dateIndex] && skipSlots[dateIndex] > 0) {
                            skipSlots[dateIndex]--;
                            return null;
                          }
                          
                          const cellData = renderBookingCell(date, timeSlot, slotIndex);
                          if (cellData.span > 1) {
                            // This booking spans multiple time slots
                            skipSlots[dateIndex] = cellData.span - 1;
                          }
                          
                          return cellData.element;
                        })}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <Message info>
              <Message.Header>How to book a room</Message.Header>
              <p>Select a room from the dropdown above, then click on any available (white) time slot to create a booking. Past time slots are grayed out.</p>
            </Message>
          </>
        )}
      </Segment>

      {/* Booking Modal */}
      <Modal
        open={showBookingModal}
        onClose={() => setShowBookingModal(false)}
        size="small"
      >
        <Modal.Header>Book Conference Room</Modal.Header>
        <Modal.Content>
          {error && (
            <Message negative>
              <Message.Header>Error</Message.Header>
              <p>{error}</p>
            </Message>
          )}
          
          <Form>
            <Form.Field>
              <label>Room</label>
              <p><strong>{selectedRoom?.title}</strong> (Capacity: {selectedRoom?.capacity})</p>
            </Form.Field>
            
            <Form.Field>
              <label>Date & Time</label>
              <p>
                {selectedSlot?.date.toLocaleDateString()} at {selectedSlot?.timeSlot.label}
              </p>
            </Form.Field>
            
            <Form.Field>
              <label>Duration</label>
              <Dropdown
                selection
                options={durationOptions}
                value={bookingForm.duration}
                onChange={handleDurationChange}
              />
            </Form.Field>
            
            <Form.Field>
              <label>Purpose (optional)</label>
              <Form.TextArea
                placeholder="What will you be using the room for?"
                value={bookingForm.purpose}
                onChange={(e) => setBookingForm({ ...bookingForm, purpose: e.target.value })}
              />
            </Form.Field>
          </Form>
        </Modal.Content>
        <Modal.Actions>
          <Button onClick={() => setShowBookingModal(false)}>
            Cancel
          </Button>
          <Button 
            primary 
            onClick={handleBookingSubmit}
            loading={submitting}
            disabled={submitting}
          >
            Create Booking
          </Button>
        </Modal.Actions>
      </Modal>
    </Container>
  );
};

export default ConferenceRoomsView;
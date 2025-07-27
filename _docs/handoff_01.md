# Camp Coordinator Project Handoff Document - Session 2

## Project Overview
Camp Coordinator is a Plone 6.1 + Volto React application for managing retreat/camp operations. The system uses Plone as the backend CMS with Volto as the React-based frontend.

## Session Summary (July 27, 2025)

### Completed in This Session

#### Conference Room Booking System - Phase 1 Complete ✅

Built a full-featured room booking calendar system with the following capabilities:

1. **Calendar View Component** (`/frontend/src/customizations/components/theme/View/ConferenceRoomsView.jsx`)
   - Week view calendar with vertical time slots (8 AM - 8 PM)
   - Days displayed horizontally (Monday - Sunday)
   - Room selector dropdown to switch between rooms
   - Visual booking blocks (green for own bookings, blue for others)
   - Click on empty slots to book
   - Week navigation (Previous/Today/Next)

2. **Booking Creation**
   - Modal form for creating bookings
   - Duration selector (30 minutes to 5 hours)
   - Optional purpose field
   - Automatic conflict detection (backend)
   - Proper timezone handling (local time display, UTC storage)

3. **Booking Management**
   - Quick cancel button (X) on own bookings
   - Click booking for details popup
   - Individual booking view page with detailed cancel functionality
   - Automatic calendar refresh after actions

4. **Technical Improvements**
   - Fixed UTC/local time conversion issues
   - Changed popup from hover to click for better usability
   - Fixed table distortion with absolute positioning for multi-slot bookings
   - Added comprehensive error handling and user feedback

### Key Implementation Details

#### Timezone Handling
- Backend stores times in UTC without 'Z' suffix
- Frontend converts UTC to local for display: `new Date(dateTimeStr + 'Z')`
- When creating bookings, convert local to UTC before sending
- Custom `parseLocalDateTime` and `formatAsUTC` functions handle conversions

#### Calendar Layout Fix
- Removed `rowSpan` which was distorting time slots
- Use absolute positioning for booking blocks
- All time slots render cells (empty or with content)
- CSS calculates booking height based on duration

#### Room Booking View
- Created `RoomBookingView.jsx` for individual booking pages
- Registered in `Views.jsx` configuration
- Shows all booking details with prominent cancel button
- Only booking owner can cancel

### Latest Fixes (End of Session)

1. **Google User Display Names**: Fixed issue where Google-authenticated users showed as numeric IDs
   - Integrated with existing `@user-display-name` public API endpoint
   - Fetches and caches display names for all booking creators
   - Updates booking titles to use proper display names
   - Shows correct names in calendar popups and booking details

### Current Issues/Observations

1. **Monday Bookings**: User reported Monday bookings might not show on calendar
   - Added extensive debugging but issue not fully confirmed
   - Check console logs for week date calculations

2. **Multiple Bookings**: Screenshot showed 3 identical bookings
   - Possible duplicate creation issue
   - May need to add duplicate prevention

3. **API Patterns**
   - Create content: POST to parent folder (e.g., `/++api++/conference-rooms/bookings`)
   - Delete content: DELETE to item URL
   - Update content: PATCH to item URL
   - Search: GET `/++api++/@search?portal_type=...`

### File Structure Created/Modified

```
frontend/src/customizations/
├── components/theme/View/
│   ├── ConferenceRoomsView.jsx (new)
│   ├── ConferenceRoomsView.css (new)
│   ├── RoomBookingView.jsx (new)
│   └── SmartDocumentView.jsx (modified - added conference room detection)
└── config/
    └── Views.jsx (modified - registered room_booking view)
```

### Next Steps

1. **Debug Monday booking issue**
   - Check if it's a display issue or creation issue
   - Review timezone calculations for week boundaries

2. **Prevent duplicate bookings**
   - Add debouncing to submit button
   - Check for existing bookings before creation

3. **Enhance booking features**
   - Recurring bookings
   - Email notifications for bookings
   - Room amenities/features display
   - Booking modification (not just cancel)
   - Export calendar to iCal/Google Calendar

4. **Performance optimizations**
   - Cache room data
   - Optimize booking queries
   - Add loading states for better UX

### Testing Checklist

1. Create bookings at different times/days
2. Verify timezone handling across DST boundaries
3. Test booking conflicts
4. Test cancel functionality
5. Verify week navigation
6. Test with different user roles

### Important Notes

1. **Room Relations**: The room field in bookings uses Plone's RelationChoice
   - Frontend sends just the room ID string
   - Backend returns full room object with @id

2. **Time Slots**: Must be on 30-minute boundaries
   - Backend validates this with `booking_utils.py`
   - Frontend enforces in UI

3. **Permissions**: All authenticated users can book rooms
   - Only booking creator can cancel
   - Consider adding room-specific permissions

### Console Debugging Commands

```javascript
// Check current bookings
console.log(bookings);

// Check week dates
console.log(weekDates.map(d => d.toDateString()));

// Check timezone parsing
console.log(parseLocalDateTime('2025-07-28T10:00:00'));
```

This handoff provides complete context for continuing development of the conference room booking system. The core functionality is complete and working, with some minor issues to address and enhancements to consider.
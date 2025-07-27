# Camp Coordinator Project Handoff Document

## Project Overview
Camp Coordinator is a Plone 6.1 + Volto React application for managing retreat/camp operations. The system uses Plone as the backend CMS with Volto as the React-based frontend.

## Current Status (July 27, 2025)

### Completed Features

1. **Issue Tracking System**
   - Content type for maintenance/facility issues
   - Activity logging with timestamps and user info
   - Comments system (append-only)
   - Status tracking (new, in-progress, resolved)
   - Priority levels (low, medium, high, critical)

2. **Participant Management**
   - Content type for camp participants
   - Basic participant information tracking

3. **Camp Alert System** ✅ (Just Completed)
   - Emergency/Event/Info alerts
   - Email notifications to all camp members
   - Active alerts displayed on homepage
   - Archive functionality
   - Management interface at `/alerts`

4. **Resource Booking System** 🚧 (In Progress - Phase 1)
   - Conference room content type ✅
   - Room booking content type ✅
   - 5 initial rooms configured ✅
   - Booking validation utilities ✅
   - Content types properly registered ✅
   - Conference rooms folder at `/conference-rooms` ✅
   - Bookings subfolder at `/conference-rooms/bookings` ✅
   - **Still needed:**
     - Calendar view component
     - Booking form component
     - Frontend integration

### Latest Updates (Since Initial Handoff)

1. **Created setup scripts for conference rooms:**
   - `setup_room_types.py` - Creates the conference_room and room_booking content types
   - `setup_conference_rooms.py` - Creates the folder structure and 5 initial rooms
   
2. **Conference Rooms Created:**
   - Downstairs Room 1 (capacity: 4)
   - Downstairs Room 2 (capacity: 4)
   - Upstairs Room 1 (capacity: 4)
   - Upstairs Room 2 (capacity: 2)
   - Upstairs Room 3 (capacity: 2)

3. **Fixed content type registration issues:**
   - Content types must be created before attempting to use them
   - Added proper workflow configuration (one_state_workflow)

### User Roles
- **Directors** (Manager role): Full admin access
- **Staff** (Editor role): Can manage content, create alerts
- **Participants** (Member role): Can create issues, book rooms
- **Anonymous**: Redirected to login

## Key Implementation Patterns

### Backend (Plone)

#### Creating New Content Types
1. **Define the interface** in `/backend/src/retreat/interfaces.py`:
```python
class IConferenceRoom(Interface):
    capacity = schema.Int(title=u"Capacity", required=True)
```

2. **Create XML definition** in `/backend/content_type_profiles/profile/types/[type_name].xml`

3. **Register in types.xml**: `/backend/content_type_profiles/profile/types.xml`

4. **Add to Docker init**: Update `/backend/docker_init_site.py` to create the content type

#### API Endpoints
- Custom endpoints are defined in `/backend/src/retreat/api.zcml`
- Example: Public portrait view, user search endpoint

#### Email Notifications
- Configured in `/backend/src/retreat/notifications.py` (issues)
- Camp alerts in `/backend/src/retreat/camp_alerts.py`
- Uses Resend API (configured via environment variables)

### Frontend (Volto/React)

#### Custom Views
Location: `/frontend/src/customizations/components/theme/View/`
- `HomepageView.jsx` - Dashboard with stats and alerts
- `IssueView.jsx` - Individual issue display
- `AlertsFolderView.jsx` - Alert management interface

#### Custom Edit Forms
Location: `/frontend/src/customizations/components/manage/Edit/`
- `IssueEditForm.jsx` - Custom form for issues
- `CampAlertEditForm.jsx` - Custom form for alerts

#### API Calls Pattern
```javascript
// Fetch data
const response = await fetch('/++api++/@search?portal_type=room_booking', {
  headers: {
    'Accept': 'application/json',
    'Authorization': `Bearer ${token}`
  }
});

// Update data
const response = await fetch(`/++api++${pathOnly}`, {
  method: 'PATCH',
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({ field: value })
});
```

#### Adding Navigation
Update `/frontend/src/customizations/components/theme/View/HomepageView.jsx` to add new sections to the quick links area.

### Docker Setup

#### Main Files
- `/backend/docker_init_site.py` - Site initialization script
- `/docker-compose.yml` - Container configuration
- Content types are created programmatically in docker_init_site.py

#### Local Development
Without Docker, use these scripts in `/backend/`:
- `start_plone.py` - Start the backend server
- `setup_*.py` scripts - Various setup utilities

## Next Steps for Resource Booking System

### 1. Create Calendar View Component
Create `/frontend/src/customizations/components/theme/View/ConferenceRoomsView.jsx`:
- Week view calendar grid
- Show all 5 rooms as rows
- Time slots as columns (half-hour increments)
- Click empty slot to book
- Display existing bookings

### 2. Create Booking Form Component
- Modal or inline form
- Pre-fill room and time from calendar click
- Duration selector (30 min increments, max 5 hours)
- Optional purpose field
- Conflict checking before save

### 3. Create Booking View Component
- Display booking details
- Cancel button (if user owns booking)
- Link back to calendar

### 4. Add API Integration
- Create bookings in `/conference-rooms/bookings/`
- Use booking_utils.py for validation
- Handle conflicts gracefully

### 5. Add to Homepage
- Add "Book a Room" card to Admin Tools or Quick Links
- Show user's upcoming bookings

## Important Technical Notes

1. **Permissions**: All authenticated users can book rooms, but the booking system uses standard `cmf.AddPortalContent` permission

2. **Workflow**: All content uses `one_state_workflow` (always published)

3. **Time Handling**: 
   - Bookings must be on half-hour boundaries
   - Use `booking_utils.round_to_half_hour()` if needed
   - Maximum 5-hour bookings

4. **Conflict Checking**: Already implemented in `booking_utils.check_booking_conflicts()`

5. **Relations**: Room bookings use RelationChoice field to reference conference rooms

6. **IMPORTANT - Content Types**: 
   - Always use `Document` instead of `Folder` for container types
   - The system doesn't have a `Folder` content type
   - Document can contain other content just like folders
   - This applies to all container creation in scripts

## Environment Variables
- `RESEND_API_KEY` - For email notifications
- `RAZZLE_API_PATH` - Backend URL for frontend

## Testing Approach
1. Create bookings via UI
2. Test conflict detection
3. Test cancellation
4. Verify permissions (all users can book)
5. Check calendar display accuracy

## Common Issues/Solutions

1. **Module not found errors**: Add `PYTHONPATH` with src directory
2. **Permission errors**: Use standard permissions instead of custom ones
3. **XML parsing errors**: Use Python interfaces instead of XML schemas
4. **Frontend 404s**: Check URL patterns, use `/++api++/` prefix for API calls
5. **"No such content type" errors**: Ensure content types are created before using them (run setup scripts in order)
6. **"No such content type: Folder"**: Use `Document` instead - Plone/Volto doesn't have a Folder type

## Contact Points
- Backend: Plone 6.1 with Dexterity content types
- Frontend: Volto 18 (React-based)
- Email: Resend API
- Database: ZODB (built into Plone)

This handoff should provide enough context to continue implementing the resource booking calendar view and complete Phase 1 of the booking system.
# Docker Deployment Verification Checklist

## Pre-deployment Checks

### ✅ Backend Configuration
- [x] `resend` package is included in requirements.txt for email notifications
- [x] `docker_init_site.py` includes all content types:
  - Issue content type
  - Participant content type  
  - Camp Alert content type
  - Conference Room content type
  - Room Booking content type
- [x] Python interfaces defined in `src/retreat/interfaces.py`:
  - ICampAlert
  - IConferenceRoom
  - IRoomBooking
- [x] Event handlers registered in `configure.zcml`:
  - Camp alert notifications
  - Issue activity tracking
  - Issue notifications

### ✅ Frontend Configuration
- [x] Custom views included:
  - ConferenceRoomsView.jsx (calendar booking system)
  - RoomBookingView.jsx (individual booking details)
  - CampAlertView.jsx (alert display)
  - AlertsFolderView.jsx (alerts dashboard)
- [x] Views registered in `config/Views.jsx`
- [x] Smart routing in `SmartDocumentView.jsx`

## Deployment Steps

### 1. Build Docker Images
```bash
# Build backend
docker-compose build backend

# Build frontend
docker-compose build frontend
```

### 2. Start Services
```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 3. Initialize Site (First Run Only)
The backend will automatically:
1. Create Plone instance if needed
2. Run `docker_init_site.py` to:
   - Create all content types
   - Set up folder structure
   - Create default conference rooms
   - Set permissions
   - Create sample users

### 4. Verify Installation

#### Backend Checks
- Access backend at: http://localhost:8080/Plone
- Login as admin/admin
- Check content types exist:
  - Go to Site Setup > Dexterity Content Types
  - Verify: issue, participant, camp_alert, conference_room, room_booking

#### Frontend Checks
- Access frontend at: http://localhost:3000
- Login as admin/admin
- Verify pages load:
  - Homepage with Quick Actions
  - /conference-rooms (booking calendar)
  - /alerts (alerts dashboard)
  - /issues (issues dashboard)

#### Conference Room Booking System
1. Navigate to /conference-rooms
2. Verify 5 rooms are available in dropdown
3. Try creating a booking:
   - Click on empty time slot
   - Fill booking form
   - Submit and verify it appears
4. Test booking management:
   - Click on your booking
   - Verify cancel button works

#### Camp Alerts System
1. Navigate to /alerts
2. As admin/staff, create new alert:
   - Click "Create Alert" button
   - Fill form and submit
3. Verify alert appears on homepage

## Environment Variables

### Required for Email Notifications
```bash
# In backend/.env or docker-compose.yml
ENABLE_ISSUE_NOTIFICATIONS=true
RESEND_API_KEY=your_resend_api_key
RESEND_TEST_MODE=false  # Set to true for testing without sending emails
```

### Optional Configurations
```bash
# CORS settings (already in docker-compose.yml)
CORS_ALLOW_ORIGIN=*
CORS_ALLOW_METHODS=DELETE,GET,OPTIONS,PATCH,POST,PUT
CORS_ALLOW_CREDENTIALS=true
```

## Troubleshooting

### Backend Issues
1. **Content types not appearing**:
   - Check if `src/retreat` directory is mounted correctly
   - Verify `retreat-configure.zcml` exists in instance/etc/package-includes/
   - Restart backend: `docker-compose restart backend`

2. **Room booking conflicts not working**:
   - Check `booking_utils.py` is loaded
   - Verify timezone handling in logs

### Frontend Issues
1. **Conference room calendar not loading**:
   - Check browser console for API errors
   - Verify backend is accessible at http://localhost:8080/Plone/++api++
   - Check CORS headers in network tab

2. **Icons not displaying**:
   - Verify Semantic UI CSS is loaded
   - Check for font loading errors in network tab

### Database Reset
If needed to start fresh:
```bash
# Stop services
docker-compose down

# Remove volumes
docker volume rm my-retreat-platform_plone-filestorage
docker volume rm my-retreat-platform_plone-blobstorage

# Start again
docker-compose up -d
```

## Sample Users (Created by init script)
- Admin: admin/admin
- Director: director1/director123
- Staff: staff1/staff123, staff2/staff123  
- Participants: participant1/participant123, etc.

## Next Steps After Deployment
1. Configure Google OAuth if needed
2. Set up email notifications with Resend API key
3. Update conference room names/capacities as needed
4. Create real user accounts
5. Delete sample users
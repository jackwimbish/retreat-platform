# Camp Coordinator Project Handoff Document - Session 3

## Project Overview
Camp Coordinator is a Plone 6.1 + Volto React application for managing retreat/camp operations. The system uses Plone as the backend CMS with Volto as the React-based frontend.

## Session Summary (July 27, 2025)

### Completed in This Session

#### 1. Homepage UI Improvements ✅
- Removed "Coming Soon" section from homepage
- Removed issue statistics cards (Total Issues, New Issues, In Progress, High Priority)
- Cleaned up unused state and API calls for statistics
- Added "tasks" icon to Issues Dashboard button (changed from non-existent "clipboard list" icon)

#### 2. Docker Deployment Configuration ✅
- Fixed configuration switching between local and Docker environments
- Created `zope.ini.docker` with proper Docker paths (`/app/instance/var/log/`)
- Updated `switch_config.sh` script to handle both `zope.conf` and `zope.ini` files
- Successfully built both backend and frontend Docker images
- Verified all content types are included in `docker_init_site.py`:
  - Issue, Participant, Camp Alert, Conference Room, Room Booking
  - Default conference rooms creation
  - Sample users creation

#### 3. Google OAuth Authentication Issues 🔧 (In Progress)
- **Problem Identified**: Users authenticated via Google OAuth cannot cancel their own bookings (401 Unauthorized)
- **Root Cause**: Mismatch between how Google OAuth users are identified:
  - Redux state stores user ID as full URL: `"http://localhost:3000/@users/112191486621124941018"`
  - Bookings store creator as numeric ID: `"112191486621124941018"`
  - Backend doesn't recognize OAuth users as having delete permissions on their content

### Current Issues

#### 1. Google OAuth Booking Cancellation (Critical)
**Symptoms**:
- 401 Unauthorized error when OAuth users try to cancel bookings
- Ownership check passes in frontend (`isOwner: true`)
- Token is present and valid
- Backend rejects the DELETE request

**Debugging Added**:
- Enhanced ownership checks to handle multiple ID formats
- Added `getUserId()` function to extract numeric ID from URL format
- Added extensive console logging for auth debugging
- Created diagnostic code to check booking permissions

**Findings**:
```javascript
// OAuth user structure:
{
  id: "http://localhost:3000/@users/112191486621124941018",
  email: "jack.wimbish@gauntletai.com",
  fullname: "Jack Wimbish"
}

// Booking creator stored as:
creators: ['112191486621124941018']
```

**Potential Solutions**:
1. Backend configuration to grant OAuth users proper permissions
2. Use workflow/status changes instead of DELETE
3. Create custom API endpoint for OAuth user actions
4. Fix permission assignment when OAuth users create content

#### 2. Frontend Hot Reload in Docker
- Changes to React components not reflecting immediately
- May need to restart frontend container for changes
- Volume mounts are correctly configured but production build might not support hot reload

### File Structure Modified

```
_docs/
├── handoff_01.md (previous session)
├── handoff_02.md (this session)
└── docker-deployment-verification.md (new)

frontend/src/customizations/
├── components/theme/View/
│   ├── ConferenceRoomsView.jsx (modified - debugging & OAuth fixes)
│   ├── RoomBookingView.jsx (modified - OAuth ownership check)
│   ├── HomepageView.jsx (modified - removed sections)
│   └── ConferenceRoomsView-GoogleAuthFix.jsx (new - workaround strategies)

backend/
├── instance/etc/
│   ├── zope.ini.docker (new - Docker log paths)
│   └── (other config files)
└── switch_config.sh (handles Docker/local switching)
```

### Key Code Changes

#### 1. OAuth User ID Extraction
```javascript
const getUserId = (user) => {
  if (!user) return null;
  // Extract numeric ID from URL format
  if (user.id && user.id.includes('@users/')) {
    return user.id.split('@users/')[1];
  }
  return user.id || user.username;
};
```

#### 2. Enhanced Ownership Check
```javascript
const creatorId = booking.creators?.[0] || booking.Creator;
const currentUserId = getUserId(currentUser);
const isOwner = creatorId === currentUserId || 
                creatorId === currentUser?.username ||
                creatorId === currentUser?.id ||
                (currentUser?.email && creatorId === currentUser.email) ||
                (currentUser?.fullname && booking.title?.includes(currentUser.fullname));
```

### Next Steps

#### 1. Fix OAuth Permissions (Priority 1)
- Check OAuth plugin configuration in Plone
- Verify OAuth users get proper roles (Member, Owner)
- Ensure `__ac_local_roles__` is set correctly on created content
- Consider custom permission adapter for OAuth users

#### 2. Alternative Approaches
- Implement "soft delete" by updating booking status/title
- Use Plone's workflow system instead of direct DELETE
- Create backend API endpoint that handles OAuth user permissions
- Add "cancelled" field to booking schema

#### 3. Testing Improvements
- Add integration tests for OAuth user scenarios
- Test booking lifecycle with different user types
- Verify Docker deployment with OAuth enabled

### Environment Setup

#### Docker Commands
```bash
# Switch to Docker configuration
cd backend
./switch_config.sh docker

# Build and run
docker-compose build
docker-compose up -d

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

#### Configuration Files
- `backend/instance/etc/zope.conf.docker` - Docker paths
- `backend/instance/etc/zope.ini.docker` - Docker logging paths
- `docker-deployment-verification.md` - Complete deployment checklist

### Known Issues

1. **Display Name API**: Fixed URL construction issue where full backend URL was being prepended
2. **Icon Compatibility**: Changed from "clipboard list" to "tasks" icon for Semantic UI compatibility
3. **Frontend Debugging**: Console logs may not appear immediately in Docker - requires container restart

### Important Notes

1. **OAuth Integration**: The `pas.plugins.oidc` package is installed but may need additional configuration for proper permission handling

2. **User Identification**: Google OAuth users have complex ID structure that differs from regular Plone users

3. **Docker Volumes**: Source code is mounted but production build may cache components

4. **Permission Model**: Plone's security model may need adaptation for OAuth users who don't follow traditional user/role patterns

This handoff provides complete context for resolving the OAuth permission issue and continuing development of the conference room booking system.
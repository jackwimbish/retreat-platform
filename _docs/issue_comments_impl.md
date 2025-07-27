# Issue Comments & Activity Implementation Plan

## Overview
Implement a unified activity stream for Issues that combines comments and system activities (status changes, assignments, etc.) into a single chronological feed.

## Data Structure

### 1. Add Activity Log Field to Issue
- Field type: `JSONField` storing array of activity objects
- Each activity has:
  ```json
  {
    "id": "unique_id",
    "type": "comment|status_change|priority_change|assignment",
    "timestamp": "2024-01-26T15:30:00Z",
    "user_id": "john_doe",
    "user_fullname": "John Doe",
    "data": {
      // Type-specific data
    },
    "deleted": false  // For soft-delete of comments
  }
  ```

### 2. Activity Types
- **comment**: `data: {text: "Comment text"}`
- **status_change**: `data: {from: "new", to: "in_progress"}`
- **priority_change**: `data: {from: "normal", to: "high"}`
- **assignment**: `data: {from: null, to: "maintenance_staff"}`

### 3. Add Assignment Field to Issue
- Field: `assigned_to` (Choice field with user vocabulary)
- Single user assignment for clear responsibility

## Backend Implementation

### 1. Update Issue Content Type
- Add `activity_log` JSONField
- Add `assigned_to` Choice field
- Create migration for existing issues

### 2. Activity Management (backend/src/retreat/activities.py)
- `add_activity(issue, activity_type, data, user)`
- `update_comment(issue, comment_id, new_text, user)`
- `delete_comment(issue, comment_id, user)`
- Handle concurrent updates with transaction retry

### 3. Event Subscribers
- Subscribe to issue modification events
- Auto-log status, priority, and assignment changes
- Integrate with existing notification system

### 4. API Endpoints
- `@activities` endpoint for GET/POST operations
- Permissions: 
  - All users can add comments
  - Users can edit/delete own comments
  - System activities are read-only

## Frontend Implementation

### 1. Activity Stream Component
- Location: `frontend/src/components/IssueActivities/IssueActivities.jsx`
- Display combined timeline of all activities
- Different styling for comments vs system activities
- Show user avatars/portraits

### 2. Comment Form Component
- Simple textarea at bottom of activity stream
- Submit button with loading state
- Clear after successful submission

### 3. Comment Actions
- Edit button (for own comments)
- Delete button (for own comments)
- Inline edit mode with save/cancel

### 4. Integration with IssueView
- Add Activities section below issue details
- Update in real-time after actions
- Show activity count in issue list views

## UI/UX Design

### Activity Stream Layout
```
[Issue Details]
---
Activities & Comments (12)
---
┌─────────────────────────────────────┐
│ 🔄 Status changed to "In Progress"  │
│ admin • Jan 26, 2024 3:30 PM        │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ 💬 "I checked and the AC unit..."   │
│ john_doe • Jan 26, 2024 3:35 PM     │
│ [Edit] [Delete]                     │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ 👤 Assigned to maintenance_staff    │
│ director • Jan 26, 2024 3:40 PM     │
└─────────────────────────────────────┘

[Add a comment...]
[Submit]
```

## Implementation Steps

1. **Backend Schema Updates** (30 min)
   - Update Issue content type XML
   - Add fields and migration

2. **Activity Management Module** (1 hour)
   - Core functions for CRUD operations
   - Transaction handling
   - Validation

3. **Event Subscribers** (30 min)
   - Auto-logging of changes
   - Integration with notifications

4. **API Endpoints** (30 min)
   - RESTful activities endpoint
   - Permission checks

5. **Frontend Components** (1.5 hours)
   - Activity stream display
   - Comment form
   - Edit/delete functionality

6. **Integration & Testing** (30 min)
   - Connect to IssueView
   - Test concurrent updates
   - Verify notifications

Total estimated time: 4.5 hours

## Future Enhancements (Not in initial scope)
- @mentions in comments
- Rich text formatting
- File attachments
- Comment reactions
- Activity filtering
- Unsubscribe from notifications
- Bulk operations
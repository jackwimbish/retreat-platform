# Retreat Experience Platform

A specialized platform for managing long-duration bootcamps, retreats, and residential events. Built on Plone 6.1 with a custom Volto frontend.

## 🎯 Project Overview

This platform transforms the enterprise-grade Plone CMS into a user-friendly system designed specifically for retreat and bootcamp management. It serves as a central hub for communication, scheduling, community building, and facility management.

### Key Features (Planned)
- **Issue Tracking System** - Report and manage facility issues
- **Participant Directory** - Searchable profiles with skills and team information
- **Resource Booking** - Calendar-based reservation system for shared resources
- **Real-Time Notifications** - Live updates for admins and participants
- **Analytics Dashboard** - Key metrics and engagement tracking
- **Calendar Integration** - Sync with external services like Google Calendar

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18.x (LTS recommended)
- Yarn package manager

### Running the Development Environment

1. **Start the Plone backend** (if not already running):
   ```bash
   # The backend should be running at http://localhost:8080
   ```

2. **Start the Volto frontend**:
   ```bash
   cd frontend
   yarn install
   yarn start
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8080

## 📁 Project Structure

```
my-retreat-platform/
├── frontend/               # Volto frontend (React-based)
│   ├── src/
│   │   └── customizations/ # Custom components and overrides
│   └── ...
├── retreat_platform_overview.md  # Detailed project specification
├── status.md              # Current development status
└── README.md             # This file
```

## 🛠️ Development

### Customizing Volto

Customizations are placed in `frontend/src/customizations/` following Volto's shadowing pattern. Current customizations include:

- **Header** - Custom header with retreat platform branding
- **Homepage** - Welcome banner for the retreat experience platform

### Making Changes

1. Edit files in the `frontend/src/customizations/` directory
2. The development server will automatically reload
3. Test your changes at http://localhost:3000

## 📚 Documentation

- [Project Overview](retreat_platform_overview.md) - Detailed project vision and requirements
- [Development Status](status.md) - Current progress and setup notes
- [Volto Documentation](https://6.docs.plone.org/volto/)
- [Plone Documentation](https://6.docs.plone.org/)

## 🤝 Contributing

This is a specialized platform for retreat management. Contributions should align with the project's goal of creating an intuitive, efficient system for managing residential events.


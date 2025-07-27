# Project Overview: The Retreat Experience Platform

## 1. High-Level Vision

To transform a powerful, enterprise-grade content management system (Plone 6.1) into a specialized, user-friendly platform for managing the complete experience of long-duration bootcamps, retreats, and other temporary residential events. The platform will serve as a central hub for communication, scheduling, community building, and facility management, enhancing the experience for both participants and the administrative team.

## 2. The Foundation: Plone 6.1

We are building upon Plone 6.1, a modern, API-first platform with a React-based frontend (Volto). While modern on the surface, its backend is a direct evolution of a 20-year-old legacy codebase (Zope), providing a robust, secure, and battle-tested foundation for content and workflow management.

This project's goal is not to migrate a legacy system, but to **extend a partially modernized one**, leveraging its powerful, deeply-rooted business logic to build new, high-value capabilities that don't exist out of the box.

## 3. Target User & Scenario

Our target user is a **small administrative team** responsible for managing a residential bootcamp or retreat that lasts from one week to two months.

- **Administrators** are responsible for the smooth operation of the facility (e.g., cleanliness, supplies, maintenance) and the coordination of the event's schedule and activities.
- **Participants** are the attendees of the event who need access to information, a way to connect with the community, and a channel to report issues.

## 4. The Core Problem & Our Solution

Managing a temporary, high-intensity community event involves constant communication and logistical challenges. Information is often scattered across emails, chat apps, and spreadsheets. Facility issues can disrupt the participant experience if not addressed quickly.

Our platform will solve this by providing a **single, unified hub** that streamlines these processes, fostering a more organized, responsive, and engaging environment for everyone involved.

## 5. Key Features to Be Implemented

We will build the following six new features on top of the Plone 6.1 foundation:

1. **Full Issue-Tracking System:** A dedicated system for participants to report facility issues (e.g., "The coffee station is empty," "Projector in Room B is not working"). Admins will manage these issues through a dedicated queue with statuses like `New`, `In Progress`, and `Resolved`.

2. **Participant Directory:** A directory of all attendees and camp staff to foster community.

3. **Resource Booking System:** A calendar-based system for reserving shared facility resources, such as meeting rooms, lab equipment, or vehicles, preventing scheduling conflicts.

4. **SSO Integration:** Sign in with your Google account or other common SSO providers.

5. **Email Notifications:** A notification system to alert admins and participants of new issue reports.

6. **Alert System:** Send e-mail alerts and show alerts on the home page for emergencies or sudden events.

## 6. Measures of Success

The project will be considered a success upon the successful implementation and integration of all six key features into a cohesive, functional platform. The final application should provide a clear and demonstrable improvement in the ability to manage a long-duration retreat compared to using disconnected, non-specialized tools.

# Legacy Frontend: AI Support Desk

The `frontend/` directory contains a complete ticket management SPA ("AI Support Desk") built with Vanilla JavaScript and Vite. This is **not** part of the Insight Monitor product.

## Relationship

This was a predecessor or reference implementation for a different product concept (AI-enhanced support ticket system). It is kept in the repository as a code reference only.

## Tech stack

- Vanilla JavaScript (no framework)
- Vite 5.x as bundler
- Bootstrap 5.3 for styling
- Hash-based SPA routing
- Token-based authentication (localStorage)

## Structure

```
frontend/
├── src/
│   ├── main.js                  # Entry point
│   ├── router.js                # Hash-based SPA router with auth guards
│   ├── components/
│   │   ├── layout.js            # Sidebar navigation layout
│   │   └── alert.js             # Toast notification system
│   ├── pages/
│   │   ├── login.js             # Login form
│   │   ├── register.js          # Registration form
│   │   ├── dashboard.js         # Stats cards, recent tickets
│   │   ├── tickets.js           # Filterable/sortable ticket list
│   │   ├── ticket-detail.js     # Ticket detail with comments
│   │   └── create-ticket.js     # Create/edit ticket form
│   ├── services/
│   │   ├── api.js               # Fetch wrapper with Bearer token
│   │   ├── auth.service.js      # Login/register/logout
│   │   ├── ticket.service.js    # Ticket CRUD + AI classify/suggest
│   │   └── comment.service.js   # Comment CRUD
│   └── styles/
│       └── main.css             # Custom CSS (228 lines)
```

## Status

Unmaintained. Not part of the MVP build pipeline (`npm run dev` does not include it). Do not use as reference for current frontend architecture.

# SweetShop Dashboard Usage

## Summary (July 2025)

- All core dashboard features are implemented and tested: login, registration, session management, sweets listing, purchase flow, and role-based access.
- Only verified users can log in and access dashboard features; unverified users are blocked.
- Sweets are grouped by category, searchable, and show out-of-stock status with clear visual cues for customers.
- Admin UI supports CRUD for sweets, user management, and stock reporting.
- Session persistence and error handling are robust.
- All major backend and frontend tests pass.

### Pending UI Tasks

#### Admin Side
- Bulk user actions and advanced role management
- Inventory analytics dashboard
- Exportable reports (CSV/PDF)
- Audit log/history UI

#### Customer Side
- Order history and tracking
- Profile editing (address, password)
- Enhanced sweet filtering (by price, rating)
- Mobile UI polish

## Latest Update (July 2025)
- Only verified users (`is_verified: true`) can log in and access the dashboard.
- Unverified users are blocked and shown an error message.

## Dashboard Sweets Display

The dashboard fetches sweets from the backend API at `/api/sweets` and displays them grouped by category. Each sweet is shown in a card with its name, description, price, and image.

### How Images Are Mapped
- The frontend tries to use `sweet.image` if provided by the API.
- If not, it auto-generates an image path using the sweet name: `/backend/sweet_images/{sweet_name}.jpg` (spaces replaced by underscores, lowercase).
- Example: `Kaju Katli` → `/backend/sweet_images/kaju_katli.jpg`

### Troubleshooting "Failed to load sweets"
- Make sure the backend is running and accessible at `/api/sweets`.
- The API must return a JSON object with an `items` array, each item having at least `name`, `description`, `price`, and `category.name`.
- If images do not load, check that the image files exist in `backend/sweet_images/` and match the sweet names (lowercase, underscores).
- If you see "Failed to load sweets", check your browser console for network errors and verify the backend API is reachable.

### Example API Response
```
{
  "items": [
    {
      "id": 1,
      "name": "Kaju Katli",
      "description": "Premium cashew fudge made with pure ghee and silver leaf",
      "price": 450.00,
      "category": { "id": 1, "name": "Dry Fruits Sweets" }
    },
    ...
  ]
}
```
# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

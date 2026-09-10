# PayCore Frontend

A professional, orange-and-white fintech wallet frontend for the **PAY_CORE** FastAPI backend.
Built with React + Vite + React Router + Axios. JavaScript only, no TypeScript.

## Quick start

```bash
# 1. Install dependencies
npm install

# 2. (Optional) configure the API URL — defaults work in development
cp .env.example .env

# 3. Start the backend first (from the repository root)
uvicorn main:app --reload --port 8000

# 4. Start the frontend (from the paycore/ folder)
npm run dev
```

Then open http://localhost:5173.

## How it talks to the backend

- All API calls go through `src/api/api.js` (a configured Axios instance)
  and use an `/api/...` prefix (e.g. `/api/users/me`).
- In development, Vite proxies `/api/*` to `http://127.0.0.1:8000`, stripping
  the prefix (see `vite.config.js`). The frontend and backend share one
  origin, so the backend's **HttpOnly JWT cookies** are attached
  automatically — the token is never readable by JavaScript, which protects
  it from XSS.
- The `/api` prefix avoids a collision: refreshing the client-side
  `/transactions` PAGE would otherwise be proxied to the backend too.
- Transfers send a unique `Idempotency-Key` header so a double-click can
  never create two transfers (handled by the backend's Redis idempotency).

## Project structure

```
src/
├── api/            # One Axios instance + one file per backend feature
├── components/     # Reusable UI pieces (sidebar, cards, transaction rows...)
├── context/        # AuthContext — "who is logged in?" for the whole app
├── pages/          # One file per route
├── utils/          # formatCurrency (Rs.), formatDate
├── App.jsx         # Routes + layout
└── main.jsx        # Entry point
```

## Backend endpoints used

| Feature        | Endpoint                          |
| -------------- | --------------------------------- |
| Register       | `POST /auth/register`             |
| Login          | `POST /auth/login` (sets cookies) |
| Logout         | `POST /auth/logout`               |
| Session check  | `GET /users/me`                   |
| Balance        | `GET /wallets/me`                 |
| Send money     | `POST /transfers/` + `Idempotency-Key` header |
| History        | `GET /transactions/?page=&page_size=` |

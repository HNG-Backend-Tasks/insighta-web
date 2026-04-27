# Insighta Labs+ — Web Portal

A simple, functional web portal for non-technical users to access the Insighta Labs+ platform. Built with FastAPI and Jinja2 templates. Uses the same backend API as the CLI.

## Pages

| Page | Path | Description |
|---|---|---|
| Login | `/login` | GitHub OAuth login |
| Dashboard | `/dashboard` | Basic metrics — total profiles, gender breakdown |
| Profiles | `/profiles` | Filterable, paginated profiles list |
| Profile detail | `/profiles/{id}` | Full profile view with delete (admin only) |
| Search | `/search` | Natural language search |
| Account | `/account` | Logged-in user info and role |

## Authentication Flow

```
1. User visits /login, clicks "Continue with GitHub"
2. Browser redirects to /auth/github on the portal
3. Portal generates state, stores in server-side session, redirects to GitHub
4. GitHub authenticates user, redirects to /auth/github/callback
5. Portal validates state (CSRF protection)
6. Portal forwards code to backend: GET /auth/github/callback
7. Backend exchanges code with GitHub, creates/updates user, returns tokens
8. Portal sets tokens as HTTP-only cookies:
   - access_token (httponly=True, samesite=lax)
   - refresh_token (httponly=True, samesite=lax)
9. User is redirected to /dashboard
```

Tokens are never accessible via JavaScript. The browser sends them automatically with every request to the portal.

## Security

**HTTP-only cookies:** Both access and refresh tokens are stored as HTTP-only cookies. JavaScript running in the browser cannot read them — protecting against XSS attacks.

**CSRF protection:** State parameter validation during OAuth prevents CSRF attacks during login. Forms that perform state-changing actions (e.g. delete profile) `.The token is validated server-side before the action is executed.

**Server-side API calls:** The portal never exposes the backend API to the browser. All calls to `/api/*` are made server-side by the portal's Python backend, which reads the access token from the cookie and forwards it as a Bearer token. The browser only receives rendered HTML.

## Role Enforcement

The portal reflects the user's role from the backend:

- **Admin** users see the "New Profile" button and "Delete Profile" button
- **Analyst** users see neither — the buttons are not rendered
- All API calls are still enforced server-side by the backend regardless of what the UI shows

## Local Setup

**Requirements:** Python 3.12+, [uv](https://github.com/astral-sh/uv)

```bash
git clone https://github.com/HNG-Backend-Tasks/insighta-web
cd insighta-web
uv sync
```

Create `.env`:
```env
BACKEND_URL=http://localhost:8000
SECRET_KEY=your-secret-key-here
GITHUB_CLIENT_ID=your_web_github_client_id
GITHUB_CLIENT_SECRET=your_web_github_client_secret
FRONTEND_URL=http://localhost:3000
```

Run the portal:
```bash
uv run uvicorn app.main:app --reload --port 3000
```

Make sure the backend is also running on port 8000.

Visit `http://localhost:3000`.

## GitHub OAuth App Setup

Register an OAuth app at GitHub → Settings → Developer settings → OAuth Apps:

| Field | Value |
|---|---|
| Homepage URL | `http://localhost:3000` (or your deployed URL) |
| Authorization callback URL | `http://localhost:3000/auth/github/callback` |

## Running Tests

```bash
uv run pytest tests/ -v
```

## Project Structure

```
app/
├── config.py              ← settings from .env
├── dependencies.py        ← get_portal_context (auth + backend client)
├── http.py                ← BackendClient (server-side API caller)
├── main.py                ← FastAPI app, middleware, exception handlers
├── templates_config.py    ← shared Jinja2Templates instance
├── routes/
│   ├── auth.py            ← login, GitHub OAuth, logout
│   └── profiles.py        ← dashboard, list, detail, search, account
└── templates/
    ├── base.html           ← layout, nav, Pico CSS
    ├── login.html
    ├── dashboard.html
    ├── account.html
    └── profiles/
        ├── list.html
        ├── detail.html
        └── search.html
static/
└── style.css
tests/
└── test_routes.py
```

## Design

The portal uses [Pico CSS](https://picocss.com) — a classless CSS framework. Semantic HTML elements (`<nav>`, `<table>`, `<article>`, `<button>`) are styled automatically. No utility class names needed in templates.
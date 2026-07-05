# Frontend

React + Vite client for the kiwi portfolio app.

## Local development

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

## Environment variables

- `VITE_API_BASE_URL`: backend API base URL, usually `http://localhost:5000`
- `VITE_COGNITO_AUTHORITY`: required Cognito issuer URL
- `VITE_COGNITO_CLIENT_ID`: required Cognito app client ID
- `VITE_COGNITO_REDIRECT_URI`: allowed callback URL
- `VITE_COGNITO_POST_LOGOUT_REDIRECT_URI`: allowed sign-out URL
- `VITE_COGNITO_SCOPE`: OIDC scopes, default `openid email profile`
- `VITE_ENABLE_DEBUG_TOOLS`: optional debug logs and sanitized API error snapshots

## Quality checks

```powershell
npm run lint
npm run build
```

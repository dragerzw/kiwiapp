# kiwi

Full-stack portfolio management app with a Flask API and a React frontend.

## Project structure

- `app/`: Flask application, models, routes, auth, and services
- `frontend/`: Vite + React client for Cognito login and portfolio workflows
- `tests/`: backend test suite
- `run.py`: local Flask entrypoint

## Backend setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Create a root `.env` file from `.env.example` and fill in the values you need.
4. Start the API:

```powershell
python run.py
```

The backend defaults to `http://localhost:5000`.

## Frontend setup

1. Change into the frontend directory:

```powershell
Set-Location frontend
```

2. Install dependencies:

```powershell
npm install
```

3. Create `frontend/.env` from `frontend/.env.example`.
4. Start the frontend:

```powershell
npm run dev
```

The frontend defaults to `http://localhost:5173`.

## Cognito configuration

The SPA uses the OIDC authorization code flow through Cognito.

Set these frontend variables:

- `VITE_COGNITO_AUTHORITY`: Cognito issuer URL, for example `https://cognito-idp.us-east-1.amazonaws.com/<user-pool-id>`
- `VITE_COGNITO_CLIENT_ID`: Cognito app client ID
- `VITE_COGNITO_DOMAIN`: optional Cognito Hosted UI domain, for example `https://your-domain.auth.us-east-1.amazoncognito.com`
- `VITE_COGNITO_REDIRECT_URI`: callback URL registered in the app client
- `VITE_COGNITO_POST_LOGOUT_REDIRECT_URI`: allowed sign-out URL registered in the app client
- `VITE_COGNITO_SCOPE`: usually `openid email profile`

Set these backend variables:

- `COGNITO_USER_POOL_ID`
- `COGNITO_APP_CLIENT_ID`
- `COGNITO_REGION`

If you plan to place trades with live quotes, also provide `ALPHA_VANTAGE_API_KEY`.

## Verification

Backend:

```powershell
python -m pytest
```

Frontend:

```powershell
Set-Location frontend
npm run lint
npm run build
```

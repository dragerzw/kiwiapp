# ──────────────────────────────────────────────
# KiwiApp React SPA — Build Stage
# Produces static assets in /app/dist for S3/CloudFront deployment.
# Also serves as a standalone Nginx container for local testing.
# ──────────────────────────────────────────────

# ── Stage 1: Build ──
FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

# Build-time env vars must be passed via --build-arg → ARG → ENV
ARG VITE_API_BASE_URL
ARG VITE_COGNITO_AUTHORITY
ARG VITE_COGNITO_CLIENT_ID
ARG VITE_COGNITO_REDIRECT_URI
ARG VITE_COGNITO_POST_LOGOUT_REDIRECT_URI
ARG VITE_COGNITO_SCOPE="openid email profile"
ARG VITE_COGNITO_DOMAIN

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL \
    VITE_COGNITO_AUTHORITY=$VITE_COGNITO_AUTHORITY \
    VITE_COGNITO_CLIENT_ID=$VITE_COGNITO_CLIENT_ID \
    VITE_COGNITO_REDIRECT_URI=$VITE_COGNITO_REDIRECT_URI \
    VITE_COGNITO_POST_LOGOUT_REDIRECT_URI=$VITE_COGNITO_POST_LOGOUT_REDIRECT_URI \
    VITE_COGNITO_SCOPE=$VITE_COGNITO_SCOPE \
    VITE_COGNITO_DOMAIN=$VITE_COGNITO_DOMAIN

RUN npm run build

# ── Stage 2: Serve (for local testing / non-S3 deployments) ──
FROM nginx:alpine AS serve

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost/ || exit 1

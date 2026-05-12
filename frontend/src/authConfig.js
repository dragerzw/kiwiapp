import { WebStorageStateStore } from "oidc-client-ts";

const DEFAULT_SCOPE = "openid email profile";
const DEFAULT_REDIRECT_URI = `${globalThis.location.origin}/`;
const DEFAULT_POST_LOGOUT_REDIRECT_URI = `${globalThis.location.origin}/signed-out`;

export const LOGOUT_MARKER_KEY = "kiwi:pause-auto-signin";

const requireEnv = (name) => {
  const value = import.meta.env[name];
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
};

const authority = requireEnv("VITE_COGNITO_AUTHORITY");
const clientId = requireEnv("VITE_COGNITO_CLIENT_ID");
const rawRedirectUri = import.meta.env.VITE_COGNITO_REDIRECT_URI || DEFAULT_REDIRECT_URI;
const redirectUri = rawRedirectUri.endsWith("/") ? rawRedirectUri : `${rawRedirectUri}/`;
const postLogoutRedirectUri =
  import.meta.env.VITE_COGNITO_POST_LOGOUT_REDIRECT_URI || DEFAULT_POST_LOGOUT_REDIRECT_URI;
const cognitoDomain = import.meta.env.VITE_COGNITO_DOMAIN?.replace(/\/+$/, "") || null;

export const SIGNED_OUT_PATH = new URL(
  postLogoutRedirectUri,
  globalThis.location.origin,
).pathname;
export const cognitoLogoutUrl = cognitoDomain
  ? `${cognitoDomain}/logout?client_id=${encodeURIComponent(clientId)}&logout_uri=${encodeURIComponent(postLogoutRedirectUri)}`
  : null;

export const getApiToken = (user) => user?.id_token || user?.access_token || null;

export const clearStoredAuthState = () => {
  const managedKeyPrefixes = [
    "oidc.",
    `oidc.user:${authority}:${clientId}`,
    `CognitoIdentityServiceProvider.${clientId}`,
  ];

  for (const storage of [globalThis.localStorage, globalThis.sessionStorage]) {
    const keysToRemove = [];
    for (let index = 0; index < storage.length; index += 1) {
      const key = storage.key(index);
      if (!key) {
        continue;
      }
      if (managedKeyPrefixes.some((prefix) => key.startsWith(prefix))) {
        keysToRemove.push(key);
      }
    }

    for (const key of keysToRemove) {
      storage.removeItem(key);
    }
  }
};

export const oidcConfig = {
  authority,
  client_id: clientId,
  redirect_uri: redirectUri,
  post_logout_redirect_uri: postLogoutRedirectUri,
  response_type: "code",
  scope: import.meta.env.VITE_COGNITO_SCOPE || DEFAULT_SCOPE,
  automaticSilentRenew: true,
  revokeTokensOnSignout: true,
  loadUserInfo: true,
  userStore: new WebStorageStateStore({ store: globalThis.localStorage }),
  onSigninCallback: () => {
    globalThis.history.replaceState({}, document.title, globalThis.location.pathname + globalThis.location.hash);
  },
};

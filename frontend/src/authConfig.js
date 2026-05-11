import { WebStorageStateStore } from "oidc-client-ts";

const DEFAULT_AUTHORITY = "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_yv9SqsmAR";
const DEFAULT_CLIENT_ID = "59r7i820vi1ns03ts61tj7409c";
const DEFAULT_SCOPE = "openid email profile";
const DEFAULT_REDIRECT_URI = `${window.location.origin}/`;
const DEFAULT_POST_LOGOUT_REDIRECT_URI = `${window.location.origin}/signed-out`;

export const LOGOUT_MARKER_KEY = "kiwi:pause-auto-signin";

const authority = import.meta.env.VITE_COGNITO_AUTHORITY || DEFAULT_AUTHORITY;
const clientId = import.meta.env.VITE_COGNITO_CLIENT_ID || DEFAULT_CLIENT_ID;
const redirectUri = import.meta.env.VITE_COGNITO_REDIRECT_URI || DEFAULT_REDIRECT_URI;
const postLogoutRedirectUri =
  import.meta.env.VITE_COGNITO_POST_LOGOUT_REDIRECT_URI || DEFAULT_POST_LOGOUT_REDIRECT_URI;
const cognitoDomain = import.meta.env.VITE_COGNITO_DOMAIN?.replace(/\/+$/, "") || null;

export const SIGNED_OUT_PATH = new URL(
  postLogoutRedirectUri,
  window.location.origin,
).pathname;
export const cognitoLogoutUrl = cognitoDomain
  ? `${cognitoDomain}/logout?client_id=${encodeURIComponent(clientId)}&logout_uri=${encodeURIComponent(postLogoutRedirectUri)}`
  : null;

export const clearStoredAuthState = () => {
  const managedKeyPrefixes = [
    "oidc.",
    `oidc.user:${authority}:${clientId}`,
    `CognitoIdentityServiceProvider.${clientId}`,
  ];

  for (const storage of [window.localStorage, window.sessionStorage]) {
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
  userStore: new WebStorageStateStore({ store: window.localStorage }),
  onSigninCallback: () => {
    window.history.replaceState({}, document.title, window.location.pathname + window.location.hash);
  },
};

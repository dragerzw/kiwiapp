import PropTypes from 'prop-types';
import { useEffect, useState } from 'react';

const debugEnabled = import.meta.env.DEV || String(import.meta.env.VITE_ENABLE_DEBUG_TOOLS || '').toLowerCase() === 'true';
const debugQueryEnabled = new URLSearchParams(globalThis.location.search).has('kiwi_debug');

function tryParse(str) {
  try {
    return JSON.parse(str);
  } catch {
    return null;
  }
}

function redactOidcUser(oidcUser) {
  if (!oidcUser) {
    return null;
  }

  const redactToken = (value) => (value ? '[REDACTED]' : undefined);
  const user = oidcUser.user;

  return {
    ...oidcUser,
    access_token: redactToken(oidcUser.access_token),
    id_token: redactToken(oidcUser.id_token),
    refresh_token: redactToken(oidcUser.refresh_token),
    user: user
      ? {
          ...user,
          access_token: redactToken(user.access_token),
          id_token: redactToken(user.id_token),
          refresh_token: redactToken(user.refresh_token),
        }
      : user,
  };
}

export default function DebugOverlay({ auth }) {
  const [oidcUser, setOidcUser] = useState(null);
  const [lastApiError, setLastApiError] = useState(null);

  useEffect(() => {
    if (!debugEnabled || !debugQueryEnabled) {
      return;
    }

    const refresh = () => {
      const keys = Object.keys(localStorage).filter((k) => k.startsWith('oidc.user'));
      if (keys.length) {
        setOidcUser(tryParse(localStorage.getItem(keys[0])));
      } else {
        setOidcUser(null);
      }
      setLastApiError(globalThis.__kiwi_last_api_error ?? null);
    };

    refresh();
    const id = setInterval(refresh, 1000);
    return () => clearInterval(id);
  }, []);

  if (!debugEnabled || !debugQueryEnabled) return null;

  return (
    <div style={{ position: 'fixed', right: 12, bottom: 12, zIndex: 9999, width: 420, maxHeight: '60vh', overflow: 'auto', background: 'rgba(255,255,255,0.98)', border: '1px solid #e2e8f0', borderRadius: 8, padding: 12, boxShadow: '0 6px 20px rgba(0,0,0,0.08)' }}>
      <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 8 }}>Kiwi Debug Overlay</div>
      <div style={{ fontSize: 12, marginBottom: 8 }}>
        <strong>Authenticated:</strong> {String(auth?.isAuthenticated)}<br />
        <strong>Active Navigator:</strong> {auth?.activeNavigator || 'N/A'}
      </div>
      <div style={{ fontSize: 12, marginBottom: 8 }}>
        <strong>OIDC User (localStorage):</strong>
        <pre style={{ whiteSpace: 'pre-wrap', fontSize: 11, marginTop: 6 }}>{JSON.stringify(redactOidcUser(oidcUser), null, 2)}</pre>
      </div>
      <div style={{ fontSize: 12 }}>
        <strong>Last API Error:</strong>
        <pre style={{ whiteSpace: 'pre-wrap', fontSize: 11, marginTop: 6 }}>{JSON.stringify(lastApiError, null, 2)}</pre>
      </div>
    </div>
  );
}

DebugOverlay.propTypes = {
  auth: PropTypes.shape({
    isAuthenticated: PropTypes.bool,
    activeNavigator: PropTypes.string,
  }),
};

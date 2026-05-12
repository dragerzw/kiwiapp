import React, { useEffect, useState } from 'react';

function tryParse(str) {
  try {
    return JSON.parse(str);
  } catch (e) {
    return null;
  }
}

export default function DebugOverlay({ auth }) {
  const [oidcUser, setOidcUser] = useState(null);
  const [lastApiError, setLastApiError] = useState(null);

  useEffect(() => {
    const refresh = () => {
      const keys = Object.keys(localStorage).filter((k) => k.startsWith('oidc.user'));
      if (keys.length) {
        setOidcUser(tryParse(localStorage.getItem(keys[0])));
      } else {
        setOidcUser(null);
      }
      setLastApiError(window.__kiwi_last_api_error ?? null);
    };

    refresh();
    const id = setInterval(refresh, 1000);
    return () => clearInterval(id);
  }, []);

  if (!new URLSearchParams(window.location.search).get('kiwi_debug')) return null;

  return (
    <div style={{position: 'fixed', right: 12, bottom: 12, zIndex: 9999, width: 420, maxHeight: '60vh', overflow: 'auto', background: 'rgba(255,255,255,0.98)', border: '1px solid #e2e8f0', borderRadius: 8, padding: 12, boxShadow: '0 6px 20px rgba(0,0,0,0.08)'}}>
      <div style={{fontSize: 12, fontWeight: 700, marginBottom: 8}}>Kiwi Debug Overlay</div>
      <div style={{fontSize: 12, marginBottom: 8}}>
        <strong>Authenticated:</strong> {String(auth?.isAuthenticated)}<br/>
        <strong>Active Navigator:</strong> {auth?.activeNavigator || 'N/A'}
      </div>
      <div style={{fontSize: 12, marginBottom: 8}}>
        <strong>OIDC User (localStorage):</strong>
        <pre style={{whiteSpace: 'pre-wrap', fontSize: 11, marginTop: 6}}>{JSON.stringify(oidcUser, null, 2)}</pre>
      </div>
      <div style={{fontSize: 12}}>
        <strong>Last API Error:</strong>
        <pre style={{whiteSpace: 'pre-wrap', fontSize: 11, marginTop: 6}}>{JSON.stringify(lastApiError, null, 2)}</pre>
      </div>
    </div>
  );
}

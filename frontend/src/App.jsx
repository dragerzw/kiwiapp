import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "./AuthContext";
import Dashboard from "./components/Dashboard";
import LoginPage from "./components/LoginPage";
import Navbar from "./components/Navbar";
import DebugOverlay from "./components/DebugOverlay";
import AdminDashboard from "./components/AdminDashboard";
import { clearStoredAuthState, LOGOUT_MARKER_KEY, cognitoLogoutUrl, SIGNED_OUT_PATH } from "./authConfig";

function App() {
  const auth = useAuth();
  const [logoutError, setLogoutError] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();
  const [showAdminView, setShowAdminView] = useState(false);
  const [wasSignedOut, setWasSignedOut] = useState(false);

  const hasAuthToken = Boolean(auth?.token);

  useEffect(() => {
    // If we are authenticated, clear any sign-out state/markers
    if (auth.isAuthenticated) {
      setWasSignedOut(false);
      sessionStorage.removeItem(LOGOUT_MARKER_KEY);
    } else {
      // If NOT authenticated, check if we just landed on the signed-out path
      // or if the session marker exists.
      const isSignedOutPath = location.pathname === SIGNED_OUT_PATH;
      const hasMarker = sessionStorage.getItem(LOGOUT_MARKER_KEY) === "true";

      if (isSignedOutPath || hasMarker) {
        setWasSignedOut(true);
        // Ensure the marker is set if we hit the path but don't have it yet
        if (isSignedOutPath && !hasMarker) {
          sessionStorage.setItem(LOGOUT_MARKER_KEY, "true");
        }
      }
    }

    // Always keep the URL clean for this SPA
    if (location.pathname !== "/" && !auth.isAuthenticated && location.pathname !== SIGNED_OUT_PATH) {
      navigate("/", { replace: true });
    }
  }, [location.pathname, navigate, auth.isAuthenticated]);

  const handleSignOut = async () => {
    try {
      setLogoutError(null);
      await auth.removeUser();
      clearStoredAuthState();
      sessionStorage.setItem(LOGOUT_MARKER_KEY, "true");
      if (cognitoLogoutUrl) {
        window.location.href = cognitoLogoutUrl;
      }
    } catch (error) {
      setLogoutError(error instanceof Error ? error.message : "Unable to complete logout.");
    }
  };

  if (!auth || auth.isLoading) {
    return (
      <div className="auth-shell">
        <div className="auth-status-card">
          <p className="auth-status-label">Loading security session...</p>
        </div>
      </div>
    );
  }

  if (auth.isAuthenticated && hasAuthToken) {
    const claims = auth.user?.profile || {};
    let groups = claims["cognito:groups"] || claims["groups"] || [];
    if (typeof groups === 'string') groups = [groups];
    
    const adminGroupNames = ['Admins', 'Admin', 'Administrators', 'Administrator'];
    const isAdmin = groups.some(g => adminGroupNames.includes(g));

    return (
      <>
        <Navbar 
          onSignOut={handleSignOut} 
          isAdmin={isAdmin}
          showAdminView={showAdminView}
          onToggleAdmin={() => setShowAdminView(!showAdminView)}
        />
        {showAdminView && isAdmin ? (
          <AdminDashboard token={auth.token} />
        ) : (
          <Dashboard />
        )}
        <DebugOverlay auth={auth} />
      </>
    );
  }

  return (
    <LoginPage
      errorMessage={logoutError || null}
      isSignedOut={wasSignedOut}
    />
  );
}

export default App;

import PropTypes from "prop-types";
import { useAuth } from "../AuthContext";

function LoginPage(props) {
  const { errorMessage = null, isSignedOut = false } = props;
  const auth = useAuth();

  const redirectingToLogin = auth?.activeNavigator === "signinRedirect";

  return (
    <div className="lp-root">
      <div className="lp-hero">
        <div className="lp-hero-content">
          <div className="lp-logo">
            <span className="lp-logo-badge" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="20" x2="18" y2="10"></line>
                <line x1="12" y1="20" x2="12" y2="4"></line>
                <line x1="6" y1="20" x2="6" y2="14"></line>
              </svg>
            </span>
            <span className="lp-logo-text">Kiwi</span>
          </div>
          <h1 className="lp-headline">Institutional-Grade Portfolio Management.</h1>
          <p className="lp-subline">
            Advanced analytics, secure execution, and comprehensive asset tracking.
          </p>
          <ul className="lp-features">
            <li><span className="lp-check">Visibility</span> Real-time visibility into all active holdings and market positions.</li>
            <li><span className="lp-check">Trading</span> Seamless execution of market orders with zero latency.</li>
            <li><span className="lp-check">Security</span> Bank-level encryption and secure role-based access control.</li>
          </ul>
        </div>
      </div>

      <div className="lp-panel">
        <div className="lp-card">
          <div className="lp-card-logo" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="18" y1="20" x2="18" y2="10"></line>
              <line x1="12" y1="20" x2="12" y2="4"></line>
              <line x1="6" y1="20" x2="6" y2="14"></line>
            </svg>
          </div>
          <h2 className="lp-card-title">{isSignedOut ? "Signed Out" : "Secure Authentication"}</h2>
          <p className="lp-card-sub">
            {isSignedOut
              ? "Your session has been securely terminated. Sign in again to access your portfolio."
              : "Securely authenticate to access your portfolio dashboard."}
          </p>
          <p className="lp-card-note">
            Access permissions are securely managed via role-based authentication.
          </p>

          {errorMessage ? (
            <div className="status-banner status-banner-error" role="alert" style={{ marginBottom: "1.5rem" }}>
              {errorMessage}
            </div>
          ) : null}

          <button
            className="lp-signin-btn"
            disabled={redirectingToLogin}
            onClick={() => auth?.signinRedirect()}
            type="button"
          >
            {redirectingToLogin ? "Redirecting..." : "Sign in with Kiwi"}
          </button>
        </div>
      </div>
    </div>
  );
}

LoginPage.propTypes = {
  errorMessage: PropTypes.string,
  isSignedOut: PropTypes.bool,
};

export default LoginPage;

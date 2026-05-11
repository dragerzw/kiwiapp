import PropTypes from "prop-types";
import { useAuth } from "react-oidc-context";

function LoginPage(props) {
  const { errorMessage = null, isSignedOut = false, onSignIn } = props;
  const auth = useAuth();

  const redirectingToLogin = auth.activeNavigator === "signinRedirect";

  return (
    <div className="lp-root">
      <div className="lp-hero">
        <div className="lp-hero-content">
          <div className="lp-logo">
            <span className="lp-logo-icon">💼</span>
            <span className="lp-logo-text">kiwi</span>
          </div>
          <h1 className="lp-headline">Manage Your Investments with Confidence</h1>
          <p className="lp-subline">
            Keep all your portfolios in one place. Track your holdings, execute trades, and see exactly where your money goes—every single transaction.
          </p>
          <ul className="lp-features">
            <li><span className="lp-check">✓</span> Bank-level security for your peace of mind</li>
            <li><span className="lp-check">✓</span> See your portfolio performance anytime, anywhere</li>
            <li><span className="lp-check">✓</span> Full transaction history—nothing gets lost</li>
          </ul>
        </div>
      </div>

      <div className="lp-panel">
        <div className="lp-card">
          <div className="lp-card-logo">💼</div>
          <h2 className="lp-card-title">{isSignedOut ? "Signed Out" : "Portal Access"}</h2>
          <p className="lp-card-sub">
            {isSignedOut
              ? "Your local session has been cleared. Sign in again when you are ready."
              : "Authenticate with Cognito to manage your kiwi portfolios."}
          </p>

          {errorMessage ? (
            <div className="status-banner status-banner-error" role="alert">
              {errorMessage}
            </div>
          ) : null}

          <button
            className="lp-signin-btn"
            disabled={redirectingToLogin}
            onClick={onSignIn}
            type="button"
          >
            {redirectingToLogin ? "Redirecting..." : "Continue with Cognito"}
          </button>
        </div>
      </div>
    </div>
  );
}

LoginPage.propTypes = {
  errorMessage: PropTypes.string,
  isSignedOut: PropTypes.bool,
  onSignIn: PropTypes.func.isRequired,
};

export default LoginPage;

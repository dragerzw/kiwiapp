import { useAuth } from "react-oidc-context";
import { Link } from "react-router-dom";

export default function Navbar({ onSignOut }) {
  const { isAuthenticated, user } = useAuth();

  return (
    <nav className="navbar">
      <Link to="/" className="nav-brand">
        <span role="img" aria-label="chart">📈</span> Kiwi
      </Link>
      {isAuthenticated && (
        <div className="nav-user">
          <span className="nav-user-label">
            {user?.profile?.name || user?.profile?.email}
          </span>
          <button className="btn btn-outline" onClick={onSignOut} type="button">
            Sign Out
          </button>
        </div>
      )}
    </nav>
  );
}

import { useAuth } from "../AuthContext";
import { Link } from "react-router-dom";

export default function Navbar({ onSignOut, isAdmin, showAdminView, onToggleAdmin }) {
  const { isAuthenticated, user } = useAuth();

  return (
    <nav className="navbar">
      <Link to="/" className="nav-brand">
        <span className="nav-brand-mark">K</span>
        <span className="nav-brand-copy">
          <span className="nav-brand-name">Kiwi</span>
          <span className="nav-brand-meta">Portfolio workspace</span>
        </span>
      </Link>
      {isAuthenticated ? (
        <div className="nav-user">
          <div className="nav-user-copy">
            <span className="nav-user-kicker">Signed in as</span>
            <span className="nav-user-label">
              {user?.profile?.name || user?.profile?.email || user?.profile?.username}
            </span>
          </div>
          {isAdmin && (
            <button className="btn btn-outline margin-right-small" onClick={onToggleAdmin}>
              {showAdminView ? "User View" : "Admin View"}
            </button>
          )}
          <button className="btn btn-outline" onClick={onSignOut} type="button">
            Sign Out
          </button>
        </div>
      ) : null}
    </nav>
  );
}

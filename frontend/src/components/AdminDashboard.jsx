import { useState, useEffect } from "react";
import { api } from "../api";
import "./AdminDashboard.css";

export default function AdminDashboard({ token }) {
  const [users, setUsers] = useState([]);
  const [portfolios, setPortfolios] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      const [u, p] = await Promise.all([
        api.getUsers(token),
        api.getPortfolios(token)
      ]);
      setUsers(u);
      setPortfolios(p);
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <div className="admin-loading">Loading administrative data...</div>;
  }

  return (
    <div className="admin-dashboard">
      <header className="admin-header">
        <h1>Administrative Console</h1>
        <button className="btn btn-primary" onClick={fetchData}>Refresh Data</button>
      </header>

      {error && <div className="status-banner status-banner-error">{error}</div>}

      <div className="admin-grid">
        <section className="admin-section">
          <div className="section-header">
            <h2>User Management</h2>
            <span className="count-badge">{users.length} Users</span>
          </div>
          <div className="admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Name</th>
                  <th>Balance</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.username}>
                    <td className="font-mono">{u.username}</td>
                    <td>{u.firstname} {u.lastname}</td>
                    <td className="font-mono">${u.balance?.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="admin-section">
          <div className="section-header">
            <h2>System Portfolios</h2>
            <span className="count-badge">{portfolios.length} Portfolios</span>
          </div>
          <div className="admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Owner</th>
                  <th>Holdings</th>
                </tr>
              </thead>
              <tbody>
                {portfolios.map(p => (
                  <tr key={p.id}>
                    <td className="font-mono">{p.id}</td>
                    <td>{p.name}</td>
                    <td>{p.owner}</td>
                    <td>{p.investments_count || 0}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
}

import { useState, useEffect } from "react";
import { api } from "../api";
import "./AdminDashboard.css";

export default function AdminDashboard({ token }) {
  const [users, setUsers] = useState([]);
  const [portfolios, setPortfolios] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [processingId, setProcessingId] = useState(null);

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

  const handleDeleteUser = async (username) => {
    if (!window.confirm(`Are you sure you want to delete user "${username}"?`)) return;
    try {
      setProcessingId(username);
      await api.deleteUser(username, token);
      await fetchData();
    } catch (e) {
      setError(`Delete user failed: ${e.message}`);
    } finally {
      setProcessingId(null);
    }
  };

  const handleUpdateBalance = async (username, currentBalance) => {
    const newBalanceStr = window.prompt(`Update balance for ${username}:`, currentBalance);
    if (newBalanceStr === null) return;
    const newBalance = parseFloat(newBalanceStr);
    if (isNaN(newBalance)) return alert("Invalid amount");
    
    try {
      setProcessingId(username);
      await api.updateUserBalance({ username, new_balance: newBalance }, token);
      await fetchData();
    } catch (e) {
      setError(`Update balance failed: ${e.message}`);
    } finally {
      setProcessingId(null);
    }
  };

  const handleDeletePortfolio = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete portfolio "${name}"?`)) return;
    try {
      setProcessingId(id);
      await api.deletePortfolio(id, token);
      await fetchData();
    } catch (e) {
      setError(`Delete portfolio failed: ${e.message}`);
    } finally {
      setProcessingId(null);
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
                  <th>Balance</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.username}>
                    <td className="font-mono">{u.username}</td>
                    <td className="font-mono">${u.balance?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                    <td>
                      <div className="admin-actions">
                        <button 
                          className="btn btn-compact" 
                          onClick={() => handleUpdateBalance(u.username, u.balance)}
                          disabled={processingId === u.username}
                        >
                          Balance
                        </button>
                        <button 
                          className="btn btn-danger btn-compact" 
                          onClick={() => handleDeleteUser(u.username)}
                          disabled={processingId === u.username || u.username === 'admin'}
                        >
                          Delete
                        </button>
                      </div>
                    </td>
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
                  <th>Name</th>
                  <th>Owner</th>
                  <th>Holdings</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {portfolios.map(p => (
                  <tr key={p.id}>
                    <td>{p.name}</td>
                    <td>{p.owner}</td>
                    <td>{p.investments_count || 0}</td>
                    <td>
                      <button 
                        className="btn btn-danger btn-compact" 
                        onClick={() => handleDeletePortfolio(p.id, p.name)}
                        disabled={processingId === p.id}
                      >
                        Delete
                      </button>
                    </td>
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

import { useState, useEffect, useCallback } from "react";
import { api } from "../api";
import BaseModal from "./BaseModal";
import "./AdminDashboard.css";

export default function AdminDashboard({ token }) {
  const [users, setUsers] = useState([]);
  const [portfolios, setPortfolios] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [processingId, setProcessingId] = useState(null);

  // Modal states
  const [activeModal, setActiveModal] = useState(null); // 'deleteUser' | 'updateBalance' | 'deletePortfolio'
  const [modalData, setModalData] = useState(null);
  const [inputValue, setInputValue] = useState("");

  const fetchData = useCallback(async () => {
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
  }, [token]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const closeModals = () => {
    setActiveModal(null);
    setModalData(null);
    setInputValue("");
    setError(null);
  };

  const confirmDeleteUser = async () => {
    try {
      const username = modalData.username;
      setProcessingId(username);
      await api.deleteUser(username, token);
      closeModals();
      await fetchData();
    } catch (e) {
      setError(`Delete user failed: ${e.message}`);
    } finally {
      setProcessingId(null);
    }
  };

  const confirmUpdateBalance = async () => {
    const newBalance = parseFloat(inputValue);
    if (isNaN(newBalance)) return alert("Invalid amount");
    
    try {
      const username = modalData.username;
      setProcessingId(username);
      await api.updateUserBalance({ username, new_balance: newBalance }, token);
      closeModals();
      await fetchData();
    } catch (e) {
      setError(`Update balance failed: ${e.message}`);
    } finally {
      setProcessingId(null);
    }
  };

  const confirmDeletePortfolio = async () => {
    const holdingsCount = modalData?.investments_count || 0;
    if (holdingsCount > 0) {
      const noun = holdingsCount === 1 ? 'holding' : 'holdings';
      setError(`Cannot delete: this portfolio still has ${holdingsCount} active ${noun}. All positions must be sold before it can be deleted.`);
      return;
    }
    try {
      const id = modalData.id;
      setProcessingId(id);
      await api.deletePortfolio(id, token);
      closeModals();
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

      {error && !activeModal && <div className="status-banner status-banner-error">{error}</div>}

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
                          onClick={() => {
                            setActiveModal('updateBalance');
                            setModalData(u);
                            setInputValue(u.balance.toString());
                          }}
                          disabled={processingId === u.username}
                        >
                          Balance
                        </button>
                        <button 
                          className="btn btn-danger btn-compact" 
                          onClick={() => {
                            setActiveModal('deleteUser');
                            setModalData(u);
                          }}
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
                        onClick={() => {
                          setActiveModal('deletePortfolio');
                          setModalData(p);
                        }}
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

      {/* Delete User Modal */}
      {activeModal === 'deleteUser' && (
        <BaseModal 
          title="Delete User" 
          onClose={closeModals}
          footer={
            <>
              <button className="btn btn-outline" onClick={closeModals}>Cancel</button>
              <button className="btn btn-danger" onClick={confirmDeleteUser} disabled={processingId}>
                {processingId ? "Deleting..." : "Confirm Delete"}
              </button>
            </>
          }
        >
          <p>Are you sure you want to delete user <strong>{modalData.username}</strong>? This will remove all their data permanently.</p>
          {error && <div className="status-banner status-banner-error banner-margin-top">{error}</div>}
        </BaseModal>
      )}

      {/* Update Balance Modal */}
      {activeModal === 'updateBalance' && (
        <BaseModal 
          title="Adjust Balance" 
          onClose={closeModals}
          footer={
            <>
              <button className="btn btn-outline" onClick={closeModals}>Cancel</button>
              <button className="btn btn-primary" onClick={confirmUpdateBalance} disabled={processingId}>
                {processingId ? "Updating..." : "Save Changes"}
              </button>
            </>
          }
        >
          <div className="form-group">
            <label>New Balance for {modalData.username}</label>
            <input 
              type="number" 
              className="form-control" 
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              autoFocus
            />
          </div>
          {error && <div className="status-banner status-banner-error banner-margin-top">{error}</div>}
        </BaseModal>
      )}

      {/* Delete Portfolio Modal */}
      {activeModal === 'deletePortfolio' && (() => {
        const holdingsCount = modalData?.investments_count || 0;
        const deleteBlocked = holdingsCount > 0;
        const blockedMessage = holdingsCount === 1
          ? `${modalData.name} still has 1 active holding. All positions must be sold before it can be deleted.`
          : `${modalData.name} still has ${holdingsCount} active holdings. All positions must be sold before it can be deleted.`;
        return (
          <BaseModal
            title="Delete Portfolio"
            onClose={closeModals}
            footer={
              <>
                <button className="btn btn-outline" onClick={closeModals} disabled={processingId}>
                  {deleteBlocked ? 'Close' : 'Cancel'}
                </button>
                {!deleteBlocked && (
                  <button className="btn btn-danger" onClick={confirmDeletePortfolio} disabled={processingId}>
                    {processingId ? 'Deleting...' : 'Confirm Delete'}
                  </button>
                )}
              </>
            }
          >
            {deleteBlocked ? (
              <>
                <p>Portfolio <strong>{modalData.name}</strong> (owner: <strong>{modalData.owner}</strong>) cannot be deleted yet.</p>
                <div className="status-banner status-banner-error banner-margin-top" role="alert">
                  {blockedMessage}
                </div>
              </>
            ) : (
              <p>Are you sure you want to delete portfolio <strong>{modalData.name}</strong> belonging to <strong>{modalData.owner}</strong>? This action cannot be undone.</p>
            )}
            {error && !deleteBlocked && <div className="status-banner status-banner-error banner-margin-top">{error}</div>}
          </BaseModal>
        );
      })()}
    </div>
  );
}

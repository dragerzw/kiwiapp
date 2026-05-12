import { useEffect, useState } from "react";
import { useAuth } from "../AuthContext";
import { api } from "../api";

import CreatePortfolioModal from "./CreatePortfolioModal";
import DeletePortfolioModal from "./DeletePortfolioModal";
import TradeForm from "./TradeForm";
import "./Dashboard.css";

const TRADABLE_ROLES = ["Owner", "Manager"];

export default function Dashboard() {
  const auth = useAuth();
  const { isAuthenticated, token: authToken } = auth || {};
  const [portfolios, setPortfolios] = useState([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quoteError, setQuoteError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [portfolioToDelete, setPortfolioToDelete] = useState(null);
  const [isTrading, setIsTrading] = useState(false);

  const fetchPortfolios = async () => {
    try {
      setError(null);
      const data = await api.getPortfolios(authToken, { includeQuotes: false });
      setPortfolios(data);
      setQuoteError(null);
    } catch (e) {
      setQuoteError(null);
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated && authToken) {
      setLoading(true);
      fetchPortfolios();
    }
  }, [isAuthenticated, authToken]);

  const fetchDetails = async (id) => {
    try {
      setError(null);
      const details = await api.getPortfolioDetails(id, authToken);
      setSelectedPortfolio(details);
      setQuoteError(details.quote_error ?? null);
      const tx = await api.getTransactions(id, authToken);
      setTransactions(tx);
      setIsTrading(false);
    } catch (e) {
      setQuoteError(null);
      setError(e.message);
    }
  };

  const refreshPortfolioData = async (id) => {
    try {
      setError(null);
      const details = await api.getPortfolioDetails(id, authToken);
      setSelectedPortfolio(details);
      setQuoteError(details.quote_error ?? null);
      const tx = await api.getTransactions(id, authToken);
      setTransactions(tx);
    } catch (e) {
      setQuoteError(null);
      setError(e.message);
    }
  };

  const handleCreate = () => {
    setShowCreateModal(true);
  };

  const handleCreateSuccess = () => {
    setError(null);
    setShowCreateModal(false);
    fetchPortfolios();
  };

  const handleDeleteClick = (portfolio, e) => {
    if (e) e.stopPropagation();
    setPortfolioToDelete(portfolio);
  };

  const handleDeleteSuccess = async (deletedPortfolio) => {
    setPortfolioToDelete(null);
    if (selectedPortfolio?.id === deletedPortfolio.id) {
      setSelectedPortfolio(null);
      setTransactions([]);
    }
    await fetchPortfolios();
  };

  const closeDetailView = () => {
    setSelectedPortfolio(null);
    setTransactions([]);
    setIsTrading(false);
    fetchPortfolios();
  };

  const formatPortfolioValue = (portfolio) => {
    if (typeof portfolio.total_portfolio_value === "number") {
      return `$${portfolio.total_portfolio_value.toFixed(2)}`;
    }
    return "$0.00";
  };

  const portfolioCount = portfolios.length;
  const totalPortfolioValue = portfolios.reduce(
    (sum, portfolio) => sum + (typeof portfolio.total_portfolio_value === "number" ? portfolio.total_portfolio_value : 0),
    0,
  );
  const canTradeSelectedPortfolio = !!selectedPortfolio && TRADABLE_ROLES.includes(selectedPortfolio.access_role);

  if (!isAuthenticated) return <p>Please sign in.</p>;
  if (loading && !selectedPortfolio) return <p className="loading">Loading your workspace...</p>;

  return (
    <div className="dashboard-container">
      {/* GLOBAL HEADER/HERO (Only show when NOT in detail view) */}
      {!selectedPortfolio && (
        <>
          <section className="dashboard-hero" style={{ paddingBottom: '2rem' }}>
            <div className="dashboard-hero-copy">
              <p className="dashboard-eyebrow">Portfolio Workspace</p>
              <h1 className="dashboard-title">Welcome back.</h1>
            </div>
            <div className="dashboard-kpis">
              <article className="dashboard-kpi">
                <span className="dashboard-kpi-label">Total Value</span>
                <strong className="dashboard-kpi-value">${totalPortfolioValue.toFixed(2)}</strong>
              </article>
              <article className="dashboard-kpi">
                <span className="dashboard-kpi-label">My Portfolios</span>
                <strong className="dashboard-kpi-value">{portfolioCount}</strong>
              </article>
            </div>
          </section>

          <header className="dashboard-header" style={{ justifyContent: "space-between", borderBottom: 'none' }}>
            <h2 className="section-title" style={{ margin: 0 }}>Your Portfolios</h2>
            <button className="btn btn-primary" onClick={handleCreate}>+ New Portfolio</button>
          </header>

          {error && <div className="status-banner status-banner-error">{error}</div>}

          <main className="dashboard-content">
            <div className="portfolio-grid">
              {portfolios.map((portfolio) => (
                <div key={portfolio.id} className="portfolio-card">
                  <button
                    className="portfolio-card-surface"
                    onClick={() => fetchDetails(portfolio.id)}
                    type="button"
                  >
                    <div className="portfolio-card-body">
                      <div className="portfolio-card-pills">
                        <span className="role-pill">{portfolio.access_role || "Viewer"}</span>
                        <span className={`state-pill ${TRADABLE_ROLES.includes(portfolio.access_role) ? "state-pill-tradable" : "state-pill-readonly"}`}>
                          {TRADABLE_ROLES.includes(portfolio.access_role) ? "Can trade" : "View only"}
                        </span>
                      </div>
                      <h4>{portfolio.name}</h4>
                      <p>{portfolio.description || "No description"}</p>
                      <div className="portfolio-card-label">Portfolio Balance</div>
                      <div className="portfolio-card-value">
                        {formatPortfolioValue(portfolio)}
                      </div>
                    </div>
                  </button>
                  {portfolio.access_role === "Owner" && (
                    <div className="portfolio-card-footer">
                      <div className="portfolio-card-actions" style={{ justifyContent: "flex-end" }}>
                        <button
                          className="btn btn-danger btn-compact"
                          disabled={(portfolio.investments_count || 0) > 0}
                          onClick={(e) => handleDeleteClick(portfolio, e)}
                          type="button"
                        >
                          {(portfolio.investments_count || 0) > 0 ? "Sell holdings first" : "Delete"}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
              {portfolios.length === 0 && (
                <div className="empty-state" style={{ gridColumn: '1 / -1' }}>
                  <h3 className="empty-state-title">No Portfolios Found</h3>
                  <p className="empty-state-copy">Create a portfolio to begin tracking your investments.</p>
                </div>
              )}
            </div>
          </main>
        </>
      )}

      {/* DETAILED VIEW (Show when a portfolio IS selected) */}
      {selectedPortfolio && (
        <div className="portfolio-detail-view">
          <header className="detail-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <button className="btn btn-outline btn-compact" onClick={closeDetailView}>← Back</button>
              <h2 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 600 }}>{selectedPortfolio.name}</h2>
              <span className="role-pill">{selectedPortfolio.access_role}</span>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button className="btn btn-outline" onClick={() => refreshPortfolioData(selectedPortfolio.id)}>Refresh Quotes</button>
              {canTradeSelectedPortfolio && (
                <button className="btn btn-primary" onClick={() => setIsTrading(!isTrading)}>
                  {isTrading ? "Cancel Trade" : "Trade"}
                </button>
              )}
            </div>
          </header>

          {error && <div className="status-banner status-banner-error">{error}</div>}
          {!error && quoteError && <div className="status-banner status-banner-error">{quoteError}</div>}

          {isTrading && canTradeSelectedPortfolio && (
            <section className="trade-view glass" style={{ marginBottom: '2rem' }}>
              <div className="section-header">
                <h3>Execute Order</h3>
              </div>
              <TradeForm 
                portfolioId={selectedPortfolio.id} 
                authToken={authToken}
                holdings={selectedPortfolio.investments || []}
                onSuccess={() => fetchDetails(selectedPortfolio.id)} 
              />
            </section>
          )}

          <div className="detail-split-layout" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '2rem' }}>
            
            {/* Holdings Column */}
            <section className="holdings-view glass" style={{ padding: '1.5rem', margin: 0 }}>
              <div className="section-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ margin: 0 }}>Current Holdings</h3>
                <span style={{ fontWeight: 600, fontSize: '1.25rem', color: '#10b981' }}>{formatPortfolioValue(selectedPortfolio)}</span>
              </div>
              <div className="table-container">
                <table style={{ margin: 0 }}>
                  <thead>
                    <tr>
                      <th>Ticker</th>
                      <th>Qty</th>
                      <th>Price</th>
                      <th>Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedPortfolio.investments?.map(inv => (
                      <tr key={inv.ticker}>
                        <td><strong>{inv.ticker}</strong></td>
                        <td>{inv.quantity}</td>
                        <td className="numeric-cell">${inv.current_price?.toFixed(2) || "---"}</td>
                        <td className="numeric-cell">${inv.total_value?.toFixed(2) || "---"}</td>
                      </tr>
                    ))}
                    {(!selectedPortfolio.investments || selectedPortfolio.investments.length === 0) && (
                      <tr><td colSpan="4" className="table-empty">No active holdings.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </section>

            {/* Transactions Column */}
            <section className="transactions-view glass" style={{ padding: '1.5rem', margin: 0 }}>
              <div className="section-header" style={{ marginBottom: '1rem' }}>
                <h3 style={{ margin: 0 }}>Recent Transactions</h3>
              </div>
              <div className="table-container">
                <table style={{ margin: 0 }}>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Type</th>
                      <th>Asset</th>
                      <th>Price</th>
                      <th>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map(t => (
                      <tr key={t.id}>
                        <td>{new Date(t.date_time).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}</td>
                        <td><span className={`badge badge-${t.type.toLowerCase()}`}>{t.type}</span></td>
                        <td><strong>{t.ticker}</strong> ({t.quantity})</td>
                        <td className="numeric-cell">${t.price.toFixed(2)}</td>
                        <td className="numeric-cell">${t.total_value.toFixed(2)}</td>
                      </tr>
                    ))}
                    {transactions.length === 0 && (
                      <tr><td colSpan="5" className="table-empty">No transaction history.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </section>

          </div>
        </div>
      )}

      {showCreateModal && (
        <CreatePortfolioModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={handleCreateSuccess}
        />
      )}
      {portfolioToDelete && (
        <DeletePortfolioModal
          portfolio={portfolioToDelete}
          authToken={authToken}
          onClose={() => setPortfolioToDelete(null)}
          onSuccess={handleDeleteSuccess}
        />
      )}
    </div>
  );
}

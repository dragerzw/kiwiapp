import { useEffect, useState, useCallback } from "react";
import { useAuth } from "../AuthContext";
import { api } from "../api";

import CreatePortfolioModal from "./CreatePortfolioModal";
import DeletePortfolioModal from "./DeletePortfolioModal";
import TradeForm from "./TradeForm";
import "./Dashboard.css";

const TRADABLE_ROLES = ["Owner", "Manager"];

export default function Dashboard() {
  const auth = useAuth();
  const { isAuthenticated, token: authToken, user } = auth || {};
  const firstName = user?.profile?.given_name || user?.profile?.name || "Investor";
  const [portfolios, setPortfolios] = useState([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quoteError, setQuoteError] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [portfolioToDelete, setPortfolioToDelete] = useState(null);
  const [isTrading, setIsTrading] = useState(false);

  const fetchPortfolios = useCallback(async () => {
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
  }, [authToken]);

  useEffect(() => {
    if (isAuthenticated && authToken) {
      setLoading(true);
      fetchPortfolios();
    }
  }, [isAuthenticated, authToken, fetchPortfolios]);

  const fetchDetails = useCallback(async (id) => {
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
  }, [authToken]);

  const refreshPortfolioData = useCallback(async (id) => {
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
  }, [authToken]);

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
    setError(null);
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
      {/* COMPACT GLOBAL HEADER (Only show when NOT in detail view) */}
      {!selectedPortfolio && (
        <>
          <section className="dashboard-floating-hero">
            <div className="hero-content-left">
              <div className="hero-status-dot"></div>
              <h1 className="hero-greeting">Welcome back, <span className="hero-accent">{firstName}</span></h1>
            </div>
            <div className="hero-content-right">
              <div className="stat-group">
                <span className="stat-label">Total Assets</span>
                <strong className="stat-value">${totalPortfolioValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong>
              </div>
              <div className="stat-divider"></div>
              <div className="stat-group">
                <span className="stat-label">Portfolios</span>
                <strong className="stat-value">{portfolioCount}</strong>
              </div>
            </div>
          </section>

          <header className="dashboard-view-header">
            <div className="view-title-group">
              <h2 className="view-title">Active Portfolios</h2>
              <div className="view-count-badge">{portfolioCount} Total</div>
            </div>
            <button className="btn btn-primary btn-with-icon" onClick={handleCreate}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              <span>New Portfolio</span>
            </button>
          </header>

          {error && <div className="status-banner status-banner-error" role="alert">{error}</div>}

          <main className="dashboard-content">
            <div className="portfolio-grid">
              {portfolios.map((portfolio) => {
                return (
                  <div key={portfolio.id} className="portfolio-card">
                    <button
                      className="portfolio-card-surface"
                      onClick={() => fetchDetails(portfolio.id)}
                      type="button"
                    >
                      <div className="portfolio-card-body">
                        <div className="portfolio-card-header-row">
                          <div className="portfolio-icon-wrapper">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path>
                            </svg>
                          </div>
                          <div className="portfolio-card-pills">
                            <span className="role-pill">{portfolio.access_role || "Viewer"}</span>
                          </div>
                        </div>
                        <h4>{portfolio.name}</h4>
                        <p>{portfolio.description || "Active investment strategy"}</p>
                        <div className="portfolio-card-value-section">
                          <div className="portfolio-card-label">Net Asset Value</div>
                          <div className="portfolio-card-value">
                            {formatPortfolioValue(portfolio)}
                          </div>
                        </div>
                      </div>
                    </button>
                    {portfolio.access_role === "Owner" && (
                      <div className="portfolio-card-footer">
                        <div className="portfolio-card-actions portfolio-card-actions-end">
                          <button
                            className="btn btn-danger btn-compact"
                            onClick={(e) => handleDeleteClick(portfolio, e)}
                            type="button"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
              {portfolios.length === 0 && (
                <div className="empty-state empty-state-full-width">
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
          <header className="detail-header detail-header-flex">
            <div className="detail-header-title-group">
              <button className="btn btn-outline btn-compact" onClick={closeDetailView}>← Back</button>
              <h2 className="detail-header-title">{selectedPortfolio.name}</h2>
              <span className="role-pill">{selectedPortfolio.access_role}</span>
            </div>
            <div className="detail-header-actions">
              <button className="btn btn-outline" onClick={() => refreshPortfolioData(selectedPortfolio.id)}>Refresh Quotes</button>
              {canTradeSelectedPortfolio && (
                <button className="btn btn-primary" onClick={() => setIsTrading(!isTrading)}>
                  {isTrading ? "Cancel Trade" : "Trade"}
                </button>
              )}
            </div>
          </header>

          {error && <div className="status-banner status-banner-error" role="alert">{error}</div>}
          {!error && quoteError && <div className="status-banner status-banner-error" role="alert">{quoteError}</div>}

          {isTrading && canTradeSelectedPortfolio && (
            <section className="trade-view glass trade-view-section">
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

          <div className="detail-split-layout detail-split-layout-grid">
            
            {/* Holdings Column */}
            <section className="holdings-view glass holdings-view-section">
              <div className="section-header section-header-flex">
                <h3 className="section-header-title">Current Holdings</h3>
                <span className="holdings-total-value">{formatPortfolioValue(selectedPortfolio)}</span>
              </div>
              <div className="table-container">
                <table className="table-no-margin">
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
                        <td className="numeric-cell">{inv.current_price != null ? `$${inv.current_price.toFixed(2)}` : "---"}</td>
                        <td className="numeric-cell">{inv.total_value != null ? `$${inv.total_value.toFixed(2)}` : "---"}</td>
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
            <section className="transactions-view glass transactions-view-section">
              <div className="section-header transactions-header">
                <h3 className="section-header-title">Recent Transactions</h3>
              </div>
              <div className="table-container">
                <table className="table-no-margin">
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

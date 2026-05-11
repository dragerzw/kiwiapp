import { useEffect, useState } from "react";
import { useAuth } from "react-oidc-context";
import { api } from "../api";
import CreatePortfolioModal from "./CreatePortfolioModal";
import TradeForm from "./TradeForm";
import "./Dashboard.css";

export default function Dashboard() {
  const { isAuthenticated, user } = useAuth();
  const idToken = user?.id_token;
  const [portfolios, setPortfolios] = useState([]);
  const [selectedPortfolio, setSelectedPortfolio] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [quoteError, setQuoteError] = useState(null);
  const [activeTab, setActiveTab] = useState("portfolios"); // portfolios | holdings | trade | transactions
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [deletingPortfolioId, setDeletingPortfolioId] = useState(null);

  const fetchPortfolios = async () => {
    try {
      setError(null);
      const data = await api.getPortfolios(idToken, { includeQuotes: false });
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
    if (isAuthenticated) fetchPortfolios();
  }, [isAuthenticated, idToken]);

  const fetchDetails = async (id) => {
    try {
      setError(null);
      const details = await api.getPortfolioDetails(id, idToken);
      setSelectedPortfolio(details);
      setQuoteError(details.quote_error ?? null);
      const tx = await api.getTransactions(id, idToken);
      setTransactions(tx);
      // Switch to holdings when a portfolio is clicked
      setActiveTab("holdings");
    } catch (e) {
      setQuoteError(null);
      setError(e.message);
    }
  };

  const refreshPortfolioData = async (id) => {
    try {
      setError(null);
      const details = await api.getPortfolioDetails(id, idToken);
      setSelectedPortfolio(details);
      setQuoteError(details.quote_error ?? null);
      const tx = await api.getTransactions(id, idToken);
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

  const handleDeletePortfolio = async (portfolio) => {
    if (!window.confirm(`Delete "${portfolio.name}"? This cannot be undone.`)) {
      return;
    }

    try {
      setError(null);
      setQuoteError(null);
      setDeletingPortfolioId(portfolio.id);
      await api.deletePortfolio(portfolio.id, idToken);

      if (selectedPortfolio?.id === portfolio.id) {
        setSelectedPortfolio(null);
        setTransactions([]);
        setActiveTab("portfolios");
      }

      await fetchPortfolios();
    } catch (e) {
      setError(e.message);
    } finally {
      setDeletingPortfolioId(null);
    }
  };

  const formatHoldingsText = (count) => {
    if (!count) return "No holdings yet";
    return `${count} holding${count === 1 ? "" : "s"}`;
  };

  const formatPortfolioValue = (portfolio) => {
    if (typeof portfolio.total_portfolio_value === "number") {
      return `$${portfolio.total_portfolio_value.toFixed(2)}`;
    }
    return "$0.00";
  };

  const canTradeSelectedPortfolio =
    !!selectedPortfolio && ["Owner", "Manager"].includes(selectedPortfolio.access_role);

  if (!isAuthenticated) return <p>Please sign in.</p>;
  if (loading) return <p className="loading">Loading your kiwi session...</p>;

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="tab-nav">
          <button 
            className={`tab-link ${activeTab === "portfolios" ? "active" : ""}`}
            onClick={() => setActiveTab("portfolios")}
          >
            Portfolios
          </button>
          <button 
            className={`tab-link ${activeTab === "holdings" ? "active" : ""}`}
            disabled={!selectedPortfolio}
            onClick={() => setActiveTab("holdings")}
          >
            Holdings
          </button>
          <button 
            className={`tab-link ${activeTab === "trade" ? "active" : ""}`}
            disabled={!selectedPortfolio || !canTradeSelectedPortfolio}
            onClick={() => setActiveTab("trade")}
          >
            Trade
          </button>
          <button 
            className={`tab-link ${activeTab === "transactions" ? "active" : ""}`}
            disabled={!selectedPortfolio}
            onClick={() => setActiveTab("transactions")}
          >
            Transactions
          </button>
        </div>
        <div className="header-actions">
          {selectedPortfolio && (
            <button
              className="btn btn-outline"
              onClick={() => refreshPortfolioData(selectedPortfolio.id)}
              type="button"
            >
              Refresh Quotes
            </button>
          )}
          <button className="btn btn-primary" onClick={handleCreate}>+ New Portfolio</button>
        </div>
      </header>

      {error && <div className="status-banner status-banner-error">{error}</div>}
      {!error && quoteError && <div className="status-banner status-banner-error">{quoteError}</div>}

      <main className="dashboard-content">
        {activeTab === "portfolios" && (
          <section>
            <h2 className="section-title">Your Portfolios</h2>
            <div className="portfolio-grid">
              {portfolios.map((portfolio) => (
                <div key={portfolio.id} className="portfolio-card">
                  <button
                    className="portfolio-card-surface"
                    onClick={() => fetchDetails(portfolio.id)}
                    type="button"
                  >
                    <div className="portfolio-card-body">
                      <h4>{portfolio.name}</h4>
                      <p>{portfolio.description || "No description"}</p>
                      <div className="portfolio-card-label">Portfolio Balance</div>
                      <div className="portfolio-card-value">
                        {formatPortfolioValue(portfolio)}
                      </div>
                      <div className="portfolio-card-meta">
                        {formatHoldingsText(portfolio.investments_count)}
                      </div>
                    </div>
                  </button>
                  <div className="portfolio-card-footer">
                    <span className="portfolio-card-role">{portfolio.access_role || "Viewer"}</span>
                    <div className="portfolio-card-actions">
                      <button
                        className="btn btn-outline btn-compact"
                        onClick={() => fetchDetails(portfolio.id)}
                        type="button"
                      >
                        View Holdings
                      </button>
                      {portfolio.access_role === "Owner" ? (
                        <button
                          className="btn btn-danger btn-compact"
                          disabled={deletingPortfolioId === portfolio.id}
                          onClick={() => handleDeletePortfolio(portfolio)}
                          type="button"
                        >
                          {deletingPortfolioId === portfolio.id ? "Deleting..." : "Delete"}
                        </button>
                      ) : null}
                    </div>
                  </div>
                </div>
              ))}
              {portfolios.length === 0 && <p className="empty-state">No portfolios yet. Create one to get started!</p>}
            </div>
          </section>
        )}

        {activeTab === "holdings" && selectedPortfolio && (
          <section className="holdings-view glass">
            <div className="section-header">
              <h3>{selectedPortfolio.name} - Holdings</h3>
            </div>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Ticker</th>
                    <th>Quantity</th>
                    <th>Current Price</th>
                    <th>Total Value</th>
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
                    <tr><td colSpan="4" className="table-empty">No holdings yet. Go to Trade to buy stocks.</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {activeTab === "trade" && selectedPortfolio && canTradeSelectedPortfolio && (
          <section className="trade-view glass">
            <div className="section-header">
              <h3>Trade on {selectedPortfolio.name}</h3>
            </div>
            <TradeForm 
              portfolioId={selectedPortfolio.id} 
              authToken={idToken}
              onSuccess={() => fetchDetails(selectedPortfolio.id)} 
            />
          </section>
        )}

        {activeTab === "transactions" && selectedPortfolio && (
          <section className="transactions-view glass">
            <div className="section-header">
              <h3>{selectedPortfolio.name} - Transaction History</h3>
            </div>
            <div className="transaction-list-full">
              {transactions.map(t => (
                <div key={t.id} className="transaction-item">
                  <span className={`badge badge-${t.type.toLowerCase()}`}>{t.type}</span>
                  <div className="tx-details">
                    <strong>{t.ticker}</strong>
                    <span>{t.quantity} shares @ ${t.price.toFixed(2)}</span>
                  </div>
                  <div className="tx-date">{new Date(t.date_time).toLocaleDateString()}</div>
                </div>
              ))}
              {transactions.length === 0 && <p className="empty-state">No transactions yet.</p>}
            </div>
          </section>
        )}
      </main>

      {showCreateModal && (
        <CreatePortfolioModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={handleCreateSuccess}
        />
      )}
    </div>
  );
}

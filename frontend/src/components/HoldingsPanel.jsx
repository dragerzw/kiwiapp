import { useEffect, useState } from "react";
import { useAuth } from "../AuthContext";
import { api } from "../api";

import TradeModal from "./TradeModal";

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

const numberFormatter = new Intl.NumberFormat("en-US");

const HoldingsPanel = ({ onBack, onSignOut, portfolioId, signOutError = null }) => {
  const auth = useAuth();
  const authToken = auth?.token;
  const [portfolio, setPortfolio] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [showTradeModal, setShowTradeModal] = useState(false);
  const canTrade = !!portfolio && ["Owner", "Manager"].includes(portfolio.access_role);

  useEffect(() => {
    if (!authToken) {
      return;
    }

    let cancelled = false;

    const loadPortfolioData = async () => {
      setLoading(true);
      try {
        const [portfolioData, transactionData] = await Promise.all([
          api.getPortfolioDetails(portfolioId, authToken),
          api.getTransactions(portfolioId, authToken),
        ]);

        if (cancelled) {
          return;
        }

        setPortfolio(portfolioData);
        setTransactions(transactionData);
        setError(null);
      } catch (requestError) {
        if (cancelled) {
          return;
        }
        setError(requestError.message);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    void loadPortfolioData();

    return () => {
      cancelled = true;
    };
  }, [authToken, portfolioId, refreshKey]);

  const refreshPortfolioData = () => {
    setRefreshKey((value) => value + 1);
  };

  const holdings = portfolio?.investments || [];
  const normalizedTransactions = transactions.map((transaction) => ({
    ...transaction,
    displayId: transaction.id ?? transaction.transaction_id,
    displayType: transaction.type ?? transaction.transaction_type,
    displayTotalValue:
      typeof transaction.total_value === "number"
        ? transaction.total_value
        : transaction.price * transaction.quantity,
  }));

  if (loading) {
    return (
      <div className="auth-shell">
        <div className="auth-status-card">
          <p className="auth-status-label">Loading holdings...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container" style={{ marginTop: "4rem" }}>
        <div className="status-banner status-banner-error" role="alert">
          <strong>Unable to load portfolio.</strong> {error}
        </div>
        <button className="btn btn-primary" onClick={onBack} type="button">
          Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div>
      <nav className="navbar">
        <button className="btn btn-outline" onClick={onBack} type="button">
          Back to Dashboard
        </button>
        <div className="nav-user">
          <span className="nav-user-label">
            {auth.user?.profile?.email ||
              auth.user?.profile?.username ||
              auth.user?.profile?.["cognito:username"] ||
              auth.user?.profile?.sub}
          </span>
          {canTrade ? (
            <button className="btn btn-primary" onClick={() => setShowTradeModal(true)} type="button">
              Execute Trade
            </button>
          ) : null}
          <button className="btn btn-outline" onClick={() => void onSignOut()} type="button">
            Sign Out
          </button>
        </div>
      </nav>

      <div className="container">
        <div className="page-header">
          <div>
            <h1>{portfolio.name}</h1>
            <p className="page-subtitle">{portfolio.description || "No description provided."}</p>
          </div>
          <div className="holding-meta">
            <span className="stat-chip">{holdings.length} assets</span>
            <span className="stat-chip">
              Value: {currencyFormatter.format(portfolio.total_portfolio_value || 0)}
            </span>
          </div>
        </div>

        {signOutError ? (
          <div className="status-banner status-banner-error" role="alert">
            {signOutError}
          </div>
        ) : null}

        {notice ? (
          <div className="status-banner status-banner-success" role="status">
            {notice}
          </div>
        ) : null}

        <section className="panel-section">
          <div className="section-header">
            <h2>Current Holdings</h2>
          </div>
          <div className="table-container card">
            <table>
              <thead>
                <tr>
                  <th>Ticker</th>
                  <th style={{ textAlign: "right" }}>Quantity</th>
                  <th style={{ textAlign: "right" }}>Current Price</th>
                  <th style={{ textAlign: "right" }}>Market Value</th>
                </tr>
              </thead>
              <tbody>
                {holdings.length > 0 ? (
                  holdings.map((investment) => (
                    <tr key={investment.ticker}>
                      <td style={{ fontWeight: "700", fontSize: "1.05rem" }}>{investment.ticker}</td>
                      <td className="numeric-cell">{numberFormatter.format(investment.quantity)}</td>
                      <td className="numeric-cell">
                        {typeof investment.current_price === "number"
                          ? currencyFormatter.format(investment.current_price)
                          : "Unavailable"}
                      </td>
                      <td className="numeric-cell">
                        {typeof investment.total_value === "number"
                          ? currencyFormatter.format(investment.total_value)
                          : "Unavailable"}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td className="table-empty" colSpan="4">
                      No holdings in this portfolio yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <section className="panel-section">
          <div className="section-header">
            <h2>Transaction History</h2>
          </div>
          <div className="table-container card">
            <table>
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Ticker</th>
                  <th style={{ textAlign: "right" }}>Quantity</th>
                  <th style={{ textAlign: "right" }}>Unit Price</th>
                  <th style={{ textAlign: "right" }}>Total Value</th>
                  <th style={{ textAlign: "right" }}>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {normalizedTransactions.length > 0 ? (
                  normalizedTransactions.map((transaction) => (
                    <tr key={transaction.displayId}>
                      <td>
                        <span className={`badge badge-${transaction.displayType.toLowerCase()}`}>
                          {transaction.displayType}
                        </span>
                      </td>
                      <td style={{ fontWeight: "700" }}>{transaction.ticker}</td>
                      <td className="numeric-cell">{numberFormatter.format(transaction.quantity)}</td>
                      <td className="numeric-cell">{currencyFormatter.format(transaction.price)}</td>
                      <td className="numeric-cell">
                        {currencyFormatter.format(transaction.displayTotalValue)}
                      </td>
                      <td className="numeric-cell">
                        {new Date(transaction.date_time).toLocaleString()}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td className="table-empty" colSpan="6">
                      No transactions recorded.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>

      {showTradeModal ? (
        <TradeModal
          investments={holdings}
          onClose={() => setShowTradeModal(false)}
          onSuccess={(message) => {
            setShowTradeModal(false);
            setNotice(message);
            refreshPortfolioData();
          }}
          portfolioId={portfolioId}
        />
      ) : null}
    </div>
  );
};

export default HoldingsPanel;

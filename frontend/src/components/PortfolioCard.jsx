import { useState } from "react";
import { useAuth } from "../AuthContext";
import { api } from "../api";


const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

const PortfolioCard = ({ portfolio, onDeleteError, onDeleteSuccess, onSelect }) => {
  const auth = useAuth();
  const authToken = auth?.token;
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async (event) => {
    event.stopPropagation();

    if (!window.confirm(`Delete "${portfolio.name}"? This cannot be undone.`)) {
      return;
    }

    try {
      setDeleting(true);
      await api.deletePortfolio(portfolio.id, authToken);
      onDeleteSuccess?.(`Deleted portfolio "${portfolio.name}".`);
    } catch (deleteError) {
      onDeleteError?.(`Unable to delete "${portfolio.name}": ${deleteError.message}`);
    } finally {
      setDeleting(false);
    }
  };

  const totalValue =
    typeof portfolio.total_portfolio_value === "number"
      ? currencyFormatter.format(portfolio.total_portfolio_value)
      : "Unavailable";

  return (
    <div className="card portfolio-card" onClick={() => onSelect(portfolio.id)} role="button" tabIndex={0}>
      <div className="card-body">
        <h3 className="card-title">{portfolio.name}</h3>
        <p className="card-description">{portfolio.description || "No description provided."}</p>
        <div className="holding-meta">
          <span className="stat-chip">{portfolio.investments_count || 0} assets</span>
          <span className="stat-chip">Value: {totalValue}</span>
        </div>
      </div>
      <div className="card-footer">
        {portfolio.access_role === "Owner" ? (
          <button className="btn btn-danger" disabled={deleting} onClick={handleDelete} type="button">
            {deleting ? "Deleting..." : "Delete"}
          </button>
        ) : null}
        <button
          className="btn btn-primary"
          onClick={(event) => {
            event.stopPropagation();
            onSelect(portfolio.id);
          }}
          type="button"
        >
          View Holdings
        </button>
      </div>
    </div>
  );
};

export default PortfolioCard;

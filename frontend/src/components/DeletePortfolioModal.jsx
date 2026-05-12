import { useState } from "react";
import { api } from "../api";

const DeletePortfolioModal = ({ portfolio, authToken, onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleDelete = async () => {
    try {
      setLoading(true);
      setError(null);
      await api.deletePortfolio(portfolio.id, authToken);
      onSuccess(portfolio);
    } catch (requestError) {
      setError(requestError.message);
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-content">
        <h2 style={{ marginBottom: "0.5rem" }}>Delete Portfolio</h2>
        <p className="modal-note" style={{ marginBottom: "1.5rem" }}>
          Are you sure you want to delete <strong>{portfolio.name}</strong>? This action cannot be undone.
        </p>
        
        {error ? (
          <div className="status-banner status-banner-error" role="alert">
            {error}
          </div>
        ) : null}

        <div className="modal-actions">
          <button className="btn btn-outline" disabled={loading} onClick={onClose} type="button">
            Cancel
          </button>
          <button className="btn btn-danger" disabled={loading} onClick={handleDelete} type="button">
            {loading ? "Deleting..." : "Delete Portfolio"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeletePortfolioModal;

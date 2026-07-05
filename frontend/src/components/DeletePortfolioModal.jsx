import { useState } from "react";
import { api } from "../api";
import BaseModal from "./BaseModal";

const DeletePortfolioModal = ({ portfolio, authToken, onClose, onSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const holdingsCount = portfolio?.investments_count || 0;
  const deleteBlocked = holdingsCount > 0;
  const blockedMessage = holdingsCount === 1
    ? "This portfolio still has an active holding. Sell it before deleting the portfolio."
    : `This portfolio still has ${holdingsCount} active holdings. Sell them before deleting the portfolio.`;

  const handleDelete = async () => {
    if (deleteBlocked) {
      return;
    }
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
    <BaseModal 
      title="Delete Portfolio" 
      onClose={onClose}
      footer={
        <>
          <button className="btn btn-outline" disabled={loading} onClick={onClose} type="button">
            {deleteBlocked ? "Close" : "Cancel"}
          </button>
          {!deleteBlocked ? (
            <button className="btn btn-danger" disabled={loading} onClick={handleDelete} type="button">
              {loading ? "Deleting..." : "Delete Portfolio"}
            </button>
          ) : null}
        </>
      }
    >
      {deleteBlocked ? (
        <>
          <p className="modal-note">
            <strong>{portfolio.name}</strong> can't be deleted yet.
          </p>
          <div className="status-banner status-banner-error banner-margin-top" role="alert">
            {blockedMessage}
          </div>
        </>
      ) : (
        <p className="modal-note">
          Are you sure you want to delete <strong>{portfolio.name}</strong>? This action cannot be undone.
        </p>
      )}
      
      {error ? (
        <div className="status-banner status-banner-error banner-margin-top" role="alert">
          {error}
        </div>
      ) : null}
    </BaseModal>
  );
};

export default DeletePortfolioModal;

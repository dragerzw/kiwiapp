import { useState } from "react";
import { api } from "../api";
import BaseModal from "./BaseModal";

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
    <BaseModal 
      title="Delete Portfolio" 
      onClose={onClose}
      footer={
        <>
          <button className="btn btn-outline" disabled={loading} onClick={onClose} type="button">
            Cancel
          </button>
          <button className="btn btn-danger" disabled={loading} onClick={handleDelete} type="button">
            {loading ? "Deleting..." : "Delete Portfolio"}
          </button>
        </>
      }
    >
      <p className="modal-note">
        Are you sure you want to delete <strong>{portfolio.name}</strong>? This action cannot be undone.
      </p>
      
      {error ? (
        <div className="status-banner status-banner-error" role="alert" style={{marginTop: '1rem'}}>
          {error}
        </div>
      ) : null}
    </BaseModal>
  );
};

export default DeletePortfolioModal;

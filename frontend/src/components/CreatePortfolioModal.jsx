import { useState } from "react";
import { useAuth } from "../AuthContext";
import { api } from "../api";


const CreatePortfolioModal = ({ onClose, onSuccess }) => {
  const auth = useAuth();
  const authToken = auth?.token;
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();

    const trimmedName = name.trim();
    if (!trimmedName) {
      setError("Portfolio name is required.");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      await api.createPortfolio(
        {
          name: trimmedName,
          description: description.trim() || null,
        },
        authToken,
      );

      onSuccess?.(`Created portfolio "${trimmedName}".`);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-content">
        <h2 style={{ marginBottom: "1.5rem" }}>Create Portfolio</h2>
        <form onSubmit={handleSubmit}>
          {error ? (
            <div className="status-banner status-banner-error" role="alert">
              {error}
            </div>
          ) : null}
          <div className="form-group">
            <label htmlFor="portfolio-name">Portfolio Name</label>
            <input
              autoFocus
              className="form-control"
              id="portfolio-name"
              onChange={(event) => setName(event.target.value)}
              placeholder="Growth Fund"
              required
              type="text"
              value={name}
            />
          </div>
          <div className="form-group">
            <label htmlFor="portfolio-description">Description (Optional)</label>
            <textarea
              className="form-control"
              id="portfolio-description"
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Long-term growth holdings"
              rows="3"
              value={description}
            />
            <p className="modal-note">
              Portfolios can be actively traded upon creation. For security, deletion is disabled while active positions remain.
            </p>
          </div>
          <div className="modal-actions">
            <button className="btn btn-outline" disabled={loading} onClick={onClose} type="button">
              Cancel
            </button>
            <button className="btn btn-primary" disabled={loading} type="submit">
              {loading ? "Creating..." : "Create Portfolio"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreatePortfolioModal;

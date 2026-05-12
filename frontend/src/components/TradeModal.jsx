import { useState } from "react";
import { useAuth } from "../AuthContext";
import { api } from "../api";


const TradeModal = ({ investments = [], onClose, onSuccess, portfolioId }) => {
  const auth = useAuth();
  const authToken = auth?.token;
  const [type, setType] = useState("BUY");
  const [ticker, setTicker] = useState("");
  const [quantity, setQuantity] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const sellableTickers = investments.map((investment) => investment.ticker).sort();
  const normalizedTicker = ticker.toUpperCase().trim();
  const activeTicker =
    type === "SELL" && !sellableTickers.includes(normalizedTicker)
      ? sellableTickers[0] || ""
      : normalizedTicker;
  const selectedHolding = investments.find((investment) => investment.ticker === activeTicker);
  const availableQuantity = selectedHolding?.quantity ?? 0;
  const sellDisabled = type === "SELL" && sellableTickers.length === 0;

  const handleSubmit = async (event) => {
    event.preventDefault();

    const parsedQuantity = Number.parseInt(quantity, 10);
    if (!activeTicker || Number.isNaN(parsedQuantity) || parsedQuantity <= 0) {
      setError("Enter a ticker and a whole-share quantity greater than zero.");
      return;
    }

    if (type === "SELL" && parsedQuantity > availableQuantity) {
      setError(`You only have ${availableQuantity} shares of ${activeTicker} available to sell.`);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const tradeData = {
        portfolio_id: portfolioId,
        ticker: activeTicker,
        quantity: parsedQuantity,
      };

      if (type === "BUY") {
        await api.buyTrade(tradeData, authToken);
      } else {
        await api.sellTrade(tradeData, authToken);
      }

      onSuccess?.(`Executed ${type} order for ${parsedQuantity} share(s) of ${activeTicker}.`);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-content">
        <h2 style={{ marginBottom: "1.5rem" }}>Execute Trade</h2>
        <form onSubmit={handleSubmit}>
          {error ? (
            <div className="status-banner status-banner-error" role="alert">
              {error}
            </div>
          ) : null}

          <div className="form-group">
            <label>Transaction Type</label>
            <div className="trade-toggle-row">
              <button
                className={`btn ${type === "BUY" ? "btn-primary" : "btn-outline"}`}
                onClick={() => {
                  setType("BUY");
                  setError(null);
                }}
                style={{ flex: 1 }}
                type="button"
              >
                BUY
              </button>
              <button
                className={`btn ${type === "SELL" ? "btn-danger" : "btn-outline"}`}
                onClick={() => {
                  setType("SELL");
                  setError(null);
                }}
                style={{ flex: 1 }}
                type="button"
              >
                SELL
              </button>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="trade-ticker">Ticker Symbol</label>
            {type === "SELL" ? (
              <select
                className="form-control"
                disabled={sellableTickers.length === 0 || loading}
                id="trade-ticker"
                onChange={(event) => setTicker(event.target.value)}
                value={activeTicker}
              >
                {sellableTickers.length === 0 ? (
                  <option value="">No holdings available to sell</option>
                ) : null}
                {sellableTickers.map((sellableTicker) => (
                  <option key={sellableTicker} value={sellableTicker}>
                    {sellableTicker}
                  </option>
                ))}
              </select>
            ) : (
              <input
                autoFocus
                className="form-control"
                id="trade-ticker"
                onChange={(event) => setTicker(event.target.value)}
                placeholder="AAPL"
                required
                type="text"
                value={ticker}
              />
            )}
          </div>

          <div className="form-group">
            <label htmlFor="trade-quantity">Quantity</label>
            <input
              className="form-control"
              id="trade-quantity"
              min="1"
              onChange={(event) => setQuantity(event.target.value)}
              placeholder="10"
              required
              type="number"
              value={quantity}
            />
            {type === "SELL" && availableQuantity > 0 ? (
              <div className="modal-help">
                <span>Available: {availableQuantity} shares</span>
                <button
                  className="btn btn-outline btn-compact"
                  onClick={() => setQuantity(String(availableQuantity))}
                  type="button"
                >
                  Sell All
                </button>
              </div>
            ) : null}
          </div>

          {sellDisabled ? (
            <p className="modal-note">Buy a position first before attempting to sell from this portfolio.</p>
          ) : null}

          <div className="modal-actions">
            <button className="btn btn-outline" disabled={loading} onClick={onClose} type="button">
              Cancel
            </button>
            <button
              className={`btn ${type === "BUY" ? "btn-primary" : "btn-danger"}`}
              disabled={loading || sellDisabled}
              type="submit"
            >
              {loading ? "Processing..." : `Confirm ${type}`}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TradeModal;

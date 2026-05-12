import { useState } from "react";
import { api } from "../api";

export default function TradeForm({ portfolioId, authToken, holdings = [], onSuccess }) {
  const [ticker, setTicker] = useState("");
  const [quantity, setQuantity] = useState("");
  const [type, setType] = useState("buy");
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const normalizedTicker = ticker.trim().toUpperCase();
    const parsedQuantity = Number(quantity);

    if (!normalizedTicker || !Number.isInteger(parsedQuantity) || parsedQuantity <= 0) {
      setMsg({ kind: "error", text: "Please enter a valid ticker and a whole-share quantity greater than zero." });
      return;
    }

    setLoading(true);
    setMsg(null);
    try {
      const payload = {
        portfolio_id: portfolioId,
        ticker: normalizedTicker,
        quantity: parsedQuantity,
      };
      if (type === "buy") {
        await api.buyTrade(payload, authToken);
      } else {
        await api.sellTrade(payload, authToken);
      }
      setMsg({ kind: "success", text: `Trade successful: ${type.toUpperCase()} ${normalizedTicker}` });
      setTicker("");
      setQuantity("");
      if (onSuccess) onSuccess();
    } catch (err) {
      setMsg({ kind: "error", text: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="trade-card">
      <h4>New Trade</h4>
      <p className="modal-note">
        Execute whole-share market orders. Live market pricing is fetched securely prior to execution.
      </p>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Type</label>
          <div className="trade-toggle-row">
            <button
              type="button"
              className={`btn ${type === "buy" ? "btn-primary" : "btn-outline"}`}
              onClick={() => { setType("buy"); setTicker(""); setQuantity(""); setMsg(null); }}
            >
              Buy
            </button>
            <button
              type="button"
              className={`btn ${type === "sell" ? "btn-danger" : "btn-outline"}`}
              onClick={() => { setType("sell"); setTicker(""); setQuantity(""); setMsg(null); }}
            >
              Sell
            </button>
          </div>
        </div>
        <div className="form-group">
          <label>Ticker</label>
          {type === "sell" ? (
            <select
              className="form-control"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              required
            >
              <option value="" disabled>Select a ticker to sell</option>
              {holdings.map((h) => (
                <option key={h.ticker} value={h.ticker}>
                  {h.ticker} ({h.quantity} shares owned)
                </option>
              ))}
            </select>
          ) : (
            <input
              type="text"
              className="form-control"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              placeholder="AAPL"
              required
            />
          )}
        </div>
        <div className="form-group">
          <label>Quantity</label>
          <input
            type="number"
            min="1"
            step="1"
            className="form-control"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            placeholder="10"
            required
          />
        </div>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? "Processing..." : `Submit ${type === "buy" ? "Buy" : "Sell"} Order`}
        </button>
      </form>
      {msg ? <p className={`status-banner status-banner-${msg.kind}`}>{msg.text}</p> : null}
    </div>
  );
}

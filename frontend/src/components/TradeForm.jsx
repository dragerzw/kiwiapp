import { useState } from "react";
import { api } from "../api";

export default function TradeForm({ portfolioId, authToken, onSuccess }) {
  const [ticker, setTicker] = useState("");
  const [quantity, setQuantity] = useState("");
  const [type, setType] = useState("buy");
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!ticker || !quantity) return;

    setLoading(true);
    setMsg(null);
    try {
      const payload = {
        portfolio_id: portfolioId,
        ticker: ticker.trim().toUpperCase(),
        quantity: Number(quantity),
      };
      if (type === "buy") {
        await api.buyTrade(payload, authToken);
      } else {
        await api.sellTrade(payload, authToken);
      }
      setMsg({ kind: "success", text: `Trade successful: ${type.toUpperCase()} ${ticker}` });
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
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Type</label>
          <div className="trade-toggle-row">
            <button
              type="button"
              className={`btn ${type === "buy" ? "btn-primary" : "btn-outline"}`}
              onClick={() => setType("buy")}
            >
              Buy
            </button>
            <button
              type="button"
              className={`btn ${type === "sell" ? "btn-danger" : "btn-outline"}`}
              onClick={() => setType("sell")}
            >
              Sell
            </button>
          </div>
        </div>
        <div className="form-group">
          <label>Ticker</label>
          <input
            type="text"
            className="form-control"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            placeholder="AAPL"
            required
          />
        </div>
        <div className="form-group">
          <label>Quantity</label>
          <input
            type="number"
            className="form-control"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            placeholder="10"
            required
          />
        </div>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? "Processing..." : "Submit Trade"}
        </button>
      </form>
      {msg && <p className={`status-banner status-banner-${msg.kind}`}>{msg.text}</p>}
    </div>
  );
}

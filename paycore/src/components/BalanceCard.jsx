/**
 * BalanceCard.jsx — the hero card on the dashboard.
 *
 * Props are how a parent passes data INTO a child component. Dashboard
 * passes `balance` and `loading`; this component only worries about
 * DISPLAYING it. Keeping display separate from fetching makes both easy
 * to change independently.
 */
import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { formatCurrency } from "../utils/formatCurrency";
import LoadingSpinner from "./LoadingSpinner";

export default function BalanceCard({ balance, loading, currency = "PKR" }) {
  // useState(false) — should the amount be visible? Each person's click
  // is local UI state; nothing here touches the backend.
  const [hidden, setHidden] = useState(false);

  // While the wallet request runs, show a skeleton-like placeholder.
  // Hiding a stale number during a reload avoids confusing flicker.
  if (loading) {
    return (
      <div className="balance-card">
        <div className="balance-label">
          <WalletIcon />
          Available Balance
        </div>
        <div className="balance-amount" style={{ opacity: 0.8 }}>
          <LoadingSpinner />
        </div>
        <div className="balance-footnote">Fetching your balance…</div>
      </div>
    );
  }

  return (
    <div className="balance-card">
      <div className="balance-label">
        <WalletIcon />
        Available Balance

        {/* The eye toggle: flips `hidden`, and the amount line below
            re-renders with dots instead of digits. */}
        <button
          className="eye-btn-light"
          onClick={() => setHidden(!hidden)}
          aria-label={hidden ? "Show balance" : "Hide balance"}
          style={{ marginLeft: "auto" }}
        >
          {hidden ? <Eye size={17} /> : <EyeOff size={17} />}
        </button>
      </div>

      <div className="balance-amount">
        {/* "•••••" while hidden — same width feel as a real amount.
            If the wallet request failed, balance is undefined → show a
            neutral placeholder instead of a fake "Rs. 0.00". */}
        {hidden
          ? "Rs. ••••••"
          : balance == null
            ? "Rs. ——"
            : formatCurrency(balance)}
      </div>

      <div className="balance-footnote">
        {currency} · Updated just now
      </div>
    </div>
  );
}

/* Tiny inline icon so the card needs no extra import clutter */
function WalletIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
      <path
        d="M3 8a3 3 0 0 1 3-3h12a3 3 0 0 1 3 3v8a3 3 0 0 1-3 3H6a3 3 0 0 1-3-3V8Z"
        stroke="currentColor"
        strokeWidth="2"
      />
      <circle cx="16.5" cy="12" r="1.4" fill="currentColor" />
    </svg>
  );
}

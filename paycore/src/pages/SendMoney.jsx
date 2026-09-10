/**
 * SendMoney.jsx — the transfer flow: Form → Confirm → Success.
 *
 * NEW CONCEPTS ON THIS PAGE:
 *   • A "step machine" with useState — one state variable `step` holds
 *     "form" | "confirm" | "success". JSX renders a different screen for
 *     each value. This is the simplest possible way to build a multi-step
 *     flow without extra libraries.
 *   • The idempotency key lives in STATE (not a plain variable) so it
 *     survives re-renders between Continue and Confirm — see the comment
 *     at handleContinue.
 *   • `crypto.randomUUID()` — a built-in browser function that generates
 *     an unpredictable unique string (works on localhost/HTTPS).
 *
 * FLOW:
 *   1. User enters username + amount, presses Continue → we validate and
 *      GENERATE the idempotency key NOW (intent created).
 *   2. Confirm screen summarizes the transfer. Confirm → POST /transfers/
 *      with that key. Cancel → back to form.
 *   3. 201 → success screen with the reference from the backend.
 */
import { useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowLeft,
  ShieldCheck,
  AlertCircle,
  Check,
} from "lucide-react";
import { sendTransfer } from "../api/transferApi";
import { getErrorMessage } from "../api/api";
import { formatCurrency } from "../utils/formatCurrency";
import LoadingSpinner from "../components/LoadingSpinner";

export default function SendMoney() {
  // ── Which screen am I showing? ────────────────────────────────────────
  const [step, setStep] = useState("form"); // "form" | "confirm" | "success"

  // ── Form fields ────────────────────────────────────────────────────────
  const [username, setUsername] = useState("");
  const [amount, setAmount] = useState("");

  // ── Validation + submission state ──────────────────────────────────────
  const [errors, setErrors] = useState({});
  const [error, setError] = useState("");       // banner (backend errors)
  const [sending, setSending] = useState(false); // disables Confirm button

  // ── Results for the confirm/success screens ────────────────────────────
  const [idempotencyKey, setIdempotencyKey] = useState(null);
  const [receipt, setReceipt] = useState(null); // backend's TransferResponse

  // Continue pressed on the form: validate locally, then move to confirm.
  function handleContinue(e) {
    e.preventDefault();
    setError("");

    const newErrors = {};
    if (!username.trim()) newErrors.username = "Receiver username is required.";
    // Number(amount) converts "" → NaN... which fails the check. Neat trick:
    // one comparison covers "empty" and "not a number".
    if (!(Number(amount) > 0)) newErrors.amount = "Enter an amount greater than zero.";

    setErrors(newErrors);
    if (Object.keys(newErrors).length > 0) return;

    // ─── Idempotency key born here ─────────────────────────────────────
    // The user's INTENT ("send Rs. X to @y") exists from this moment.
    // Generating the key here (not inside the send function) guarantees
    // every retry of this same transfer reuses this SAME key — which is
    // the entire point of idempotency. crypto.randomUUID() is available
    // in all modern browsers (localhost and HTTPS).
    setIdempotencyKey(crypto.randomUUID());

    setStep("confirm"); // re-render → the confirm screen appears
  }

  // Confirm pressed: fire the real request with the stored key.
  async function confirmTransfer() {
    setSending(true); // button shows "Sending..." and can't be re-clicked
    setError("");

    try {
      // The actual network call. The Idempotency-Key header is attached
      // inside transferApi.sendTransfer().
      const response = await sendTransfer(username.trim(), amount, idempotencyKey);

      // 201 Created → backend returns TransferResponse:
      // { reference, amount, currency, status, sender_wallet_id,
      //   receiver_wallet_id, created_at }
      setReceipt(response.data);
      setStep("success");
    } catch (err) {
      // Special case: 409 means "this key is still processing". The user
      // should simply retry with the SAME key — so we stay on confirm.
      if (err.response?.status === 409) {
        setError("That transfer is still being processed. Press Confirm again in a moment.");
      } else {
        // 400 "Insufficient wallet balance." / "Cannot transfer to your
        // own wallet." / 429 rate limit / network failure... all mapped
        // to friendly sentences by getErrorMessage().
        setError(getErrorMessage(err));
        setStep("form"); // back to the form so the user can fix the issue
      }
    } finally {
      setSending(false);
    }
  }

  // Cancel from the confirm screen: back to the form. The old key is kept
  // but a fresh one is generated on the next Continue — a cancelled intent
  // should never collide with a future one.
  function handleCancel() {
    setStep("form");
  }

  // Success → "Done" restarts the flow completely (fresh form + fresh key).
  function handleDone() {
    setUsername("");
    setAmount("");
    setReceipt(null);
    setIdempotencyKey(null);
    setStep("form");
  }

  // ─────────────────────────────────────────────────────────────────────────
  // RENDER: the `step` value decides which screen JSX to return.
  // ─────────────────────────────────────────────────────────────────────────
  if (step === "success") {
    return (
      <div className="card success-card">
        <div className="success-circle">
          <Check size={36} strokeWidth={3} />
        </div>

        <h2>Transfer Successful</h2>
        <div className="success-amount">{formatCurrency(receipt?.amount)}</div>

        <div className="review-row">
          <span className="k">Sent to</span>
          <span className="v">@{username}</span>
        </div>
        <div className="review-row">
          <span className="k">Reference</span>
          <span className="v">{receipt?.reference}</span>
        </div>
        <div className="review-row">
          <span className="k">Status</span>
          <span className="v badge badge-completed">{receipt?.status}</span>
        </div>

        <div className="success-actions">
          <button className="btn btn-primary btn-block" onClick={handleDone}>
            Done
          </button>
          {/* receipt.id is not in TransferResponse — the transactions list
              is the reliable way to find this transfer afterwards. */}
          <Link className="btn btn-secondary btn-block" to="/transactions">
            View Transactions
          </Link>
        </div>
      </div>
    );
  }

  if (step === "confirm") {
    return (
      <div className="card card-pad send-card">
        <button className="back-btn" onClick={handleCancel}>
          <ArrowLeft size={18} /> Back
        </button>

        <h2 style={{ textAlign: "center", marginBottom: 4 }}>Confirm Transfer</h2>
        <p className="confirm-sub" style={{ textAlign: "center", color: "var(--text-secondary)", fontSize: 14, marginBottom: 12 }}>
          Please review the details before you send
        </p>

        {/* The big centered amount — the star of the review screen */}
        <div className="review-amount">{formatCurrency(amount)}</div>

        <div className="review-row">
          <span className="k">To</span>
          <span className="v">@{username}</span>
        </div>
        <div className="review-row">
          <span className="k">From</span>
          <span className="v">Your PayCore Wallet</span>
        </div>

        {error && (
          <div className="alert alert-error" role="alert">
            <AlertCircle size={17} />
            {error}
          </div>
        )}

        <div className="review-actions">
          <button className="btn btn-secondary" onClick={handleCancel} disabled={sending}>
            Cancel
          </button>
          <button className="btn btn-primary" onClick={confirmTransfer} disabled={sending}>
            {sending ? (
              <>
                <LoadingSpinner /> Sending...
              </>
            ) : (
              "Confirm Transfer"
            )}
          </button>
        </div>

        <div className="secure-note">
          <ShieldCheck size={15} />
          Protected by PayCore idempotency — double submissions can never send money twice.
        </div>
      </div>
    );
  }

  // ── step === "form" (default screen) ────────────────────────────────────
  return (
    <div className="card card-pad send-card">
      <h2 style={{ marginBottom: 4 }}>Send Money</h2>
      <p style={{ color: "var(--text-secondary)", fontSize: 14, marginBottom: 18 }}>
        Transfer instantly to any PayCore user.
      </p>

      {error && (
        <div className="alert alert-error" role="alert">
          <AlertCircle size={17} />
          {error}
        </div>
      )}

      <form onSubmit={handleContinue} noValidate>
        <div className="field">
          <label htmlFor="username">Receiver Username</label>
          <input
            id="username"
            className="input"
            placeholder="e.g. ahmed"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoFocus
          />
          {errors.username && <p className="field-error">{errors.username}</p>}
        </div>

        <div className="field">
          <label htmlFor="amount">Amount</label>
          <div className="amount-input-wrap">
            <span className="amount-prefix">Rs.</span>
            {/* inputMode="decimal" shows the numeric keypad on phones */}
            <input
              id="amount"
              className="input"
              inputMode="decimal"
              placeholder="0.00"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
          </div>
          {errors.amount && <p className="field-error">{errors.amount}</p>}

          {/* Quick amount chips — small UX touch from real wallet apps */}
          <div className="amount-chips">
            {[500, 1000, 5000].map((value) => (
              <button
                key={value}
                type="button"
                className="chip"
                onClick={() => setAmount(String(value))}
              >
                Rs. {value.toLocaleString()}
              </button>
            ))}
          </div>
        </div>

        <button className="btn btn-primary btn-block">
          Continue
        </button>
      </form>

      <div className="secure-note">
        <ShieldCheck size={15} />
        Money moves only after you confirm on the next screen.
      </div>
    </div>
  );
}

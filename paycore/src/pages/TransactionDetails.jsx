/**
 * TransactionDetails.jsx — a receipt-style view of one transaction.
 *
 * NEW CONCEPTS ON THIS PAGE:
 *   • useParams — React Router's hook that reads the DYNAMIC part of the
 *     URL. For the route /transactions/:id and the URL /transactions/42,
 *     useParams() gives { id: "42" }.
 *   • Guards before rendering — the id might be garbage ("abc") or the
 *     fetch might fail; every case renders a proper screen instead of a
 *     crash or a blank page.
 */
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, ArrowDownLeft, ArrowUpRight, AlertCircle } from "lucide-react";
import { getMyTransactions } from "../api/transactionApi";
import { getErrorMessage } from "../api/api";
import { formatCurrency } from "../utils/formatCurrency";
import { formatDate } from "../utils/formatDate";
import LoadingSpinner from "../components/LoadingSpinner";

export default function TransactionDetails() {
  // ":id" from the route path. Note: URL params are always STRINGS.
  const { id } = useParams();

  const [transaction, setTransaction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        // The backend exposes no single-transaction endpoint (only the
        // paginated history), so we pull the history and find our row by
        // id. Honest limitation — no fake endpoints invented. A scan of
        // a few pages is plenty for a demo app; a real backend would
        // offer GET /transactions/:id (worth requesting!).
        const response = await getMyTransactions(1, 100);
        const found = response.data.transactions.find(
          (t) => String(t.id) === String(id)
        );

        if (found) {
          setTransaction(found);
        } else {
          setError("Transaction not found. It may be outside your recent history.");
        }
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]); // re-run if the id in the URL changes

  // Loading / error screens come first — a component can simply return
  // different JSX in different states.
  if (loading) {
    return <LoadingSpinner fullPage label="Loading transaction..." />;
  }

  if (error || !transaction) {
    return (
      <div className="card card-pad" style={{ maxWidth: 480, margin: "40px auto" }}>
        <div className="alert alert-error" role="alert">
          <AlertCircle size={17} />
          {error || "Something went wrong."}
        </div>
        <Link to="/transactions" className="btn btn-secondary btn-block">
          Back to Transactions
        </Link>
      </div>
    );
  }

  const isDebit = transaction.entry_type === "debit";
  const label = isDebit ? "Money Transfer" : "Money Received";

  return (
    <div className="card card-pad" style={{ maxWidth: 480, margin: "0 auto" }}>
      <button className="back-btn" onClick={() => window.history.back()}>
        <ArrowLeft size={18} /> Back
      </button>

      {/* Hero section: direction icon + amount */}
      <div className="tx-hero">
        <span className={`tx-icon ${isDebit ? "debit" : "credit"}`}>
          {isDebit ? <ArrowUpRight size={22} /> : <ArrowDownLeft size={22} />}
        </span>
        <span
          className={`tx-amount ${isDebit ? "debit" : "credit"}`}
          style={{ fontSize: 30 }}
        >
          {isDebit ? "− " : "+ "}
          {formatCurrency(transaction.amount)}
        </span>
        <span className="tx-sub">{label}</span>
      </div>

      {/* Receipt rows */}
      <div style={{ marginTop: 18 }}>
        <div className="review-row">
          <span className="k">Reference</span>
          <span className="v">{transaction.reference}</span>
        </div>
        <div className="review-row">
          <span className="k">Type</span>
          <span className="v" style={{ textTransform: "capitalize" }}>
            {transaction.type}
          </span>
        </div>
        <div className="review-row">
          <span className="k">Status</span>
          <span className={`badge badge-${transaction.status.toLowerCase()}`}>
            {transaction.status}
          </span>
        </div>
        <div className="review-row">
          <span className="k">Date</span>
          <span className="v">{formatDate(transaction.created_at)}</span>
        </div>
        <div className="review-row">
          <span className="k">Direction</span>
          <span className="v">{isDebit ? "Money sent (debit)" : "Money received (credit)"}</span>
        </div>
      </div>
    </div>
  );
}

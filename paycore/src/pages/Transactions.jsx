/**
 * Transactions.jsx — full history with "Load more" pagination.
 *
 * NEW CONCEPTS ON THIS PAGE:
 *   • Deriving UI from data — the "Today"/"Yesterday" headings are not
 *     stored anywhere; they are COMPUTED from created_at at render time.
 *     When the data changes, the headings update automatically.
 *   • Cursor-less pagination — we keep a `page` number in state and ask
 *     the backend for the next page; results are APPENDED with the spread
 *     operator: setList([...list, ...newItems]).
 */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { AlertCircle, Inbox } from "lucide-react";
import { getMyTransactions } from "../api/transactionApi";
import { getErrorMessage } from "../api/api";
import { dateGroupLabel } from "../utils/formatDate";
import TransactionItem from "../components/TransactionItem";
import LoadingSpinner from "../components/LoadingSpinner";

const PAGE_SIZE = 10;

export default function Transactions() {
  const [transactions, setTransactions] = useState([]); // accumulated rows
  const [page, setPage] = useState(1);                  // next page to fetch
  const [total, setTotal] = useState(0);                // from the backend
  const [loading, setLoading] = useState(true);         // first page loading
  const [loadingMore, setLoadingMore] = useState(false); // Load more button
  const [error, setError] = useState("");

  useEffect(() => {
    loadPage(1); // fresh mount → load page 1
  }, []);

  // Separated from useEffect so the "Load more" button can reuse it.
  async function loadPage(pageToLoad) {
    // First load uses the big spinner; later pages use the button spinner.
    if (pageToLoad === 1) {
      setLoading(true);
    } else {
      setLoadingMore(true);
    }

    try {
      const response = await getMyTransactions(pageToLoad, PAGE_SIZE);
      const newItems = response.data.transactions;

      // Append instead of replace — that is what makes "Load more" work.
      setTransactions((prev) => [...prev, ...newItems]);
      setTotal(response.data.total);
      setPage(pageToLoad + 1); // remember where to continue next time
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }

  // "Load more" hidden when everything is already on screen.
  const hasMore = transactions.length < total;

  // ── Group transactions by day for the "Today / Yesterday" headings ──
  // reduce() builds a plain object: { "Today": [...], "08 September 2026": [...] }
  const groups = transactions.reduce((acc, t) => {
    const label = dateGroupLabel(t.created_at);
    if (!acc[label]) acc[label] = []; // first time seeing this day
    acc[label].push(t);
    return acc;
  }, {});

  return (
    <div>
      <div className="page-header">
        <h1>Transactions</h1>
        <p>Your complete PayCore activity</p>
      </div>

      <div className="card card-pad">
        {loading ? (
          <div className="panel-loading">
            <LoadingSpinner />
            <span>Loading transactions...</span>
          </div>
        ) : error ? (
          <div className="alert alert-error" role="alert">
            <AlertCircle size={17} />
            {error}
          </div>
        ) : transactions.length === 0 ? (
          <div className="empty-state">
            <Inbox size={40} />
            <strong>No transactions yet</strong>
            <span>Money you send or receive will appear here.</span>
          </div>
        ) : (
          <>
            {/* Object.entries turns { "Today": [...], ... } into
                [["Today", [...]], ...] so we can .map over it. */}
            {Object.entries(groups).map(([label, items]) => (
              <section key={label}>
                <h2 className="date-group-label">{label}</h2>
                <div className="tx-list">
                  {items.map((t) => (
                    // Each row links to the receipt page /transactions/:id
                    <Link
                      to={`/transactions/${t.id}`}
                      key={t.id}
                      className="tx-item"
                    >
                      <TransactionItem transaction={t} />
                    </Link>
                  ))}
                </div>
              </section>
            ))}

            {hasMore && (
              <div className="load-more">
                <button
                  className="btn btn-secondary"
                  onClick={() => loadPage(page)}
                  disabled={loadingMore}
                >
                  {loadingMore ? (
                    <>
                      <LoadingSpinner /> Loading...
                    </>
                  ) : (
                    "Load more"
                  )}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

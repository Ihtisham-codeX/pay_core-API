/**
 * Dashboard.jsx — home screen after login.
 *
 * NEW CONCEPTS ON THIS PAGE:
 *   • useEffect + async: useEffect's callback cannot be async directly
 *     (React expects a cleanup function, not a promise), so the standard
 *     pattern is: define an async function INSIDE, then call it.
 *   • Loading / error / empty — every screen that fetches data has three
 *     extra "states" besides success. Handling all four is what separates
 *     a real product from a tutorial.
 *   • Multiple pieces of state for one data load:
 *       data / loading / error is the classic trio.
 */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Send,
  ArrowLeftRight,
  Plus,
  Receipt,
  ArrowRight,
  Inbox,
  AlertCircle,
  TrendingUp,
  TrendingDown,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { getMyWallet } from "../api/walletApi";
import { getMyTransactions } from "../api/transactionApi";
import { getErrorMessage } from "../api/api";
import { formatCurrency } from "../utils/formatCurrency";
import BalanceCard from "../components/BalanceCard";
import TransactionItem from "../components/TransactionItem";
import QuickAction from "../components/QuickAction";
import LoadingSpinner from "../components/LoadingSpinner";

export default function Dashboard() {
  const { user } = useAuth(); // logged-in user from context (for greeting)

  // ── State trio for the wallet ────────────────────────────────────────
  const [wallet, setWallet] = useState(null);
  const [walletLoading, setWalletLoading] = useState(true);
  const [walletError, setWalletError] = useState("");

  // ── State trio for recent transactions ───────────────────────────────
  const [transactions, setTransactions] = useState([]);
  const [txLoading, setTxLoading] = useState(true);
  const [txError, setTxError] = useState("");

  // Runs once when the Dashboard mounts. Each block fails INDEPENDENTLY:
  // if the transactions endpoint is down, the balance still shows.
  useEffect(() => {
    async function loadWallet() {
      try {
        const response = await getMyWallet();
        setWallet(response.data);
      } catch (error) {
        setWalletError(getErrorMessage(error));
      } finally {
        setWalletLoading(false);
      }
    }

    async function loadTransactions() {
      try {
        // page_size=5 → only the 5 most recent for the dashboard panel.
        const response = await getMyTransactions(1, 5);
        setTransactions(response.data.transactions);
      } catch (error) {
        setTxError(getErrorMessage(error));
      } finally {
        setTxLoading(false);
      }
    }

    loadWallet();
    loadTransactions();
  }, []); // [] = run once, not on every re-render

  // Friendly time-based greeting, like real banking apps.
  const hour = new Date().getHours();
  const greeting =
    hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";

  // "Ali" — first name if available, username otherwise.
  const displayName = user?.first_name || user?.username || "there";

  // Totals for the small insights panel. reduce() folds the array into a
  // single number: it walks each transaction and adds to the accumulator.
  const totalIn = transactions
    .filter((t) => t.entry_type === "credit")
    .reduce((sum, t) => sum + Math.abs(t.amount), 0);
  const totalOutNum = transactions
    .filter((t) => t.entry_type === "debit")
    .reduce((sum, t) => sum + Math.abs(t.amount), 0);

  return (
    <div>
      {/* ── Greeting ─────────────────────────────────────────────────── */}
      <div className="greeting">
        <h1>
          {greeting}, {displayName} 👋
        </h1>
        <p>Welcome back to PayCore</p>
      </div>

      {/* ── Balance card ─────────────────────────────────────────────── */}
      <BalanceCard
        balance={wallet?.balance}
        loading={walletLoading}
        currency={wallet?.currency}
      />

      {/* Balance failed → inline alert, rest of the dashboard still usable */}
      {walletError && (
        <div className="alert alert-error" role="alert">
          <AlertCircle size={17} />
          {walletError}
        </div>
      )}

      {/* ── Quick actions ────────────────────────────────────────────── */}
      <div className="quick-actions">
        <QuickAction to="/send-money" icon={Send} label="Send Money" />
        <QuickAction to="/transactions" icon={ArrowLeftRight} label="Transactions" />
        {/* Backend has no top-up or bills endpoints yet — honest
            placeholders instead of fake features. */}
        <QuickAction icon={Plus} label="Add Money" disabled />
        <QuickAction icon={Receipt} label="Pay Bills" disabled />
      </div>

      {/* ── Two-column area: recent transactions + insights ──────────── */}
      <div className="dashboard-grid">
        <section className="card card-pad">
          <div className="panel-head">
            <h2 className="section-title">Recent Transactions</h2>
            <Link className="view-all" to="/transactions">
              View All <ArrowRight size={14} />
            </Link>
          </div>

          {txLoading ? (
            <div className="panel-loading">
              <LoadingSpinner />
            </div>
          ) : txError ? (
            <div className="alert alert-error" role="alert">
              <AlertCircle size={17} />
              {txError}
            </div>
          ) : transactions.length === 0 ? (
            <div className="empty-state">
              <Inbox size={40} />
              <strong>No transactions yet</strong>
              <span>Your recent activity will appear here.</span>
            </div>
          ) : (
            <div className="tx-list">
              {/* .map() turns each data object into JSX. The `key` prop
                  helps React track rows efficiently between renders. */}
              {transactions.map((t) => (
                <div className="tx-item" key={t.id}>
                  <TransactionItem transaction={t} />
                </div>
              ))}
            </div>
          )}
        </section>

        <aside className="card card-pad">
          <h2 className="section-title" style={{ marginBottom: 8 }}>
            This Session
          </h2>

          <div className="insight-row">
            <span className="k">
              <TrendingUp size={14} style={{ verticalAlign: "-2px" }} /> Money in
            </span>
            <span className="v" style={{ color: "var(--success)" }}>
              {formatCurrency(totalIn)}
            </span>
          </div>
          <div className="insight-row">
            <span className="k">
              <TrendingDown size={14} style={{ verticalAlign: "-2px" }} /> Money out
            </span>
            <span className="v">{formatCurrency(totalOutNum)}</span>
          </div>
          <div className="insight-row">
            <span className="k">Transactions</span>
            <span className="v">{transactions.length}</span>
          </div>
        </aside>
      </div>
    </div>
  );
}

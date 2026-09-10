/**
 * TransactionItem.jsx — one row in a transactions list.
 *
 * Used by BOTH the dashboard (recent transactions) and the transactions
 * page. When wrapped in a <Link> by the parent, clicking navigates to the
 * details page. Rendering "the same thing" in one component means fixes
 * apply everywhere at once.
 */
import { ArrowDownLeft, ArrowUpRight } from "lucide-react";
import { formatCurrency } from "../utils/formatCurrency";
import { formatDateTime } from "../utils/formatDate";

export default function TransactionItem({ transaction }) {
  // entry_type: "debit" = money left me (sent), "credit" = money came to me.
  const isDebit = transaction.entry_type === "debit";

  // Honest labels from the data the backend actually sends: the type plus
  // status. (The API has no counterparty name field.)
  const label = isDebit ? "Money Transfer" : "Money Received";

  return (
    <>
      {/* Circle icon: orange ↓ for outgoing, green ↑ for incoming */}
      <span className={`tx-icon ${isDebit ? "debit" : "credit"}`}>
        {isDebit ? (
          <ArrowUpRight size={19} />
        ) : (
          <ArrowDownLeft size={19} />
        )}
      </span>

      <span className="tx-info">
        <span className="tx-name">{label}</span>
        <span className="tx-sub">
          {formatDateTime(transaction.created_at)}
        </span>
      </span>

      <span className={`tx-amount ${isDebit ? "debit" : "credit"}`}>
        {/* formatCurrency strips the sign, so we add our own arrow so the
            direction is unmistakable even for colorblind users. */}
        {isDebit ? "− " : "+ "}
        {formatCurrency(transaction.amount)}
      </span>
    </>
  );
}

/**
 * App.jsx — the map of the whole application.
 *
 * NEW CONCEPTS ON THIS PAGE:
 *   • BrowserRouter enables client-side routing: React swaps pages in the
 *     browser without full reloads, like a native app.
 *   • <Routes>/<Route> — each Route matches a URL path to a component.
 *     `:id` is a dynamic segment (matches /transactions/42, /transactions/7...).
 *     `path="*"` catches anything unmatched → our 404 page.
 *   • A LAYOUT component with an <Outlet /> — the shared shell (sidebar +
 *     topbar + bottom nav) renders ONCE around every private page. The
 *     <Outlet /> is the hole where the matched page appears. Without it,
 *     every page would repeat the layout markup.
 *   • ProtectedRoute — wraps the layout so EVERY child route is guarded
 *     by the same doorman.
 */
import { BrowserRouter, Routes, Route, Outlet, Navigate } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";
import BottomNavigation from "./components/BottomNavigation";

// Pages
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import SendMoney from "./pages/SendMoney";
import Transactions from "./pages/Transactions";
import TransactionDetails from "./pages/TransactionDetails";
import Profile from "./pages/Profile";
import NotFound from "./pages/NotFound";

/**
 * AppLayout — the authenticated shell. ProtectedRoute guarantees that by
 * the time this renders, a user is logged in.
 */
function AppLayout() {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-area">
        <Navbar />
        {/* The matched child route renders here */}
        <main className="page-content">
          <Outlet />
        </main>
      </div>
      <BottomNavigation />
    </div>
  );
}

export default function App() {
  return (
    // AuthProvider wraps EVERYTHING so useAuth() works on any page,
    // including Login (which reads login() from it).
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes — no session required */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Private routes — all wrapped in the layout + guard */}
          <Route
            element={
              <ProtectedRoute>
                <AppLayout />
              </ProtectedRoute>
            }
          >
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/send-money" element={<SendMoney />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/transactions/:id" element={<TransactionDetails />} />
            <Route path="/profile" element={<Profile />} />
          </Route>

          {/* Send "/" to the dashboard (ProtectedRoute bounces guests to
              /login automatically). */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />

          {/* Catch-all 404 for unknown URLs */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

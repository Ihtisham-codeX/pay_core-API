/**
 * main.jsx — the entry point Vite loads first.
 *
 * Two lines matter:
 *   1. import "./index.css"  → global theme applied before anything renders.
 *   2. <App /> inside the #root div → React takes over the page.
 *
 * StrictMode is a development-only helper that double-invokes some logic to
 * surface bugs early. It renders nothing and disappears in production.
 */
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);

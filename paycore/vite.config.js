import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // The dev server runs on 5173. Every request starting with "/api" is
    // forwarded to the FastAPI backend on port 8000, and the "/api" prefix
    // is STRIPPED (rewrite) so the backend sees its normal paths:
    //   browser:  /api/auth/login   →  backend:  /auth/login
    //
    // WHY A PROXY? (important, read this)
    //   The backend stores the JWT inside HttpOnly cookies. Cookies are
    //   only attached automatically when frontend and backend share the
    //   same "origin" (same host + port). During development they run on
    //   different ports (5173 vs 8000), so instead of configuring CORS on
    //   the backend, Vite re-writes the requests for us. The browser thinks
    //   everything comes from localhost:5173 — cookies just work.
    //
    // WHY THE "/api" PREFIX? (clever but simple)
    //   The React app ALSO has a page at /transactions. Without the prefix,
    //   refreshing that page would send the request to the BACKEND (proxy
    //   match) instead of loading the app — you'd see raw JSON. With
    //   "/api" only real API traffic is proxied; page URLs stay clean.
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})

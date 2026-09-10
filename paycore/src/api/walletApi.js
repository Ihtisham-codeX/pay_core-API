import api from "./api";

export function getMyWallet() {
  return api.get("/wallets/me");
}

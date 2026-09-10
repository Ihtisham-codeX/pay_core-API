import api from "./api";

export function getMyTransactions(page = 1, pageSize = 10) {

  return api.get("/transactions/", { params: { page, page_size: pageSize } });
}

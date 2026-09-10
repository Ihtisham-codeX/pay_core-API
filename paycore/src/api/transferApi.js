
import api from "./api";

export function sendTransfer(receiverUsername, amount, idempotencyKey) {
  return api.post(
    "/transfers/",
    { receiver_username: receiverUsername, amount: Number(amount) },
    {
      headers: { "Idempotency-Key": idempotencyKey },
    }
  );
}

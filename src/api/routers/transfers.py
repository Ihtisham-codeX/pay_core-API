from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse
from src.schemas.transfer      import TransferRequest, TransferResponse
from src.services              import transfer_service, audit_service
from src.services.redis_service import RedisService, RedisUnavailableError
from src.security.dependencies import get_current_user, enforce_user_rate_limit
from src.exceptions.handlers import (
    IdempotencyInProgressException,
    IdempotencyKeyRequiredException,
    RedisUnavailableException,
)


router = APIRouter(prefix="/transfers", tags=["Transfers"])


def _redis() -> RedisService:
    return RedisService()


@router.post("/", response_model=TransferResponse, status_code=201)
def create_transfer(
    request:          Request,
    body:             TransferRequest,
    user:             dict = Depends(get_current_user),
    _:                None = Depends(enforce_user_rate_limit),
    idempotency_key:  str | None = Header(None, alias="Idempotency-Key"),
):
    """
    Send money to another user.

    Idempotency is gated in Redis (SET NX EX), not PostgreSQL.
    PostgreSQL remains the permanent ledger for the transfer itself.
    """
    user_id = user["user_id"]

    if not idempotency_key:
        raise IdempotencyKeyRequiredException()

    redis_svc = _redis()
    if not redis_svc.is_available():
        raise RedisUnavailableException()

    redis_key = redis_svc.idempotency_key(user_id, idempotency_key)

    try:
        claimed = redis_svc.claim_idempotency_key(redis_key)
    except RedisUnavailableError:
        raise RedisUnavailableException()

    if not claimed:
        record = redis_svc.get_idempotency_record(redis_key)
        if record is None:
            raise RedisUnavailableException()
        if record["status"] == "PENDING":
            raise IdempotencyInProgressException()
        return JSONResponse(content=record["result"], status_code=200)

    try:
        result = transfer_service.execute_transfer(
            sender_user_id    = user_id,
            receiver_username = body.receiver_username,
            amount_major      = body.amount,
        )
    except Exception:
        redis_svc.release_idempotency_key(redis_key)
        raise

    redis_svc.complete_idempotency(redis_key, result.model_dump(mode="json"))

    audit_service.log(
        user_id     = user_id,
        action      = audit_service.TRANSFER_COMPLETED,
        resource    = "transaction",
        resource_id = result.reference,
        ip_address  = request.client.host,
        metadata    = {"amount": body.amount, "to": body.receiver_username},
    )

    return result

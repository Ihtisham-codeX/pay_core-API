import json
from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse
from src.schemas.transfer      import TransferRequest, TransferResponse
from src.services              import transfer_service, audit_service
from src.repositories          import idempotency_repository
from src.security.dependencies import get_current_user


router = APIRouter(prefix="/transfers", tags=["Transfers"])

_ENDPOINT = "POST /transfers"

#_________________________________________________________________________________________

@router.post("/", response_model=TransferResponse, status_code=201)
#_________________________________________________________________________________________

def create_transfer(
    request:          Request,
    body:             TransferRequest,
    user:             dict = Depends(get_current_user),
    idempotency_key:  str | None = Header(None, alias="Idempotency-Key"),
):
    """
    Send money to another user.

    Idempotency:
      Include an  Idempotency-Key: <uuid>  header with every request.
      If the same key is sent again, the saved response is returned
      immediately — money is NOT moved a second time.

    Workflow:
      1. Check Idempotency-Key against DB
      2. If found → return cached response
      3. If not   → execute transfer → save key + response → return
      4. Log audit event
    """
    user_id = user["user_id"]

#_________________________________________________________________________________________

    # Idempotency check 
#_________________________________________________________________________________________

    if idempotency_key:
        existing = idempotency_repository.find(
            key      = idempotency_key,
            user_id  = user_id,
            endpoint = _ENDPOINT,
        )
        if existing:
            # Key was already used , return the saved response 
            saved_body = json.loads(existing[4])   # index 4 = response_body
            return JSONResponse(content=saved_body, status_code=200)

#_________________________________________________________________________________________

    # Execute the transfer 
#_________________________________________________________________________________________

    result = transfer_service.execute_transfer(
        sender_user_id    = user_id,
        receiver_username = body.receiver_username,
        amount_major      = body.amount,
    )

#_________________________________________________________________________________________

    # Step 3: Save idempotency key + response 
#_________________________________________________________________________________________

    if idempotency_key:
        idempotency_repository.save(
            key           = idempotency_key,
            user_id       = user_id,
            endpoint      = _ENDPOINT,
            response_body = result.model_dump_json(),
        )
#_________________________________________________________________________________________

    # Audit log                                                                        
#_________________________________________________________________________________________

    audit_service.log(
        user_id     = user_id,
        action      = audit_service.TRANSFER_COMPLETED,
        resource    = "transaction",
        resource_id = result.reference,
        ip_address  = request.client.host,
        metadata    = {"amount": body.amount, "to": body.receiver_username},
    )

    return result


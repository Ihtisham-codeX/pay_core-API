import uuid
from src.database.connection import conn
from src.repositories import user_repository, wallet_repository, transaction_repository
from src.schemas.transfer import TransferResponse
from src.exceptions.handlers import (
    UserNotFoundException,
    WalletNotFoundException,
    WalletFrozenException,
    InsufficientBalanceException,
    SelfTransferException,
)
from src.config import settings


_MINOR_UNIT_DIVISOR = 100   # 1 PKR = 100 paisa

#_________________________________________________________________________________________

def _generate_reference() -> str:
#_________________________________________________________________________________________

    """Generate a unique transaction reference"""
    return f"TXN-{uuid.uuid4().hex[:8].upper()}"

#_________________________________________________________________________________________

def execute_transfer(sender_user_id: int, receiver_username: str, amount_major: float) -> TransferResponse:
#_________________________________________________________________________________________

    """
    Transfer money from the authenticated user's wallet to another user's wallet with complete
    workflow and failure at any point will cause the roll back
    """
#_________________________________________________________________________________________

    # Convert to minor units
#_________________________________________________________________________________________

    amount_minor = int(round(amount_major, 2) * 100)
#_________________________________________________________________________________________

    #  Validate receiver 
#_________________________________________________________________________________________

    receiver_user = user_repository.find_by_username(receiver_username)
    if receiver_user is None:
        raise UserNotFoundException()

    if receiver_user[0] == sender_user_id:
        raise SelfTransferException()
#_________________________________________________________________________________________

    # Get both wallet records 
#_________________________________________________________________________________________

    sender_wallet_row   = wallet_repository.find_by_user_id(sender_user_id)
    receiver_wallet_row = wallet_repository.find_by_user_id(receiver_user[0])

    if sender_wallet_row is None:
        raise WalletNotFoundException()
    if receiver_wallet_row is None:
        raise WalletNotFoundException()

    sender_wallet_id   = sender_wallet_row[0]
    receiver_wallet_id = receiver_wallet_row[0]
#_________________________________________________________________________________________

    # Check wallet statuses before entering the DB transaction
#_________________________________________________________________________________________

    if sender_wallet_row[4] != "active":      # index 4 = status
        raise WalletFrozenException()
    if receiver_wallet_row[4] != "active":
        raise WalletFrozenException()


    cursor = conn.cursor()

    try:
#_________________________________________________________________________________________

        # Lock BOTH wallet rows
#_________________________________________________________________________________________

        first_id, second_id = sorted([sender_wallet_id, receiver_wallet_id])
        locked_first  = wallet_repository.find_for_update(first_id,  cursor)
        locked_second = wallet_repository.find_for_update(second_id, cursor)

#_________________________________________________________________________________________

        # Map locked rows back to sender/receiver
#_________________________________________________________________________________________

        if first_id == sender_wallet_id:
            locked_sender   = locked_first
            locked_receiver = locked_second
        else:
            locked_sender   = locked_second
            locked_receiver = locked_first
#_________________________________________________________________________________________

        # read balance from the locked row and validate
#_________________________________________________________________________________________
    
        sender_balance = locked_sender[2]     # index 2 = balance (minor units)

        if sender_balance < amount_minor:
            conn.rollback()
            raise InsufficientBalanceException()
#_________________________________________________________________________________________

        # Debit sender and credit receiver 
#_________________________________________________________________________________________

        wallet_repository.debit(sender_wallet_id, amount_minor, cursor)

        wallet_repository.credit(receiver_wallet_id, amount_minor, cursor)
#_________________________________________________________________________________________

        # Insert transaction record
#_________________________________________________________________________________________

        reference = _generate_reference()
        txn_row = transaction_repository.insert_transaction(
            reference          = reference,
            sender_wallet_id   = sender_wallet_id,
            receiver_wallet_id = receiver_wallet_id,
            amount             = amount_minor,
            currency           = settings.DEFAULT_CURRENCY,
            cursor             = cursor,
        )
#_________________________________________________________________________________________

        # Insert double-entry ledger rows
#_________________________________________________________________________________________

        transaction_repository.insert_ledger_entry(
            transaction_id = txn_row[0],
            wallet_id      = sender_wallet_id,
            entry_type     = "debit",
            amount         = amount_minor,
            cursor         = cursor,
        )
        transaction_repository.insert_ledger_entry(
            transaction_id = txn_row[0],
            wallet_id      = receiver_wallet_id,
            entry_type     = "credit",
            amount         = amount_minor,
            cursor         = cursor,
        )

        # all changes finalised, locks released
        conn.commit()

    except Exception:
        # incase of any error roll back every change made since the cursor was opened
        conn.rollback()
        raise   # re-raise the original exception to the router

    finally:
        cursor.close()
#_________________________________________________________________________________________

    #  Build and return the response
#_________________________________________________________________________________________

    return TransferResponse(
        reference          = txn_row[1],
        amount             = txn_row[4] / _MINOR_UNIT_DIVISOR,  # minor → major
        currency           = txn_row[5],
        status             = txn_row[7],
        sender_wallet_id   = txn_row[2],
        receiver_wallet_id = txn_row[3],
        created_at         = txn_row[8],
    )

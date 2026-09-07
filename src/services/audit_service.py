import json
from src.repositories import audit_repository



# Action Constants
# Typo caught immediately by Python , All logs use identical strings  , Full autocomplete support

USER_REGISTERED     = "USER_REGISTERED"
USER_LOGIN          = "USER_LOGIN"
USER_LOGOUT         = "USER_LOGOUT"
PROFILE_UPDATED     = "PROFILE_UPDATED"

TRANSFER_COMPLETED  = "TRANSFER_COMPLETED"
TRANSFER_FAILED     = "TRANSFER_FAILED"


# Log Helper

def log(
    user_id:      int | None,
    action:       str,
    resource:     str | None = None,
    resource_id:  str | None = None,
    ip_address:   str | None = None,
    metadata:    dict | None = None,
) -> None:
    """Record an audit event. Converts metadata dict to JSON string for storage."""
    metadata_str = json.dumps(metadata) if metadata else None

    audit_repository.log(
        user_id     = user_id,
        action      = action,
        resource    = resource,
        resource_id = resource_id,
        ip_address  = ip_address,
        metadata    = metadata_str,
    )

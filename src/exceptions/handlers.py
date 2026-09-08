from fastapi import HTTPException


########### Auth Exceptions ###########

class UserAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Email or username already registered.")


class InvalidCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid email or password.")


class LoginRequiredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Authentication required. Please log in.")


class InvalidAccessTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid or expired access token.")


class MissingRefreshTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="No refresh token provided.")


class InvalidRefreshTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid or expired refresh token.")


class RefreshTokenRevokedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Refresh token has been revoked. Please log in again.")


############ Authorization Exceptions ###########

class AdminOnlyException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Access denied. Admins only.")


########### User Exceptions ###########

class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="User not found.")


class AccountSuspendedException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Your account has been suspended.")


########### Wallet Exceptions ###########

class WalletNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Wallet not found.")


class WalletAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="A wallet already exists for this user.")


class WalletFrozenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Wallet is frozen. Contact support.")


class InsufficientBalanceException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Insufficient wallet balance.")


################### Transfer Exceptions ####################

class SelfTransferException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Cannot transfer to your own wallet.")


class RedisUnavailableException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=503,
            detail="Service temporarily unavailable. Please retry shortly.",
        )


class RateLimitExceededException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=429,
            detail="Too many requests. Please wait and try again.",
        )


class IdempotencyInProgressException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=409,
            detail="A request with this Idempotency-Key is still in progress. Retry shortly.",
        )


class IdempotencyKeyRequiredException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Idempotency-Key header is required for transfers.",
        )

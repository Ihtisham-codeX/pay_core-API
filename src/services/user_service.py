import json
from src.repositories import user_repository
from src.schemas.user   import UserResponse, UpdateProfileRequest
from src.exceptions.handlers import UserNotFoundException
from src.services.redis_service import RedisService

#_________________________________________________________________________________________

def _row_to_user_response(row: tuple) -> UserResponse:
#_________________________________________________________________________________________

    """Map a raw DB tuple to a UserResponse schema.
    Column order must match the SELECT in user_repository.
    """
    return UserResponse(
        id         = row[0],
        email      = row[1],
        username   = row[2],
        # row[3] = password_hash — intentionally skipped
        first_name = row[4],
        last_name  = row[5],
        phone      = row[6],
        role       = row[7],
        status     = row[8],
        created_at = row[9],
    )

#_________________________________________________________________________________________

def get_profile(user_id: int) -> UserResponse:
#_________________________________________________________________________________________

    redis_svc = RedisService()
    cache_key = redis_svc.cache_user_key(user_id)
    cached = redis_svc.cache_get(cache_key)
    if cached is not None:
        return UserResponse.model_validate(json.loads(cached))

    row = user_repository.find_by_id(user_id)
    if row is None:
        raise UserNotFoundException()
    profile = _row_to_user_response(row)
    redis_svc.cache_set(cache_key, profile.model_dump_json())
    return profile

#_________________________________________________________________________________________

def update_profile(user_id: int, data: UpdateProfileRequest) -> UserResponse:
#_________________________________________________________________________________________

    row = user_repository.update_profile(
        user_id    = user_id,
        first_name = data.first_name,
        last_name  = data.last_name,
        phone      = data.phone,
    )
    if row is None:
        raise UserNotFoundException()
    redis_svc = RedisService()
    redis_svc.cache_invalidate(redis_svc.cache_user_key(user_id))
    return _row_to_user_response(row)

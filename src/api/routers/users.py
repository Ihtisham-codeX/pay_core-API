from fastapi import APIRouter, Depends
from src.schemas.user     import UserResponse, UpdateProfileRequest
from src.services         import user_service
from src.security.dependencies import get_current_user



router = APIRouter(prefix="/users", tags=["Users"])

#_________________________________________________________________________________________

@router.get("/me", response_model=UserResponse)
#_________________________________________________________________________________________

def get_my_profile(user: dict = Depends(get_current_user)):
    """
    Return the authenticated user's profile.

    Workflow:
      JWT payload (via middleware) → extract user_id
      → user_service.get_profile() → UserResponse (no password_hash)
    """
    return user_service.get_profile(user_id=user["user_id"])

#_________________________________________________________________________________________

@router.patch("/me", response_model=UserResponse)
#_________________________________________________________________________________________

def update_my_profile(body: UpdateProfileRequest, user: dict = Depends(get_current_user)):
    """
    Update mutable profile fields (first_name, last_name, phone).
    Fields omitted from the body are left unchanged (COALESCE in SQL).
    """
    return user_service.update_profile(user_id=user["user_id"], data=body)

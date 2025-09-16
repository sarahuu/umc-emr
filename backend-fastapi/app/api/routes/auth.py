from fastapi import APIRouter
from datetime import timedelta
from app.services.odoo_client import OdooClient
from app.core.security import create_access_token
from app.core.config import settings
from app.schemas.token import Token
from app.schemas.user import LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])
odoo_client = OdooClient()

@router.post("/login", response_model=Token)
def login(request: LoginRequest):
    uid = odoo_client.authenticate(request.email, request.password)
    if not uid:
        raise ValueError("Invalid credentials")
    user_info = odoo_client.get_user_info(uid, request.password)
    if not user_info:
        raise ValueError("User not found")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"email": user_info["email"],"uid": user_info["id"],"name":user_info["name"],"date_of_birth":user_info["date_of_birth"],
                                             "gender":user_info["gender"],"phone":user_info["phone"],"user_id":user_info["user_id"]},expires_delta=access_token_expires,)
    return Token(access_token=access_token)

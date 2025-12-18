from fastapi import APIRouter, Response, Depends, HTTPException, status
from api.schemas import Token
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_db
from api.actions.auth import authenticate_user, config, security, get_current_user_from_token
from db.models.models import UsersOrm
from authx.exceptions import JWTDecodeError


login_router = APIRouter()

@login_router.post("/token", response_model=Token)
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)) -> Token:
    user = await authenticate_user(email=form_data.username, password=form_data.password, session=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="incorrect username or pass")
    
    access_token = security.create_access_token(uid=str(user.user_id))
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, access_token)
    return {"access_token": access_token, "token_type": "bearer"}

@login_router.get("/test_auth")
async def test(current_user: UsersOrm = Depends(get_current_user_from_token)):
    try:
        return {"success": True, "current_user": current_user}
    except JWTDecodeError as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired or invalid")     



















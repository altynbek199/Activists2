from authx import AuthX, AuthXConfig, RequestToken
from settings import settings
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from db.dals import UserDAL
from api.schemas import UserShowDTO
from sqlalchemy.dialects.postgresql import UUID
from typing import Optional
from hashing import Hasher
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from db.database import get_db
from jose import JWTError
from db.models import UsersOrm


config = AuthXConfig(
    JWT_SECRET_KEY=settings.SECRET_KEY,
    JWT_ACCESS_COOKIE_NAME="my_access_token",
    JWT_TOKEN_LOCATION=["cookies"],
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
)

security = AuthX(config=config)

async def _get_user_by_email_for_auth(email: str, session: AsyncSession) -> UsersOrm:
    async with session.begin():
        user_dal = UserDAL(db_session=session)
        return await user_dal.get_user_by_email(email=email)
    
async def _get_user_by_id_for_auth(user_id: UUID, session: AsyncSession) -> UsersOrm:
    async with session.begin():
        user_dal = UserDAL(db_session=session)
        return await user_dal.get_user_by_id(user_id=user_id)

async def authenticate_user(email: str, password: str, session: AsyncSession) -> Optional[UserShowDTO]:
    user = await _get_user_by_email_for_auth(email=email, session=session)
    if user is None:
         return None
         
    if not Hasher.verify_password(plain_password=password, hashed_password=user.hashed_password):
        return None
    return user       
    

# Use for Dependancy

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")

async def get_current_user_from_token(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> UsersOrm:
        cred_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

        try:
             request_token = RequestToken(token=token, type="access", location="headers")
             payload = security.verify_token(request_token)
             user_id: str = payload.sub
             print("Username extracted is:", user_id)
             
             if user_id is None:
                  raise cred_exception
        except JWTError:
             raise cred_exception
        user = await _get_user_by_id_for_auth(user_id, session=db)
        if user is None:
             raise cred_exception
        return user      









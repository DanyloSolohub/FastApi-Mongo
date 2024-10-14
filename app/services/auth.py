from datetime import datetime, timedelta, timezone

import jwt
from core.config import settings
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from models import User
from passlib.context import CryptContext
from starlette import status

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/v1/accounts/token')


class AuthService:
    @staticmethod
    async def get_user(username: str) -> User | None:
        return await User.find_one(User.username == username)

    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    @classmethod
    async def authenticate_user(cls, username: str, password: str):
        user = await cls.get_user(username)
        if not user or not cls.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        except (jwt.exceptions.DecodeError, jwt.exceptions.ExpiredSignatureError):
            raise credentials_exception
        else:
            username: str = payload.get('sub')
            if username is None:
                raise credentials_exception
        user = await AuthService.get_user(username)
        if user is None:
            raise credentials_exception
        return user

    @staticmethod
    async def get_current_active_user(current_user: User = Depends(get_current_user)):
        current_user = await current_user
        if not current_user.is_active:
            raise HTTPException(status_code=400, detail='Inactive user')
        return current_user

from .token_interface import TokenInterface
from jose import jwt, JWTError
from fastapi import HTTPException, status
from datetime import datetime, timedelta


class TokenService(TokenInterface):
    async def decode_refresh_token(self, refresh_token: str, secret_key: str, algorithm: str) -> dict:
        try:
            payload: dict = jwt.decode(token=refresh_token, key=secret_key, algorithms=algorithm)
            if payload['token_type'] == 'refresh_token':
                return payload
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid type for token')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Refresh token expired')
        except jwt.JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')

    async def create_token(self, data: dict, token_type: str, secret_key: str, exp_time: int, algorithm: str) -> str:
        _data = data.copy()
        expire_time = datetime.utcnow() + timedelta(minutes=exp_time)
        _data.update({'iat': datetime.utcnow(), 'exp': expire_time, 'token_type': token_type})
        return jwt.encode(_data, key=secret_key, algorithm=algorithm)

    async def decode_access_token(self, token: str, secret_key: str, algorithm: str) -> dict:
        try:
            payload: dict = jwt.decode(token=token, key=secret_key, algorithms=algorithm)
            if payload['token_type'] == 'access_token':
                return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Access token expired')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate credentials', headers={"WWW-Authenticate": "Bearer"})

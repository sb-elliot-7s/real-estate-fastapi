from passlib.context import CryptContext
from .password_interface import PasswordInterface


class PasswordService(PasswordInterface):

    def __init__(self, context: CryptContext):
        self._context = context

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self._context.verify(secret=plain_password, hash=hashed_password)

    async def hashed_password(self, password: str) -> str:
        return self._context.hash(secret=password)


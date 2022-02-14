from abc import ABC, abstractmethod


class PasswordInterface(ABC):

    @abstractmethod
    async def verify_password(self, plain_password: str, hashed_password: str) -> bool: pass

    @abstractmethod
    async def hashed_password(self, password: str) -> str: pass

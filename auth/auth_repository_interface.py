from abc import ABC, abstractmethod
from typing import Optional
from profile.models import User


class AuthRepositoryInterface(ABC):

    # @abstractmethod
    # async def retrieve_user_by_params(self, params: dict) -> User: pass

    @abstractmethod
    async def retrieve_user_by_email(self, email: str) -> User: pass

    @abstractmethod
    async def retrieve_user_by_username(self, username: str) -> User: pass

    @abstractmethod
    async def save_user(self, username: str, password: str, email: Optional[str]) -> User: pass

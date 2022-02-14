from abc import ABC, abstractmethod


class TokenInterface(ABC):
    @abstractmethod
    async def create_token(self, data: dict, token_type: str, secret_key: str, exp_time: int, algorithm: str) -> str: pass

    # retrieve access_token and return username
    @abstractmethod
    async def decode_access_token(self, token: str, secret_key: str, algorithm: str) -> dict: pass

    # retrieve refresh_token and return username
    @abstractmethod
    async def decode_refresh_token(self, refresh_token: str, secret_key: str, algorithm: str) -> dict: pass

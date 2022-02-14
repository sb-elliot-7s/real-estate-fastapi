import pytest
from passlib.context import CryptContext
from ..password_service import PasswordService


class TestPasswordService:

    @pytest.fixture
    def get_password_security(self):
        return PasswordService(context=CryptContext(schemes=['bcrypt'], deprecated='auto'))

    @pytest.mark.parametrize('password', ('1234567890', 'los-angeles'))
    @pytest.mark.asyncio
    async def test_successfully_verify_passwords(self, get_password_security, password):
        hashed_password = await get_password_security.hashed_password(password=password)
        assert await get_password_security.verify_password(plain_password=password, hashed_password=hashed_password)

import pytest
from httpx import AsyncClient


class TestProfileController:
    MORE_THEN_255 = "When we create, modify or delete a file, these changes will happen in our local and won't be included in the next commit " \
                    "(unless we change the configurations).We need to use the git add command to include the changes of a file(s) into our next " \
                    "commit.12345"

    @pytest.mark.parametrize('username, email, first_name, last_name, phone',
                             [('first_user', 'something@gmail.com', 'elliot', 'alderson', '7000000000')])
    @pytest.mark.asyncio
    async def test_successfully_update_profile(self, first_user_client_with_jwt: AsyncClient, username: str, email: str, first_name: str,
                                               last_name: str, phone: str):
        data = {'email': email, 'username': username, 'phone': phone, 'first_name': first_name, 'last_name': last_name}
        response = await first_user_client_with_jwt.put(url='/profile/', json=data)
        assert response.status_code == 200
        assert response.json()['email'] == email
        assert response.json()['username'] == username
        assert response.json()['phone'] == phone
        assert response.json()['last_name'] == last_name
        assert response.json()['first_name'] == first_name

    @pytest.mark.asyncio
    async def test_failure_update_profile_not_authenticated(self, client_without_jwt: AsyncClient):
        data = {'email': 'new@gmail.com'}
        response = await client_without_jwt.put(url='/profile/', json=data)
        assert response.status_code == 401

    @pytest.mark.parametrize('first_name, last_name, status,', [(MORE_THEN_255, MORE_THEN_255, 422)])
    @pytest.mark.asyncio
    async def test_failure_update_profile(self, first_user_client_with_jwt: AsyncClient, first_name, last_name, status):
        data = {'first_name': first_name, 'last_name': last_name}
        response = await first_user_client_with_jwt.put(url='/profile/', json=data)
        assert response.status_code == status

    @pytest.mark.asyncio
    async def test_successfully_delete_user(self, first_user_client_with_jwt: AsyncClient):
        response = await first_user_client_with_jwt.delete(url='/profile/')
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_failure_delete_user_not_authenticated(self, client_without_jwt: AsyncClient):
        response = await client_without_jwt.delete(url='/profile/')
        assert response.status_code == 401

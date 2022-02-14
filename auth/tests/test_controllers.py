import asyncio
import pytest
from httpx import AsyncClient
from collections import namedtuple


class TestAuthController:
    HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}
    USERNAME_FIELD_REQUIRED = [{'loc': ['body', 'username'], 'msg': 'field required', 'type': 'value_error.missing'}]
    PASSWORD_FIELD_REQUIRED = [{'loc': ['body', 'password'], 'msg': 'field required', 'type': 'value_error.missing'}]
    LESS_THAN_10_CHARACTERS_IN_PASSWORD = [
        {'loc': ['body', 'password'], 'msg': 'ensure this value has at least 10 characters', 'type': 'value_error.any_str.min_length',
         'ctx': {'limit_value': 10}}]
    SignUpUser = namedtuple('SignUpUser', 'username, password, email')

    elliot = SignUpUser(username='elliot', password='1234567890', email='elliot@gmail.com')
    xxxxx = SignUpUser(username='xxxxy', password='1234567890', email=None)
    yyyyy = SignUpUser(username='yyyyy', password='1234567890', email=None)
    tommy = SignUpUser(username='tommy', password='1234567890', email='tommy@gmail.com')
    alice = SignUpUser(username='alice', password='1234567890', email='alice@gmail.com')
    fake_elliot = SignUpUser(username='fake_elliot', password='1234567890', email='elliot@gmail.com')

    @pytest.mark.parametrize('username, password, email, status_code', [(*elliot, 201), (*tommy, 201)])
    @pytest.mark.asyncio
    async def test_signup(self, client_without_jwt: AsyncClient, username, password, email, status_code):
        response = await client_without_jwt.post(url='/auth/signup', json={'username': username, 'email': email, 'password': password})
        assert response.status_code == status_code
        assert response.json()['username'] == username
        assert response.json()['email'] == email

    @pytest.mark.parametrize('username, password, email, status_code, key, value', [
        ('jack', '123456789', None, 422, 'detail', LESS_THAN_10_CHARACTERS_IN_PASSWORD),
        (elliot.username, elliot.password, elliot.email, 400, 'detail', 'User with this username or email exists'),
        (fake_elliot.username, fake_elliot.password, fake_elliot.email, 400, 'detail', 'User with this email exists')
    ])
    @pytest.mark.asyncio
    async def test_failure_signup(self, client_without_jwt: AsyncClient, username, password, email, status_code, key, value):
        res = await client_without_jwt.post(url='/auth/signup', json={'username': username, 'password': password, 'email': email})
        assert res.status_code == status_code
        assert res.json()[key] == value

    @pytest.mark.parametrize('username, password, status_code', [(elliot.username, elliot.password, 200), (tommy.username, tommy.password, 200)])
    @pytest.mark.asyncio
    async def test_successfully_login(self, client_without_jwt: AsyncClient, username, password, status_code):
        response = await client_without_jwt.post(url='/auth/login', data={'username': username, 'password': password}, headers=self.HEADERS)
        assert 'access_token' in response.json()
        assert 'refresh_token' in response.json()
        assert response.status_code == status_code

    @pytest.mark.parametrize('username, password, status_code, key, value', [
        (elliot.username, 'wrong-password', 400, 'detail', 'Incorrect username or password'),
        (alice.username, alice.password, 400, 'detail', 'Incorrect username or password'),
        (None, '1234567890', 422, 'detail', USERNAME_FIELD_REQUIRED),
        (elliot.username, None, 422, 'detail', PASSWORD_FIELD_REQUIRED),
        (xxxxx.username, xxxxx.password, 400, 'detail', 'Incorrect username or password'),
        (yyyyy.username, yyyyy.password, 400, 'detail', 'Incorrect username or password')
    ])
    @pytest.mark.asyncio
    async def test_failure_login(self, client_without_jwt: AsyncClient, username, password, status_code, key, value):
        res = await client_without_jwt.post(url='/auth/login', data={'username': username, 'password': password}, headers=self.HEADERS)
        assert res.status_code == status_code
        assert res.json()[key] == value
        assert 'access_token' not in res.json()

    @pytest.mark.parametrize('username, password', [(elliot.username, elliot.password)])
    @pytest.mark.asyncio
    async def test_retrieve_access_and_refresh_token(self, client_without_jwt: AsyncClient, first_user_client_with_jwt: AsyncClient, username,
                                                     password):
        response = await client_without_jwt.post(url='/auth/login', data={'username': username, 'password': password})
        refresh_token = response.json()['refresh_token']
        await asyncio.sleep(1)
        new_response = await client_without_jwt.post(url='/auth/refresh_token', json={'refresh_token': refresh_token})
        refresh_token = response.json()['refresh_token']
        data = {'refresh_token': refresh_token}
        new_response = await client_without_jwt.post(url='/auth/refresh_token', json=data)
        updated_refresh_token = new_response.json()['refresh_token']
        assert 'refresh_token' in new_response.json()
        assert 'access_token' in new_response.json()
        assert refresh_token != updated_refresh_token
        assert new_response.status_code == 201

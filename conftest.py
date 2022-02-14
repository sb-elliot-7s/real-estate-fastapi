import asyncio
import pytest
from sqlalchemy.orm import sessionmaker
from auth.token_interface import TokenInterface
from settings import get_settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from database import Base, get_db
from httpx import AsyncClient
from main import app
from auth.token_service import TokenService

settings = get_settings()


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope='session')
def token_service():
    return TokenService()


database_url = get_settings().test_database_url
test_engine = create_async_engine(database_url, future=True)


@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def db_session():
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def client_without_jwt(db_session) -> AsyncClient:
    async with AsyncClient(app=app, base_url='http://test_server') as client:
        yield client


async def get_test_db():
    async_test_session = sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_test_session() as session:
        yield session


async def save_user(client, username, password, email):
    data = {'username': username, 'password': password, 'email': email}
    response = await client.post('/auth/signup', json=data)
    return response.json()


@pytest.fixture(scope='module')
async def first_user(client_without_jwt):
    return await save_user(client=client_without_jwt, username='first_user', password='1234567890', email='f@gmail.com')


@pytest.fixture(scope='module')
async def second_user(client_without_jwt):
    return await save_user(client=client_without_jwt, username='second_user', password='1234567890', email=None)


async def retrieve_token(token_service: TokenInterface, username: str):
    kw = {'secret_key': get_settings().secret_key,
          'token_type': 'access_token',
          'exp_time': get_settings().access_token_expire_minutes,
          'algorithm': get_settings().algorithm}
    token = await token_service.create_token(data={'sub': username}, **kw)
    return token


@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def first_user_client_with_jwt(token_service: TokenInterface, first_user):
    token = await retrieve_token(token_service=token_service, username=first_user['username'])
    async with AsyncClient(app=app, base_url='http://test_server') as client:
        client.headers.update({'Authorization': f'Bearer {token}'})
        yield client


@pytest.fixture(scope='module')
@pytest.mark.asyncio
async def second_user_client_with_jwt(token_service: TokenInterface, second_user):
    token = await retrieve_token(token_service=token_service, username=second_user['username'])
    async with AsyncClient(app=app, base_url='http://test_server') as client:
        client.headers.update({'Authorization': f'Bearer {token}'})
        yield client


app.dependency_overrides[get_db] = get_test_db

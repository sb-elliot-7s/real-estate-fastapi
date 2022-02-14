from datetime import datetime, timedelta
import pytest
from jose import JWSError
from ..token_service import TokenService
from settings import get_settings
from fastapi import HTTPException


class TestTokenService:

    @pytest.mark.parametrize('username, access_token_exp_time, refresh_token_exp_time', [('elliot77', 10, 60)])
    @pytest.mark.asyncio
    async def test_create_token(self, token_service: TokenService, username: str, access_token_exp_time: int, refresh_token_exp_time: int):
        access_token = await token_service.create_token(data={'sub': username}, token_type='access_token', exp_time=access_token_exp_time,
                                                        secret_key=get_settings().secret_key, algorithm=get_settings().algorithm)
        refresh_token = await token_service.create_token(data={'sub': username}, token_type='refresh_token', exp_time=refresh_token_exp_time,
                                                         secret_key=get_settings().secret_key, algorithm=get_settings().algorithm)
        assert len(access_token.split('.')) == 3
        access_token_payload = await token_service.decode_access_token(token=access_token, secret_key=get_settings().secret_key,
                                                                       algorithm=get_settings().algorithm)
        refresh_token_payload = await token_service.decode_refresh_token(refresh_token=refresh_token, secret_key=get_settings().secret_key,
                                                                         algorithm=get_settings().algorithm)
        assert access_token_payload.get('sub') is not None
        assert access_token_payload.get('token_type') == 'access_token'
        assert access_token_payload.get('sub') == username
        assert refresh_token_payload.get('sub') == username
        assert refresh_token_payload.get('token_type') == 'refresh_token'
        access_token_time_exp = datetime.fromtimestamp(int(access_token_payload.get('exp'))).strftime('%Y-%m-%d %H:%M')
        refresh_token_time_exp = datetime.fromtimestamp(int(refresh_token_payload.get('exp'))).strftime('%Y-%m-%d %H:%M')
        time = datetime.now()
        access_token_delta = timedelta(minutes=access_token_exp_time)
        refresh_token_delta = timedelta(minutes=refresh_token_exp_time)
        acc_token_expected_time = (time + access_token_delta).strftime('%Y-%m-%d %H:%M')
        rf_token_expected_time = (time + refresh_token_delta).strftime('%Y-%m-%d %H:%M')
        assert access_token_time_exp == acc_token_expected_time
        assert refresh_token_time_exp == rf_token_expected_time

    @pytest.mark.asyncio
    async def test_failure_verify_access_token(self, token_service: TokenService):
        wrong_token = 'errortoken'
        with pytest.raises(HTTPException) as exc:
            _ = await token_service.decode_access_token(token=wrong_token, secret_key=get_settings().secret_key, algorithm=get_settings().algorithm)
        assert exc.value.detail == 'Could not validate credentials'
        assert exc.value.status_code == 401

    @pytest.mark.parametrize('data, secret_key, algorithm, expected_error', [
        ({'sub': 'alice'}, None, get_settings().algorithm, JWSError),
        ({'sub': 'bob'}, get_settings().secret_key, None, JWSError),
        ('str', get_settings().secret_key, get_settings().algorithm, AttributeError),
        (None, get_settings().secret_key, get_settings().algorithm, AttributeError),
    ])
    @pytest.mark.asyncio
    async def test_invalid_create_access_token(self, token_service, data, secret_key, algorithm, expected_error):
        with pytest.raises(expected_error):
            _ = await token_service.create_token(data=data, token_type='access_token', secret_key=secret_key,
                                                 exp_time=get_settings().access_token_expire_minutes, algorithm=algorithm)

    @pytest.mark.parametrize('rfr_token, secret_key, alg, error_detail, status_code', [
        ('wrong_token', get_settings().secret_key, get_settings().algorithm, 'Invalid refresh token', 401),
    ])
    @pytest.mark.asyncio
    async def test_failure_decode_refresh_token(self, token_service, rfr_token, secret_key, alg, error_detail, status_code):
        with pytest.raises(HTTPException) as exc:
            _ = await token_service.decode_refresh_token(refresh_token=rfr_token, secret_key=secret_key, algorithm=alg)

        assert exc.value.detail == error_detail
        assert exc.value.status_code == status_code



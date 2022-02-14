from functools import lru_cache
from pathlib import Path

from pydantic import BaseSettings

IMAGES_DIR = Path(__file__).resolve().parent.joinpath('images')
LISTINGS_IMAGES_DIR = IMAGES_DIR / 'listings'
USERS_IMAGES_DIR = IMAGES_DIR / 'profiles'


class Settings(BaseSettings):
    secret_key: str

    listings_image_url: str

    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int

    database_url: str
    postgres_user: str
    postgres_password: str
    postgres_db_name: str
    postgres_server: str
    postgres_port: int

    test_database_url: str
    test_image_path: str
    test_listing_image_path: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


@lru_cache
def get_settings() -> Settings:
    return Settings()

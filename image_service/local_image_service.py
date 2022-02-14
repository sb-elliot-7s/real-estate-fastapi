from fastapi import UploadFile
from .image_service_interface import ImageServiceInterface
import aiofiles
from pathlib import Path


class ImageService(ImageServiceInterface):
    def __init__(self, path: str):
        self._path = path

    async def write_image(self, file: UploadFile, filename: str, **kwargs):
        path_to_images = f'{self._path}/{filename}'
        async with aiofiles.open(path_to_images, mode='wb') as f:
            content = await file.read()
            await f.write(content)

    async def read_image(self, filename: str, **kwargs):
        path_to_images = f'{self._path}/{filename}'
        async with aiofiles.open(path_to_images, mode='rb') as f:
            image = await f.read()
        return image

    async def delete_image(self, filename: str, **kwargs):
        p = f'{self._path}/{filename}'
        path_file = Path(p)
        try:
            path_file.unlink()
        except OSError as error:
            raise OSError(error.args[-1])
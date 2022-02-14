from abc import ABC, abstractmethod
from fastapi import UploadFile


class ImageServiceInterface(ABC):

    @abstractmethod
    async def write_image(self, file: UploadFile, filename: str, **kwargs): pass

    @abstractmethod
    async def read_image(self, filename: str, **kwargs): pass

    @abstractmethod
    async def delete_image(self, filename: str, **kwargs): pass

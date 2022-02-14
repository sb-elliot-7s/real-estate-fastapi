import pytest
from ..local_image_service import ImageService
from fastapi import UploadFile
from settings import get_settings


class TestImageService:
    @pytest.fixture()
    def get_image_service(self, tmpdir_factory):
        base_temp = tmpdir_factory.getbasetemp()
        return ImageService(path=base_temp)

    @pytest.mark.asyncio
    async def test_write_image(self, get_image_service):
        await get_image_service.write_image(filename='tesla.jpg', file=UploadFile(get_settings().test_image_path))

    @pytest.mark.asyncio
    async def test_get_image(self, get_image_service):
        await get_image_service.read_image(filename='tesla.jpg')

    @pytest.mark.asyncio
    async def test_delete_image(self, get_image_service):
        await get_image_service.delete_image(filename='tesla.jpg')

    @pytest.mark.asyncio
    async def test_failure_delete_image(self, get_image_service):
        with pytest.raises(OSError) as e:
            await get_image_service.delete_image(filename='No_such_file_or_directory.jpg')
        assert str(e.value) == 'No such file or directory'

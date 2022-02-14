from ..create_slug import create_slug
import pytest


class TestUtils:

    @pytest.mark.parametrize('text, expected_value', [
        ('At Real Python you can learn all things Python from the ground up.', 'at-real-python-you-can-learn-all-things-python-from-the-ground-up'),
        ('Real Python has been around since 2012.', 'real-python-has-been-around-since-2012')
    ])
    def test_create_slug(self, text: str, expected_value: str):
        slug = create_slug(text=text)
        assert expected_value == slug

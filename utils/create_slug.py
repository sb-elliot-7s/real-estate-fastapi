from slugify import slugify


def create_slug(text: str):
    return slugify(text=text)

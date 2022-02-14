from datetime import datetime
from fastapi import Form, Query
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class Category(str, Enum):
    RENT = 'RENT'
    SELL = 'SELL'
    DAILY_RENT = 'DAILY_RENT'


class WallType(str, Enum):
    BRICK = 'BRICK'
    WOOD = 'WOOD'
    PANEL = 'PANEL'


class HouseType(str, Enum):
    NEW_BUILDING = 'NEW_BUILDING'
    SECONDARY_HOUSING = 'SECONDARY_HOUSING'


class ImageSchema(BaseModel):
    id: int
    photo: str
    listing_id: int

    class Config:
        orm_mode = True


class BaseAddressSchema(BaseModel):
    country: Optional[str]
    city: Optional[str]
    street: Optional[str]
    region: Optional[str]
    district: Optional[str]
    house_number: Optional[str] = Field(None, max_length=10)

    @classmethod
    def as_form(cls, country: Optional[str] = Form(None), city: Optional[str] = Form(None), street: Optional[str] = Form(None),
                region: Optional[str] = Form(None), district: Optional[str] = Form(None), house_number: Optional[str] = Form(None)):
        return cls(country=country, city=city, street=street, region=region, district=district, house_number=house_number)

    @classmethod
    def as_query(cls, country: Optional[str] = Query(None), city: Optional[str] = Query(None), street: Optional[str] = Query(None),
                 region: Optional[str] = Query(None), district: Optional[str] = Query(None), house_number: Optional[str] = Query(None)):
        return cls(country=country, city=city, street=street, region=region, district=district, house_number=house_number)


class BaseBuildingSchema(BaseModel):
    number_of_rooms: Optional[int]
    category_type: Optional[Category] = 'SELL'
    house_type: Optional[HouseType] = HouseType.NEW_BUILDING.value
    wall_type: Optional[WallType] = WallType.BRICK.value
    elevator: Optional[bool] = Field(True)

    class Config:
        use_enum_values = True

    @classmethod
    def as_query(cls, category_type: Category = Query(None), house_type: Optional[HouseType] = Query(None),
                 wall_type: Optional[WallType] = Query(None), elevator: Optional[bool] = Query(None),
                 number_of_rooms: Optional[int] = Query(None)):
        return cls(category_type=category_type, house_type=house_type, wall_type=wall_type, elevator=elevator, number_of_rooms=number_of_rooms)


class BuildingSchema(BaseBuildingSchema):
    total_area: Optional[float]
    number_of_floors: Optional[int] = 1
    year_built: Optional[int] = Field(None)


class UpdateListingSchema(BuildingSchema):
    price: Optional[float] = Field(None, gt=0)
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str]

    @classmethod
    def as_form(cls, category_type: Optional[Category] = Form(None), number_of_rooms: Optional[int] = Form(None),
                total_area: Optional[float] = Form(None), price: Optional[float] = Form(None), title: Optional[str] = Form(None),
                description: Optional[str] = Form(None), house_type: Optional[HouseType] = Form(HouseType.NEW_BUILDING),
                wall_type: Optional[WallType] = Form(WallType.BRICK), year_built: Optional[int] = Form(None), number_of_floors: int = Form(1),
                elevator: bool = Form(True)):
        return cls(category_type=category_type, number_of_rooms=number_of_rooms, total_area=total_area, price=price, title=title,
                   description=description, house_type=house_type, wall_type=wall_type, number_of_floors=number_of_floors, elevator=elevator,
                   year_built=year_built)


class CreateListingSchema(BuildingSchema):
    price: float = Field(..., gt=0)
    title: str = Field(..., max_length=255)
    description: Optional[str]

    @classmethod
    def as_form(cls, category_type: Category = Form(Category.RENT), number_of_rooms: Optional[int] = Form(None),
                total_area: Optional[float] = Form(None), price: float = Form(...), title: str = Form(...),
                description: Optional[str] = Form(None), house_type: Optional[HouseType] = Form(HouseType.NEW_BUILDING),
                wall_type: Optional[WallType] = Form(WallType.BRICK), year_built: Optional[int] = Form(None), number_of_floors: int = Form(1),
                elevator: bool = Form(True)):
        return cls(category_type=category_type, number_of_rooms=number_of_rooms, total_area=total_area, price=price, title=title,
                   description=description, house_type=house_type, wall_type=wall_type, number_of_floors=number_of_floors, elevator=elevator,
                   year_built=year_built)


class ListingSchema(CreateListingSchema, BaseAddressSchema):
    id: int
    user_id: int
    longitude: Optional[float]
    latitude: Optional[float]
    full_address: Optional[str]
    created: datetime
    updated: datetime
    is_published: bool = True
    slug: Optional[str]
    images: list[ImageSchema] = []

    class Config:
        orm_mode = True
        use_enum_values = True
        json_encoders = {datetime: lambda f: f.strftime('%Y-%m-%d %H:%M')}


class FavoriteSchema(BaseModel):
    id: int
    user_id: int
    is_favorite: bool = Field(False)
    listings: list[ListingSchema]

    class Config:
        orm_mode = True


class BuildingQuerySchema(BaseModel):
    min_total_area: Optional[float]
    max_total_area: Optional[float]
    min_number_of_floors: Optional[int] = 1
    max_number_of_floors: Optional[int] = 1
    from_year_built: Optional[int] = Field(None)
    to_year_built: Optional[int] = Field(None)

    @classmethod
    def as_query(cls, min_total_area: Optional[float] = Query(None), max_total_area: Optional[float] = Query(None),
                 min_number_of_floors: Optional[int] = Query(None), max_number_of_floors: Optional[int] = Query(None),
                 from_year_built: Optional[int] = Query(None), to_year_built: Optional[int] = Query(None)):
        return cls(min_total_area=min_total_area, max_total_area=max_total_area, min_number_of_floors=min_number_of_floors,
                   max_number_of_floors=max_number_of_floors, from_year_built=from_year_built, to_year_built=to_year_built)


class PriceQuerySchema(BaseModel):
    min_price: Optional[float]
    max_price: Optional[float]

    @classmethod
    def as_query(cls, min_price: Optional[float] = Query(None), max_price: Optional[float] = Query(None)):
        return cls(min_price=min_price, max_price=max_price)

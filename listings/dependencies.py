from typing import Optional


class LimitOffsetQueryParams:
    def __init__(self, limit: int = 20, offset: int = 0):
        self.limit = limit
        self.offset = offset


# class FilterQueryParams:
#     def __init__(self, country: Optional[str] = None, city: Optional[str] = None,
#                  street: Optional[str] = None, region: Optional[str] = None, district: Optional[str] = None,
#                  house_number: Optional[str] = None, number_of_rooms: Optional[int] = None, total_area: Optional[float] = None,
#                  category_name: Optional[str] = None, house_type: Optional[str] = None, wall_type: Optional[str] = None,
#                  number_of_floors: Optional[int] = None, elevator: Optional[bool] = None, year_built: Optional[int] = None,
#                  with_image: Optional[bool] = None, min_price: Optional[float] = None, max_price: Optional[float] = None):
#         self.country = country
#         self.city = city
#         self.street = street
#         self.region = region
#         self.district = district
#         self.house_number = house_number
#         self.number_of_rooms = number_of_rooms
#         self.total_area = total_area
#         self.category_name = category_name
#         self.house_type = house_type
#         self.wall_type = wall_type
#         self.number_of_floors = number_of_floors
#         self.elevator = elevator
#         self.year_built = year_built
#         self.min_price = min_price
#         self.max_price = max_price

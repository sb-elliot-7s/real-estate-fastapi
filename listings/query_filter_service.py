from sqlalchemy import between, Column

from listings.models import Listing


class QueryListingParamsService:
    @staticmethod
    async def _compared(column, lower, upper):
        return between(column, lower_bound=lower, upper_bound=upper) if lower and upper \
            else column >= lower if not upper \
            else column <= upper if not lower \
            else None

    async def price_params(self, stm, price_params: dict):
        if price_params:
            price_expr = await self._compared(column=Listing.price, lower=price_params.get('min_price'),
                                              upper=price_params.get('max_price'))
            stm = stm.where(price_expr)
        return stm

    async def advanced_building_params(self, stm, advanced_building_params: dict):
        if advanced_building_params:
            min_total_area = advanced_building_params.get('min_total_area')
            max_total_area = advanced_building_params.get('max_total_area')
            min_number_of_floors = advanced_building_params.get('min_number_of_floors')
            max_number_of_floors = advanced_building_params.get('max_number_of_floors')
            from_year_built = advanced_building_params.get('from_year_built')
            to_year_built = advanced_building_params.get('to_year_built')

            if min_total_area or max_total_area:
                total_area_expr = await self._compared(column=Listing.total_area, lower=min_total_area, upper=max_total_area)
                stm = stm.where(total_area_expr)
            if min_number_of_floors or max_number_of_floors:
                main_number_floors_expr = await self._compared(column=Listing.number_of_floors, lower=min_number_of_floors,
                                                               upper=max_number_of_floors)
                stm = stm.where(main_number_floors_expr)
            if from_year_built or to_year_built:
                year_built_expr = await self._compared(column=Listing.year_built, lower=from_year_built, upper=to_year_built)
                stm = stm.where(year_built_expr)
        return stm

    @staticmethod
    async def _address_param(stm, address_params: dict, key: str, column: Column):
        if address_params.get(key):
            country_expr = column.ilike(address_params.get(key))
            stm = stm.where(country_expr)
        return stm

    async def common_address_params(self, stm, address_params: dict):
        if address_params:
            stm = await self._address_param(address_params=address_params, stm=stm, key='country', column=Listing.country)
            stm = await self._address_param(address_params=address_params, stm=stm, key='city', column=Listing.city)
            stm = await self._address_param(address_params=address_params, stm=stm, key='street', column=Listing.street)
            stm = await self._address_param(address_params=address_params, stm=stm, key='region', column=Listing.region)
            stm = await self._address_param(address_params=address_params, stm=stm, key='district', column=Listing.district)
            stm = await self._address_param(address_params=address_params, stm=stm, key='house_number', column=Listing.house_number)
        return stm

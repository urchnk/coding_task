import asyncio

import aiohttp

from utils.services import add_address_to_data, fetch_station_data, transform_data


async def main():
    async with aiohttp.ClientSession() as session:
        # Fetching and transforming API data
        station_data = await fetch_station_data(session)
        transformed_data = await transform_data(station_data)

        # Fetching addresses for coordinates
        data_with_address = await add_address_to_data(transformed_data, session)

        # Outputting the final list of stations
        for station in data_with_address:
            print(station)


if __name__ == "__main__":
    asyncio.run(main())

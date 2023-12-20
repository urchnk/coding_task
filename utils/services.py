import time


async def fetch_station_data(session):
    url = "https://wegfinder.at/api/v1/stations"
    async with session.get(url) as response:
        return await response.json()


async def fetch_address(session, latitude, longitude):
    url = f"https://api.i-mobility.at/routing/api/v1/nearby_address?latitude={latitude}&longitude={longitude}"
    async with session.get(url) as response:
        # This is a horrible (HORRIBLE!) crutch and noone should ever use it in production.
        # However, it looks like there is some sort of throttling rule and right now I don't have means to overcome it.
        if response.status == 429:
            time.sleep(1)
            return await fetch_address(session, latitude, longitude)

        data = await response.json()
        print(data)
        return data.get("data", {}).get("name", "")


async def transform_data(station_data):
    transformed_data = []
    for station in station_data:
        if station["free_bikes"] > 0:
            transformed_station = {
                "id": station["id"],
                "name": station["name"],
                "active": station["status"] == "aktiv",
                "description": station["description"],
                "boxes": station["boxes"],
                "free_boxes": station["free_boxes"],
                "free_bikes": station["free_bikes"],
                "free_ratio": station["free_boxes"] / station["boxes"],
                "coordinates": [station["longitude"], station["latitude"]],
            }
            transformed_data.append(transformed_station)

    transformed_data.sort(key=lambda x: (x["name"]))
    transformed_data.sort(key=lambda x: (x["free_bikes"]), reverse=True)

    return transformed_data


async def add_address_to_data(data, session):
    for station in data:
        longitude, latitude = station["coordinates"]
        address = await fetch_address(session, latitude, longitude)
        station["address"] = address

    return data

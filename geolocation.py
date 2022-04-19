# ----------------------------------------------------------------------------------------------------------------------

import winrt.windows.devices.geolocation as wdg  # For dynamic location.
import asyncio  # wdg requires asynchronous input/output.
from geopy.geocoders import Nominatim  # To get city name from coordinates.


# -----------------------------------------------------------------------------------------------------------------------
async def get_geoposition():
    # Geolocator class provided by WinRT
    geolocator = wdg.Geolocator()
    # Asynchronous operation to retrieve geoposition
    geoposition = await geolocator.get_geoposition_async()
    return [geoposition.coordinate.latitude, geoposition.coordinate.longitude]


def get_location():
    return asyncio.run(get_geoposition())

# API key for OpenWeather API.
api_key = "7b58f1ac37aa6eed43c8083af305e913"
# Provided by GeoPy.
geolocator = Nominatim(user_agent="geoapiExercises")

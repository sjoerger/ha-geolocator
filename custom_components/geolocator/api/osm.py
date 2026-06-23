from .base import GeoLocatorAPI

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

class OSMAPI(GeoLocatorAPI):
    """GeoLocator API using OpenStreetMap's Nominatim service."""

    def __init__(self, session, user_agent: str = "geo_locator_home_assistant"):
        super().__init__(session)
        self.user_agent = user_agent

    async def reverse_geocode(self, latitude, longitude, language="en"):
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "jsonv2",
            "addressdetails": 1,
        }
        async with self.session.get(NOMINATIM_URL, params=params, headers={"User-Agent": self.user_agent}) as resp:
            return await resp.json()

    async def get_timezone(self, latitude, longitude, language="en", geocode_data=None):
        return None

    def format_full_address(self, data):
        return data.get("display_name", "")

    def extract_neighborhood(self, data):
        return data.get("address", {}).get("neighbourhood")

    def extract_city(self, data):
        return data.get("address", {}).get("city") or \
               data.get("address", {}).get("town") or \
               data.get("address", {}).get("village")

    def extract_state_long(self, data):
        return data.get("address", {}).get("state")

    def extract_country(self, data):
        return data.get("address", {}).get("country")

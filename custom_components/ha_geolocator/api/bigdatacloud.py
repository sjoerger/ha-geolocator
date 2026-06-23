import logging
from .base import GeoLocatorAPI

_LOGGER = logging.getLogger(__name__)

BIGDATACLOUD_URL = "https://api.bigdatacloud.net/data/reverse-geocode-client"


class BigDataCloudAPI(GeoLocatorAPI):
    """GeoLocator API using BigDataCloud (no key required)."""

    def __init__(self, session):
        super().__init__(session)

    async def reverse_geocode(self, latitude, longitude, language="en"):
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "localityLanguage": "en"
        }
        async with self.session.get(BIGDATACLOUD_URL, params=params) as resp:
            data = await resp.json()
            _LOGGER.debug("BigDataCloud response: %s", data)
            return data

    async def get_timezone(self, latitude, longitude, language="en", geocode_data=None):
        data = geocode_data if geocode_data is not None else await self.reverse_geocode(latitude, longitude)
        informative = data.get("localityInfo", {}).get("informative", [])
        for item in informative:
            if item.get("description", "").lower() == "time zone":
                return item.get("name")
        return None

    def format_full_address(self, data):
        locality = data.get("locality", "")
        state = data.get("principalSubdivision", "")
        country = data.get("countryName", "")
        parts = [p for p in [locality, state, country] if p]
        return ", ".join(parts)

    def extract_neighborhood(self, data):
        return None

    def extract_city(self, data):
        return data.get("locality")

    def extract_state_long(self, data):
        return data.get("principalSubdivision")

    def extract_country(self, data):
        return data.get("countryName")

import logging
from .base import GeoLocatorAPI

_LOGGER = logging.getLogger(__name__)
GEOCODE_URL = "https://api.opencagedata.com/geocode/v1/json"

class OpenCageAPI(GeoLocatorAPI):
    def __init__(self, api_key, session):
        super().__init__(session)
        self.api_key = api_key

    async def reverse_geocode(self, lat, lon, language="en"):
        params = {
            "q": f"{lat},{lon}",
            "key": self.api_key,
            "language": language,
        }
        async with self.session.get(GEOCODE_URL, params=params) as resp:
            data = await resp.json()
            _LOGGER.debug("OpenCage reverse geocode response: %s", data)
            return data

    async def get_timezone(self, lat, lon, language="en", geocode_data=None):
        data = geocode_data if geocode_data is not None else await self.reverse_geocode(lat, lon, language)
        try:
            return data["results"][0]["annotations"]["timezone"]["name"]
        except (IndexError, KeyError):
            _LOGGER.warning("OpenCage: Failed to extract timezone from response")
            return None

    def format_full_address(self, data):
        try:
            return data["results"][0]["formatted"]
        except (IndexError, KeyError):
            return ""

    def extract_locality(self, data):
        try:
            return data["results"][0]["components"].get("city") or \
                   data["results"][0]["components"].get("town") or \
                   data["results"][0]["components"].get("village") or \
                   data["results"][0]["components"].get("county")
        except (IndexError, KeyError):
            return None

    def extract_state_long(self, data):
        try:
            return data["results"][0]["components"].get("state")
        except (IndexError, KeyError):
            return None

    def extract_country(self, data):
        try:
            return data["results"][0]["components"].get("country")
        except (IndexError, KeyError):
            return None

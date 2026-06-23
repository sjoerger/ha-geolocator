from .base import GeoLocatorAPI

GEONAMES_REVERSE_URL = "http://api.geonames.org/findNearestAddressJSON"
GEONAMES_PLACE_URL = "http://api.geonames.org/findNearbyPlaceNameJSON"
GEONAMES_TIMEZONE_URL = "http://api.geonames.org/timezoneJSON"

class GeoNamesAPI(GeoLocatorAPI):
    def __init__(self, username: str, session):
        super().__init__(session)
        self.username = username

    async def reverse_geocode(self, lat, lon, language="en"):
        async with self.session.get(GEONAMES_REVERSE_URL, params={"lat": lat, "lng": lon, "username": self.username}) as reverse_resp:
            reverse_data = await reverse_resp.json()
        async with self.session.get(GEONAMES_PLACE_URL, params={"lat": lat, "lng": lon, "username": self.username, "cities": "cities500"}) as place_resp:
            place_data = await place_resp.json()
        return {"reverse": reverse_data, "place": place_data}

    async def get_timezone(self, lat, lon, language="en", geocode_data=None):
        params = {
            "lat": lat,
            "lng": lon,
            "username": self.username,
        }
        async with self.session.get(GEONAMES_TIMEZONE_URL, params=params) as resp:
            data = await resp.json()
            return data.get("timezoneId")

    def _get_top_result(self, data):
        if "geonames" in data:
            return data.get("geonames", [{}])[0]
        elif "address" in data:
            return data["address"]
        return {}

    def format_full_address(self, data):
        reverse_top = self._get_top_result(data.get("reverse", {}))
        place_top = self._get_top_result(data.get("place", {}))

        street_number = reverse_top.get("streetNumber")
        street = reverse_top.get("street")
        street_line = f"{street_number} {street}".strip() if street or street_number else None

        placename = reverse_top.get("placename")
        if not placename:
            placename = place_top.get("name")

        admin = reverse_top.get("adminCode1")
        postal = reverse_top.get("postalcode")
        region_line = f"{admin} {postal}".strip() if admin or postal else None

        country = place_top.get("countryName")

        return ", ".join(filter(None, [street_line, placename, region_line, country]))

    def extract_locality(self, data):
        reverse_top = self._get_top_result(data.get("reverse", {}))
        city = reverse_top.get("placename")

        if not city:
            place_top = self._get_top_result(data.get("place", {}))
            city = place_top.get("name")

        return city

    def extract_state_long(self, data):
        reverse_top = self._get_top_result(data.get("reverse", {}))
        return reverse_top.get("adminName1")

    def extract_country(self, data):
        place_top = self._get_top_result(data.get("place", {}))
        return place_top.get("countryName")

    def extract_postcode(self, data):
        reverse_top = self._get_top_result(data.get("reverse", {}))
        return reverse_top.get("postalcode")

    def extract_country_code(self, data):
        reverse_top = self._get_top_result(data.get("reverse", {}))
        return reverse_top.get("countryCode")

    def extract_county(self, data):
        reverse_top = self._get_top_result(data.get("reverse", {}))
        return reverse_top.get("adminName2")

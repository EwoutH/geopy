"""
:class:`.OpenMapQuest` geocoder.
"""

from geopy.compat import json

from urllib import urlencode
from urllib2 import urlopen

from geopy.geocoders.base import Geocoder
from geopy.util import logger, decode_page


class OpenMapQuest(Geocoder): # pylint: disable=W0223
    """
    Geocoder using MapQuest Open Platform Web Services. Documentation at:
        http://developer.mapquest.com/web/products/open/geocoding-service
    """

    def __init__(self, api_key=None, format_string=None):
        """Initialize an Open MapQuest geocoder with location-specific
        address information, no API Key is needed by the Nominatim based
        platform.

        ``format_string`` is a string containing '%s' where the string to
        geocode should be interpolated before querying the geocoder.
        For example: '%s, Mountain View, CA'. The default is just '%s'.
        """
        super(OpenMapQuest, self).__init__(format_string)

        self.api_key = api_key or ''
        self.api = "http://open.mapquestapi.com/nominatim/v1/search" \
                    "?format=json&%s"

    def geocode(self, string, exactly_one=True): # pylint: disable=W0221
        if isinstance(string, unicode):
            string = string.encode('utf-8')
        params = {'q': self.format_string % string}
        url = self.api % urlencode(params)
        logger.debug("%s.geocode: %s", self.__class__.__name__, url)

        page = urlopen(url)

        return self.parse_json(page, exactly_one)

    @classmethod
    def parse_json(cls, page, exactly_one=True):
        """
        Parse display name, latitude, and longitude from an JSON response.
        """
        if not isinstance(page, basestring):
            page = decode_page(page)
        resources = json.loads(page)

        if exactly_one and len(resources) != 1:
            from warnings import warn
            warn("Didn't find exactly one resource!" + \
                "(Found %d.), use exactly_one=False\n" % len(resources)
            )

        if exactly_one:
            return cls.parse_resource(resources[0])
        else:
            return [cls.parse_resource(resource) for resource in resources]

    @classmethod
    def parse_resource(cls, resource):
        """
        Return location and coordinates tuple from dict.
        """
        location = resource['display_name']

        latitude = resource['lat'] or None
        longitude = resource['lon'] or None
        if latitude and longitude:
            latitude = float(latitude)
            longitude = float(longitude)

        return (location, (latitude, longitude))
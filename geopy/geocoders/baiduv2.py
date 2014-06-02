#!/usr/bin/env python
# -*- coding: utf-8 -*- 
"""
:class:`.BaiduV2` geocoder.
"""

from geopy.compat import urlencode
from geopy.geocoders.base import Geocoder, DEFAULT_FORMAT_STRING, \
    DEFAULT_TIMEOUT
from geopy.location import Location
from geopy.util import logger
from geopy.exc import (
    GeocoderQueryError
)

class BaiduV2(Geocoder):
    """
    Geocoder using the Baidu Maps Locations API. Documentation at:
        http://developer.baidu.com/map/webservice-geocoding.htm
    """

    def __init__(self, ak, format_string=DEFAULT_FORMAT_STRING,
                        scheme='http', timeout=DEFAULT_TIMEOUT, proxies=None):
        """Initialize a customized Baidu geocoder with location-specific
        address information and your Baidu Maps API key.

        :param string ak: Should be a valid Baidu Maps ak.

        :param string format_string: String containing '%s' where the
            string to geocode should be interpolated before querying the
            geocoder. For example: '%s, Mountain View, CA'. The default
            is just '%s'.

        :param string scheme: Use 'https' or 'http' as the API URL's scheme.
            Default is https. Note that SSL connections' certificates are not
            verified.

            .. versionadded:: 0.97

        :param int timeout: Time, in seconds, to wait for the geocoding service
            to respond before raising a :class:`geopy.exc.GeocoderTimedOut`
            exception.

            .. versionadded:: 0.97

        :param dict proxies: If specified, routes this geocoder's requests
            through the specified proxy. E.g., {"https": "192.0.2.0"}. For
            more information, see documentation on
            :class:`urllib2.ProxyHandler`.

            .. versionadded:: 0.96
        """
        super(BaiduV2, self).__init__(format_string, scheme, timeout, proxies)
        self.ak = ak
        self.api = "%s://api.map.baidu.com/geocoder/v2/" % self.scheme

    def geocode(self, query, city=None, exactly_one=True, timeout=None):
        """
        Geocode an address.

        :param string query: The address or query you wish to geocode.
        
        :param string city: The city of the address you wish to geocode.

        :param bool exactly_one: Return one result or a list of results, if
            available.

        :param int timeout: Time, in seconds, to wait for the geocoding service
            to respond before raising a :class:`geopy.exc.GeocoderTimedOut`
            exception. Set this only if you wish to override, on this call only,
            the value set during the geocoder's initialization.

            .. versionadded:: 0.97
        """
        params = {
            'address': self.format_string % query,
            'output': 'json',
            'ak': self.ak
        }
        
        if city:
            params['city'] = city        

        url = "?".join((self.api, urlencode(params)))
        logger.debug("%s.geocode: %s", self.__class__.__name__, url)
        return self._parse_json(self._call_geocoder(url, timeout=timeout), exactly_one)

    def reverse(self, query, coordtype='bd09ll', exactly_one=True, timeout=None): # pylint: disable=W0221
        """
        Reverse geocode a point.

        :param query: The coordinates for which you wish to obtain the
            closest human-readable addresses.
        :type query: :class:`geopy.point.Point`, list or tuple of (latitude,
            longitude), or string as "%(latitude)s, %(longitude)s".

        :param bool exactly_one: Return one result, or a list?

        :param int timeout: Time, in seconds, to wait for the geocoding service
            to respond before raising a :class:`geopy.exc.GeocoderTimedOut`
            exception. Set this only if you wish to override, on this call only,
            the value set during the geocoder's initialization.

            .. versionadded:: 0.97
        """
        params = {
                  'location': self._coerce_point_to_string(query),
                  'coordtype': coordtype,
                  'output': 'json',
                  'ak': self.ak
                  }
        url = "%s?%s" % (
            self.api, urlencode(params))

        logger.debug("%s.reverse: %s", self.__class__.__name__, url)
        return self._parse_json(self._call_geocoder(url, timeout=timeout), exactly_one)

    def _parse_json(self, response, exactly_one=True): # pylint: disable=W0221
        """
        Parse a location name, latitude, and longitude from an JSON response.
        """
        logger.warn(response)
        result = response.get('results', [])
        if not len(result): # pragma: no cover
            self._check_status(response.get('status'))
            return None

        def parse_result(result):
            """
            Parse each return object.
            """
            level = result['level']

            latitude = result['location']['lat'] or None
            longitude = result['location']['lng'] or None
            if latitude and longitude:
                latitude = float(latitude)
                longitude = float(longitude)

            return Location(level, (latitude, longitude), result)

        return parse_result(response)

    @staticmethod
    def _check_status(status):
        """
        Validates error statuses.
        """
        if status == 0:
            # When there are no results, just return.
            return
        if status == 1:
            raise GeocoderQueryError('Server internal error.')
        elif status == 2:
            raise GeocoderQueryError('Invalid request.')
        elif status == 3:
            raise GeocoderQueryError('Permission validation failed.')
        elif status == 4:
            raise GeocoderQueryError('Quota validation failed.')
        elif status == 5:
            raise GeocoderQueryError('Invalid ak.')
        elif status == 101:
            raise GeocoderQueryError('Service disabled.')
        elif status == 102:
            raise GeocoderQueryError('Failed to pass the whitelist or wrong security code.')
        else:
            raise GeocoderQueryError('Unknown error.')
        
if __name__ == '__main__':
    import logging
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)
    b = BaiduV2('09fb9fc373671eaaac6dcd1518fb2ee4')
    #place, (lat, lng) = b.geocode("上海市虹桥路3号")
    #print "%s: %.5f, %.5f" % (place, lat, lng)
    place, (lat, lng) = b.reverse("39.983424, 116.322987")
    print "%s: %.5f, %.5f" % (place, lat, lng)    
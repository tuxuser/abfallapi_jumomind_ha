#!/usr/bin/env python3

"""
Abfall Jumomind
Based on:

* https://play.google.com/store/apps/details?id=com.jumomind.zaw
* https://github.com/jensweimann/awb

Thanks to @jensweimann and 
"""
import sys
import logging
import json
import urllib.request

_LOGGER = logging.getLogger(__name__)

SERVICES = {
    'ZAW': 'zaw',
    'Aurich': 'lka',
    'Altötting': 'aoe',
    #'Bad Homburg vdH': 'hom',
    'Lübbecke': 'lue',
    #'Hattersheim am Main': 'ham',
    'Barnim': 'bdg',
    'Minden': 'sbm',
    'Rhein-Hunsrück': 'rhe',
    'Recklinghausen': 'ksr',
    #'Ingolstadt': 'inkb',
    'Uckermark': 'udg',
    #'Groß-Gerau': 'aws'
}

class JumomindAbfallApi(object):
    def __init__(self, service):
        self.service = service
        self.base_url = 'https://{}.jumomind.com/mmapp/api.php'.format(self.service)

    def _request(self, endpoint):
        return urllib.request.urlopen(self.base_url + endpoint)

    def get_cities(self):
        return self._request('?r=cities&city_id=&area_id=')
    
    def get_streets(self, city_id):
        return self._request('?r=streets&city_id={}&area_id='.format(city_id))

    def get_trash(self, city_id, area_id):
        return self._request('?r=trash&city_id={}&area_id={}'.format(city_id, area_id))
    
    def get_dates(self, city_id, area_id):
        return self._request('?r=dates/0&city_id={}&area_id={}'.format(city_id, area_id))
    
    def get_housenr(self, street, city_id):
        """
        street: Alsbacher+Str.%2Fundefined
        """
        return self._request('?r=housenr/{}&city_id={}&area_id='.format(street, city_id))
    
    def check_address(self, address, city_id, area_id):
        """
        address: Bickenbach%2FAlsbacher+Str.
        """
        return self._request('?r=checkaddress/{}&city_id={}&area_id={}'.format(address, city_id, area_id))
    
    def get_calendar(self, year, month, city_id, area_id):
        return self._request('?r=calendar/{}-{:02d}&city_id={}&area_id={}'.format(year, month, city_id, area_id))

    def clear_dates(self):
        return self._request('?r=clearDates&city_id=&area_id=')

    def add_dates(self):
        return self._request('?r=addDates&city_id=&area_id=')
    
    def get_reg_id(self):
        return self._request('?r=getRegId&city_id=&area_id=')


def main():
    api = JumomindAbfallApi(SERVICES['ZAW'])
    
    choice = 0

    trash = None
    cities = None
    streets = None
    dates = None

    city_name = ''
    city_id = 0
    
    street_name = ''
    street_id = 0
    area_id = 0

    _LOGGER.info('Getting list of CITIES')
    with api.get_cities() as resp:
        print('CITIES:')
        try:
            cities = json.loads(resp.read().decode('utf-8'))
            for index, entry in enumerate(cities):
                print('{}: Id: {} => {} region_code: {} area_id: {} has_streets: {}'.format(
                    index, entry['id'], entry['name'], entry['region_code'], entry['area_id'], entry['has_streets']))
        except Exception as e:
            _LOGGER.error('Failed to get list of CITIES, Msg: {}'.format(e))
            sys.exit(1)

    try:
        choice = int(input("Choose CITIES Id: "))
        if choice > len(cities):
            raise IndexError()
    except:
        _LOGGER.error('Invalid choice on CITIES')
        sys.exit(1)

    city_name = cities[choice]['name']
    city_id = cities[choice]['id']
    _LOGGER.info('Choosing first Ort: {} => {}'.format(city_name, city_id))

    _LOGGER.info('Getting list of STREETS')
    with api.get_streets(city_id) as resp:
        print('STREETS:')
        try:
            streets = json.loads(resp.read().decode())
            print(streets)
            for index, entry in enumerate(streets):
                print('{}: Id: {} => {} area_id: {}'.format(index, entry['id'], entry['name'], entry['area_id']))
        except Exception as e:
            _LOGGER.error('Failed to get list of STREETS, Msg: {}'.format(e))
            sys.exit(2)

    try:
        choice = int(input("Choose street Id: "))
        if choice > len(streets):
            raise IndexError()
    except:
        _LOGGER.error('Invalid choice on STREETS')
        sys.exit(2)

    street_name = streets[choice]['name']
    street_id = streets[choice]['id']
    area_id = streets[choice]['area_id']
    _LOGGER.info('Choosing first street: {} => {} area_id: {}'.format(street_name, street_id, area_id))

    _LOGGER.info('Getting list of TRASH')
    with api.get_trash(city_id, area_id) as resp:
        print('TRASH:')
        try:
            trash = json.loads(resp.read().decode())
            for entry in trash:
                print(entry)
        except Exception as e:
            _LOGGER.error('Failed to get list of TRASH, Msg: {}'.format(e))
            sys.exit(3)

    _LOGGER.info('Getting list of DATES')
    with api.get_dates(city_id, area_id) as resp:
        print('DATES:')
        try:
            dates = json.loads(resp.read().decode())
            for entry in dates:
                print(entry['day'], '->', entry['title'])
        except Exception as e:
            _LOGGER.error('Failed to get list of DATES, Msg: {}'.format(e))
            sys.exit(3)

if __name__ == '__main__':
    main()
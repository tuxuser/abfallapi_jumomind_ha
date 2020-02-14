#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Jumomind ZAW App:
https://play.google.com/store/apps/details?id=com.jumomind.zaw
"""

import logging
from homeassistant.const import (
    CONF_NAME,
    CONF_VALUE_TEMPLATE,
    STATE_UNKNOWN)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
import voluptuous as vol
import urllib.request
import json
from datetime import datetime
from datetime import timedelta

from .jumomind_abfall_api import JumomindAbfallApi, SERVICES

_LOGGER = logging.getLogger(__name__)

DATE_FORMAT = '%Y-%m-%d'

CONF_SERVICE_ID = 'service_id'
CONF_CITY_ID = 'city_id'
CONF_AREA_ID = 'area_id'
CONF_TRASH_TYPES = 'trash_types'

_QUERY_SCHEME = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_SERVICE_ID): cv.string,
    vol.Required(CONF_CITY_ID): cv.string,
    vol.Required(CONF_AREA_ID): cv.string,
    vol.Optional(CONF_TRASH_TYPES, default=[]):
        vol.All(cv.ensure_list, [cv.string]),
    vol.Optional(CONF_VALUE_TEMPLATE): cv.template
})

def setup_platform(
    hass,
    config,
    add_devices,
    discovery_info=None
    ):
    """Setup the sensor platform."""
    value_template = config.get(CONF_VALUE_TEMPLATE)
    if value_template is not None:
        value_template.hass = hass

    service_id = config.get(CONF_SERVICE_ID)
    service = SERVICES[service_id]

    add_devices([JumomindAbfallSensor(config.get(CONF_NAME),
                                     service,
                                     config.get(CONF_CITY_ID),
                                     config.get(CONF_AREA_ID),
                                     config.get(CONF_TRASH_TYPES),
                                     value_template)])

class JumomindAbfallSensor(Entity):

    """Representation of a Sensor."""
    def __init__(self, name, service, city_id, area_id, trash_types, value_template):
        """Initialize the sensor."""
        self._name = name

        self._city_id = city_id
        self._area_id = area_id
        self._trash_types = trash_types

        self._api = JumomindAbfallApi(service)

        self._value_template = value_template
        self._state = STATE_UNKNOWN
        self._attributes = None

        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return None

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    def update(self):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        tommorow = datetime.now() + timedelta(days=1)

        dates = None
        """
        Get dates
        """
        try:
            with self._api.get_dates(self._city_id, self._area_id) as url:
                dates = json.loads(url.read().decode())
        except Exception as e:
            _LOGGER.error('API call error: GET_DATES, error: {}'.format(e))
            return
        
        attributes = {}
        
        if self._trash_types:
            # If provided filter for wanted trash types
            dates = [d for d in dates if d['trash_name'] in self._trash_types]
        
        for date in dates:
            # Example: {'id': '9499937', 'title': 'Gelber Sack', 'trash_name': 'ZAW_GELB', 'day': '2020-11-19', 'description': '', 'color': '#dcef08'}
            day = date['day']
            title = date['title']

            if day in attributes:
                title = ', '.join(attributes[day], title)

            attributes.update({day: title})
        
        attributes.update({'Zuletzt aktualisiert': datetime.now().strftime(DATE_FORMAT + ' %H:%M:%S')})
        data = attributes.get(tommorow.strftime(DATE_FORMAT), "Keine")

        if self._value_template is not None:
            self._state = self._value_template.async_render_with_possible_json_value(
                data, None)
        else:
            self._state = data

        self._attributes = dict(sorted(attributes.items()))

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

# Home Assistant sensor for german waste collection schedule (Jumomind)

## Functionality

The sensor shows the bin which will be collected the next day. The complete collection schedule is available as attributes of the sensor

Supported services:

* ZAW
* Aurich
* Altötting
* Lübbecke
* Barnim
* Minden
* Rhein-Hunsrück
* Recklinghausen
* Uckermark

Non-working:

* Bad Homburg vdH
* Hattersheim am Main
* Ingolstadt
* Groß-Gerau

![alt text](https://github.com/tuxuser/abfallapi_jumomind_ha/blob/master/preview1.png "glance card")

![alt text](https://github.com/tuxuser/abfallapi_jumomind_ha/blob/master/preview2.png "glance card details")

## Credits

Based on [AWB Köln Home Assistant sensor](https://github.com/jensweimann/awb) by [jensweimann](https://github.com/jensweimann)

## Installation

### Manual

Copy all files from custom_components/abfallapi_jumomind/ to custom_components/abfallapi_jumomind/ inside your config Home Assistant directory.

### Hacs

Add this repo in the settings as integration then install and restart home assistant

<!---
## Discussion

[Home Assistant Community Forum](https://community.home-assistant.io/t/german-mullabfuhr-sensor/168244)
-->

## Configuration

### Find service_id, city_id and area_id

To assemble the matching endpoint, take the value of the SERVICES dictionary in `jumomind_abfall_api.py`.
Example:

```python
  SERVICES : {
    ...
    'Minden': 'sbm',
    ...
  }
```

Endpoint: sbm

#### service_id

service_id is the human-readable string found in `jumomind_abfall_api.py` -> SERVICES

Example:

```yaml
service_id: Minden
```

#### city_id

`GET https://<ENDPOINT>.jumomind.com/mmapp/api.php?r=cities&city_id=&area_id=`

Example output:

```json
[
  {"name": "Alsbach-Hähnlein", "_name": "Alsbach-Hähnlein", "id": "87", "region_code": "05", "area_id": "0", "img": null, "has_streets": true},
  ...
]
```

Example for *Alsbach-Hähnlein*:

```yaml
city_id: 87
```

#### area_id

`GET https://<ENDPOINT>.jumomind.com/mmapp/api.php?r=streets&city_id=<city_id>&area_id=`

Example output:

```json
[
 {"name": "Weiterstädter Weg", "_name": "Weiterstädter Weg", "id": "4571", "area_id": "257"},
 {"name": "Westendstr.", "_name": "Westendstr.", "id": "4572", "area_id": "258"},
 ...
]
```

Example for *Weiterstädter Weg*:

```yaml
area_id: 257
```

### Setup sensor

```yaml
- platform: abfallapi_jumomind
  name: muellabfuhr
  scan_interval: 3600
  service_id: Minden
  city_id: 87
  area_id: 257
```

### Customize

```yaml
sensor.muellabfuhr:
  friendly_name: Heute Mülltonne rausstellen
  icon: mdi:delete
```

### Automation

```yaml
- alias: Abfall Notification
  trigger:
    - platform: time
      at: "18:00:00"
    - entity_id: binary_sensor.someone_is_home
      from: 'off'
      platform: state
      to: 'on'
  condition:
    - condition: and
      conditions:
      - condition: time
        after: '09:00:00'
      - condition: time
        before: '23:00:00'
      - condition: template
        value_template: "{{ (states.sensor.muellabfuhr.state != 'Keine') and (states.sensor.muellabfuhr.state != 'unknown') }}"
  action:
    - service: notify.my_telegram
      data_template:
        message: "{{ states.sensor.muellabfuhr.state }}"
```

## DISCLAIMER

This project is in no way endorsed by or affiliated with Jumomind, or any associated subsidiaries, logos or trademarks.

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

### HACS

Add `https://github.com/tuxuser/abfallapi_jumomind_ha` in HACS -> Settings as integration, search & install the integration and restart home assistant.

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
 {"name":"TANNENWEG","_name":"TANNENWEG","id":"372409","area_id":"089110001","houseNumberFrom":"0001","houseNumberTo":"0001","comment":"","houseNumbers":[["0001","089110001"],["0002","089110002"],["0002A","089110002A"],["0004","089110004"],["0006","089110006"]]},
 ...
]
```

Example for *Tannenweg 1*:

```yaml
area_id: 089110001
```

Example for *Tannenweg 2*:

```yaml
area_id: 089110002
```

#### (Optional) Filter for trash types
If you just want specific types of trash collection to be respected...

`GET https://<ENDPOINT>.jumomind.com/mmapp/api.php?r=trash&city_id=<city_id>&area_id=<area_id>`

Example output for Service ZAW:
```json
[
  {"title":"Biomüll","name":"ZAW_BIO","_name":"ZAW_BIO","color":"06c53c"},
  {"title":"Gelber Sack","name":"ZAW_GELB","_name":"ZAW_GELB","color":"dcef08"},
  {"title":"Papier Tonnen und Container","name":"ZAW_PAP","_name":"ZAW_PAP","color":"2b52e7"},
  {"title":"Restmüll Container wöchentlich","name":"ZAW_REST_W","_name":"ZAW_REST_W","color":"99999"},
  {"title":"Restmüll Tonnen und Container 14-täglich","name":"ZAW_REST_2W","_name":"ZAW_REST_2W","color":"717170"},
  {"title":"Schadstoffmobil","name":"ZAW_SCHAD","_name":"ZAW_SCHAD","color":"e0483d"}
]
```

Configuration entry:
```yaml
trash_types:
  - ZAW_BIO
  - ZAW_GELD
  - ZAW_PAP
  - ZAW_REST_2W
```

### Setup sensor

```yaml
- platform: abfallapi_jumomind
  name: muellabfuhr
  scan_interval: 3600
  service_id: Minden
  city_id: 87
  area_id: 089110001
```

Or for ZAW, filtering for specific trash types:
```yaml
- platform: abfallapi_jumomind
  name: muellabfuhr
  scan_interval: 3600
  service_id: ZAW
  city_id: 106
  area_id: 49
  trash_types:
    - ZAW_BIO
    - ZAW_GELD
    - ZAW_PAP
    - ZAW_REST_2W
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

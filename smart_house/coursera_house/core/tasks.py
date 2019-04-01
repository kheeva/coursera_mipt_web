from __future__ import absolute_import, unicode_literals
from celery import task

import requests
import json
from django.conf import settings
from .models import Setting


def get_sensors_data():
    auth_header = {'Authorization': f'Bearer {settings.SMART_HOME_ACCESS_TOKEN}'}
    user_request = requests.get(settings.SMART_HOME_API_URL, headers=auth_header)
    return user_request.json()


def update_sensors_data(data):
    data_to_send = {"controllers": []}
    for key, value in data.items():
        data_to_send['controllers'].append(
            {"name": key, "value": value}
        )
    auth_header = {'Authorization': f'Bearer {settings.SMART_HOME_ACCESS_TOKEN}'}
    r = requests.post(settings.SMART_HOME_API_URL,
                  headers=auth_header,
                  data=json.dumps(data_to_send))
    print('xxx')
    print(json.dumps(data_to_send))

@task()
def smart_home_manager():
    sensors_raw_data = get_sensors_data()
    sensors_dict = {}
    updated_sensors_dict = {}

    bedroom_target_temperature = Setting.objects.get(
        label='bedroom_target_temperature').value

    hot_water_target_temperature = Setting.objects.get(
        label='hot_water_target_temperature').value


    for sensor in sensors_raw_data['data']:
        sensors_dict[sensor['name']] = sensor['value']

    if sensors_dict['leak_detector']:
        updated_sensors_dict['cold_water'] = False
        updated_sensors_dict['hot_water'] = False
        updated_sensors_dict['boiler'] = False
        updated_sensors_dict['washing_machine'] = False

    if not sensors_dict['cold_water']:
        updated_sensors_dict['boiler'] = False
        updated_sensors_dict['washing_machine'] = False

    if sensors_dict['cold_water'] and not sensors_dict['smoke_detector']:
        hot_water_koef = sensors_dict['boiler_temperature']/(
            hot_water_target_temperature)

        if round((hot_water_koef-1)*100) <= -10:
            updated_sensors_dict['boiler'] = True

        if round((hot_water_koef-1)*100) >= 10:
            updated_sensors_dict['boiler'] = False

    if not sensors_dict['curtains'] == 'slightly_open':
        if sensors_dict['outdoor_light'] < 50 and not sensors_dict['bedroom_light']:
            updated_sensors_dict['curtains'] = 'open'

        if sensors_dict['outdoor_light'] > 50 or sensors_dict['bedroom_light']:
            updated_sensors_dict['curtains'] = 'close'

    if sensors_dict['smoke_detector']:
        for device in ['air_conditioner', 'bedroom_light', 'bathroom_light',
                       'boiler', 'washing_machine']:
            updated_sensors_dict[device] = False

    if not sensors_dict['smoke_detector']:
        temp_koef = sensors_dict['bedroom_temperature'] / (
            bedroom_target_temperature)

        if round((temp_koef-1)*100) >= 10:
            sensors_dict['air_conditioner'] = True

        if round((temp_koef-1)*100) <= -10:
            sensors_dict['air_conditioner'] = False

    update_sensors_data(updated_sensors_dict)

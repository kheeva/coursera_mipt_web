from __future__ import absolute_import, unicode_literals
from celery import task

import requests
import json
from django.conf import settings
from django.core.mail import EmailMessage
from .models import Setting


def get_sensors_data():
    auth_header = {'Authorization': f'Bearer {settings.SMART_HOME_ACCESS_TOKEN}'}
    try:
        api_response = requests.get(settings.SMART_HOME_API_URL, headers=auth_header)
        api_data = api_response.json()
    except Exception:
        return {}
    else:
        return api_data


def update_sensors_data(data):
    if not data:
        return
    data_to_send = {"controllers": []}
    for key, value in data.items():
        data_to_send['controllers'].append(
            {"name": key, "value": value}
        )
    auth_header = {'Authorization': f'Bearer {settings.SMART_HOME_ACCESS_TOKEN}'}
    try:
        response = requests.post(settings.SMART_HOME_API_URL,
                      headers=auth_header,
                      data=json.dumps(data_to_send))
        response = response.json()
    except Exception:
        status = 502
    else:
        status = 200 if response.get('status') == 'ok' else 502

    return status


@task()
def smart_home_manager():
    sensors_raw_data = get_sensors_data()

    if not sensors_raw_data.get('data'):
        return 502
    sensors_dict = {}
    updated_sensors_dict = {}
    leak_file = 'leak.state'
    try:
        with open(leak_file) as f:
            leak_emailed = f.read()
    except Exception:
        leak_emailed = 0
    else:
        pass

    bedroom_target_temperature = Setting.objects.get(
        controller_name='bedroom_target_temperature').value

    hot_water_target_temperature = Setting.objects.get(
        controller_name='hot_water_target_temperature').value

    for sensor in sensors_raw_data['data']:
        sensors_dict[sensor['name']] = sensor['value']

    if sensors_dict['leak_detector']:
        if sensors_dict['cold_water']:
            updated_sensors_dict['cold_water'] = 0

        if sensors_dict['hot_water']:
            updated_sensors_dict['hot_water'] = 0

        if sensors_dict['boiler']:
            updated_sensors_dict['boiler'] = 0

        if sensors_dict['washing_machine'] != 'off':
            updated_sensors_dict['washing_machine'] = 'off'

        if leak_emailed != '1':
            email = EmailMessage('leak_detector', 'Leak detected!',
                                 to=[settings.EMAIL_RECEPIENT])
            email.send()
            with open(leak_file, 'w') as f:
                f.write('1')
    else:
        with open(leak_file, 'w') as f:
            f.write('0')

    if not sensors_dict['cold_water']:
        if sensors_dict['boiler']:
            updated_sensors_dict['boiler'] = 0
        if sensors_dict['washing_machine'] != 'off':
            updated_sensors_dict['washing_machine'] = 'off'

    if sensors_dict['cold_water'] and not sensors_dict['smoke_detector'] and (
            not sensors_dict['leak_detector']):
        hot_water_koef = sensors_dict['boiler_temperature']/(
            hot_water_target_temperature)

        if round((hot_water_koef-1)*100) < -10:
            if not sensors_dict['boiler']:
                updated_sensors_dict['boiler'] = 1

        if round((hot_water_koef-1)*100) > 10:
            if sensors_dict['boiler']:
                updated_sensors_dict['boiler'] = 0

    if not sensors_dict['curtains'] == 'slightly_open':
        if sensors_dict['outdoor_light'] < 50 and not sensors_dict['bedroom_light']:
            if sensors_dict['curtains'] != 'open':
                updated_sensors_dict['curtains'] = 'open'

        if sensors_dict['outdoor_light'] > 50 or sensors_dict['bedroom_light']:
            if sensors_dict['curtains'] != 'close':
                updated_sensors_dict['curtains'] = 'close'

    if sensors_dict['smoke_detector']:
        for device in ['air_conditioner', 'bedroom_light', 'bathroom_light',
                       'boiler']:
            if sensors_dict[device]:
                updated_sensors_dict[device] = 0
        if sensors_dict['washing_machine'] != "off":
            updated_sensors_dict['washing_machine'] = "off"

    if not sensors_dict['smoke_detector']:
        temp_koef = sensors_dict['bedroom_temperature'] / (
            bedroom_target_temperature)

        if round((temp_koef-1)*100) > 10:
            if not sensors_dict['air_conditioner']:
                updated_sensors_dict['air_conditioner'] = 1

        if round((temp_koef-1)*100) < -10:
            if sensors_dict['air_conditioner']:
                updated_sensors_dict['air_conditioner'] = 0

    # if sensors_dict['washing_machine'] == 'broken':
    #     if sensors_dict['washing_machine']:
    #         updated_sensors_dict['washing_machine'] = 0
    #     if sensors_dict['cold_water']:
    #         updated_sensors_dict['cold_water'] = 0

    if updated_sensors_dict:
        # print(updated_sensors_dict)
        return update_sensors_data(updated_sensors_dict)

    return 200

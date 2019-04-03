from __future__ import absolute_import, unicode_literals
from celery import task

import requests
import json
from django.conf import settings
from django.core.mail import send_mail
from .models import Setting


def get_sensors_data():
    auth_header = {'Authorization': f'Bearer {settings.SMART_HOME_ACCESS_TOKEN}'}
    try:
        user_request = requests.get(settings.SMART_HOME_API_URL, headers=auth_header)
    except Exception:
        return {}
    else:
        return user_request.json()


def update_sensors_data(data):
    data_to_send = {"controllers": []}
    for key, value in data.items():
        data_to_send['controllers'].append(
            {"name": key, "value": value}
        )
    auth_header = {'Authorization': f'Bearer {settings.SMART_HOME_ACCESS_TOKEN}'}
    try:
        request = requests.post(settings.SMART_HOME_API_URL,
                      headers=auth_header,
                      data=json.dumps(data_to_send))
    except Exception:
        status = 502
    else:
        status = request.status_code
    return status


@task()
def smart_home_manager():
    sensors_raw_data = get_sensors_data()
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
        updated_sensors_dict['cold_water'] = 0
        updated_sensors_dict['hot_water'] = 0
        updated_sensors_dict['boiler'] = 0
        updated_sensors_dict['washing_machine'] = "off"

        if leak_emailed != '1':
            send_mail(
                subject='Leak detected',
                message='Leak detected! Water has been closed.',
                from_email=settings.EMAIL_USER,
                recipient_list=[settings.EMAIL_RECIPIENT, settings.EMAIL_RECEPIENT],
                fail_silently=True
            )
            with open(leak_file, 'w') as f:
                f.write('1')
    else:
        with open(leak_file, 'w') as f:
            f.write('0')

    if not sensors_dict['cold_water']:
        updated_sensors_dict['boiler'] = 0
        updated_sensors_dict['washing_machine'] = "off"

    if sensors_dict['cold_water'] and not sensors_dict['smoke_detector']:
        hot_water_koef = sensors_dict['boiler_temperature']/(
            hot_water_target_temperature)

        if round((hot_water_koef-1)*100) <= -10:
            updated_sensors_dict['boiler'] = 1

        if round((hot_water_koef-1)*100) >= 10:
            updated_sensors_dict['boiler'] = 0

    if not sensors_dict['curtains'] == 'slightly_open':
        if sensors_dict['outdoor_light'] < 50 and not sensors_dict['bedroom_light']:
            updated_sensors_dict['curtains'] = 'open'

        if sensors_dict['outdoor_light'] > 50 or sensors_dict['bedroom_light']:
            updated_sensors_dict['curtains'] = 'close'

    if sensors_dict['smoke_detector']:
        for device in ['air_conditioner', 'bedroom_light', 'bathroom_light',
                       'boiler']:
            updated_sensors_dict[device] = 0
        updated_sensors_dict['washing_machine'] = "off"

    if not sensors_dict['smoke_detector']:
        temp_koef = sensors_dict['bedroom_temperature'] / (
            bedroom_target_temperature)

        if round((temp_koef-1)*100) >= 10:
            updated_sensors_dict['air_conditioner'] = 1

        if round((temp_koef-1)*100) <= -10:
            updated_sensors_dict['air_conditioner'] = 0

    status = 200
    if updated_sensors_dict:
        status = update_sensors_data(updated_sensors_dict)
    return status

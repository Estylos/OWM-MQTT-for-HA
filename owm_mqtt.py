# Copyright (c) 2023 Esteban Cadic 
# This code is licensed under MIT license (see LICENSE file for details)

import os
import logging
import json
import time
import random
import requests
from paho.mqtt import client as mqtt_client
from requests.exceptions import HTTPError

# Logger
logging.basicConfig(
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOGGER_FILE')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('owm-mqtt')
logger.setLevel(level=os.getenv('LOGGER_LEVEL'))

# Generate a Client ID with the subscribe prefix
clientId = f'owm-mqtt-{random.randint(0, 100)}'

# OWM API
owmCall = f'https://api.openweathermap.org/data/2.5/onecall?units=metric&exclude=minutely&lat={os.getenv("OWM_LAT")}&lon={os.getenv("OWM_LON")}&appid={os.getenv("OWM_APIKEY")}'

# Datas to be published for HA
# [device_class, unique_id, name, value_template, additionals parameters]
deviceID = os.getenv('HA_DEVICE_ID')
deviceName = os.getenv('HA_DEVICE_NAME')
deviceTopic = os.getenv('HA_DEVICE_TOPIC')
datasToPublish = [
    ['temperature', 'current_temp', 'Température actuelle', '{{ value_json.current.temp }}', '"unit_of_measurement": "°C",'],
    ['humidity', 'current_hum', 'Humidité actuelle', '{{ value_json.current.humidity }}', '"unit_of_measurement": "%",'],
    ['temperature', 'today_max_temp', 'Température maximale aujourd\'hui', '{{ value_json.daily.0.temp.max }}', '"unit_of_measurement": "°C",'],
    ['temperature', 'tomorrow_temp', 'Température demain', '{{ value_json.daily.1.temp.day }}', '"unit_of_measurement": "°C",'],
    ['enum', 'current_weather', 'Météo actuelle', '{{ value_json.current.weather.0.main }}', ''],
    ['enum', '1h_weather', 'Météo dans 1h', '{{ value_json.hourly.1.weather.0.main }}', ''],
    ['enum', '2h_weather', 'Météo dans 2h', '{{ value_json.hourly.2.weather.0.main }}', ''],
    ['enum', '3h_weather', 'Météo dans 3h', '{{ value_json.hourly.3.weather.0.main }}', '']
    # YOU CAN ADD OR REMOVE LINES HERE
]

# Global variables
flagConnected = 0

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.info('Connected to MQTT Broker!')
            global flagConnected 
            flagConnected = 1
        else:
            logger.error('Failed to connect, return code %d\n', rc)

    client = mqtt_client.Client(clientId)
    client.username_pw_set(os.getenv('BROKER_USER'), os.getenv('BROKER_PASS'))
    client.on_connect = on_connect
    client.connect(os.getenv('BROKER_IP'), int(os.getenv('BROKER_PORT')))
    return client


def publish(client):

    while(not flagConnected):
        time.sleep(0.1)
        pass

    logger.info('Starting to publish OWM datas')
    logger.info('Publishing HA automatic MQTT discovery messages')

    for data in datasToPublish:
        configTopic = f'{deviceTopic}/{deviceID}/{data[1]}/config'
        msg = '{"device_class": "' + data[0] + '", "name": "' + data[2] + '", "state_topic":"' + deviceTopic + '/' + deviceID + '/state", "value_template": "' + data[3] + '","unique_id": "' + data[1] + '",' + data[4] + '"device": {"identifiers": ["' + deviceID + '"], "name": "' + deviceName + '", "manufacturer":"' + os.getenv("HA_DEVICE_MANUFACTURER") + '","model":"' + os.getenv("HA_DEVICE_MODEL") + '"}}'

        # Publish retain config messages for HA 
        result = client.publish(configTopic, msg, qos=0,retain=True) 
        if result[0] == 0:
            logger.debug(f'Send HA config "{msg}" to topic "{configTopic}"')
        else:
            logger.error(f'Failed to send HA config message to topic "{configTopic}"')


    while True:

        stateTopic = f'{deviceTopic}/{deviceID}/state'

        try:
            logger.info("Call OWM API")
            response = requests.get(owmCall)
            response.raise_for_status()
            jsonResponseStr = json.dumps(response.json()) # Raise an error if the response is not in JSON

            # Publish state messages for HA 
            result = client.publish(stateTopic, jsonResponseStr)
            
            if result[0] == 0:
                logger.debug(f'Send state "{jsonResponseStr}" to topic "{stateTopic}"')
            else:
                logger.error(f'Failed to send state message to topic "{stateTopic}"')

        # Catch if HTTP error occurred
        except HTTPError as http_err:
            logger.error(f'HTTP error occurred: {http_err}')
            client.publish(stateTopic, "HTTP error occurred (in the python script)")
        except Exception as err:
            logger.error(f'Other error occurred: {err}')
            client.publish(stateTopic, "Other error occurred (in the python script)")

        # Sleep for 30 mn
        time.sleep(60*30)
        
def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)
    client.loop_stop()


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        logger.info('Interrupted')

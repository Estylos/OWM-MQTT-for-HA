# OpenWeatherMap API to MQTT for Home Assistant

Simple python script that exposes elements of the OpenWeatherMap API on Home Assistant via MQTT. The script enables [automatic discovery](https://www.home-assistant.io/integrations/mqtt#mqtt-discovery) of the desired parameters by Home Assistant.
Finally, this script allows any desired value returned by the OWM API to be used on HA, enabling the creation of advanced routines using the weather.

## Getting Started

These instructions will cover usage information and for publishing OWM API parameters in MQTT and the docker container.

### Prerequisities

In order to run this container you'll need [docker installed](https://docs.docker.com/get-started/).

### Usage

#### Customisation of attributes to be published in MQTT

In the Python script, the variable ``datasToPublish`` contains the parameters returned by the OWM API to be published in MQTT to HA.
Each line contains 4 elements:
1. [The device class of the sensor in HA](https://www.home-assistant.io/integrations/sensor/)
2. The unique id of the sensor
3. The value template for decoding the parameter in the OWM API JSON response
4. Additional parameters to be added to the sensor configruation payload (like the unit of measurement...)

By default, the script publishes the current temperature and humidity, the current weather, the maximum tempeature for today and tomorrow, and the weather in one, two and three hours' time. With a well-managed alert on your home assistant, you can be alerted, for example, of the risk of rain in the next few hours (cyclists will thank you). The script uses [OWM's One Call 2.5 API](https://openweathermap.org/api/one-call-api), which already returns a lot of information on current weather and forecasts by hours and days (temperatures, humidity, weather, wind, rain, clouds...). If you have more specific needs, you should easily be able to modify the OWM API call to [another of their APIs](https://openweathermap.org/api).

#### Build and run the container

* Build the app:

```shell
docker build -t owmmqtt:latest .
```

* Run the app (environments variables are specified below)

```shell
docker run --env 'BROKER_IP=IP' --env 'BROKER_USER=USER' --env 'BROKER_PASS=PASS' --env 'OWM_APIKEY=KEY' owmmqtt
```

And now, if the connection to the MQTT broker is successful and the script is able to access the OWM API, you should see a new device appear in the Home Assistant MQTT integration.

#### Environment Variables

* `LOGGER_LEVEL` - Level of the logger (try DEBUG if you encounter a problem).
* `LOGGER_FILE` - Log file location in the container.
* `BROKER_IP` - IP of the MQTT broker.
* `BROKER_PORT` - Port of the MQTT broker.
* `BROKER_USER` - Account name on the MQTT broker.
* `BROKER_PASS` - Account password on the MQTT broker.
* `OWM_LAT` - OpenWeatherMap latitude of the geographical point. 
* `OWM_LON` - OpenWeatherMap longitude of the geographical point. 
* `OWM_APIKEY` - OpenWeatherMap API key. The free plan is clearly sufficient for domestic use. You must have one [here](https://openweathermap.org/).
* `HA_DEVICE_ID` - Home Assistant unique device ID. 
* `HA_DEVICE_NAME` - Home Assistant device name.
* `HA_DEVICE_TOPIC` - Home Assistant device MQTT topic.
* `HA_DEVICE_MANUFACTURER` - Home Assistant device manufacturer (useless).
* `HA_DEVICE_MODEL` - Home Assistant device model (useless).
  

## Built With

* Python 3.10:
  * paho-mqtt==1.6.1
  * requests==2.31.0


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Thanks to [IE-Concept](https://www.ie-concept.fr/), the company where I developed this piece of software as part of my internship project involving the home automation of their offices.
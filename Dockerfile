# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Logger
ENV LOGGER_LEVEL="INFO"
ENV LOGGER_FILE="latest.log"

# MQTT Config
ENV BROKER_IP=127.0.0.1
ENV BROKER_PORT=1883
ENV BROKER_USER="user"
ENV BROKER_PASS="password"

# OWM Config
ENV OWM_LAT=44.9332277
ENV OWM_LON=4.8920811
ENV OWM_APIKEY=

# Sensor config
ENV HA_DEVICE_ID="owmdata"
ENV HA_DEVICE_NAME="OWM Data"
ENV HA_DEVICE_TOPIC="homeassistant/sensor"
ENV HA_DEVICE_MANUFACTURER="Estylos"
ENV HA_DEVICE_MODEL="OWM API Client 1.0"


# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "owm_mqtt.py"]

FROM jfloff/alpine-python:3.6

COPY ./ha-alexa-tts /ha-alexa-tts
COPY alexa-tts-mqtt.py /

RUN apk add curl jq

RUN pip install paho-mqtt

CMD [ "python", "/alexa-tts-mqtt.py" ]
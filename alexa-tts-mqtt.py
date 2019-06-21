import json
import time
import paho.mqtt.client as mqtt
from subprocess import Popen, PIPE, STDOUT, call
from os import environ

MQTT_BROKER = environ.get('MQTT_BROKER')
MQTT_PORT = environ.get('MQTT_PORT', 1883)
MQTT_USER = environ.get('MQTT_USER')
MQTT_PASS = environ.get('MQTT_PASS')
MQTT_BASE_TOPIC = environ.get('MQTT_TOPIC', 'alexa')
MQTT_STATUS_TOPIC = 'status'


def send_alexa_message(device, msg):
    cmd = '/ha-alexa-tts/alexa_remote_control.sh -d "{}" -e speak:"{}"'.format(
        device, msg)

    cmd_output = _call(cmd)

    print(cmd_output)


def get_device_list():
    cmd = '/ha-alexa-tts/alexa_remote_control.sh -a'

    cmd_output = _call(cmd)

    return list(filter(None, cmd_output.split('\n')))


def on_message(client, userdata, message):
    parts = message.topic.replace('{}/'.format(MQTT_BASE_TOPIC), '').split('/')

    device = parts[1] or None
    tts_message = str(message.payload.decode("utf-8"))

    print(device)
    print(tts_message)

    try:
        send_alexa_message(device, tts_message)
    except RuntimeError as e:
        _handle_exception(client, e)


def on_connect(client, userData, flags, rc):
    if rc == 0:
        try:
            devices = get_device_list()

            # Subscribe to TTS topic
            client.subscribe('{}/tts/#'.format(MQTT_BASE_TOPIC), 0)

            client.publish('{}/{}'.format(MQTT_BASE_TOPIC, MQTT_STATUS_TOPIC),
                           json.dumps(dict(status='online',
                                           available_devices=devices)),
                           retain=True)

        except RuntimeError as e:
            _handle_exception(client, e)

    else:
        print("Connection error ", rc)


def on_disconnect(client, userData, rc):
    client.loop_stop()


def on_log(client, userdata, level, buf):
    print(buf)


def _call(cmd):
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
              close_fds=True)

    p.wait()

    cmd_output = p.stdout.read().decode('utf-8')

    if p.returncode is 1:
        raise RuntimeError(cmd_output)

    return cmd_output


def _handle_exception(client, e):
    client.publish('{}/{}'.format(MQTT_BASE_TOPIC, MQTT_STATUS_TOPIC),
                   json.dumps(dict(status='offline', message=e)), retain=True)
    client.disconnect()

    raise e


client = mqtt.Client("alexatts")

if MQTT_USER and MQTT_PASS:
    client.username_pw_set(MQTT_USER, password=MQTT_PASS)

client.on_message = on_message
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_log = on_log

client.connect(MQTT_BROKER, port=MQTT_PORT)

client.loop_forever()

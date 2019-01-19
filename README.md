# alexa-tts-mqtt

Make Alexa speak via MQTT!

Adapted from [walthowd/ha-alexa-tts](https://github.com/walthowd/ha-alexa-tts).

## Usage
```
docker create \
    --name alexa-tts-mqtt \
    -v </path/to/config>:/config \
    -e PYTHONUNBUFFERED=0 \
    -e MQTT_BROKER=<MQTT_BROKER_IP> \
    -e MQTT_USER=<MQTT_BROKER_USER> \
    -e MQTT_PASS=<MQTT_BROKER_PASSWORD>" \
    oblogic7/alexa-tts-mqtt
```

## Parameters (Required)

* `-v /config` - Path where your `secrets.yaml` file and `.alexa.cookie` files are located.
* `-e PYTHONUNBUFFERED=0` - Required for container logging to work properly.
* `-e MQTT_BROKER` - IP or hostname for your MQTT broker

## Parameters (Optional)
* `-e MQTT_USER` - User name used to authenticate to your MQTT broker.
* `-e MQTT_PASS` - Password used to authenticate to your MQTT broker.
* `-e MQTT_TOPIC` - Override the root MQTT topic to listen on.  Default: `alexa`

## Info
Some changes have been made to the original [walthowd/ha-alexa-tts](https://github.com/walthowd/ha-alexa-tts)
scripts for compatibility.  Currently, only TTS action is supported, but other
commands may be added in the future.

### Config Files
As documented by [walthowd/ha-alexa-tts](https://github.com/walthowd/ha-alexa-tts), the `secrets.yaml` file should contain
two keys (`alexa_email`, `alexa_password`).  These keys are used to authenticate
against the alexa service.  If authentication fails, a cookie file can be used
to authenticate instead.  For use in this container, these files should be availble
in the volume mapped to the `/config` directory.

### TTS Messages
Messages are routed to a specific Alexa device by using the device name in the
message topic.  The published payload is used as the message.  The device name
is case sensitive.  Apostrophes _should_ work assuming that they are not escaped
by the client publishing the message.

For example, publishing a message to the topic `alexa/tts/Kitchen` will play the
message on the Alexa device named Kitchen.

### Status Updates
Status update messages are published and retained on the `MQTT_STATUS_TOPIC`.
It is useful to subscribe to these messages to be notified of issues with the
Alexa cookie or other errors that may be encountered.

#####Online Message:
```
{
    'status': 'online',
    'available_devices': [...]  // list of device names
}
```

#####Offline Message:
```
{
    'status': 'offline',
    'message': 'RuntimeError('ERROR: Amazon Login was unsuccessful.)'
}
```
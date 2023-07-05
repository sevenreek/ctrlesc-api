
from fastapi_mqtt import FastMQTT, MQTTConfig

mqtt_config = MQTTConfig()
mqtt = FastMQTT(config=mqtt_config)


@mqtt.on_connect()
def connect(client, flags, rc, properties):
    pass


@mqtt.on_message()
async def message(client, topic, payload, qos, properties):
    pass


@mqtt.subscribe("my/mqtt/topic/#")
async def message_to_topic(client, topic, payload, qos, properties):
    pass


@mqtt.on_disconnect()
def disconnect(client, packet, exc=None):
    pass


@mqtt.on_subscribe()
def subscribe(client, mid, qos, properties):
    pass

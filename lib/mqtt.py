from gmqtt import Client as MQTTClient
from os import getpid
from settings import settings
from typing import Literal, Callable, Annotated
from collections import defaultdict
from fastapi import Depends

MessageHandler = Callable[[str, bytes], None]
MessageHandlerTuple = tuple[str, MessageHandler]


client = MQTTClient(f"fastapi-{getpid()}")
message_handlers: list[MessageHandlerTuple] = []


def subscribe(topic: str, handler: MessageHandler):
    message_handlers.append((topic, handler))


def on_connect(client, flags, rc, properties):
    print("MQTT Connected")


def on_message(client: MQTTClient, topic: str, payload: bytes, qos: int, properties):
    for handler_topic, handler in message_handlers:
        if not topic.startswith(handler_topic):
            continue
        handler(topic, payload)


def on_disconnect(client, packet, exc=None):
    print("MQTT Disconnected")


def on_subscribe(client, mid, qos, properties):
    print("MQTT Subscribed")


client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.on_subscribe = on_subscribe


def get_client():
    return client


DependsMQTT = Annotated[MQTTClient, Depends(get_client)]


async def on_start():
    await client.connect(settings.mqtt_url, int(settings.mqtt_port))


async def on_exit():
    await client.disconnect()

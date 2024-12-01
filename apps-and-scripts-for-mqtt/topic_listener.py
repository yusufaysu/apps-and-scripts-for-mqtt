import os
import paho.mqtt.client as mqtt

broker_address = "icemqtt.com.tr"
port = 1883

client = mqtt.Client(callback_api_version=2)
client.connect(broker_address, port, 60)


def on_message(client, userdata, message):
    topic = message.topic
    payload = message.payload.decode("utf-8")
    print(f"topic: {topic} Data: {payload}")

client.on_message = on_message
client.subscribe("/#")
client.loop_start()

try:
    while True:
        pass
except KeyboardInterrupt:
    # Ctrl+C olayı
    client.disconnect()
    client.loop_stop()

import os
import paho.mqtt.client as mqtt
from dotenv import find_dotenv, load_dotenv

env_file_path = find_dotenv()
load_dotenv(env_file_path)

broker_address = os.getenv("MQTT_BROKER")
port = int(os.getenv("MQTT_PORT"))

client = mqtt.Client()
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
